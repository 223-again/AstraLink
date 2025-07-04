import requests
import json
import asyncio
from load_config import load_config

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

def get_model_config(model_type="task_execution"):
    """
    获取指定类型的模型配置
    """
    config = load_config()
    if not config or "silicon" not in config:
        raise RuntimeError("配置文件缺少 silicon 配置")
    
    # 获取模型配置
    models_config = config["silicon"].get("models", {})
    model_config = models_config.get(model_type, {})
    
    # 如果没有找到特定配置，使用默认配置
    if not model_config:
        # 回退到旧版本的单一模型配置
        model_name = config["silicon"].get("model", "Qwen/Qwen3-32B")
        model_config = {
            "name": model_name,
            "temperature": 0.7,
            "max_tokens": 1024,
            "enable_thinking": False
        }
    
    return model_config

def execute_task(task_type, original_input, SILICON_KEY, model_type="task_execution"):
    """
    根据任务类型执行具体操作
    """
    API_TOKEN = SILICON_KEY
    config = load_config()
    if not config or "silicon" not in config:
        raise RuntimeError("配置文件缺少 silicon 配置")
    
    # 获取模型配置
    model_config = get_model_config(model_type)
    model_name = model_config["name"]
    temperature = model_config.get("temperature", 0.7)
    max_tokens = model_config.get("max_tokens", 1024)
    enable_thinking = model_config.get("enable_thinking", False)
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json",
    }

    # 根据任务类型选择对应的工具和prompt
    if task_type == "PLAY_MUSIC":
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "play_music",
                    "description": "播放音乐",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "music_name": {"type": "string", "description": "要播放的歌曲名，必须从原始用户输入中提取具体歌曲名称"}
                        },
                        "required": ["music_name"]
                    }
                }
            }
        ]
        prompt = f"""你是音乐播放助手。用户说：{original_input}

请从用户输入中提取具体的歌曲名称，调用play_music工具播放。

规则：
1. 必须从原始输入中提取歌曲名称
2. 如果用户说"我想听XXX"，XXX就是歌曲名称
3. 如果用户说"播放XXX"，XXX就是歌曲名称
4. 禁止返回random或模糊描述
5. 必须调用play_music工具

示例：
- 用户说"我想听鸳鸯戏" → music_name: "鸳鸯戏"
- 用户说"播放青花瓷" → music_name: "青花瓷"
"""

    elif task_type in ["VOLUME_UP", "VOLUME_DOWN", "VOLUME_SET"]:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "volume_control",
                    "description": "音量控制",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "volume_command": {"type": "string", "description": "音量控制命令"}
                        },
                        "required": ["volume_command"]
                    }
                }
            }
        ]
        
        if task_type == "VOLUME_UP":
            volume_cmd = "volume_up"
        elif task_type == "VOLUME_DOWN":
            volume_cmd = "volume_down"
        else:  # VOLUME_SET
            # 从原始输入中提取数字
            import re
            numbers = re.findall(r'\d+', original_input)
            if numbers:
                volume_cmd = f"volume_set_{numbers[0]}"
            else:
                volume_cmd = "volume_up"  # 默认
        
        prompt = f"""你是音量控制助手。用户说：{original_input}

请调用volume_control工具，volume_command字段设为：{volume_cmd}，如果用户说“音量调到最大”，则volume_command字段设为：volume_set_100
"""

    elif task_type == "RECOMMEND_MOVIE":
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "recommend_movie",
                    "description": "推荐电影",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie": {"type": "string", "description": "推荐的电影名称"}
                        },
                        "required": ["movie"]
                    }
                }
            }
        ]
        prompt = f"""你是电影推荐助手。用户说：{original_input}

请推荐一部具体的电影，调用recommend_movie工具。
电影名称要准确完整，禁止返回模糊类别。
"""

    elif task_type == "DRINK_REQUEST":
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "drink_request",
                    "description": "饮料请求",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "drink": {"type": "boolean", "description": "是否需要饮料"}
                        },
                        "required": ["drink"]
                    }
                }
            }
        ]
        prompt = f"""你是饮料服务助手。用户说：{original_input}

如果用户明确表达想喝饮料，调用drink_request工具，drink字段设为true。
"""

    else:
        print(f"未知任务类型: {task_type}")
        return None

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": original_input},
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": temperature,
        "top_p": 0.95,
        "max_tokens": max_tokens,
        "enable_thinking": enable_thinking
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
            # 如果没有工具调用，返回None表示无法处理
            print("AI没有调用任何工具，无法处理请求")
            return None

        tool_call = message["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        args_str = tool_call["function"].get("arguments", "")
        try:
            args = json.loads(args_str)
        except Exception:
            args = {"raw": args_str}
        
        # 添加调试信息
        print(f"🔧 工具调用: {tool_name}")
        print(f"📝 工具参数: {args}")
        
        return {"tool_name": tool_name, "args": args}

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"处理响应失败: {str(e)}")
        return None

