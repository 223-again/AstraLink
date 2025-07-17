#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星链风格界面测试脚本
专门用于测试星链风格的炫酷效果
"""

import requests
import time
import random
import threading
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def starlink_visual_test():
    """星链风格视觉效果测试"""
    print("🚀 星链风格视觉效果测试")
    print("=" * 50)
    print("访问 http://127.0.0.1:5000/starlink 查看效果")
    print("=" * 50)
    
    # 快速表情切换测试
    print("🎭 快速表情切换测试...")
    moods = ['happy', 'thinking', 'cool', 'smiling', 'surprised', 'default']
    for i in range(10):
        mood = random.choice(moods)
        try:
            requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=2)
            print(f"  ✅ 表情: {mood}")
        except:
            print(f"  ❌ 表情: {mood}")
        time.sleep(0.3)
    
    # 对话流测试
    print("\n💬 对话流测试...")
    conversations = [
        ("系统启动", "星链系统已就绪，所有模块运行正常"),
        ("检查轨道", "检测到42颗卫星在轨运行，信号强度优秀"),
        ("天气查询", "当前轨道天气晴朗，能见度良好"),
        ("任务状态", "所有任务执行中，系统性能达到预期"),
        ("连接测试", "WebSocket连接稳定，实时数据传输正常")
    ]
    
    for i, (msg, resp) in enumerate(conversations):
        try:
            requests.post(f"{BASE_URL}/api/add_history", 
                         json={'message': msg, 'response': resp}, 
                         timeout=2)
            print(f"  ✅ 对话 {i+1}: {msg}")
        except:
            print(f"  ❌ 对话 {i+1}: {msg}")
        time.sleep(1)
    
    # WiFi质量波动测试
    print("\n📶 WiFi质量波动测试...")
    for i in range(20):
        quality = random.randint(30, 100)
        try:
            requests.post(f"{BASE_URL}/api/wifi_quality", 
                         json={'wifi_quality': quality}, 
                         timeout=2)
            print(f"  📊 WiFi质量: {quality}%")
        except:
            print(f"  ❌ WiFi质量更新失败")
        time.sleep(0.2)
    
    # 状态切换测试
    print("\n🔴 状态切换测试...")
    for i in range(10):
        status = random.choice([0, 1])
        try:
            requests.post(f"{BASE_URL}/api/status", 
                         json={'status': status}, 
                         timeout=2)
            status_text = "活跃" if status == 1 else "空闲"
            print(f"  🔄 状态: {status_text}")
        except:
            print(f"  ❌ 状态更新失败")
        time.sleep(0.5)

def continuous_data_stream():
    """持续数据流测试"""
    print("\n🌊 持续数据流测试 (按Ctrl+C停止)...")
    
    def stream_data():
        while True:
            try:
                # 随机表情
                mood = random.choice(['happy', 'thinking', 'cool', 'smiling'])
                requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=1)
                
                # 随机WiFi质量
                wifi_quality = random.randint(50, 100)
                requests.post(f"{BASE_URL}/api/wifi_quality", json={'wifi_quality': wifi_quality}, timeout=1)
                
                # 随机状态
                status = random.choice([0, 1])
                requests.post(f"{BASE_URL}/api/status", json={'status': status}, timeout=1)
                
                print(f"  🔄 数据流: {mood} | WiFi:{wifi_quality}% | 状态:{status}")
                
            except Exception as e:
                print(f"  ❌ 数据流错误: {e}")
            
            time.sleep(0.5)
    
    # 在后台线程中运行
    stream_thread = threading.Thread(target=stream_data, daemon=True)
    stream_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ 数据流测试已停止")

def test_webSocket_effects():
    """测试WebSocket特效"""
    print("\n🔌 WebSocket特效测试...")
    
    # 模拟高频数据更新
    for i in range(30):
        try:
            # 快速表情切换
            mood = random.choice(['happy', 'thinking', 'cool', 'smiling', 'surprised'])
            requests.post(f"{BASE_URL}/api/mood", json={'mood': mood}, timeout=1)
            
            # 快速WiFi变化
            wifi_quality = random.randint(20, 100)
            requests.post(f"{BASE_URL}/api/wifi_quality", json={'wifi_quality': wifi_quality}, timeout=1)
            
            # 快速状态切换
            status = random.choice([0, 1])
            requests.post(f"{BASE_URL}/api/status", json={'status': status}, timeout=1)
            
            print(f"  ⚡ 特效 {i+1}/30: {mood} | {wifi_quality}% | {status}")
            
        except Exception as e:
            print(f"  ❌ 特效错误: {e}")
        
        time.sleep(0.1)  # 100ms间隔，测试实时性

def main():
    """主函数"""
    print("🚀 星链风格界面测试脚本")
    print("=" * 60)
    print(f"目标服务器: {BASE_URL}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查服务器连接
    try:
        response = requests.get(f"{BASE_URL}/starlink", timeout=5)
        if response.status_code == 200:
            print("✅ 星链风格页面可访问")
        else:
            print(f"⚠️ 星链风格页面响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法访问星链风格页面: {e}")
        print("请确保ScreenDisplay服务正在运行")
        return
    
    # 运行测试
    starlink_visual_test()
    test_webSocket_effects()
    
    # 询问是否运行持续数据流测试
    try:
        choice = input("\n是否运行持续数据流测试？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            continuous_data_stream()
    except KeyboardInterrupt:
        print("\n⏹️ 测试已停止")
    
    print("\n🎉 星链风格测试完成!")
    print("💡 提示:")
    print("  - 访问 http://localhost:5000/starlink 查看星链风格界面")
    print("  - 按 F 键进入全屏模式")
    print("  - 按 T 键测试轨道动画")
    print("  - 按 Ctrl+R 强制更新传感器数据")

if __name__ == "__main__":
    main() 