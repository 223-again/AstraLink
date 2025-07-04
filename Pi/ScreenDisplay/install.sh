#!/bin/bash

echo "正在安装 ScreenDisplay 依赖..."

# 检查Python版本
python3 --version

# 升级pip
python3 -m pip install --upgrade pip

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 检查安装结果
echo "检查安装结果..."
python3 -c "import flask, flask_socketio, requests; print('所有依赖安装成功！')"

echo "安装完成！"
echo "运行命令启动服务："
echo "python3 app.py" 