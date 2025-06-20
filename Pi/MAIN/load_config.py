# 迁移自Esp32/load_config.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

import json

def load_config(filename="config.json"):
    """加载 JSON 配置文件"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return None

# ... existing code ... 