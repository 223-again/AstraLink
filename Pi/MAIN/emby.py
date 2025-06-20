import requests
import json
import base64
import asyncio

async def send_movie_name(movie_name):
    url = "http://192.168.101.217:5001/play" # 播放端IP(电脑)
    data = {"movie_name": movie_name}
    json_data = json.dumps(data)
    # Base64 编码
    encoded_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"encoded_data": encoded_data}
    try:
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.post(url, json=payload, headers=headers))
        print(f"服务器返回: {resp.text}")
        resp.close()
    except Exception as e:
        print(f"发送请求失败: {e}")

# 测试代码
async def test():
    await send_movie_name("疾速追杀4")

if __name__ == '__main__':
    asyncio.run(test()) 