#!/usr/bin/env python3
"""
核心AI处理模块
负责prompt构建、响应解析和任务执行
通过接口调用不同的API服务商
"""

import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

def _convert_chinese_numbers_in_movie_name(text: str) -> str:
    """将电影名称中的中文数字转换为阿拉伯数字"""
    # 中文数字到阿拉伯数字的映射
    chinese_to_arabic = {
        '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
        '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20'
    }
    
    # 尝试匹配常见的电影名称模式
    movie_patterns = [
        r'流浪地球([一二三四五六七八九十]+)',
        r'战狼([一二三四五六七八九十]+)',
        r'速度与激情([一二三四五六七八九十]+)',
        r'复仇者联盟([一二三四五六七八九十]+)',
        r'星球大战([一二三四五六七八九十]+)',
        r'([一二三四五六七八九十]+)'
    ]
    
    for pattern in movie_patterns:
        match = re.search(pattern, text)
        if match:
            chinese_num = match.group(1)
            if chinese_num in chinese_to_arabic:
                arabic_num = chinese_to_arabic[chinese_num]
                return text.replace(chinese_num, arabic_num)
    
    # 如果没有找到匹配的模式，返回原文本
    return text

class AIProvider(ABC):
    """AI服务提供者接口"""
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成接口"""
        pass
    
    @abstractmethod
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """获取模型配置"""
        pass

class AI:
    """核心AI处理器"""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示词"""
        last_movie = context.get("last_movie", "")
        movie_context = f"\n上一次推荐的电影：{last_movie}" if last_movie else ""
        
        return f"""你是一个智能助手，能够理解用户需求并执行相应操作。

{movie_context}

请分析用户输入，识别意图并返回JSON格式的响应：

{{
    "intent": "用户意图分类",
    "audio_content": "语音播报内容",
    "actions": [
        {{
            "action_type": "操作类型",
            "parameters": {{}}
        }}
    ],
    "emoji": "表情选择"
}}

支持的操作类型：
1. play_music - 播放音乐
   - music_name: 歌曲名称（如果用户指定了具体歌曲）

2. volume_control - 音量控制
   - command: "volume_up", "volume_down", "volume_set_X"（X为0-100的数字）

3. recommend_movie - 推荐电影
   - movie_name: 电影名称（注意：如果电影名称包含中文数字，请自动转换为阿拉伯数字）
   - 当用户要求观看电影、推荐电影、开始观影时，自动添加ha_action动作来开启灯光
   - 请返回具体的电影名称，不要返回电影的类型

4. drink_request - 饮料请求（通过步进电机提供饮料）
   - provide_drink: true/false

5. ha_action - 智能家居控制
   - action: "light_on" 或 "light_off"

6. ai_chat - 普通对话回复
   - 当用户询问一般性问题时使用

意图分类：
- PLAY_MUSIC: 播放音乐相关
- VOLUME_CONTROL: 音量控制相关
- RECOMMEND_MOVIE: 电影推荐相关（注意：当用户要求看电影、推荐电影时，应同时执行开灯动作）
- DRINK_REQUEST: 饮料需求相关（通过步进电机提供）
- HA_CONTROL: 智能家居控制相关
- GENERAL_CHAT: 一般对话

表情选择：[嘿嘿, 惊恐, 吃惊, 酷酷, 思考, 吐舌, 抱抱, 嘻嘻, 喜笑颜开, 眨眼, 微笑]

示例：
用户："我想听鸳鸯戏"
响应：{{
    "intent": "PLAY_MUSIC",
    "audio_content": "好的，正在为您播放《鸳鸯戏》。",
    "actions": [
        {{
            "action_type": "play_music",
            "parameters": {{"music_name": "鸳鸯戏"}}
        }}
    ],
    "emoji": "微笑"
}}

用户："开灯"
响应：{{
    "intent": "HA_CONTROL",
    "audio_content": "好的，我来为您开启灯光。",
    "actions": [
        {{
            "action_type": "ha_action",
            "parameters": {{"action": "light_on"}}
        }}
    ],
    "emoji": "眨眼"
}}

用户："我想看流浪地球二"
响应：{{
    "intent": "RECOMMEND_MOVIE",
    "audio_content": "好的，我来为您推荐《流浪地球2》，并为您开启观影灯光。",
    "actions": [
        {{
            "action_type": "ha_action",
            "parameters": {{"action": "light_on"}}
        }},
        {{
            "action_type": "recommend_movie",
            "parameters": {{"movie_name": "流浪地球2"}}
        }}
    ],
    "emoji": "喜笑颜开"
}}

用户："我要喝饮料"
响应：{{
    "intent": "DRINK_REQUEST",
    "audio_content": "好的，我来为您提供饮料。",
    "actions": [
        {{
            "action_type": "drink_request",
            "parameters": {{"provide_drink": true}}
        }}
    ],
    "emoji": "抱抱"
}}



只返回JSON格式，不要其他解释。"""
    
    async def process_user_input(self, user_input: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        处理用户输入，返回统一的响应格式
        """
        if context is None:
            context = {}
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            # 调用API提供者
            response = await self.provider.chat_completion(
                messages,
                model_type="unified",
                temperature=0.7,
                max_tokens=1024,
                timeout=15
            )
            
            # 解析AI响应
            ai_content = response["choices"][0]["message"]["content"].strip()
            return self._parse_ai_response(ai_content, user_input)
            
        except Exception as e:
            print(f"AI处理失败: {e}")
            return self._create_error_response()
    
    def _parse_ai_response(self, ai_content: str, user_input: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试解析JSON
            response_data = json.loads(ai_content)
            
            # 验证必要字段
            if not all(key in response_data for key in ["intent", "audio_content", "actions", "emoji"]):
                raise ValueError("响应缺少必要字段")
            
            return {
                "success": True,
                "data": response_data,
                "raw_response": ai_content
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"AI原始响应: {ai_content}")
            return self._create_fallback_response(user_input)
        except Exception as e:
            print(f"响应解析失败: {e}")
            return self._create_fallback_response(user_input)
    
    def _create_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """创建备用响应"""
        # 简单的关键词匹配作为备用方案
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["音乐", "播放", "听"]):
            return {
                "success": True,
                "data": {
                    "intent": "PLAY_MUSIC",
                    "audio_content": "好的，我来为您播放音乐。",
                    "actions": [{"action_type": "play_music", "parameters": {"music_name": "随机音乐"}}],
                    "emoji": "微笑"
                }
            }
        elif any(word in user_input_lower for word in ["音量", "声音"]):
            return {
                "success": True,
                "data": {
                    "intent": "VOLUME_CONTROL",
                    "audio_content": "我来为您调节音量。",
                    "actions": [{"action_type": "volume_control", "parameters": {"command": "volume_up"}}],
                    "emoji": "思考"
                }
            }
        elif any(word in user_input_lower for word in ["电影", "推荐"]):
            # 尝试从用户输入中提取电影名称并进行数字转换
            movie_name = _convert_chinese_numbers_in_movie_name(user_input)
            return {
                "success": True,
                "data": {
                    "intent": "RECOMMEND_MOVIE",
                    "audio_content": f"我来为您推荐《{movie_name}》，并为您开启观影灯光。",
                    "actions": [
                        {"action_type": "ha_action", "parameters": {"action": "light_on"}},
                        {"action_type": "recommend_movie", "parameters": {"movie_name": movie_name}}
                    ],
                    "emoji": "喜笑颜开"
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "intent": "GENERAL_CHAT",
                    "audio_content": "我理解您的意思，让我为您处理。",
                    "actions": [{"action_type": "ai_chat", "parameters": {}}],
                    "emoji": "思考"
                }
            }
    
    def _create_error_response(self) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "success": False,
            "error": "AI处理失败",
            "data": {
                "intent": "GENERAL_CHAT",
                "audio_content": "抱歉，我现在无法处理您的请求，请稍后再试。",
                "actions": [],
                "emoji": "思考"
            }
        }

# 工厂函数
def create_ai(provider: AIProvider) -> AI:
    """创建AI实例"""
    return AI(provider) 