import requests
import json
import asyncio

SERVER_URL = 'http://127.0.0.1:5001/api/mood'

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