import asyncio
import random
from pathlib import Path

# 导入必要的模块
from active import TriggerManager
from music_interrupt import MusicInterruptHandler
from baidu_audio import recongize, speech_tts
from load_config import *
from mic import AudioRecorder
from silicon_deepseek import ask_question
from stepper_motor_control import move_motor, TOTAL_TRAVEL_STEPS
from ha_command import ha_action
from send_data import send_data
from emby import send_movie_name

# 音乐目录
MUSIC_DIR = "/home/Shattered/Music"

# 全局变量
movie_name = "0"

class Application:
    def __init__(self, mic_device):
        self.trigger_manager = None
        self.config = None
        self.mic_device = mic_device
        self.music_handler = MusicInterruptHandler(MUSIC_DIR)  # 创建音乐中断处理器

    async def initialize(self):
        try:
            print("开始加载配置...")
            self.config = load_config()
            if not self.config:
                raise RuntimeError("配置加载失败")
            print("配置加载成功")
            
            # 检查关键字段
            if "baidu" not in self.config or "api_key" not in self.config["baidu"] or "secret_key" not in self.config["baidu"]:
                raise RuntimeError("配置文件缺少 baidu.api_key 或 baidu.secret_key")
            print("配置检查通过")
            
            print("开始初始化触发器...")
            await self.init_trigger_manager()
            print("触发器初始化完成")
            
            print("系统初始化完成")
            
        except Exception as e:
            print(f"系统初始化失败: {e}")
            raise

    async def connect_wifi(self):
        try:
            print("WiFi连接成功")
        except Exception as e:
            print(f"WiFi连接失败: {e}")
            raise

    async def init_trigger_manager(self):
        try:
            print("开始初始化TriggerManager...")
            self.trigger_manager = TriggerManager(
                handler=self.handle_trigger_actions,
                baudrate=9600,
                serial_port='/dev/ttyUSB0' 
            )
            print("TriggerManager创建成功")
            
            # 确保process_triggers任务被正确启动并保存
            print("准备启动process_triggers任务...")
            self.process_triggers_task = asyncio.create_task(self.trigger_manager.process_triggers())
            print(f"串口触发器已初始化，process_triggers任务ID: {id(self.process_triggers_task)}")
            
            # 等待一下确保任务启动
            print("等待任务启动...")
            await asyncio.sleep(1)
            
            # 检查任务状态
            if self.process_triggers_task.done():
                print("警告: process_triggers任务已完成，可能有异常")
                try:
                    await self.process_triggers_task  # 这会抛出异常
                except Exception as e:
                    print(f"process_triggers任务异常: {e}")
                    raise
            else:
                print("process_triggers任务正在运行")
            
            print("TriggerManager初始化完成")
            
        except Exception as e:
            print(f"TriggerManager初始化失败: {e}")
            raise

    async def handle_trigger_actions(self):
        print("=== handle_trigger_actions 开始执行 ===")
        # 停止当前可能正在播放的音乐
        await self.music_handler.stop_current_music()
        print("音乐已停止")
        
        if not self.config or \
           "baidu" not in self.config or \
           "api_key" not in self.config["baidu"] or \
           "secret_key" not in self.config["baidu"]:
            print("配置未正确初始化，无法执行后续操作")
            return
        print("配置检查通过，开始执行主要逻辑...")
        
        try:
            # 1. 播放主动响应
            active_response = random.choice([
                "你好，我在呢。",
                "你好，需要帮忙吗？",
                "你好，我已经准备好了。",
                "你好，随时为您服务。",
                "你好，请问需要做什么？"
            ])
            print(f"播放主动响应: {active_response}")
            await speech_tts(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                active_response
            )

            # 2. 录音处理（新增）
            print("开始录音...")
            recorder = AudioRecorder()
            recorder.record_audio_pcm(5, "recording.pcm", device=self.mic_device)
            recorder.deinit()
            print("录音完成")

            # 3. 语音识别（新增）
            print("开始语音识别...")
            text = recongize(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                "recording.pcm"
            )
            print(f"识别结果: {text}")

            # 4. AI处理（新增）
            print("开始AI处理...")
            response = ask_question(
                text,
                self.config["silicon"]["api_token"],
                last_movie=movie_name
            )
            
            print(f"AI响应: {response}")
            
            if not response or not isinstance(response, dict) or not all(key in response for key in ["audio_content", "command", "emoji", "movie"]):
                print("AI处理失败，返回默认响应")
                response = {
                    "audio_content": "抱歉，我现在有点累，能换个方式说吗？",
                    "command": "",
                    "emoji": "thinking",
                    "movie": "0"
                }

            # 6. 响应处理（新增）
            print("开始响应处理...")
            try:
                # 1. 播放AI的TTS响应
                if response.get("audio_content"):
                    print(f"播放AI TTS响应: {response['audio_content']}")
                    await speech_tts(
                        self.config["baidu"]["api_key"],
                        self.config["baidu"]["secret_key"],
                        response["audio_content"]
                    )
                
                # 2. 串行处理所有任务
                # 2.1 饮料业务（电机）
                if response.get("command") == "drink":
                    print("检测到用户观影想喝饮料，启动电机上升到顶，等待5秒后下降到底。")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, move_motor, TOTAL_TRAVEL_STEPS)
                    await asyncio.sleep(5)
                    await loop.run_in_executor(None, move_motor, -TOTAL_TRAVEL_STEPS)
                
                # 2.2 听歌业务（music）- 使用异步任务播放
                if response.get("music"):
                    print("检测到用户有听歌需求，随机播放一首歌曲。")
                    # 使用异步任务播放音乐，不等待完成
                    asyncio.create_task(self.music_handler.play_random_music())
                    print("AI音乐播放已启动")
                
                # 2.3 其他命令
                if response.get("command") and response.get("command") != "drink":
                    print(f"执行命令: {response['command']}")
                    await ha_action(response["command"])
                
                # 2.4 表情
                if response.get("emoji"):
                    print(f"发送表情: {response['emoji']}")
                    await send_data("emoji", response["emoji"])
                
                # 2.5 电影
                if response.get("movie") != "0":
                    print(f"发送电影: {response['movie']}")
                    await send_movie_name(response["movie"])
                
                print("响应处理完成")
                
            except Exception as e:
                print(f"响应处理异常: {e}")
                # 如果响应处理失败，仍然播放测试音乐
                print("响应处理失败，播放测试音乐...")
                await asyncio.sleep(1)
                asyncio.create_task(self.music_handler.play_random_music())
                print("测试歌曲已开始播放，等待触发中断...")
            
        except Exception as e:
            print(f"处理异常: {e}")
            
        finally:
            print("=== handle_trigger_actions 执行完成 ===")

async def main():
    # --- 初始化应用 ---
    app = Application(mic_device="default")  # 简化版本不需要实际检测麦克风
    try:
        await app.initialize()
        print("测试系统运行中... 按 Ctrl+C 退出")
        
        # 主循环/事件监听
        while True:
            await asyncio.sleep(30)  # 每30秒检查一次任务状态
    except Exception as e:
        print(f"系统崩溃: {e}")

if __name__ == '__main__':
    asyncio.run(main()) 