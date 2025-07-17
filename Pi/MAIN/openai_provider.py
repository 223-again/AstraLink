#!/usr/bin/env python3
"""
OpenAI API提供者
实现AIProvider接口，提供OpenAI API的调用能力
"""

import json
import asyncio
import requests
from typing import Dict, Any, List
from ai import AIProvider
from load_config import load_config

class OpenAIProvider(AIProvider):
    """OpenAI API提供者"""
    
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        # 从配置文件加载设置
        config = load_config()
        if config and "openai" in config:
            openai_config = config["openai"]
            self.api_key = api_key or openai_config.get("api_key")
            self.base_url = base_url or openai_config.get("base_url", "https://api.openai.com/v1")
        else:
            self.api_key = api_key
            self.base_url = base_url or "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置，请在配置文件中设置或传入参数")
    
    def get_model_config(self, model_type: str = "default") -> Dict[str, Any]:
        """获取模型配置"""
        # 从配置文件加载模型配置
        config = load_config()
        if config and "openai" in config and "models" in config["openai"]:
            models = config["openai"]["models"]
            return models.get(model_type, models.get("default", {}))
        
        # 默认配置（如果配置文件没有模型配置）
        default_models = {
            "default": {
                "name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1024
            },
            "advanced": {
                "name": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "fast": {
                "name": "gpt-3.5-turbo-instruct",
                "temperature": 0.7,
                "max_tokens": 1024
            }
        }
        return default_models.get(model_type, default_models["default"])
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """OpenAI聊天完成接口"""
        model_config = self.get_model_config(kwargs.get("model_type", "default"))
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_config["name"],
            "messages": messages,
            "temperature": kwargs.get("temperature", model_config.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", model_config.get("max_tokens", 1024))
        }
        
        # 添加可选参数
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    timeout=kwargs.get("timeout", 15)
                )
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            raise

# 工厂函数
def create_openai_provider(api_key: str | None = None, base_url: str | None = None) -> OpenAIProvider:
    """创建OpenAI提供者"""
    return OpenAIProvider(api_key, base_url)

# 测试函数
async def test_openai_provider():
    """测试OpenAI提供者"""
    try:
        provider = create_openai_provider()  # 从配置文件加载
        print("✅ OpenAI提供者创建成功")
        
        # 测试模型配置
        config = provider.get_model_config("default")
        print(f"📋 默认模型配置: {config}")
        
        # 测试API调用
        messages = [
            {"role": "system", "content": "你是一个测试助手。"},
            {"role": "user", "content": "你好"}
        ]
        
        response = await provider.chat_completion(messages, timeout=10)
        print(f"✅ API调用成功: {response.get('choices', [{}])[0].get('message', {}).get('content', '')[:50]}...")
        
    except Exception as e:
                    print(f"❌ 测试失败: {e}")

    async def test_connection(self) -> bool:
        """测试OpenAI API连接"""
        try:
            messages = [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "测试连接"}
            ]
            
            response = await self.chat_completion(messages, timeout=5)
            return response is not None and "choices" in response
        except Exception as e:
            print(f"OpenAI连接测试失败: {e}")
            return False

if __name__ == "__main__":
    print("📚 OpenAI提供者示例")
    print("从配置文件加载OpenAI设置...")
    asyncio.run(test_openai_provider()) 