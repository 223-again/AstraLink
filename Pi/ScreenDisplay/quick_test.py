#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScreenDisplay 快速测试脚本
简化版本，用于快速测试基本功能
"""

import requests
import time
import random

BASE_URL = "http://localhost:5000"

def quick_test():
    """快速测试所有功能"""
    print("🚀 ScreenDisplay 快速测试")
    print("=" * 30)
    
    # 测试表情
    moods = ['happy', 'thinking', 'cool', 'smiling']
    for mood in moods:
        try:
            requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=3)
            print(f"✅ 表情: {mood}")
            time.sleep(0.5)
        except:
            print(f"❌ 表情: {mood}")
    
    # 测试对话
    try:
        requests.post(f"{BASE_URL}/api/add_history", 
                     json={'message': '测试消息', 'response': '测试回复'}, 
                     timeout=3)
        print("✅ 对话更新")
    except:
        print("❌ 对话更新")
    
    # 测试WiFi质量
    try:
        requests.post(f"{BASE_URL}/api/wifi_quality", 
                     json={'wifi_quality': random.randint(50, 100)}, 
                     timeout=3)
        print("✅ WiFi质量")
    except:
        print("❌ WiFi质量")
    
    # 测试状态
    try:
        requests.post(f"{BASE_URL}/api/status", 
                     json={'status': random.choice([0, 1])}, 
                     timeout=3)
        print("✅ 状态更新")
    except:
        print("❌ 状态更新")
    
    # 测试传感器
    try:
        response = requests.get(f"{BASE_URL}/api/sensor", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 传感器: {data.get('temperature', 'N/A')}°C, {data.get('humidity', 'N/A')}%")
        else:
            print("❌ 传感器")
    except:
        print("❌ 传感器")
    
    print("=" * 30)
    print("🎉 快速测试完成!")

if __name__ == "__main__":
    quick_test() 