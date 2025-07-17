import asyncio
import random
import signal

# 导入必要的模块
from active import TriggerManager
from music_interrupt import MusicInterruptHandler
from baidu_audio import recongize, speech_tts
from load_config import *
from mic import AudioRecorder
from ai import create_ai
from silicon_provider import create_silicon_provider
from xunfei_provider import create_xunfei_provider
from openai_provider import create_openai_provider
from stepper_motor_control import move_up, move_down, business_cycle, start_business_cycle_thread
from ha_command import ha_action
from data_sender import send_data, send_movie_name, start_chassis
from volume_control import handle_volume_command
from optimization_config import performance_monitor

class SimplifiedApplication:
    def __init__(self, mic_device="default"):
        """初始化应用"""
        # 基础属性
        self.trigger_manager = None
        self.config = None
        self.mic_device = mic_device
        self.music_handler = None
        self.ai = None
        self.last_recommended_movie = ""
        self.running = True
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    # ==================== 信号处理 ====================
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"\n收到信号 {signum}，正在退出...")
        self.running = False

    # ==================== 系统初始化和配置 ====================
    async def initialize(self):
        """初始化应用"""
        try:
            performance_monitor.start_timing("系统初始化")
            print("🚀 开始系统初始化...")
            
            # 加载配置
            print("📋 加载配置...")
            self.config = load_config()
            if not self.config:
                raise RuntimeError("配置加载失败")
            print("✅ 配置加载成功")
            
            # 检查关键配置
            await self._check_config()
            
            # 初始化各个组件
            await self._init_music_handler()
            await self._init_ai_processor()
            await self._init_trigger_manager()
            
            print("✅ 系统初始化完成")
            performance_monitor.end_timing("系统初始化")
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            raise

    async def _check_config(self):
        """检查关键配置"""
        if not self.config:
            raise RuntimeError("配置为空")
            
        if "baidu" not in self.config or not self.config["baidu"] or "api_key" not in self.config["baidu"] or "secret_key" not in self.config["baidu"]:
            raise RuntimeError("配置文件缺少 baidu.api_key 或 baidu.secret_key")
        print("✅ 百度API配置检查通过")
        
        if "music_dir" not in self.config:
            raise RuntimeError("配置文件缺少 music_dir")
        print("✅ 音乐目录配置检查通过")

    async def _init_music_handler(self):
        """初始化音乐处理器"""
        print("🎵 初始化音乐处理器...")
        if not self.config:
            raise RuntimeError("配置未初始化")
        self.music_handler = MusicInterruptHandler(self.config["music_dir"])
        print("✅ 音乐处理器初始化完成")

    async def _init_ai_processor(self):
        """初始化AI处理器"""
        print("🤖 初始化AI处理器...")
        try:
            # 尝试多种AI提供者
            xunfei_config = self.config.get("xunfei", {}) if self.config else {}
            xunfei_password = xunfei_config.get("api_password", "")
            
            providers_to_try = [
                ("OpenAI", lambda: create_openai_provider()),
                ("讯飞星火", lambda: create_xunfei_provider(xunfei_password)),
                ("硅基流动", lambda: create_silicon_provider())
            ]
            
            for provider_name, provider_creator in providers_to_try:
                try:
                    print(f"🔄 尝试初始化 {provider_name} 提供者...")
                    provider = provider_creator()
                    
                    # 测试连接
                    if hasattr(provider, 'test_connection'):
                        is_connected = await provider.test_connection()
                        if not is_connected:
                            print(f"⚠️ {provider_name} 连接测试失败，尝试下一个...")
                            continue
                    
                    self.ai = create_ai(provider)
                    print(f"✅ AI处理器初始化完成 (使用 {provider_name})")
                    return
                    
                except Exception as e:
                    print(f"⚠️ {provider_name} 初始化失败: {e}")
                    continue
            
            # 如果所有提供者都失败，使用默认的硅基流动
            print("⚠️ 所有AI提供者初始化失败，使用默认硅基流动提供者")
            provider = create_silicon_provider()
            self.ai = create_ai(provider)
            print("✅ AI处理器初始化完成 (使用默认硅基流动)")
            
        except Exception as e:
            print(f"⚠️ AI处理器初始化失败: {e}")
            print("系统将继续运行，但AI功能可能不可用")

    async def _init_trigger_manager(self):
        """初始化触发器管理器"""
        print("🔧 初始化触发器管理器...")
        try:
            self.trigger_manager = TriggerManager(
                handler=self.handle_trigger_actions,
                baudrate=9600,
                serial_port='/dev/ttyUSB0' 
            )
            print("✅ 触发器管理器创建成功")
            
            # 启动触发器处理任务
            self.process_triggers_task = asyncio.create_task(self.trigger_manager.process_triggers())
            print("✅ 触发器管理器初始化完成")
            
        except Exception as e:
            print(f"⚠️ 触发器管理器初始化失败: {e}")
            print("系统将继续运行，但硬件触发功能可能不可用")

    # ==================== 固定方法 ====================
    def _check_basic_config(self):
        """检查基本配置"""
        if not self.config or \
           "baidu" not in self.config or \
           "api_key" not in self.config["baidu"] or \
           "secret_key" not in self.config["baidu"]:
            print("❌ 配置未正确初始化，无法执行后续操作")
            return False
        return True

    async def _start_chassis(self):
        """启动底盘"""
        print("🚗 启动底盘...")
        await start_chassis()

    async def _play_active_response(self, baidu_cfg):
        """播放主动响应"""
        performance_monitor.start_timing("主动响应TTS")
        
        active_responses = [
            "你好，我在呢。",
            "你好，需要帮忙吗？",
            "你好，我已经准备好了。",
            "你好，随时为您服务。",
            "你好，请问需要做什么？"
        ]
        
        response = random.choice(active_responses)
        print(f"🎤 播放主动响应: {response}")
        
        await speech_tts(
            baidu_cfg.get("api_key", ""),
            baidu_cfg.get("secret_key", ""),
            response
        )
        performance_monitor.end_timing("主动响应TTS")

    async def _record_and_recognize(self, baidu_cfg):
        """录音和识别"""
        print("🎙️ 开始录音...")
        await send_data("status", "1")
        
        recorder = AudioRecorder()
        recorder.record_audio_pcm(5, "recording.pcm", device=self.mic_device)
        recorder.deinit()
        
        performance_monitor.start_timing("语音识别")
        print("🔍 开始语音识别...")
        text = recongize(
            baidu_cfg.get("api_key", ""),
            baidu_cfg.get("secret_key", ""),
            "recording.pcm"
        )
        performance_monitor.end_timing("语音识别")
        
        print(f"📝 识别结果: {text}")
        return text

    async def _process_with_ai(self, text):
        """使用AI处理"""
        if not self.ai:
            print("❌ AI处理器未初始化")
            return {"success": False, "error": "AI处理器未初始化"}
        
        performance_monitor.start_timing("AI处理")
        print("🤖 开始AI处理...")
        
        # 立即发送"思考"表情
        asyncio.create_task(send_data("emoji", "思考"))
        
        # 构建上下文
        context = {
            "last_movie": self.last_recommended_movie
        }
        
        # 使用AI处理器
        result = await self.ai.process_user_input(text, context)
        performance_monitor.end_timing("AI处理")
        
        return result

    async def _handle_ai_failure(self, baidu_cfg):
        """处理AI失败"""
        print("❌ AI处理失败，播放错误信息")
        
        # 发送失败表情
        print("😔 发送失败表情...")
        await send_data("emoji", "惊恐")
        
        error_msg = "抱歉，我现在无法理解您的意思，请稍后再试。"
        await speech_tts(
            baidu_cfg.get("api_key", ""),
            baidu_cfg.get("secret_key", ""),
            error_msg
        )

    async def _handle_ai_result(self, ai_result, text, baidu_cfg):
        """处理AI结果"""
        ai_data = ai_result["data"]
        audio_content = ai_data.get("audio_content", "")
        actions = ai_data.get("actions", [])
        emoji = ai_data.get("emoji", "思考")
        
        print(f"🎭 选择表情: {emoji}")
        print(f"📢 播报内容: {audio_content}")
        print(f"⚡ 执行动作: {len(actions)} 个")
        
        await send_data("emoji", emoji)
        
        # 发送对话信息到显示界面
        if text and text.strip():
            await send_data("ai_chat", text, audio_content)
        
        # 播放TTS
        if audio_content:
            performance_monitor.start_timing("TTS播报")
            asyncio.create_task(speech_tts(
                baidu_cfg.get("api_key", ""),
                baidu_cfg.get("secret_key", ""),
                audio_content
            ))
            performance_monitor.end_timing("TTS播报")
        
        # 执行动作
        if actions:
            performance_monitor.start_timing("动作执行")
            await self.execute_actions(actions, audio_content)
            performance_monitor.end_timing("动作执行")

    def _print_performance_summary(self):
        """打印性能统计"""
        print("\n" + "="*50)
        print("📊 性能统计")
        print("="*50)
        print(performance_monitor.get_timing_summary())
        print("="*50)

    # ==================== 主要处理流程 ====================
    async def handle_trigger_actions(self):
        """处理触发器动作 - 主要处理流程"""
        performance_monitor.start_timing("完整响应处理")
        print("\n" + "="*60)
        print("🎯 开始处理用户请求")
        print("="*60)
        
        # 停止当前音乐
        if self.music_handler:
            await self.music_handler.stop_current_music()
        
        # 检查配置
        if not self._check_basic_config():
            return
        
        try:
            if not self.config:
                print("❌ 配置未初始化")
                return
            baidu_cfg = self.config.get("baidu") or {}
            
            # 启动底盘
            await self._start_chassis()
            
            # 播放主动响应
            await self._play_active_response(baidu_cfg)
            
            # 录音和识别
            text = await self._record_and_recognize(baidu_cfg)
            if not text or not text.strip():
                print("⚠️ 语音识别结果为空")
                # 发送事件结束状态
                print("📡 语音识别为空时发送事件结束状态...")
                await send_data("status", "0")
                return
            
            # AI处理
            ai_result = await self._process_with_ai(text)
            if not ai_result.get("success"):
                await self._handle_ai_failure(baidu_cfg)
                # 发送事件结束状态
                print("📡 AI处理失败时发送事件结束状态...")
                await send_data("status", "0")
                return
            
            # 处理AI结果
            await self._handle_ai_result(ai_result, text, baidu_cfg)
            
            # 打印性能统计
            self._print_performance_summary()
            
            # 发送事件结束状态
            print("📡 发送事件结束状态...")
            await send_data("status", "0")
            
        except Exception as e:
            print(f"❌ 处理异常: {e}")
            # 异常时也发送事件结束状态
            print("📡 异常时发送事件结束状态...")
            await send_data("status", "0")
        finally:
            performance_monitor.end_timing("完整响应处理")

    # ==================== 动作执行 ====================
    async def execute_actions(self, actions, audio_content=""):
        """执行AI返回的动作列表"""
        if not actions:
            return
        
        print(f"🚀 开始执行 {len(actions)} 个动作...")
        
        for i, action in enumerate(actions, 1):
            action_type = action.get("action_type")
            parameters = action.get("parameters", {})
            
            print(f"📋 执行动作 {i}/{len(actions)}: {action_type}")
            print(f"   参数: {parameters}")
            
            try:
                performance_monitor.start_timing(f"执行动作_{action_type}")
                
                if action_type == "volume_control":
                    await self._execute_volume_control(parameters)
                elif action_type == "play_music":
                    await self._execute_play_music(parameters)
                elif action_type == "recommend_movie":
                    await self._execute_recommend_movie(parameters)
                elif action_type == "drink_request":
                    await self._execute_drink_request(parameters)
                elif action_type == "ha_action":
                    await self._execute_ha_action(parameters)
                elif action_type == "ai_chat":
                    print("💬 AI聊天动作 - TTS已播放")
                else:
                    print(f"⚠️ 未知动作类型: {action_type}")
                
                performance_monitor.end_timing(f"执行动作_{action_type}")
                
            except Exception as e:
                print(f"❌ 执行动作 {action_type} 时出错: {e}")

    async def _execute_volume_control(self, parameters):
        """执行音量控制"""
        volume_command = parameters.get("command") or parameters.get("volume_command")
        if volume_command:
            print(f"🔊 调节音量: {volume_command}")
            result = await handle_volume_command(volume_command)
            print(f"🔊 音量控制结果: {result}")
        else:
            print("⚠️ 音量控制参数缺失")

    async def _execute_play_music(self, parameters):
        """执行音乐播放"""
        if not self.music_handler:
            print("⚠️ 音乐处理器未初始化")
            return
            
        music_name = parameters.get("music_name", "")
        print(f"🎵 播放音乐: '{music_name}'")
        
        if music_name == "随机音乐" or not music_name:
            print("🎲 随机播放音乐")
            asyncio.create_task(self.music_handler.play_random_music())
        else:
            print(f"🎵 尝试播放指定音乐: {music_name}")
            try:
                asyncio.create_task(self.music_handler.play_music_by_name(music_name))
            except Exception as e:
                print(f"🎵 指定音乐'{music_name}'播放失败，改为随机播放: {e}")
                asyncio.create_task(self.music_handler.play_random_music())

    async def _execute_recommend_movie(self, parameters):
        """执行电影推荐"""
        movie_name = parameters.get("movie_name", "")
        if movie_name and movie_name != "0":
            print(f"🎬 推荐电影: '{movie_name}'")
            self.last_recommended_movie = movie_name
            await send_movie_name(movie_name)

    async def _execute_drink_request(self, parameters):
        """执行饮料请求（通过步进电机提供饮料）"""
        provide_drink = parameters.get("provide_drink", False)
        if provide_drink:
            print("🥤 提供饮料（步进电机控制）")
            # 使用新的步进电机函数，在后台线程中执行，不阻塞主函数
            loop = asyncio.get_event_loop()
            # 启动业务循环线程（向上到顶->等待3秒->向下到底）
            await loop.run_in_executor(None, start_business_cycle_thread)

    async def _execute_ha_action(self, parameters):
        """执行智能家居动作"""
        action = parameters.get("action")
        if action == "light_on":
            print("💡 开启灯光")
            await ha_action("light_on")
        elif action == "light_off":
            print("🌙 关闭灯光")
            await ha_action("light_off")
        else:
            print(f"⚠️ 未知的HA动作: {action}")

    # ==================== 系统运行和清理 ====================
    async def run(self):
        """运行应用"""
        try:
            await self.initialize()
            print("✅ 系统运行中... 按 Ctrl+C 退出")
            
            # 主循环
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⚠️ 收到键盘中断信号")
        except Exception as e:
            print(f"❌ 系统崩溃: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        print("🧹 正在清理资源...")
        
        # 停止音乐
        if self.music_handler:
            await self.music_handler.stop_current_music()
        
        # 取消任务
        if hasattr(self, 'process_triggers_task'):
            self.process_triggers_task.cancel()
            try:
                await self.process_triggers_task
            except asyncio.CancelledError:
                pass
        
        print("✅ 资源清理完成")

async def main():
    """主函数"""
    # 创建应用实例
    app = SimplifiedApplication()
    
    # 运行应用
    await app.run()

if __name__ == '__main__':
    asyncio.run(main()) 