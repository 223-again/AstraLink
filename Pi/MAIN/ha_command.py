import requests
import json
import asyncio
from load_config import load_config

config = load_config()
if not config or "ha" not in config or "url" not in config["ha"] or "api_token" not in config["ha"]:
    raise RuntimeError("配置文件缺少 ha.url 或 ha.api_token")
HA_URL = config["ha"]["url"]
API_TOKEN = config["ha"]["api_token"]

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
    if command == "light_on":
        print("启动观影模式...")
        await call_scene("scene.kai_qi_guan_ying")
    elif command == "light_off":
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