def parse_tasks_and_audio(user_input, api_token, model_type="task_planning"):
    """
    任务编排+总TTS：
    输入一句自然语言，返回{"tasks": [{"intent": ...}, ...], "audio_content": ...}
    使用任务编排专用模型
    """
    # 获取任务编排模型配置
    model_config = get_model_config(model_type)
    model_name = model_config["name"]
    temperature = model_config.get("temperature", 0.3)
    max_tokens = model_config.get("max_tokens", 512)
    enable_thinking = model_config.get("enable_thinking", False)
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json",
    }
    prompt = (
        "你是一个任务编排助手。请分析用户输入，识别需要执行的任务类型，返回固定的任务关键词。\n"
        "支持的任务类型：\n"
        "- PLAY_MUSIC: 播放音乐\n"
        "- VOLUME_UP: 音量加10%\n"
        "- VOLUME_DOWN: 音量减10%\n"
        "- VOLUME_SET: 设置特定音量\n"
        "- RECOMMEND_MOVIE: 推荐电影\n"
        "- DRINK_REQUEST: 饮料请求\n"
        "\n"
        "返回JSON格式：\n"
        "{\n"
        "  \"tasks\": [\n"
        "    {\"intent\": \"任务关键词\"}\n"
        "  ],\n"
        "  \"audio_content\": \"语音播报内容\"\n"
        "}\n"
        "\n"
        "示例：\n"
        "输入：'我想听鸳鸯戏'\n"
        "输出：{\"tasks\": [{\"intent\": \"PLAY_MUSIC\"}], \"audio_content\": \"好的，正在为您播放《鸳鸯戏》。\"}\n"
        "\n"
        "只返回JSON，不要解释。"
    )
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_thinking": enable_thinking
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

async def process_tasks_parallel(tasks, api_token, config, original_input=""):
    """
    并行处理多个任务，提高执行效率
    使用子任务执行专用模型
    """
    async def process_single_task(task):
        intent = task.get('intent', '')
        print(f"并行处理子任务: {intent}")
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: execute_task(intent, original_input, api_token, model_type="task_execution")
        )
        print(f"子任务 {intent} 完成，AI返回：{result}")
        return result

    # 并行执行所有任务
    tasks_to_execute = [process_single_task(task) for task in tasks]
    results = await asyncio.gather(*tasks_to_execute, return_exceptions=True)
    
    # 处理结果
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"任务 {i} 执行失败: {result}")
            processed_results.append(None)
        else:
            processed_results.append(result)
    
    return processed_results

def batch_process_tasks(tasks, api_token, model_type="batch_processing", original_input=""):
    """
    批量处理任务，减少API调用次数
    使用批量处理专用模型
    """
    if not tasks:
        return []
    
    # 如果只有一个任务，直接处理
    if len(tasks) == 1:
        result = execute_task(tasks[0].get('intent', ''), original_input, api_token, model_type="task_execution")
        return [result] if result else [None]
    
    # 获取批量处理模型配置
    model_config = get_model_config(model_type)
    model_name = model_config["name"]
    temperature = model_config.get("temperature", 0.3)
    max_tokens = model_config.get("max_tokens", 1024)
    enable_thinking = model_config.get("enable_thinking", False)
    
    # 多个任务时，尝试批量处理
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json",
    }
    
    # 构建批量处理的prompt
    intents = [task.get('intent', '') for task in tasks]
    combined_intent = "；".join(intents)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "batch_execute",
                "description": "批量执行多个操作",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {"type": "string"},
                                    "args": {"type": "object"}
                                }
                            },
                            "description": "要执行的操作列表"
                        },
                        "audio_content": {"type": "string", "description": "AI回复的文本内容"}
                    },
                    "required": ["actions"]
                }
            }
        }
    ]
    
    prompt = f"""你是一个AI助手，需要批量处理以下操作：{combined_intent}
    
    请分析每个操作并返回相应的工具调用。支持的工具包括：
    - play_music: 播放音乐
    - recommend_movie: 推荐电影  
    - volume_control: 调节音量
    - drink_request: 饮料请求
    
    请为每个操作选择合适的工具并返回批量执行结果。
    """
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"请处理这些操作：{combined_intent}"},
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_thinking": enable_thinking
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=15
        )
        response.raise_for_status()
        json_data = response.json()
        
        if not json_data.get("choices"):
            raise ValueError("API返回空choices")

        message = json_data["choices"][0].get("message", {})
        if message.get("tool_calls"):
            tool_call = message["tool_calls"][0]
            args_str = tool_call["function"].get("arguments", "")
            try:
                args = json.loads(args_str)
                actions = args.get("actions", [])
                # 将批量结果转换为单个任务结果格式
                results = []
                for action in actions:
                    results.append({
                        "tool_name": action.get("tool_name"),
                        "args": action.get("args", {})
                    })
                return results
            except Exception as e:
                print(f"批量处理解析失败: {e}")
                return [None] * len(tasks)
        
        return [None] * len(tasks)
        
    except Exception as e:
        print(f"批量处理失败: {e}")
        return [None] * len(tasks)

