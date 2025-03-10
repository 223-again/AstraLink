from wifi_connect import do_connect
import active 
from audio import play_audio
import uasyncio as asyncio

async def audio_handler():
    print("检测到触发, 播放音频...")
    try:
        await play_audio("http://192.168.101.164:6799/nihao.wav")
    except Exception as e:
        print("播放失败:", e)
        
def trigger_callback():
    """回调函数，执行音频播放"""
    await audio_handler() 
    print("音频播放完成，继续执行其他任务...") 

async def main():
    print("Welcome to MicroPython!")
    
    # 注册触发回调
    active.register_trigger_callback(trigger_callback)
    
    # 连接WiFi
    await do_connect()
    
    # 启动触发监控任务
    asyncio.create_task(active.monitor_triggers())
    
    # 保持事件循环运行
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
