import asyncio
from mic import *
from baidu_audio import recongize, speech_tts
from silicon_deepseek import ask_question
from active import TriggerManager  
from load_config import *
from ha_command import ha_action
from send_data import send_data
import random
from emby import send_movie_name
from device_finder import find_usb_mic_device, find_i2s_dac_device

movie_name = None

class Application:
    def __init__(self, mic_device, i2s_device):
        self.trigger_manager = None
        self.config = None
        self.mic_device = mic_device
        self.i2s_device = i2s_device

    async def initialize(self):
        self.config = load_config()
        if not self.config:
            raise RuntimeError("配置加载失败")
        # 检查关键字段
        if "baidu" not in self.config or "api_key" not in self.config["baidu"] or "secret_key" not in self.config["baidu"]:
            raise RuntimeError("配置文件缺少 baidu.api_key 或 baidu.secret_key")
        if "silicon" not in self.config or "api_token" not in self.config["silicon"]:
            raise RuntimeError("配置文件缺少 silicon.api_token")
        await self.connect_wifi()
        self.init_trigger_manager()
        print("系统初始化完成")

    async def connect_wifi(self):
        try:
            print("WiFi连接成功")
            await send_data("wifi_quality", "N/A")
        except Exception as e:
            print(f"WiFi连接失败: {e}")
            raise

    def init_trigger_manager(self):
        self.trigger_manager = TriggerManager(
            handler=self.handle_trigger_actions,
            baudrate=9600,
            serial_port='/dev/ttyUSB0' 
        )
        asyncio.create_task(self.trigger_manager.process_triggers())
        print("串口触发器已初始化")

    async def handle_trigger_actions(self):
        if not self.config or \
           "baidu" not in self.config or \
           "api_key" not in self.config["baidu"] or \
           "secret_key" not in self.config["baidu"] or \
           "silicon" not in self.config or \
           "api_token" not in self.config["silicon"]:
            print("配置未正确初始化，无法执行后续操作")
            return
        await send_data("status", 1)
        global movie_name
        text = ""
        response = None
        try:
            active_response = random.choice([
                "你好，我在呢。",
                "你好，需要帮忙吗？",
                "你好，我已经准备好了。",
                "你好，随时为您服务。",
                "你好，请问需要做什么？"
            ])
            await speech_tts(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                active_response,
                i2s_device=self.i2s_device
            )

            # 录音处理
            recorder = AudioRecorder()
            recorder.record_audio_pcm(5, "recording.pcm", device=self.mic_device)
            recorder.deinit()

            # 语音识别
            text = recongize(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                "recording.pcm"
            )

            # AI处理
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

            # 响应处理
            tasks = []
            try:
                if response.get("command"):
                    tasks.append(ha_action(response["command"]))
                if response.get("emoji"):
                    tasks.append(send_data("emoji", response["emoji"]))
                if response.get("movie") != "0":
                    tasks.append(send_movie_name(response["movie"]))
                if response.get("audio_content"):
                    tasks.append(speech_tts(
                        self.config["baidu"]["api_key"],
                        self.config["baidu"]["secret_key"],
                        response["audio_content"],
                        i2s_device=self.i2s_device
                    ))            

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    print("没有需要执行的任务")
            except Exception as e:
                print(f"任务执行异常: {e}")
                await send_data("ai_chat", "任务执行异常", str(e))
        finally:
            await send_data("ai_chat", text, response.get("audio_content", "") if isinstance(response, dict) else "")
            await send_data("status", 0)

async def main():
    # --- 设备检测 ---
    mic_device = find_usb_mic_device()
    i2s_device = find_i2s_dac_device()

    if not mic_device:
        print("致命错误: 未找到USB麦克风，程序退出。")
        return
    if not i2s_device:
        print("致命错误: 未找到I2S DAC设备，程序退出。")
        return

    # --- 初始化应用 ---
    app = Application(mic_device=mic_device, i2s_device=i2s_device)
    try:
        await app.initialize()
        print("系统运行中... 按 Ctrl+C 退出")
        # 主循环/事件监听可以放在这里，目前是休眠
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"系统崩溃: {e}")

if __name__ == '__main__':
    asyncio.run(main()) 