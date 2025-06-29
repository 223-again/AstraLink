import os
import random
import shutil
import subprocess
import psutil
import signal
import time
import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MusicInterrupt")

class MusicInterruptHandler:
    def __init__(self, music_dir="/home/Shattered/Music"):
        """
        基于已验证播放实现的音乐中断处理器
        
        使用经过验证的子进程管理方法
        支持多种播放器（mpg123, ffplay, aplay）
        支持多种音频格式（wav, mp3, flac, ogg, m4a）
        """
        self.music_dir = music_dir
        self.music_process = None
        self.music_process_group = None
        self.music_task = None
        self.lock = asyncio.Lock()
        logger.info(f"音乐处理器初始化完成，音乐目录: {music_dir}")
    
    def get_music_files(self) -> list:
        """获取音乐目录下的所有音乐文件"""
        if not os.path.isdir(self.music_dir):
            logger.error(f"音乐目录不存在: {self.music_dir}")
            return []
        
        exts = (".wav", ".mp3", ".flac", ".ogg", ".m4a")
        files = [f for f in os.listdir(self.music_dir) if f.lower().endswith(exts)]
        
        logger.info(f"找到 {len(files)} 个音乐文件")
        return files
    
    async def play_random_music(self) -> bool:
        """播放随机一首音乐"""
        async with self.lock:
            # 停止当前可能正在播放的音乐
            await self.stop_current_music()
            
            # 获取音乐文件
            files = self.get_music_files()
            if not files:
                logger.error("没有可用的音乐文件")
                return False
            
            # 随机选择一首音乐
            song = random.choice(files)
            song_path = os.path.join(self.music_dir, song)
            logger.info(f"准备播放: {song}")
            
            # 创建并启动播放任务
            self.music_task = asyncio.create_task(self._play_music_task(song_path))
            return True
    
    async def _play_music_task(self, song_path: str):
        """内部播放任务实现"""
        try:
            # 选择播放器命令
            if song_path.lower().endswith(".mp3"):
                if self._has_bin("mpg123"):
                    cmd = ["mpg123", "-q", song_path]
                elif self._has_bin("ffplay"):
                    cmd = ["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", song_path]
                else:
                    logger.error("未找到 mpg123 或 ffplay，无法播放 mp3 文件")
                    return
            elif song_path.lower().endswith(".wav") or song_path.lower().endswith(".pcm"):
                cmd = ["aplay", song_path]
            elif song_path.lower().endswith((".flac", ".ogg", ".m4a")):
                if self._has_bin("ffplay"):
                    cmd = ["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", song_path]
                elif self._has_bin("mpg123") and song_path.lower().endswith(".flac"):
                    cmd = ["mpg123", "-q", song_path]
                else:
                    logger.error("未找到 ffplay，无法播放该格式音频")
                    return
            else:
                logger.error(f"未知音频格式: {song_path}")
                return
            
            # 启动子进程播放，使用进程组
            logger.info(f"执行命令: {' '.join(cmd)}")
            self.music_process = subprocess.Popen(
                cmd, 
                preexec_fn=os.setsid,  # 创建新的进程组
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.music_process_group = os.getpgid(self.music_process.pid)
            logger.info(f"音乐播放进程已启动，PID: {self.music_process.pid}, 进程组: {self.music_process_group}")
            
            # 等待进程完成或被取消
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.music_process.wait)
                logger.info("音乐播放完成")
            except asyncio.CancelledError:
                logger.info("音乐播放被取消")
                self._stop_music_playback()
                raise
        except Exception as e:
            logger.error(f"播放音乐出错: {str(e)}")
        finally:
            self.music_process = None
            self.music_process_group = None
            self.music_task = None
    
    def _has_bin(self, binname: str) -> bool:
        """检查二进制文件是否存在"""
        return shutil.which(binname) is not None
    
    async def stop_current_music(self):
        """停止当前正在播放的音乐"""
        if self.music_task and not self.music_task.done():
            logger.info("取消音乐播放任务")
            self.music_task.cancel()
            try:
                await self.music_task
            except asyncio.CancelledError:
                logger.info("音乐播放已取消")
        
        # 确保停止所有播放进程
        self._stop_music_playback()
    
    def _stop_music_playback(self):
        """使用多种方式强制终止音乐播放"""
        killed = False
        logger.info("开始中断音乐播放...")
        
        # 方法1: 终止进程组
        if self.music_process_group:
            try:
                logger.info(f"尝试终止进程组: {self.music_process_group}")
                os.killpg(self.music_process_group, signal.SIGTERM)
                time.sleep(0.5)  # 给进程一点时间优雅退出
                
                # 检查是否还在运行
                try:
                    os.killpg(self.music_process_group, 0)  # 检查进程组是否存在
                    logger.info("进程组仍在运行，强制终止")
                    os.killpg(self.music_process_group, signal.SIGKILL)
                except OSError:
                    logger.info("进程组已成功终止")
                    killed = True
            except Exception as e:
                logger.error(f"终止进程组失败: {e}")
        
        # 方法2: 终止具体进程
        if self.music_process and self.music_process.poll() is None:
            try:
                logger.info(f"尝试终止进程: {self.music_process.pid}")
                self.music_process.terminate()
                try:
                    self.music_process.wait(timeout=2)
                    killed = True
                except subprocess.TimeoutExpired:
                    logger.info("进程未响应，强制杀死")
                    self.music_process.kill()
                    self.music_process.wait()
                    killed = True
            except Exception as e:
                logger.error(f"终止进程失败: {e}")
        
        # 方法3: 使用psutil递归杀进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                pname = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(player in pname or player in cmdline for player in ["mpg123", "ffplay", "aplay"]):
                    logger.info(f"发现音乐进程: {pname} (PID: {proc.info['pid']})")
                    # 递归杀死子进程
                    try:
                        parent = psutil.Process(proc.info['pid'])
                        children = parent.children(recursive=True)
                        for child in children:
                            logger.info(f"终止子进程: {child.pid} {child.name()}")
                            child.kill()
                        parent.kill()
                        killed = True
                    except Exception as e:
                        logger.error(f"终止进程 {proc.info['pid']} 失败: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 方法4: 兜底用pkill
        for player in ["mpg123", "ffplay", "aplay"]:
            try:
                result = os.system(f"pkill -9 {player}")
                if result == 0:
                    logger.info(f"pkill成功终止 {player}")
                    killed = True
            except Exception as e:
                logger.error(f"pkill {player} 失败: {e}")
        
        # 清理状态
        self.music_process = None
        self.music_process_group = None
        
        if killed:
            logger.info("音乐播放已成功中断")
        else:
            logger.info("没有检测到需要终止的音乐播放进程")

# 测试函数
async def test_music_handler():
    """测试音乐中断处理器"""
    # 创建处理器实例 - 请替换为你的实际音乐目录
    MUSIC_DIR = "/home/Shattered/Music"
    handler = MusicInterruptHandler(MUSIC_DIR)
    
    print("=== 测试1: 播放随机音乐 ===")
    await handler.play_random_music()
    await asyncio.sleep(5)  # 播放5秒
    
    print("\n=== 测试2: 中断当前播放 ===")
    await handler.stop_current_music()
    await asyncio.sleep(1)
    
    print("\n=== 测试3: 播放另一首随机音乐 ===")
    await handler.play_random_music()
    await asyncio.sleep(10)  # 播放10秒
    
    print("\n=== 测试4: 自然结束播放 ===")
    # 等待可能还在播放的音乐结束
    await asyncio.sleep(5)
    
    print("\n=== 测试完成 ===")

# 运行测试
if __name__ == "__main__":
    # 安装必要依赖（如果未安装）
    required_bins = ["mpg123", "ffplay", "aplay"]
    missing_bins = [bin for bin in required_bins if shutil.which(bin) is None]
    
    if missing_bins:
        print(f"警告: 缺少以下必要程序: {', '.join(missing_bins)}")
        print("请安装: sudo apt install mpg123 ffmpeg alsa-utils")
    
    # 运行测试
    asyncio.run(test_music_handler())