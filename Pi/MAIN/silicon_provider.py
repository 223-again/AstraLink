#!/usr/bin/env python3
"""
硅基流动API提供者
实现AIProvider接口，提供硅基流动API的调用能力
"""

import json
import asyncio
import requests
from typing import Dict, Any, List
from load_config import load_config
from ai import AIProvider

class SiliconProvider(AIProvider):
    """硅基流动API提供者"""
    
    def __init__(self, api_token: str | None = None):
        self.api_token = api_token
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.config = load_config()
        
        # 如果没有传入api_token，从配置文件获取
        if not self.api_token and self.config and "silicon" in self.config:
            self.api_token = self.config["silicon"].get("api_token")
        
        if not self.api_token:
            raise RuntimeError("缺少硅基流动API令牌")
    
    def get_model_config(self, model_type: str = "default") -> Dict[str, Any]:
        """获取模型配置"""
        if not self.config or "silicon" not in self.config:
            # 默认配置
            return {
                "name": "Qwen/Qwen3-32B",
                "temperature": 0.7,
                "max_tokens": 1024,
                "enable_thinking": False,
                "frequency_penalty": 0.0
            }
        
        # 获取多模型配置
        models_config = self.config["silicon"].get("models", {})
        model_config = models_config.get(model_type, {})
        
        if not model_config:
            # 回退到旧版本配置
            model_name = self.config["silicon"].get("model", "Qwen/Qwen3-32B")
            model_config = {
                "name": model_name,
                "temperature": 0.7,
                "max_tokens": 1024,
                "enable_thinking": False,
                "frequency_penalty": 0.0
            }
        
        return model_config
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """硅基流动聊天完成接口"""
        model_config = self.get_model_config(kwargs.get("model_type", "default"))
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_config["name"],
            "messages": messages,
            "temperature": kwargs.get("temperature", model_config.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", model_config.get("max_tokens", 1024)),
            "enable_thinking": kwargs.get("enable_thinking", model_config.get("enable_thinking", False)),
            "frequency_penalty": kwargs.get("frequency_penalty", model_config.get("frequency_penalty", 0.0))
        }
        
        # 添加可选参数
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    self.base_url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    timeout=kwargs.get("timeout", 15)
                )
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"硅基流动API调用失败: {e}")
            raise

# 工厂函数
def create_silicon_provider(api_token: str | None = None) -> SiliconProvider:
    """创建硅基流动提供者"""
    return SiliconProvider(api_token)

# 测试函数
async def test_silicon_provider():
    """测试硅基流动提供者"""
    try:
        provider = create_silicon_provider()
        print("✅ 硅基流动提供者创建成功")
        
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

if __name__ == "__main__":
    asyncio.run(test_silicon_provider()) 