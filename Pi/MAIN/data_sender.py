import json
import requests
import asyncio
import base64
import time

# 本地API端点配置
ENDPOINTS = {
    "ai_chat":     "/api/add_history",
    "status":      "/api/status",
    "emoji":       "/api/mood",
    "sensor":      "/api/sensor",
    "time":        "/api/time",
    "yiyan":       "/api/yiyan",
    "conversation": "/api/conversation"
}

# 服务器配置
LOCAL_HOST = "http://127.0.0.1:5000"
EMBY_HOST = "http://192.168.101.217:5001"

async def send_data(attr, content1, content2="", timeout=5):
    """发送数据到本地API服务器"""
    path = ENDPOINTS.get(attr)
    if not path:
        print(f'Error: Unknown attribute "{attr}"')
        return None
    
    url = LOCAL_HOST + path
    if attr == "ai_chat":
        payload = {
            "message": content1,
            "response": content2
        }
    elif attr == "emoji":
        payload = {
            "mood": content1
        }
    else:
        payload = {attr: content1}
    
    try:
        headers = {"Content-Type": "application/json"}
        json_str = json.dumps(payload)
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.post(url, data=json_str.encode('utf-8'), headers=headers, timeout=timeout))
        print(f"{attr}发送完成")
        resp.close()
        return resp
    except Exception as e:
        print(f"Exception during send_data: {e}")
        return None

async def send_movie_name(movie_name, timeout=5):
    """发送电影信息到Emby播放端"""
    url = f"{EMBY_HOST}/play"
    data = {"movie_name": movie_name}
    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"encoded_data": encoded_data}
    
    try:
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.post(url, json=payload, headers=headers, timeout=timeout))
        print(f"电影信息发送完成，服务器返回: {resp.text}")
        resp.close()
        return resp
    except Exception as e:
        print(f"发送电影信息失败: {e}")
        return None

async def send_to_server(server_type, data, timeout=5):
    """通用服务器数据发送函数"""
    if server_type == "local":
        return await send_data(data.get("type"), data.get("content1"), data.get("content2", ""), timeout)
    elif server_type == "emby":
        return await send_movie_name(data.get("movie_name"), timeout)
    else:
        print(f"未知的服务器类型: {server_type}")
        return None

async def start_chassis(timeout=2):
    """
    控制底盘启动的异步GET请求 http://192.168.101.161:8080/
    """
    url = "http://192.168.101.161:8080/"
    try:
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.get(url, timeout=timeout))
        print(f"start_chassis {url} 状态码: {resp.status_code}")
        resp.close()
        return resp.status_code
    except Exception as e:
        print(f"start_chassis 异常: {e}")
        return None

# ==================== 测试函数 ====================

async def test_send_data():
    """测试send_data函数"""
    print("=== 测试send_data函数 ===")
    
    # 测试ai_chat
    print("\n1. 测试ai_chat发送...")
    result = await send_data("ai_chat", "用户消息", "AI回复")
    print(f"ai_chat测试结果: {result.status_code if result else '失败'}")
    
    # 测试status
    print("\n2. 测试status发送...")
    result = await send_data("status", "1")
    print(f"status测试结果: {result.status_code if result else '失败'}")
    
    # 测试emoji
    print("\n3. 测试emoji发送...")
    result = await send_data("emoji", "smiling")
    print(f"emoji测试结果: {result.status_code if result else '失败'}")
    
    # 测试未知属性
    print("\n4. 测试未知属性...")
    result = await send_data("unknown", "test")
    print(f"未知属性测试结果: {result}")

async def test_send_movie_name():
    """测试send_movie_name函数"""
    print("\n=== 测试send_movie_name函数 ===")
    
    # 测试具体电影名称
    print("\n1. 测试具体电影名称...")
    result = await send_movie_name("复仇者联盟4：终局之战")
    print(f"具体电影测试结果: {result.status_code if result else '失败'}")
    
    # 测试中文电影名称
    print("\n2. 测试中文电影名称...")
    result = await send_movie_name("泰坦尼克号")
    print(f"中文电影测试结果: {result.status_code if result else '失败'}")
    
    # 测试英文电影名称
    print("\n3. 测试英文电影名称...")
    result = await send_movie_name("The Dark Knight")
    print(f"英文电影测试结果: {result.status_code if result else '失败'}")

async def test_send_to_server():
    """测试send_to_server函数"""
    print("\n=== 测试send_to_server函数 ===")
    
    # 测试本地服务器
    print("\n1. 测试本地服务器...")
    local_data = {"type": "emoji", "content1": "cool"}
    result = await send_to_server("local", local_data)
    print(f"本地服务器测试结果: {result.status_code if result else '失败'}")
    
    # 测试Emby服务器
    print("\n2. 测试Emby服务器...")
    emby_data = {"movie_name": "钢铁侠"}
    result = await send_to_server("emby", emby_data)
    print(f"Emby服务器测试结果: {result.status_code if result else '失败'}")
    
    # 测试未知服务器类型
    print("\n3. 测试未知服务器类型...")
    result = await send_to_server("unknown", {})
    print(f"未知服务器类型测试结果: {result}")

async def test_all_functions():
    """测试所有函数"""
    print("开始测试data_sender模块的所有功能...")
    
    try:
        await test_send_data()
        await test_send_movie_name()
        await test_send_to_server()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现异常: {e}")

if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_all_functions()) 