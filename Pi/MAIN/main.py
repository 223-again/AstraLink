import asyncio
import random
from pathlib import Path

# 导入必要的模块
from active import TriggerManager
from music_interrupt import MusicInterruptHandler
from baidu_audio import recongize, speech_tts
from load_config import *
from mic import AudioRecorder
from silicon_ai import execute_task, parse_tasks_and_audio, process_tasks_parallel, batch_process_tasks, get_available_models, select_emoji
from stepper_motor_control import move_motor, TOTAL_TRAVEL_STEPS
from ha_command import ha_action
from data_sender import send_data, send_movie_name, start_chassis
from volume_control import handle_volume_command
from optimization_config import performance_monitor, get_processing_strategy, get_api_timeout

# 全局变量
movie_name = "0"

class Application:
    def __init__(self, mic_device):
        self.trigger_manager = None
        self.config = None
        self.mic_device = mic_device
        self.music_handler = None  # 初始化时先不创建，等配置加载后再创建

    async def initialize(self):
        try:
            performance_monitor.start_timing("系统初始化")
            print("开始加载配置...")
            self.config = load_config()
            if not self.config:
                raise RuntimeError("配置加载失败")
            print("配置加载成功")
            
            # 检查关键字段
            if "baidu" not in self.config or "api_key" not in self.config["baidu"] or "secret_key" not in self.config["baidu"]:
                raise RuntimeError("配置文件缺少 baidu.api_key 或 baidu.secret_key")
            print("配置检查通过")
            
            # 检查音乐目录
            if "music_dir" not in self.config:
                raise RuntimeError("配置文件缺少 music_dir")
            self.music_handler = MusicInterruptHandler(self.config["music_dir"])  # 用配置文件中的音乐目录创建音乐中断处理器
            
            print("开始初始化触发器...")
            await self.init_trigger_manager()
            print("触发器初始化完成")
            
            print("系统初始化完成")
            performance_monitor.end_timing("系统初始化")
            
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
            
            self.process_triggers_task = asyncio.create_task(self.trigger_manager.process_triggers())
            print("TriggerManager初始化完成")
            
        except Exception as e:
            print(f"TriggerManager初始化失败: {e}")
            raise

    async def _async_task_planning(self, text, api_token):
        """
        异步任务编排方法
        """
        performance_monitor.start_timing("任务编排")
        print("开始任务编排...")
        try:
            # 在线程池中执行同步的任务编排函数
            loop = asyncio.get_event_loop()
            plan = await loop.run_in_executor(
                None, 
                lambda: parse_tasks_and_audio(text, api_token, model_type="task_planning")
            )
            return plan
        finally:
            performance_monitor.end_timing("任务编排")

    async def execute_task_result(self, result):
        """
        执行单个任务结果
        """
        if not result or not isinstance(result, dict):
            return
        
        tool = result.get("tool_name")
        args = result.get("args", {})
        
        print(f"🚀 开始执行任务: {tool}")
        print(f"📋 任务参数: {args}")
        
        try:
            performance_monitor.start_timing(f"执行任务_{tool}")
            
            if tool == "volume_control" and args.get("volume_command"):
                volume_command = args.get("volume_command")
                print(f"🔊 调节音量: {volume_command}")
                await handle_volume_command(volume_command)
            elif tool == "play_music":
                music_name = args.get("music_name", "")
                print(f"🎵 播放音乐: '{music_name}'")
                if self.music_handler:
                    if music_name == "随机音乐" or not music_name:
                        print("🎲 随机播放音乐")
                        asyncio.create_task(self.music_handler.play_random_music())
                    else:
                        print(f"🎵 尝试播放指定音乐: {music_name}")
                        # 先尝试精确匹配，如果失败则随机播放
                        try:
                            asyncio.create_task(self.music_handler.play_music_by_name(music_name))
                        except Exception as e:
                            print(f"🎵 指定音乐'{music_name}'播放失败，改为随机播放: {e}")
                            asyncio.create_task(self.music_handler.play_random_music())
            elif tool == "recommend_movie" and args.get("movie") and args["movie"] != "0":
                movie_name = args.get("movie", "")
                print(f"🎬 推荐电影: '{movie_name}'")
                await send_movie_name(movie_name)
            elif tool == "drink_request" and args.get("drink") is True:
                print("🥤 提供饮料")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, move_motor, TOTAL_TRAVEL_STEPS)
                await asyncio.sleep(5)
                await loop.run_in_executor(None, move_motor, -TOTAL_TRAVEL_STEPS)
            
            performance_monitor.end_timing(f"执行任务_{tool}")
            
        except Exception as e:
            print(f"执行任务 {tool} 时出错: {e}")

    async def handle_trigger_actions(self):
        performance_monitor.start_timing("完整响应处理")
        print("=== handle_trigger_actions 开始执行 ===")
        
        if self.music_handler:
            await self.music_handler.stop_current_music()
        
        if not self.config or \
           "baidu" not in self.config or \
           "api_key" not in self.config["baidu"] or \
           "secret_key" not in self.config["baidu"]:
            print("配置未正确初始化，无法执行后续操作")
            return
        
        print("配置检查通过，开始执行主要逻辑...")
        try:
            baidu_cfg = self.config.get("baidu") or {}
            silicon_cfg = self.config.get("silicon") or {}
            
            # ====== 控制底盘启动 ======
            #await start_chassis()
            # =========================
            
            # 播放主动响应
            performance_monitor.start_timing("主动响应TTS")
            active_response = random.choice([
                "你好，我在呢。",
                "你好，需要帮忙吗？",
                "你好，我已经准备好了。",
                "你好，随时为您服务。",
                "你好，请问需要做什么？"
            ])
            await speech_tts(
                baidu_cfg.get("api_key", ""),
                baidu_cfg.get("secret_key", ""),
                active_response
            )
            performance_monitor.end_timing("主动响应TTS")

            # ====== 录音和识别 ======
            performance_monitor.start_timing("录音")
            recorder = AudioRecorder()
            recorder.record_audio_pcm(5, "recording.pcm", device=self.mic_device)
            recorder.deinit()
            performance_monitor.end_timing("录音")
            
            performance_monitor.start_timing("语音识别")
            text = recongize(
                baidu_cfg.get("api_key", ""),
                baidu_cfg.get("secret_key", ""),
                "recording.pcm"
            )
            performance_monitor.end_timing("语音识别")
            
            # ====== 异步任务编排 ======
            task_planning_task = asyncio.create_task(
                self._async_task_planning(text, silicon_cfg.get("api_token", ""))
            )
            
            # 立即发送默认表情，不等待任务编排完成
            await send_data("emoji", "thinking")
            
            # 等待任务编排完成
            plan = await task_planning_task
            tasks = plan.get("tasks") or []
            audio_content = plan.get("audio_content") or ""
            
            # 任务编排完成后立即播放TTS
            if audio_content:
                performance_monitor.start_timing("任务TTS")
                asyncio.create_task(speech_tts(
                    baidu_cfg.get("api_key", ""),
                    baidu_cfg.get("secret_key", ""),
                    audio_content
                ))
                performance_monitor.end_timing("任务TTS")
            
            # 异步选择表情
            async def select_emoji_async():
                try:
                    performance_monitor.start_timing("表情选择")
                    emoji = select_emoji(text, plan.get("audio_content", ""), silicon_cfg.get("api_token", ""))
                    if emoji and emoji != "thinking":
                        await send_data("emoji", emoji)
                    performance_monitor.end_timing("表情选择")
                except Exception as e:
                    print(f"表情选择失败: {e}")
                    performance_monitor.end_timing("表情选择")
            
            # 创建表情选择任务，不等待完成
            emoji_task = asyncio.create_task(select_emoji_async())
            
            if not tasks:
                return
            
            # 根据任务数量选择处理策略
            strategy, description = get_processing_strategy(len(tasks))
            
            # 异步性能监控，不阻塞主流程
            async def monitor_performance():
                performance_monitor.start_timing(f"任务处理_{strategy}")
            
            # 创建性能监控任务，不等待完成
            perf_task = asyncio.create_task(monitor_performance())
            
            if strategy == "direct":
                # 单个任务，直接处理 - 使用子任务执行专用模型
                async def execute_single_task():
                    try:
                        performance_monitor.start_timing("子任务执行")
                        result = execute_task(
                            tasks[0].get('intent', ''), 
                            text,
                            silicon_cfg.get("api_token", ""),
                            model_type="task_execution"  # 使用子任务执行专用模型
                        )
                        if result:
                            await self.execute_task_result(result)
                        performance_monitor.end_timing("子任务执行")
                    except Exception as e:
                        print(f"子任务执行失败: {e}")
                        performance_monitor.end_timing("子任务执行")
                
                # 创建子任务执行任务，不等待完成
                task_execution_task = asyncio.create_task(execute_single_task())
            elif strategy == "parallel":
                # 少量任务，使用并行处理 - 使用子任务执行专用模型
                context = f"原始输入：{text}\n播报内容：{audio_content}"
                
                # 异步执行并行任务，不阻塞主流程
                async def execute_parallel_tasks():
                    try:
                        results = await process_tasks_parallel(tasks, silicon_cfg.get("api_token", ""), self.config, original_input=context)
                        # 并行执行任务结果
                        execution_tasks = [self.execute_task_result(result) for result in results if result]
                        if execution_tasks:
                            await asyncio.gather(*execution_tasks, return_exceptions=True)
                    except Exception as e:
                        print(f"并行任务执行失败: {e}")
                
                # 创建并行任务执行任务，不等待完成
                parallel_task = asyncio.create_task(execute_parallel_tasks())
                
            elif strategy == "batch":
                # 多个任务，尝试批量处理 - 使用批量处理专用模型
                context = f"原始输入：{text}\n播报内容：{audio_content}"
                
                # 异步执行批量任务，不阻塞主流程
                async def execute_batch_tasks():
                    try:
                        results = batch_process_tasks(
                            tasks, 
                            silicon_cfg.get("api_token", ""), 
                            model_type="batch_processing",  # 使用批量处理专用模型
                            original_input=context
                        )
                        # 并行执行任务结果
                        execution_tasks = [self.execute_task_result(result) for result in results if result]
                        if execution_tasks:
                            await asyncio.gather(*execution_tasks, return_exceptions=True)
                    except Exception as e:
                        print(f"批量任务执行失败: {e}")
                
                # 创建批量任务执行任务，不等待完成
                batch_task = asyncio.create_task(execute_batch_tasks())
            
            # 异步结束性能监控
            async def end_performance_monitoring():
                performance_monitor.end_timing(f"任务处理_{strategy}")
            
            # 创建结束监控任务，不等待完成
            end_perf_task = asyncio.create_task(end_performance_monitoring())
            
            # 打印性能统计
            print("\n" + "="*50)
            print(performance_monitor.get_timing_summary())
            print("="*50)
            
        except Exception as e:
            print(f"处理异常: {e}")
        finally:
            performance_monitor.end_timing("完整响应处理")

async def main():
    # --- 初始化应用 ---
    app = Application(mic_device="default")  # 简化版本不需要实际检测麦克风
    try:
        await app.initialize()
        print("系统运行中... 按 Ctrl+C 退出")
        
        # 主循环/事件监听
        while True:
            await asyncio.sleep(30)  # 每30秒检查一次任务状态
    except Exception as e:
        print(f"系统崩溃: {e}")

if __name__ == '__main__':
    asyncio.run(main()) 