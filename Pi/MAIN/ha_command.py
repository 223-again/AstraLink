# 迁移自Esp32/ha_command.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

import requests
import json
import asyncio

# 请根据你的 Home Assistant 实例地址进行修改
HA_URL = "http://192.168.101.246:8123"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmQ1ZDI1NGZhNTA0NTRhOTRhZDRjYzYyZGU5MWVkYyIsImlhdCI6MTc0MTY5NjI0NywiZXhwIjoyMDU3MDU2MjQ3fQ.dIc5ebY-FBbCApzPNKcfUweKxpdoKIx9EddOdGmbEV8"

async def call_scene(scene_entity):
    url = HA_URL + "/api/services/scene/turn_on"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {"entity_id": scene_entity}
    try:
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, data=json.dumps(payload)))
        print("状态码:", resp.status_code)
        # print("响应内容:", resp.text)
        resp.close()
    except Exception as e:
        print("调用场景时发生异常:", str(e))

async def ha_action(command):
    if command == "movie_on":
        print("启动观影模式...")
        await call_scene("scene.kai_qi_guan_ying")
    elif command == "movie_off":
        print("停止观影模式...")
        await call_scene("scene.wan_cheng_guan_ying")
    else:
        print(f"未知的命令: {command}")

# 测试代码
async def test():
    action = "movie_off"
    await ha_action(action)

if __name__ == "__main__":
    asyncio.run(test()) 