def get_available_models():
    """
    获取所有可用的模型配置
    """
    config = load_config()
    if not config or "silicon" not in config:
        return {}
    
    models_config = config["silicon"].get("models", {})
    if not models_config:
        # 如果没有多模型配置，返回默认配置
        default_model = config["silicon"].get("model", "Qwen/Qwen3-32B")
        return {
            "task_planning": {"name": default_model, "description": "默认模型"},
            "task_execution": {"name": default_model, "description": "默认模型"},
            "batch_processing": {"name": default_model, "description": "默认模型"},
            "emoji_selection": {"name": default_model, "description": "默认模型"}
        }
    
    return models_config

def select_emoji(user_input, audio_content, api_token, model_type="emoji_selection"):
    """
    表情选择：根据用户输入和播报内容智能选择表情
    """
    try:
        # 获取表情选择模型配置
        model_config = get_model_config(model_type)
        model_name = model_config["name"]
        temperature = model_config.get("temperature", 0.3)
        max_tokens = model_config.get("max_tokens", 100)
        
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json",
        }
        
        prompt = (
            "你是一个表情选择助手。根据用户输入和任务内容，从以下可选表情中智能推荐一个最合适的："
            "[cool, default, happy, kissing, laughing, shushing, smiling, smirking, surprised, tasty, thinking]。"
            "只能从这些表情中选一个，输出英文小写单词，不要加后缀。"
            "例如：用户说'播放音乐'，选择'happy'；用户说'推荐电影'，选择'thinking'。"
            "只返回表情单词，不要有其他内容。"
        )
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"用户输入：{user_input}\n任务内容：{audio_content}"},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), timeout=10)
        result = response.json()
        emoji = result["choices"][0]["message"]["content"].strip()
        
        # 验证emoji是否在允许列表中
        allowed_emojis = ["cool", "default", "happy", "kissing", "laughing", "shushing", "smiling", "smirking", "surprised", "tasty", "thinking"]
        if emoji in allowed_emojis:
            return emoji
        else:
            return "default"
            
    except Exception as e:
        print(f"表情选择失败: {e}")
        return "default"

if __name__ == "__main__":
    config = load_config()
    if config and "silicon" in config and "api_token" in config["silicon"]:
        print("\n任务编排+总TTS测试...")
        SILICON_KEY = config["silicon"]["api_token"]
        
        # 显示可用模型
        print("\n可用模型配置:")
        models = get_available_models()
        for model_type, model_config in models.items():
            print(f"  {model_type}: {model_config.get('name', 'N/A')} - {model_config.get('description', 'N/A')}")
        
        question = "我想听鸳鸯戏"
        plan = parse_tasks_and_audio(question, SILICON_KEY, model_type="task_planning")
        print("任务编排结果：", plan)
        print("\n最终TTS播报：")
        print(plan["audio_content"])
        
        # 测试子任务执行
        print("\n" + "="*50)
        print("子任务执行测试...")
        if plan.get("tasks"):
            for i, task in enumerate(plan["tasks"]):
                print(f"\n--- 子任务 {i+1}: {task.get('intent', '')} ---")
                result = execute_task(
                    task.get('intent', ''), 
                    question,
                    SILICON_KEY,
                    model_type="task_execution"
                )
                print(f"子任务结果: {result}")
    else:
        print("缺少 silicon.api_token")