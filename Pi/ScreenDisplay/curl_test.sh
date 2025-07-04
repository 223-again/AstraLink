#!/bin/bash

# ScreenDisplay curl测试脚本
BASE_URL="http://localhost:5000"

echo "🚀 ScreenDisplay curl测试脚本"
echo "================================"

# 测试表情更新
echo "🎭 测试表情更新..."
curl -X POST "$BASE_URL/api/mood" \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy"}' \
  -w " - 状态码: %{http_code}\n"

sleep 1

curl -X POST "$BASE_URL/api/mood" \
  -H "Content-Type: application/json" \
  -d '{"mood": "thinking"}' \
  -w " - 状态码: %{http_code}\n"

sleep 1

curl -X POST "$BASE_URL/api/mood" \
  -H "Content-Type: application/json" \
  -d '{"mood": "cool"}' \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试对话更新
echo "💬 测试对话更新..."
curl -X POST "$BASE_URL/api/add_history" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "response": "你好！有什么可以帮助你的吗？"}' \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试WiFi质量
echo "📶 测试WiFi质量..."
curl -X POST "$BASE_URL/api/wifi_quality" \
  -H "Content-Type: application/json" \
  -d '{"wifi_quality": 85}' \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试状态更新
echo "🔴 测试状态更新..."
curl -X POST "$BASE_URL/api/status" \
  -H "Content-Type: application/json" \
  -d '{"status": 1}' \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试传感器数据
echo "🌡️ 测试传感器数据..."
curl -X GET "$BASE_URL/api/sensor" \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试强制更新传感器
echo "🔄 测试强制更新传感器..."
curl -X GET "$BASE_URL/api/sensor/force_update" \
  -w " - 状态码: %{http_code}\n"

echo ""

# 测试一言
echo "📝 测试一言..."
curl -X GET "$BASE_URL/api/yiyan" \
  -w " - 状态码: %{http_code}\n"

echo ""
echo "🎉 curl测试完成!" 