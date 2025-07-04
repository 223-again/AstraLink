from flask import Flask, jsonify, send_from_directory, render_template, request
from flask_socketio import SocketIO, emit
import datetime
import threading
import time
import requests
import asyncio
import concurrent.futures
from functools import lru_cache
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Home Assistant配置
HA_BASE_URL = "http://192.168.101.246:8123"
HA_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmQ1ZDI1NGZhNTA0NTRhOTRhZDRjYzYyZGU5MWVkYyIsImlhdCI6MTc0MTY5NjI0NywiZXhwIjoyMDU3MDU2MjQ3fQ.dIc5ebY-FBbCApzPNKcfUweKxpdoKIx9EddOdGmbEV8"
HA_HEADERS = {
    "Authorization": f"Bearer {HA_API_KEY}",
    "Content-Type": "application/json"
}

_data_lock = threading.Lock()
_current_data = {
    'temperature': None,
    'humidity': None,
    'last_update': None,
    'status': 'waiting'
}

# 添加对话历史变量
_conversation = {
    'message': None,
    'response': None
}

# 添加WiFi信号和状态变量
_wifi_quality = 0
_status = 0

# 缓存机制
_cache = {}
_cache_timeout = 2  # 2秒缓存

def get_cache_key(key):
    return f"cache_{key}"

def is_cache_valid(key):
    cache_key = get_cache_key(key)
    if cache_key in _cache:
        timestamp, _ = _cache[cache_key]
        return time.time() - timestamp < _cache_timeout
    return False

def get_cached_data(key):
    cache_key = get_cache_key(key)
    if is_cache_valid(key):
        return _cache[cache_key][1]
    return None

def set_cached_data(key, data):
    cache_key = get_cache_key(key)
    _cache[cache_key] = (time.time(), data)

def get_ha_sensor_data():
    # 检查缓存
    cached_data = get_cached_data("ha_sensor")
    if cached_data:
        return cached_data
    
    try:
        # 并行获取温度和湿度数据
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            temp_future = executor.submit(
                requests.get,
                f"{HA_BASE_URL}/api/states/sensor.temperature_humidity_sensor_12a5_temperature",
                headers=HA_HEADERS,
                timeout=3  # 减少超时时间
            )
            humidity_future = executor.submit(
                requests.get,
                f"{HA_BASE_URL}/api/states/sensor.temperature_humidity_sensor_12a5_humidity",
                headers=HA_HEADERS,
                timeout=3
            )
            
            temp_response = temp_future.result()
            humidity_response = humidity_future.result()
        
        if temp_response.status_code == 200 and humidity_response.status_code == 200:
            temp_data = temp_response.json()
            humidity_data = humidity_response.json()
            
            result = {
                'temperature': round(float(temp_data['state']), 1),
                'humidity': round(float(humidity_data['state']), 1),
                'last_update': time.time(),
                'status': 'success'
            }
            
            # 设置缓存
            set_cached_data("ha_sensor", result)
            return result
        else:
            return {'status': 'error'}
    except Exception as e:
        print(f"Error fetching HA data: {e}")
        return {'status': 'error'}

def update_sensor_data():
    time.sleep(1)  # 减少初始延迟
    while True:
        try:
            sensor_data = get_ha_sensor_data()
            with _data_lock:
                _current_data.update(sensor_data)
            
            # 通过WebSocket推送数据更新
            socketio.emit('sensor_update', sensor_data)
            
        except Exception as e:
            print(f"Error in update_sensor_data: {e}")
            with _data_lock:
                _current_data['status'] = 'error'
        time.sleep(2)  # 减少轮询间隔到2秒

# 启动传感器数据更新线程
sensor_thread = threading.Thread(target=update_sensor_data, daemon=True)
sensor_thread.start()

current_mood = 'default'

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # 连接时立即发送当前数据
    with _data_lock:
        socketio.emit('sensor_update', _current_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update():
    """客户端请求立即更新数据"""
    sensor_data = get_ha_sensor_data()
    with _data_lock:
        _current_data.update(sensor_data)
    socketio.emit('sensor_update', sensor_data)

# 移除时间API，改为前端直接获取
# @app.route('/api/time')
# def get_time():
#     now = datetime.datetime.now()
#     return jsonify({
#         'time': now.strftime('%H:%M:%S'),
#         'date': now.strftime('%Y-%m-%d')
#     })

@app.route('/api/yiyan')
def get_yiyan():
    # 检查缓存
    cached_yiyan = get_cached_data("yiyan")
    if cached_yiyan:
        return jsonify(cached_yiyan)
    
    try:
        resp = requests.get('http://192.168.101.129:8000/?encode=text&c=i', timeout=2)
        result = {'yiyan': resp.text.strip()}
        set_cached_data("yiyan", result)
        return jsonify(result)
    except:
        return jsonify({'yiyan': '获取失败'})

@app.route('/api/mood', methods=['GET', 'POST'])
def api_mood():
    if request.method == 'POST':
        data = request.get_json() or request.form
        mood = data.get('mood')
        if mood:
            global current_mood
            current_mood = mood
            # 通过WebSocket推送表情更新
            socketio.emit('mood_update', {'mood': mood})
            return jsonify({'status': 'ok', 'mood': mood})
        return jsonify({'status': 'error', 'msg': 'No mood provided'}), 400
    else:
        return jsonify({'mood': current_mood})

@app.route('/api/sensor')
def get_sensor():
    with _data_lock:
        return jsonify(_current_data)

@app.route('/api/sensor/force_update')
def force_update_sensor():
    """强制更新传感器数据"""
    sensor_data = get_ha_sensor_data()
    with _data_lock:
        _current_data.update(sensor_data)
    socketio.emit('sensor_update', sensor_data)
    return jsonify(sensor_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emoji/<filename>')
def emoji(filename):
    return send_from_directory('emoji', filename)

@app.route('/api/add_history', methods=['POST'])
def add_history():
    data = request.get_json() or request.form
    message = data.get('message')
    response = data.get('response')
    
    if message and response:
        global _conversation
        _conversation = {
            'message': message,
            'response': response
        }
        # 通过WebSocket推送对话更新
        socketio.emit('conversation_update', _conversation)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'msg': 'Missing message or response'}), 400

@app.route('/api/conversation')
def get_conversation():
    return jsonify(_conversation)

@app.route('/api/wifi_quality', methods=['GET', 'POST'])
def wifi_quality():
    global _wifi_quality
    if request.method == 'POST':
        data = request.get_json() or request.form
        quality = data.get('wifi_quality')
        if quality is not None:
            _wifi_quality = int(quality)
            # 通过WebSocket推送WiFi质量更新
            socketio.emit('wifi_update', {'quality': _wifi_quality})
            return jsonify({'status': 'ok'})
        return jsonify({'status': 'error', 'msg': 'No quality value provided'}), 400
    return jsonify({'quality': _wifi_quality})

@app.route('/api/status', methods=['GET', 'POST'])
def status():
    global _status
    if request.method == 'POST':
        data = request.get_json() or request.form
        status = data.get('status')
        if status is not None:
            _status = int(status)
            # 通过WebSocket推送状态更新
            socketio.emit('status_update', {'status': _status})
            return jsonify({'status': 'ok'})
        return jsonify({'status': 'error', 'msg': 'No status value provided'}), 400
    return jsonify({'status': _status})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
