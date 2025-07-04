from silicon_ai import ask_question
from load_config import load_config
import requests
import json

# 用大模型拆解多意图并生成总TTS

def parse_tasks_and_audio(user_input, api_token, model_name):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json",
    }
    prompt = (
        "你是一个任务编排助手。请把用户的一句话指令拆分为所有需要执行的独立操作，每个操作用一句简短的中文描述，放在 tasks 字段的 intent 数组中。"
        "同时，生成一整段自然、连贯的语音播报内容，放在 audio_content 字段中。"
        "返回一个JSON对象，包含 tasks 和 audio_content 字段。例如：\n"
        "输入：'调高音量并随机播放一首歌，再推荐一部动作片，还要一个酷酷的表情'\n"
        "输出：\n"
        "{\n  \"tasks\": [\n    {\"intent\": \"调高音量\"},\n    {\"intent\": \"随机播放一首歌\"},\n    {\"intent\": \"推荐动作片\"},\n    {\"intent\": \"发送酷酷表情\"}\n  ],\n  \"audio_content\": \"好的，已为您调高音量，正在为您随机播放一首歌，为您推荐《碟中谍7》，已发送一个酷酷的表情。\"\n}\n"
        "只返回JSON对象，不要有多余解释。"
    )
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }
    resp = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), timeout=10)
    try:
        obj = json.loads(resp.json()["choices"][0]["message"]["content"].strip())
        if isinstance(obj, dict) and "tasks" in obj and "audio_content" in obj:
            return obj
    except Exception as e:
        print("任务编排失败：", e)
        print(resp.text)
    return {"tasks": [{"intent": user_input}], "audio_content": ""}

# 伪TTS函数（实际用 speech_tts 替换）
def fake_tts(text):
    print(f"[TTS] {text}")

if __name__ == "__main__":
    config = load_config()
    if not config or "silicon" not in config or "api_token" not in config["silicon"]:
        print("缺少 silicon.api_token")
        exit(1)
    SILICON_KEY = config["silicon"]["api_token"]
    model_name = config["silicon"]["model"]

    # 多意图输入
    question = "帮我调高音量并随机播放一首歌，再推荐一部动作片，还要一个酷酷的表情"
    print("用户输入：", question)
    plan = parse_tasks_and_audio(question, SILICON_KEY, model_name)
    print("任务编排结果：", plan)
    results = []

    for task in plan["tasks"]:
        intent = task.get('intent', '')
        print(f"处理子任务: {intent}")
        result = ask_question(intent, SILICON_KEY)
        print("AI返回：", result)
        results.append(result)

    print("\n最终TTS播报：")
    fake_tts(plan["audio_content"]) 