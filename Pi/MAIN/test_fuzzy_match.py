#!/usr/bin/env python3
"""
模糊匹配测试脚本
用于测试音乐文件的模糊匹配功能
"""

import asyncio
from music_interrupt import MusicInterruptHandler
from load_config import load_config

async def test_fuzzy_matching():
    """测试模糊匹配功能"""
    config = load_config()
    if not config or "music_dir" not in config:
        print("配置文件中缺少 music_dir")
        return
    
    music_dir = config["music_dir"]
    print(f"音乐目录: {music_dir}")
    
    # 创建音乐处理器
    music_handler = MusicInterruptHandler(music_dir)
    
    # 获取所有音乐文件
    music_files = music_handler.get_music_files()
    print(f"\n找到 {len(music_files)} 个音乐文件:")
    for i, file_path in enumerate(music_files, 1):
        filename = os.path.basename(file_path)
        normalized = music_handler._normalize_filename(filename)
        print(f"  {i}. {filename}")
        print(f"     标准化后: {normalized}")
    
    # 测试用例
    test_cases = [
        "shape of you",
        "ed sheeran",
        "鸳鸯戏",
        "随机播放",
        "音乐",
        "歌曲",
        "播放",
        "shape",
        "you",
        "ed",
        "sheeran"
    ]
    
    print(f"\n开始测试模糊匹配...")
    for test_query in test_cases:
        print(f"\n测试查询: '{test_query}'")
        print("-" * 50)
        
        # 计算每个文件的相似度
        similarities = []
        for file_path in music_files:
            filename = os.path.basename(file_path)
            similarity = music_handler._calculate_similarity(test_query, filename)
            similarities.append((file_path, similarity, filename))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 显示前3个最匹配的结果
        print("匹配结果:")
        for i, (file_path, similarity, filename) in enumerate(similarities[:3], 1):
            print(f"  {i}. {filename} (相似度: {similarity:.2f})")
        
        if similarities and similarities[0][1] > 0:
            print(f"最佳匹配: {similarities[0][2]} (相似度: {similarities[0][1]:.2f})")
        else:
            print("没有找到匹配")

if __name__ == "__main__":
    import os
    asyncio.run(test_fuzzy_matching()) 