# 迁移自Esp32/mood.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

import requests
import json
import asyncio

SERVER_URL = 'http://192.168.101.246:5001/api/mood'

async def send_mood(mood):
    headers = {'Content-Type': 'application/json'}
    data = {'mood': mood}
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: requests.post(SERVER_URL, data=json.dumps(data), headers=headers))
        # print('Server response:', response.text)
    except Exception as e:
        print('Error sending data:', e)

# 测试代码
async def test():
    await send_mood("cool")

if __name__ == '__main__':
    asyncio.run(test()) 