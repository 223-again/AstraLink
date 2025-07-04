import os
import random
import asyncio
import subprocess

class MusicInterruptHandler:
    def __init__(self, music_dir: str):
        self.music_dir = music_dir
        self.current_process = None
        self.lock = asyncio.Lock()
        print(f"音乐处理器初始化完成，音乐目录: {music_dir}")
    
    @staticmethod
    async def stop_all_music_immediately():
        try:
            print("开始立即停止所有音乐播放...")
            result = os.system("pkill -9 vlc")
            if result == 0:
                print("成功终止VLC进程")
            else:
                print("没有检测到VLC进程")
        except Exception as e:
            print(f"立即停止音乐播放时出错: {e}")
    
    def get_music_files(self) -> list:
        if not os.path.exists(self.music_dir):
            print(f"音乐目录不存在: {self.music_dir}")
            return []
        
        valid_files = []
        for root, _, files in os.walk(self.music_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_valid_audio(file_path):
                    valid_files.append(file_path)
        
        print(f"找到 {len(valid_files)} 个有效音乐文件")
        return valid_files
    
    def _is_valid_audio(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ('.mp3', '.wav', '.flac', '.ogg', '.m4a')
    
    async def play_random_music(self) -> bool:
        async with self.lock:
            await self.stop_current_music()
            
            music_files = self.get_music_files()
            if not music_files:
                return False
            
            chosen_file = random.choice(music_files)
            print(f"尝试播放: {os.path.basename(chosen_file)}")
            
            success = await self._vlc_program_play(chosen_file)
            if not success:
                print(f"VLC程序播放失败: {chosen_file}")
                return False
            
            return True
    
    async def _vlc_program_play(self, file_path: str) -> bool:
        try:
            cmd = [
                "vlc",
                "--intf", "dummy",
                "--play-and-exit",
                "--no-xlib",
                file_path
            ]
            
            print(f"执行VLC命令: {' '.join(cmd)}")
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            await asyncio.sleep(0.5)
            if self.current_process.poll() is None:
                print(f"VLC程序播放已启动: {os.path.basename(file_path)}")
                return True
            else:
                print("VLC程序启动失败")
                return False
        
        except Exception as e:
            print(f"VLC程序播放出错: {str(e)}")
            return False
    
    async def stop_current_music(self):
        if hasattr(self, 'current_process') and self.current_process:
            try:
                self.current_process.terminate()
                try:
                    self.current_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.current_process.kill()
                    self.current_process.wait()
                print("VLC程序进程已停止")
            except Exception as e:
                print(f"停止VLC程序进程失败: {e}")
            finally:
                self.current_process = None
    
    def _normalize_filename(self, filename: str) -> str:
        """标准化文件名，去除特殊字符和格式"""
        # 去除文件扩展名
        name = os.path.splitext(filename)[0]
        # 替换常见的特殊字符
        name = name.replace('+', ' ').replace('-', ' ').replace('_', ' ')
        # 去除方括号内容
        import re
        name = re.sub(r'\[.*?\]', '', name)
        # 去除多余空格
        name = ' '.join(name.split())
        return name.lower()
    
    def _calculate_similarity(self, query: str, filename: str) -> float:
        """计算查询词与文件名的相似度"""
        query = query.lower()
        normalized_filename = self._normalize_filename(filename)
        
        # 完全匹配
        if query in normalized_filename or normalized_filename in query:
            return 1.0
        
        # 分词匹配
        query_words = query.split()
        filename_words = normalized_filename.split()
        
        # 计算匹配的单词数
        matched_words = sum(1 for qw in query_words if any(qw in fw or fw in qw for fw in filename_words))
        
        if not query_words:
            return 0.0
        
        return matched_words / len(query_words)
    
    async def play_music_by_name(self, music_name: str) -> bool:
        async with self.lock:
            await self.stop_current_music()
            music_files = self.get_music_files()
            if not music_files:
                print("没有找到任何音乐文件")
                return False
            
            print(f"搜索音乐: {music_name}")
            print(f"可用音乐文件: {[os.path.basename(f) for f in music_files]}")
            
            # 计算每个文件的相似度
            similarities = []
            for file_path in music_files:
                filename = os.path.basename(file_path)
                similarity = self._calculate_similarity(music_name, filename)
                similarities.append((file_path, similarity, filename))
                print(f"  {filename}: 相似度 {similarity:.2f}")
            
            # 按相似度排序，选择最匹配的
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            if not similarities or similarities[0][1] == 0:
                print(f"未找到匹配的音乐: {music_name}")
                return False
            
            chosen_file, similarity, filename = similarities[0]
            print(f"选择最匹配的音乐: {filename} (相似度: {similarity:.2f})")
            
            success = await self._vlc_program_play(chosen_file)
            if not success:
                print(f"VLC程序播放失败: {chosen_file}")
                return False
            return True