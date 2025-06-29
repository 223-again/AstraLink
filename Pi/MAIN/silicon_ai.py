import requests
import json
from load_config import *

def format_response(audio_content: str, command: str, emoji: str, movie: str, drink: bool, music: bool, volume: str = "none"):
    return {
        "audio_content": audio_content,
        "command": command,           # 只用于HA（如灯光）
        "emoji": emoji,
        "movie": movie,
        "drink": drink,               # 只用于饮料需求
        "music": music,               # 只用于听歌需求
        "volume": volume,             # 音量控制命令
    }

def safe_extract_args(args_str):
    try:
        data = json.loads(args_str)
        if "drink" not in data:
            data["drink"] = False
        if "music" not in data:
            data["music"] = False
        if "command" not in data:
            data["command"] = "none"
        if "volume" not in data:
            data["volume"] = "none"
        return data
    except json.JSONDecodeError:
        return {
            "audio_content": args_str.strip()[:100],
            "command": "none",
            "emoji": "thinking",
            "movie": "0",
            "drink": False,
            "music": False,
            "volume": "none",
        }

def ask_question(question, SILICON_KEY, last_movie=None):
    API_TOKEN = SILICON_KEY
    config = load_config()
    if not config or "silicon" not in config or "model" not in config["silicon"]:
        raise RuntimeError("配置文件缺少 silicon.model")
    
    model_name = config["silicon"]["model"]
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json",
    }

    movie_context = f"用户刚刚看完电影《{last_movie}》。\n" if last_movie else ""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "format_response",
                "description": "格式化观影助手的响应，字段含义见参数说明。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "audio_content": {"type": "string", "description": "回答文本"},
                        "command": {"type": "string", "enum": ["none", "light_on", "light_off"]},
                        "emoji": {"type": "string", "enum": [
                            "cool", "laughing", "smiling", "kissing", "tasty",
                            "thinking", "smirking", "shushing", "surprised"]},
                        "movie": {"type": "string", "description": "具体电影名称，禁止返回模糊类别。无推荐时设为'0'"},
                        "drink": {"type": "boolean", "description": "用户观影时是否明确想喝饮料"},
                        "music": {"type": "boolean", "description": "用户观影时是否明确想听歌/播放音乐"},
                        "volume": {"type": "string", "enum": [
                            "none", "volume_up", "volume_down", 
                            "volume_set_30", "volume_set_50", "volume_set_70", "volume_set_100"
                        ], "description": "音量控制命令：none=无操作，volume_up=调高音量，volume_down=调低音量，volume_set_X=设置特定音量"}
                    },
                    "required": ["audio_content", "command", "emoji", "movie", "drink", "music", "volume"],
                },
            },
        }
    ]

    prompt = f"""你是一个AI观影助手，请严格按照以下要求回答：
    1. 回复必须简短风趣
    2. 使用format_response工具返回结构化数据
    3. 字段说明：command 只用于智能家居（如灯光），drink 为布尔型饮料需求标志，music 为布尔型听歌需求标志，volume 为音量控制命令。
    4. 电影上下文：{movie_context}
    5. 如果用户观影时明确表达想喝饮料，请将 drink 字段设为 true，否则为 false。
    6. 如果用户明确表达想听歌或播放音乐，请将 music 字段设为 true，否则为 false。
    7. 如果用户明确表达想调节音量（如"声音太小了"、"调高音量"等），请设置相应的 volume 命令：
       - volume_up: 调高音量
       - volume_down: 调低音量  
       - volume_set_30/50/70/100: 设置特定音量
       - none: 无音量操作
    8. 电影推荐规则：
       - movie字段必须返回具体的电影名称，如"复仇者联盟4：终局之战"、"泰坦尼克号"等
       - 禁止返回模糊类别如"漫威电影"、"动作片"、"喜剧片"等
       - 如果用户要求推荐某类电影，请选择该类别的经典代表作
       - 如果用户没有明确要求推荐电影，movie字段设为"0"
       - 电影名称要准确完整
    """

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        "tools": tools,
        "tool_choice": {"type": "function", "function": {"name": "format_response"}},
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1024,
        "enable_thinking": False,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=10
        )
        response.raise_for_status()
        json_data = response.json()
        
        if not json_data.get("choices"):
            raise ValueError("API返回空choices")

        message = json_data["choices"][0].get("message", {})
        if not message.get("tool_calls"):
            raise ValueError("响应缺少tool_calls")

        tool_call = message["tool_calls"][0]
        if tool_call["function"]["name"] != "format_response":
            raise ValueError("工具名称不匹配")

        args_str = tool_call["function"].get("arguments", "")
        return safe_extract_args(args_str)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"处理响应失败: {str(e)}")
        return None

if __name__ == "__main__":
    
    config = load_config()
    if config and "silicon" in config and "api_token" in config["silicon"]:
        print("\n开始真实API测试...")
        SILICON_KEY = config["silicon"]["api_token"]
        question = "推荐一部动作片"
        content = ask_question(question, SILICON_KEY)
        if content:
            print("API测试结果:", json.dumps(content, ensure_ascii=False, indent=2))
        else:
            print("API测试失败")