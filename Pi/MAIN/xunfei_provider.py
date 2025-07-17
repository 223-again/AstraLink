#!/usr/bin/env python3
"""
讯飞星火API提供者
实现AIProvider接口，提供讯飞星火API的调用能力
"""

import json
import asyncio
import requests
from typing import Dict, Any, List
from ai import AIProvider
from load_config import load_config

class XunfeiProvider(AIProvider):
    """讯飞星火API提供者"""
    
    def __init__(self, api_password: str, base_url: str = "https://spark-api-open.xf-yun.com/v1"):
        self.api_password = api_password
        self.base_url = base_url
    
    @classmethod
    def from_config(cls):
        """从config.json自动读取讯飞星火密钥"""
        config = load_config() or {}
        xunfei_cfg = config.get("xunfei", {})
        api_password = xunfei_cfg.get("api_password", "")
        base_url = "https://spark-api-open.xf-yun.com/v1"
        return cls(api_password, base_url)
    
    def get_model_config(self, model_type: str = "default") -> Dict[str, Any]:
        """获取模型配置"""
        # 讯飞星火模型配置
        models = {
            "default": {
                "name": "generalv3.5",
                "temperature": 0.7,
                "max_tokens": 1024
            },
            "advanced": {
                "name": "generalv3.5",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "fast": {
                "name": "generalv3.5",
                "temperature": 0.5,
                "max_tokens": 512
            }
        }
        return models.get(model_type, models["default"])
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """讯飞星火聊天完成接口"""
        model_config = self.get_model_config(kwargs.get("model_type", "default"))
        
        headers = {
            "Authorization": f"Bearer {self.api_password}",
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
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            payload["tool_choice"] = kwargs["tool_choice"]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=kwargs.get("timeout", 15)
                )
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 检查讯飞星火的响应格式
            if result.get("code") != 0:
                error_msg = result.get("message", "未知错误")
                raise Exception(f"讯飞星火API错误: {error_msg}")
            
            # 转换为标准格式
            choices = result.get("choices", [])
            if not choices:
                raise Exception("讯飞星火API返回空choices")
            
            # 提取消息内容
            message = choices[0].get("message", {})
            if not message:
                raise Exception("讯飞星火API返回空message")
            
            # 返回标准格式
            return {
                "choices": [{
                    "message": {
                        "content": message.get("content", ""),
                        "role": message.get("role", "assistant")
                    }
                }],
                "usage": result.get("usage", {}),
                "sid": result.get("sid", "")
            }
            
        except Exception as e:
            print(f"讯飞星火API调用失败: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_messages = [
                {"role": "user", "content": "你好"}
            ]
            
            response = await self.chat_completion(test_messages, timeout=10)
            choices = response.get("choices")
            return bool(choices and len(choices) > 0)
            
        except Exception as e:
            print(f"讯飞星火连接测试失败: {e}")
            return False

def create_xunfei_provider(api_password: str = "", base_url: str = "https://spark-api-open.xf-yun.com/v1") -> XunfeiProvider:
    """创建讯飞星火提供者，优先从参数获取密钥，否则自动读取config"""
    if api_password:
        return XunfeiProvider(api_password, base_url)
    return XunfeiProvider.from_config()

# 测试函数
async def test_xunfei_provider():
    """测试讯飞星火提供者"""
    from load_config import load_config
    config = load_config() or {}
    xunfei_cfg = config.get("xunfei", {})
    api_password = xunfei_cfg.get("api_password", "")
    
    if not api_password or api_password.startswith("PKK****"):
        print("⚠️ 跳过讯飞星火测试，请在config.json设置有效的API密码")
        return
    
    try:
        provider = create_xunfei_provider()
        print("✅ 讯飞星火提供者创建成功")
        
        # 测试连接
        is_connected = await provider.test_connection()
        if not is_connected:
            print("❌ 讯飞星火API连接失败")
            return
        
        print("✅ 讯飞星火API连接成功")
        
        # 测试模型配置
        config = provider.get_model_config("default")
        print(f"📋 默认模型配置: {config}")
        
        # 测试API调用
        messages = [
            {"role": "system", "content": "你是一个测试助手。"},
            {"role": "user", "content": "你好，请简单介绍一下你自己"}
        ]
        
        response = await provider.chat_completion(messages, timeout=15)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✅ API调用成功: {content[:50]}...")
        
        # 显示使用情况
        usage = response.get("usage", {})
        if usage:
            print(f"📊 Token使用情况: {usage}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_xunfei_models():
    """测试讯飞星火模型配置"""
    from load_config import load_config
    config = load_config() or {}
    xunfei_cfg = config.get("xunfei", {})
    api_password = xunfei_cfg.get("api_password", "")
    
    if not api_password or api_password.startswith("PKK****"):
        print("⚠️ 跳过模型配置测试，请在config.json设置有效的API密码")
        return
    
    try:
        provider = create_xunfei_provider()
        
        # 测试不同模型配置
        model_types = ["default", "advanced", "fast"]
        
        for model_type in model_types:
            print(f"\n🔄 测试 {model_type} 模型配置...")
            config = provider.get_model_config(model_type)
            print(f"配置: {config}")
            
            # 测试API调用
            messages = [
                {"role": "user", "content": f"请用一句话回答：{model_type}模型测试"}
            ]
            
            response = await provider.chat_completion(
                messages, 
                model_type=model_type,
                timeout=10
            )
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"响应: {content[:50]}...")
            
            # 显示使用情况
            usage = response.get("usage", {})
            if usage:
                print(f"Token使用: {usage}")
    
    except Exception as e:
        print(f"❌ 模型配置测试失败: {e}")

if __name__ == "__main__":
    print("📚 讯飞星火提供者示例")
    print("要运行测试，请设置有效的讯飞星火API密码")
    asyncio.run(test_xunfei_provider()) 