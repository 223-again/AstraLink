# AstraLink - 智能观影助手系统

<div align="center">

![AstraLink Logo](https://img.shields.io/badge/AstraLink-智能观影助手-blue?style=for-the-badge&logo=raspberry-pi)

**基于树莓派的智能观影助手，集成语音识别、AI对话、智能家居控制等功能**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5B-red.svg)](https://www.raspberrypi.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📋 项目概述

AstraLink是一个基于树莓派的智能语音助手系统，集成了语音识别、自然语言处理、智能家居控制、音乐播放、电影推荐等多种功能。系统采用模块化设计，支持多种AI提供者，具备良好的扩展性和稳定性。

## 🏗️ 系统架构

```
AstraLink/
├── Pi/                   # 树莓派端
│   ├── MAIN/               # 核心功能模块
│   └── ScreenDisplay/      # 屏幕显示模块
└── Win/                  # Windows端
```

## 🚀 核心功能


### 🎤 语音交互
- **语音识别**: 基于百度语音识别API
- **语音合成**: 支持TTS播报
- **多轮对话**: 支持上下文理解

### 🤖 AI智能处理
- **多AI提供者**: 支持OpenAI、讯飞星火、硅基流动等
- **智能理解**: 自然语言处理和理解
- **动作执行**: 根据用户意图执行相应动作

### 🎵 多媒体功能
- **音乐播放**: 支持本地音乐播放与中断
- **电影推荐**: 智能电影推荐系统
- **音量控制**: 系统音量调节

### 🏠 智能家居集成
- **Home Assistant**: 通过Docker容器运行，提供完整的智能家居控制平台
- **设备联动**: 支持灯光、传感器、开关等多种智能设备
- **自动化**: 支持复杂的自动化场景和规则

### ⚙️ 硬件控制
- **步进电机**: 饮料提供系统
- **底盘控制**: 移动底盘支持
- **传感器**: 环境感知能力

## 📁 项目结构

### Pi/MAIN - 核心功能模块

```
Pi/MAIN/
├── main_simplified.py          # 主程序入口
├── active.py                   # 触发器管理
├── ai.py                       # AI处理核心
├── baidu_audio.py              # 百度语音API
├── mic.py                      # 麦克风控制
├── music_interrupt.py          # 音乐播放管理
├── stepper_motor_control.py    # 步进电机控制
├── ha_command.py               # HA智能家居控制
├── data_sender.py              # 数据发送模块
├── volume_control.py           # 音量控制
├── optimization_config.py      # 性能监控
├── load_config.py              # 配置加载
├── silicon_provider.py         # 硅基AI提供者
├── xunfei_provider.py          # 讯飞AI提供者
├── openai_provider.py          # OpenAI提供者
└── config.json                 # 配置文件
```

**主要特性:**
- 模块化设计，易于维护和扩展
- 支持多种AI提供者，确保服务稳定性
- 完整的语音交互流程
- 硬件控制集成
- 性能监控和优化

### Pi/ScreenDisplay - 屏幕显示模块

```
Pi/ScreenDisplay/
├── 显示界面程序
├── 表情动画
├── 状态显示
└── 用户交互界面
```

**主要功能:**
- 实时显示系统状态
- 表情动画展示
- 用户交互界面
- 数据可视化

### Win/ - Windows端模块

```
Win/
├── Windows端程序
└── 远程控制功能
```

**主要功能:**
- Windows端控制界面
- 远程配置和调试
- 系统监控工具
- 开发辅助功能

## 🛠️ 技术栈

### 容器化技术
- **Docker**: 容器化部署和隔离
- **Docker Compose**: 多服务编排和管理
- **Home Assistant**: 智能家居平台容器

### 后端技术
- **Python 3.11+**: 主要开发语言
- **asyncio**: 异步编程框架
- **百度语音API**: 语音识别和合成
- **多种AI API**: 
  - **OpenAI**: GPT-4/GPT-3.5模型，支持自定义base_url
  - **讯飞星火**: 中文优化的大语言模型
  - **硅基流动**: 支持多模型配置，包括默认、创意和精确模型

### 硬件支持
- **树莓派5B**: 主控制器
- **ASRPRO**: 语音唤醒
- **麦克风**: 语音输入
- **扬声器**: 音频输出
- **步进电机**: 硬件控制
- **LCD显示屏**: 状态显示

### 软件架构
- **模块化设计**: 功能模块独立
- **异步处理**: 提高系统响应速度
- **配置驱动**: 灵活的配置管理
- **错误处理**: 完善的异常处理机制
- **容器化部署**: 使用Docker Compose管理服务

## 📦 安装和配置

### 环境要求
- 树莓派5B (推荐)
- Python 3.11+
- 麦克风和扬声器
- 网络连接
- Docker & Docker Compose

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/AstraLink.git
cd AstraLink
```

2. **安装依赖**
```bash
cd Pi
python -m venv env
source env/bin/activate  # Linux/Mac
# 或
env\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **启动Home Assistant服务**
```bash
# 使用Docker Compose启动Home Assistant
docker-compose up -d homeassistant

# 等待服务启动完成（首次启动可能需要几分钟）
docker-compose logs -f homeassistant
```

4. **配置API密钥**
```bash
# 编辑 config.json 文件
{
  "baidu": {
    "api_key": "your_baidu_api_key",
    "secret_key": "your_baidu_secret_key"
  },
  "openai": {
    "api_key": "your_openai_api_key",
    "base_url": "https://api.openai.com/v1"
    "models": {
            "default": {
                "name": "gpt-4o",
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
  },
  "silicon": {
    "api_token": "your_silicon_api_token",
    "model": "Qwen/Qwen3-32B",
    "models": {
      "default": {
        "name": "Qwen/Qwen3-32B",
        "description": "默认模型 - 通用对话处理",
        "temperature": 0.7,
        "max_tokens": 1024,
        "enable_thinking": false,
        "frequency_penalty": 0.0
      },
      "creative": {
        "name": "Pro/deepseek-ai/DeepSeek-V3",
        "description": "DeepSeek-V3大模型，适合创意和发散思维",
        "temperature": 0.9,
        "max_tokens": 1024,
        "enable_thinking": false,
        "frequency_penalty": 0.5
      },
      "precise": {
        "name": "Pro/Qwen/Qwen2.5-7B-Instruct", 
        "description": "精确模型 - 适合精确回答和工具调用",
        "temperature": 0.3,
        "max_tokens": 1024,
        "enable_thinking": false,
        "frequency_penalty": 2.0
      }
    }
  },
  "xunfei": {
    "api_password": "your_xunfei_api_password",
    "appid": "your_xunfei_appid",
    "api_secret": "your_xunfei_api_secret",
    "api_key": "your_xunfei_api_key"
  },
  "ha": {
    "url": "http://your_home_assistant_ip:8123",
    "api_token": "your_home_assistant_token"
  },
  "music_dir": "/path/to/your/music/directory"
}
```

**Docker服务说明:**
- **homeassistant**: Home Assistant智能家居平台，提供智能设备控制功能
  - 容器名称: homeassistant
  - 镜像: ghcr.io/home-assistant/home-assistant:stable
  - 网络模式: host（直接使用主机网络）
  - 时区: Asia/Shanghai
  - 配置目录: /home/Shattered/HA/config
  - 自动重启: unless-stopped

**配置说明:**
- **baidu**: 百度语音识别和合成API配置
- **openai**: OpenAI API配置，支持自定义base_url
- **silicon**: 硅基流动API配置，支持多模型配置
- **xunfei**: 讯飞星火API配置
- **ha**: Home Assistant智能家居配置
- **music_dir**: 音乐文件目录路径

4. **运行系统**
```bash
cd Pi/MAIN
python main_simplified.py
```

## 🎯 使用说明

### 基本操作
1. **启动系统**: 运行主程序
2. **语音唤醒**: 通过硬件触发器或语音唤醒
3. **语音交互**: 说出您的需求
4. **功能执行**: 系统自动执行相应动作

### 支持的命令
- "播放音乐" - 播放本地音乐
- "推荐电影" - 智能电影推荐
- "调节音量" - 系统音量控制
- "开灯/关灯" - 智能家居控制
- "提供饮料" - 硬件控制演示

## 🔧 开发指南

### 添加新功能
1. 在相应模块中添加功能代码
2. 在AI处理中prompt添加意图识别
3. 在动作执行中添加具体实现
4. 更新配置文件

### 调试方法
- 查看控制台日志输出
- 使用性能监控工具
- 检查配置文件设置
- 验证API密钥有效性

## 📊 性能特性

- **响应速度**: 语音识别到响应 < 2秒
- **识别准确率**: 语音识别准确率 > 95%
- **系统稳定性**: 7x24小时稳定运行
- **扩展性**: 支持多种AI提供者和硬件设备

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/Shattered217/AstraLink)
- 问题反馈: [Issues](https://github.com/Shattered217/AstraLink/issues)
- 邮箱: shattered0217@gmail.com

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我一个星标！**

Made with ❤️ by Shattered217

</div>
