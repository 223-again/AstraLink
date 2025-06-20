# 迁移自Esp32/baidu_audio.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

# ... existing code ... 

import json
import time
import binascii
import requests
import asyncio
import uuid

# 配置音频采样率与设备ID
audiorate = 16000
# 树莓派下用uuid生成唯一ID
try:
    dev_cuid = uuid.getnode()
    dev_cuid = hex(dev_cuid)[2:]
except Exception:
    dev_cuid = "raspberrypi"

global_token = None
token_expiration_time = 0

def fetch_token(API_Key, Secret_Key):
    start_time = time.time()
    url = f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers)
    print(f"获取 token 耗时: {time.time() - start_time:.2f} 秒")
    response_data = response.json()
    access_token = response_data.get("access_token")
    expires_in = response_data.get("expires_in", 0)
    expiration_time = time.time() + expires_in
    return access_token, expiration_time

def get_token(API_Key, Secret_Key):
    global global_token, token_expiration_time
    if not global_token or time.time() >= token_expiration_time:
        print("Token 不存在或已过期，正在重新获取...")
        global_token, token_expiration_time = fetch_token(API_Key, Secret_Key)
    return global_token

def recongize(apikey, sercretkey, audiofile, dev_pid=80001, chunk_size=4096):
    token = get_token(apikey, sercretkey)
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={token}'
    headers = {
        'Content-Type': 'audio/pcm;rate=16000',
    }
    start_time = time.time()
    response = None
    try:
        with open(audiofile, 'rb') as f:
            response = requests.post(url, data=f, headers=headers)
        print(f"上传音频耗时: {time.time() - start_time:.2f} 秒")
        response_text = response.text
        print(f"原始响应文本: {response_text}")
        results = json.loads(response_text)
        print(f"返回数据: {results}")
        if not results:
            raise ValueError("返回数据为空")
        if results.get("err_no") == 0:
            if "result" in results and results["result"]:
                result_text = "".join(results["result"])
                return result_text
            else:
                raise ValueError("返回数据中没有识别结果")
        else:
            error_msg = results.get("err_msg", "未知错误")
            error_no = results.get("err_no", "未知错误码")
            raise ValueError(f"识别错误: {error_msg}, 错误码: {error_no}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应文本: {response_text}")
        raise ValueError(f"JSON解析错误: {e}")
    except ValueError as e:
        print(f"处理错误: {e}")
        raise
    except Exception as e:
        print(f"请求异常: {str(e)}")
        raise
    finally:
        if response:
            response.close()

async def speech_tts(apikey, sercretkey, text_tts):
    token = get_token(apikey, sercretkey)
    text = binascii.hexlify(text_tts.encode('utf-8')).decode("utf-8")
    text_urlencode = ''
    for i in range(0, len(text)):
        if i % 2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={token}&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
    try:
        response = requests.get(tts_url, stream=True)
        if response.status_code != 200:
            raise ValueError(f"TTS请求失败，状态码: {response.status_code}")
        # 保存音频流到文件
        with open("tts_output.wav", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("TTS音频已保存为 tts_output.wav")
        # 可选：播放音频（需安装playsound或pyaudio/wave等）
        # from playsound import playsound
        # playsound("tts_output.wav")
    except Exception as e:
        print(f"TTS处理异常: {str(e)}")
        raise
    finally:
        if response:
            response.close()

if __name__ == "__main__":
    apikey = "your_api_key"
    sercretkey = "your_secret_key"
    try:
        recognized_text = recongize(apikey, sercretkey, "recording.wav")
        print(f"识别结果: {recognized_text}")
    except ValueError as e:
        print(f"语音识别错误: {e}")
    try:
        asyncio.run(speech_tts(apikey, sercretkey, "你好，世界！"))
    except Exception as e:
        print(f"语音合成错误: {e}") 