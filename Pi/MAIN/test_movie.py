#!/usr/bin/env python3
"""
测试影片发送脚本
用于测试data_sender的send_movie_name功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_sender import send_movie_name

async def test_movie_sending():
    """测试发送影片名称"""
    
    # 测试影片列表
    test_movies = [
        "肖申克的救赎",
        "阿甘正传", 
        "泰坦尼克号",
        "星球大战",
        "复仇者联盟",
        "指环王",
        "哈利波特",
        "功夫熊猫",
        "疯狂动物城",
        "寻梦环游记"
    ]
    
    # 随机选择一个影片
    import random
    movie = random.choice(test_movies)
    
    print("🎬 开始测试影片发送功能...")
    print("=" * 50)
    print(f"📽️ 随机选择影片: {movie}")
    
    try:
        await send_movie_name(movie)
        print(f"✅ 成功发送影片: {movie}")
    except Exception as e:
        print(f"❌ 发送失败: {e}")
    
    print("=" * 50)
    print("🎬 影片发送测试完成!")

async def test_single_movie(movie_name):
    """测试发送单个影片"""
    print(f"🎬 测试发送单个影片: {movie_name}")
    try:
        await send_movie_name(movie_name)
        print(f"✅ 成功发送影片: {movie_name}")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，测试单个影片
        movie_name = sys.argv[1]
        asyncio.run(test_single_movie(movie_name))
    else:
        # 否则运行完整测试
        asyncio.run(test_movie_sending()) 