import os
import random
import asyncio
import logging
from typing import Optional, Tuple
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MusicInterrupt")

class MusicInterruptHandler:
    def __init__(self, music_dir: str):
        """
        简化版音乐中断处理器
        
        使用VLC程序播放，便于检测和停止
        """
        self.music_dir = music_dir
        self.current_process = None
        self.lock = asyncio.Lock()
        
        logger.info(f"音乐处理器初始化完成，音乐目录: {music_dir}")
    
    @staticmethod
    async def stop_all_music_immediately():
        """立即停止所有音乐播放进程"""
        try:
            logger.info("开始立即停止所有音乐播放...")
            
            # 简化的检测逻辑：只检测VLC程序进程
            killed_count = 0
            
            # 方法1: 使用pkill终止VLC进程
            try:
                result = os.system("pkill -9 vlc")
                if result == 0:
                    logger.info("成功终止VLC进程")
                    killed_count += 1
            except Exception as e:
                logger.error(f"终止VLC失败: {e}")
            
            # 方法2: 使用pgrep查找并终止VLC进程
            try:
                result = os.system("pgrep vlc")
                if result == 0:
                    logger.info("发现VLC进程，尝试终止...")
                    os.system("pkill vlc")
                    killed_count += 1
            except Exception as e:
                logger.error(f"查找VLC进程失败: {e}")
            
            if killed_count > 0:
                logger.info(f"成功终止了 {killed_count} 个VLC进程")
            else:
                logger.info("没有检测到VLC进程")
                
        except Exception as e:
            logger.error(f"立即停止音乐播放时出错: {e}")
    
    def get_music_files(self) -> list:
        """获取有效的音乐文件列表"""
        if not os.path.exists(self.music_dir):
            logger.error(f"音乐目录不存在: {self.music_dir}")
            return []
        
        valid_files = []
        for root, _, files in os.walk(self.music_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_valid_audio(file_path):
                    valid_files.append(file_path)
        
        logger.info(f"找到 {len(valid_files)} 个有效音乐文件")
        return valid_files
    
    def _is_valid_audio(self, file_path: str) -> bool:
        """检查文件是否为有效音频"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ('.mp3', '.wav', '.flac', '.ogg', '.m4a')
    
    async def play_random_music(self) -> bool:
        """使用VLC程序播放随机音乐"""
        async with self.lock:
            await self.stop_current_music()
            
            music_files = self.get_music_files()
            if not music_files:
                return False
            
            chosen_file = random.choice(music_files)
            logger.info(f"尝试播放: {os.path.basename(chosen_file)}")
            
            # 使用VLC程序播放
            success = await self._vlc_program_play(chosen_file)
            if not success:
                logger.error(f"VLC程序播放失败: {chosen_file}")
                return False
            
            return True
    
    async def _vlc_program_play(self, file_path: str) -> bool:
        """使用VLC程序播放"""
        try:
            # 使用VLC程序播放，后台运行
            cmd = [
                "vlc",
                "--intf", "dummy",  # 无界面模式
                "--play-and-exit",  # 播放完成后退出
                "--no-xlib",        # 不使用X11
                file_path
            ]
            
            logger.info(f"执行VLC命令: {' '.join(cmd)}")
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待一下确保进程启动
            await asyncio.sleep(0.5)
            if self.current_process.poll() is None:
                logger.info(f"VLC程序播放已启动: {os.path.basename(file_path)}")
                return True
            else:
                logger.error("VLC程序启动失败")
                return False
        
        except Exception as e:
            logger.error(f"VLC程序播放出错: {str(e)}")
            return False
    
    async def stop_current_music(self):
        """停止当前正在播放的音乐"""
        # 停止VLC程序进程
        if hasattr(self, 'current_process') and self.current_process:
            try:
                self.current_process.terminate()
                try:
                    self.current_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.current_process.kill()
                    self.current_process.wait()
                logger.info("VLC程序进程已停止")
            except Exception as e:
                logger.error(f"停止VLC程序进程失败: {e}")
            finally:
                self.current_process = None

# 测试函数
async def test_music_handler():
    """简化版测试函数"""
    MUSIC_DIR = "/home/Shattered/Music"
    handler = MusicInterruptHandler(MUSIC_DIR)
    
    print("=== 测试1: 播放随机音乐 ===")
    await handler.play_random_music()
    await asyncio.sleep(5)  # 正常播放5秒
    
    print("\n=== 测试2: 中断当前播放 ===")
    await handler.stop_current_music()
    await asyncio.sleep(1)
    
    print("\n=== 测试3: 播放另一首随机音乐 ===")
    await handler.play_random_music()
    await asyncio.sleep(10)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    # 检查VLC程序是否安装
    import shutil
    if shutil.which("vlc") is None:
        print("警告: VLC程序未安装，请安装: sudo apt install vlc")
    else:
        print("VLC程序已安装")
    
    # 运行测试
    asyncio.run(test_music_handler())