# 迁移自Esp32/send_data.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

import json
import requests
import asyncio

ENDPOINTS = {
    "wifi_quality": "/api/wifi_quality",
    "ai_chat":     "/api/add_history",
    "status":      "/api/status",
    "emoji":       "/api/mood"
}

HOST = "http://192.168.101.246:5000"

async def send_data(attr, content1, content2="", timeout=5):
    path = ENDPOINTS.get(attr)
    if not path:
        print(f'Error: Unknown attribute "{attr}"')
        return None
    url = HOST + path
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
        # 用线程池避免阻塞主线程
        resp = await loop.run_in_executor(None, lambda: requests.post(url, data=json_str.encode('utf-8'), headers=headers, timeout=timeout))
        print(attr+"发送完成")
        resp.close()
        return resp
    except Exception as e:
        print("Exception during send_data:", e)
        return None

# 测试代码
async def test():
    await send_data("wifi_quality", 70)
    await send_data("ai_chat", "你好，今天的天气如何？", "123")
    await send_data("status", 1)
    await send_data("emoji", "cool")

if __name__ == "__main__":
    asyncio.run(test()) 