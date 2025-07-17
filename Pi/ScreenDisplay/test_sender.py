#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScreenDisplay 测试发送脚本
用于测试各种数据发送功能
"""

import requests
import json
import time
import random
from datetime import datetime

# ScreenDisplay服务地址
BASE_URL = "http://localhost:5000"

def test_mood_update():
    """测试表情更新"""
    print("🎭 测试表情更新...")
    
    moods = ['happy', 'sad', 'angry', 'surprised', 'cool', 'default', 'thinking', 'smiling']
    
    for mood in moods:
        try:
            response = requests.post(f"{BASE_URL}/api/mood", 
                                   json={'mood': mood}, 
                                   timeout=5)
            if response.status_code == 200:
                print(f"✅ 表情更新成功: {mood}")
            else:
                print(f"❌ 表情更新失败: {mood} - {response.status_code}")
        except Exception as e:
            print(f"❌ 表情更新异常: {mood} - {e}")
        
        time.sleep(1)  # 等待1秒

def test_conversation_update():
    """测试对话更新"""
    print("\n💬 测试对话更新...")
    
    conversations = [
        {
            "message": "你好，今天天气怎么样？",
            "response": "今天天气晴朗，温度25度，非常适合外出活动。"
        },
        {
            "message": "播放音乐",
            "response": "好的，正在为您播放《青花瓷》。"
        },
        {
            "message": "推荐一部电影",
            "response": "我推荐《星际穿越》，这是一部非常经典的科幻电影。"
        },
        {
            "message": "调节音量",
            "response": "已将音量调节到50%。"
        }
    ]
    
    for conv in conversations:
        try:
            response = requests.post(f"{BASE_URL}/api/add_history", 
                                   json=conv, 
                                   timeout=5)
            if response.status_code == 200:
                print(f"✅ 对话更新成功: {conv['message'][:20]}...")
            else:
                print(f"❌ 对话更新失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 对话更新异常: {e}")
        
        time.sleep(1)

def test_wifi_quality():
    """测试WiFi质量更新"""
    print("\n📶 测试WiFi质量更新...")
    
    for quality in range(0, 101, 10):
        try:
            response = requests.post(f"{BASE_URL}/api/wifi_quality", 
                                   json={'wifi_quality': quality}, 
                                   timeout=5)
            if response.status_code == 200:
                print(f"✅ WiFi质量更新成功: {quality}%")
            else:
                print(f"❌ WiFi质量更新失败: {quality}% - {response.status_code}")
        except Exception as e:
            print(f"❌ WiFi质量更新异常: {quality}% - {e}")
        
        time.sleep(0.5)

def test_status_update():
    """测试状态更新"""
    print("\n🔴 测试状态更新...")
    
    for status in [0, 1]:
        try:
            response = requests.post(f"{BASE_URL}/api/status", 
                                   json={'status': status}, 
                                   timeout=5)
            if response.status_code == 200:
                status_text = "活跃" if status == 1 else "空闲"
                print(f"✅ 状态更新成功: {status_text}")
            else:
                print(f"❌ 状态更新失败: {status} - {response.status_code}")
        except Exception as e:
            print(f"❌ 状态更新异常: {status} - {e}")
        
        time.sleep(1)

def test_sensor_force_update():
    """测试传感器强制更新"""
    print("\n🌡️ 测试传感器强制更新...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sensor/force_update", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 传感器强制更新成功")
            print(f"   温度: {data.get('temperature', 'N/A')}°C")
            print(f"   湿度: {data.get('humidity', 'N/A')}%")
            print(f"   状态: {data.get('status', 'N/A')}")
        else:
            print(f"❌ 传感器强制更新失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 传感器强制更新异常: {e}")

def test_api_endpoints():
    """测试所有API端点"""
    print("\n🔍 测试API端点...")
    
    endpoints = [
        ("/api/mood", "GET"),
        ("/api/sensor", "GET"),
        ("/api/conversation", "GET"),
        ("/api/wifi_quality", "GET"),
        ("/api/status", "GET"),
        ("/api/yiyan", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - 正常")
            else:
                print(f"❌ {method} {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint} - 异常: {e}")

def test_webSocket_simulation():
    """模拟WebSocket事件（通过HTTP API）"""
    print("\n🔌 模拟WebSocket事件...")
    
    # 模拟快速连续的数据更新
    for i in range(5):
        # 随机表情
        mood = random.choice(['happy', 'thinking', 'cool', 'smiling'])
        requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=2)
        
        # 随机WiFi质量
        wifi_quality = random.randint(20, 100)
        requests.post(f"{BASE_URL}/api/wifi_quality", json={'wifi_quality': wifi_quality}, timeout=2)
        
        # 随机状态
        status = random.choice([0, 1])
        requests.post(f"{BASE_URL}/api/status", json={'status': status}, timeout=2)
        
        print(f"✅ 第{i+1}轮WebSocket模拟完成")
        time.sleep(0.5)

def interactive_test():
    """交互式测试"""
    print("\n🎮 交互式测试模式")
    print("输入命令进行测试:")
    print("1. mood <表情名> - 更新表情")
    print("2. conv <消息> <回复> - 更新对话")
    print("3. wifi <质量> - 更新WiFi质量")
    print("4. status <0/1> - 更新状态")
    print("5. sensor - 强制更新传感器")
    print("6. quit - 退出")
    
    while True:
        try:
            command = input("\n请输入命令: ").strip()
            if command == "quit":
                break
            elif command == "sensor":
                test_sensor_force_update()
            elif command.startswith("mood "):
                mood = command.split(" ", 1)[1]
                response = requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=5)
                print(f"表情更新: {'成功' if response.status_code == 200 else '失败'}")
            elif command.startswith("conv "):
                parts = command.split(" ", 2)
                if len(parts) >= 3:
                    message, response_text = parts[1], parts[2]
                    response = requests.post(f"{BASE_URL}/api/add_history", 
                                           json={'message': message, 'response': response_text}, 
                                           timeout=5)
                    print(f"对话更新: {'成功' if response.status_code == 200 else '失败'}")
                else:
                    print("格式错误: conv <消息> <回复>")
            elif command.startswith("wifi "):
                try:
                    quality = int(command.split(" ")[1])
                    response = requests.post(f"{BASE_URL}/api/wifi_quality", 
                                           json={'wifi_quality': quality}, 
                                           timeout=5)
                    print(f"WiFi质量更新: {'成功' if response.status_code == 200 else '失败'}")
                except ValueError:
                    print("WiFi质量必须是数字")
            elif command.startswith("status "):
                try:
                    status = int(command.split(" ")[1])
                    response = requests.post(f"{BASE_URL}/api/status", 
                                           json={'status': status}, 
                                           timeout=5)
                    print(f"状态更新: {'成功' if response.status_code == 200 else '失败'}")
                except ValueError:
                    print("状态必须是0或1")
            else:
                print("未知命令")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")

def main():
    """主函数"""
    print("🚀 ScreenDisplay 测试发送脚本")
    print("=" * 50)
    print(f"目标服务器: {BASE_URL}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 检查服务器连接
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保ScreenDisplay服务正在运行")
        return
    
    # 运行测试
    test_api_endpoints()
    test_mood_update()
    test_conversation_update()
    test_wifi_quality()
    test_status_update()
    test_sensor_force_update()
    test_webSocket_simulation()
    
    # 交互式测试
    interactive_test()
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    main() 