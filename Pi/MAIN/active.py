import serial
import asyncio
import time

class TriggerManager:
    def __init__(self, handler, uart_num=1, baudrate=9600, rx_pin=None, serial_port='/dev/ttyUSB0'):
        # serial_port需根据实际树莓派串口设备名调整
        try:
            print(f"尝试连接串口: {serial_port}")
            self.ser = serial.Serial(serial_port, baudrate=baudrate, timeout=0.1)
            print("串口连接成功")
        except Exception as e:
            print(f"串口连接失败: {e}")
            # 创建一个模拟的串口对象，避免程序崩溃
            self.ser = None
        
        self._trigger_event = asyncio.Event()
        self.debounce_ms = 500
        self._last_trigger = 0
        self.handler = handler
        self._uart_task = None
        print("TriggerManager 初始化完成，开始监听串口...")
        # 注意：这里不创建任务，而是在process_triggers中创建

    async def _uart_listener(self):
        buffer = b''
        print("串口监听器已启动")
        try:
            while True:
                await asyncio.sleep(0.01)
                # 检查串口是否可用
                if self.ser is None:
                    print("串口不可用，跳过读取")
                    continue
                
                # 检查串口是否有数据
                if self.ser.in_waiting > 0:
                    print(f"串口有 {self.ser.in_waiting} 字节数据")
                    
                while self.ser.in_waiting > 0:
                    buffer += self.ser.read(1)
                    try:
                        message = buffer.decode('utf-8')
                        if '\n' in message:
                            line, rest = message.split('\n', 1)
                            print(f"收到串口数据: {line.strip()}")
                            await self._process_command(line.strip())
                            buffer = rest.encode('utf-8')
                    except UnicodeDecodeError:
                        buffer = b''
        except Exception as e:
            print(f"串口监听器异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("串口监听器已停止")

    async def _process_command(self, cmd):
        if cmd == "TRIGGER":
            now = int(time.time() * 1000)
            if now - self._last_trigger > self.debounce_ms:
                self._last_trigger = now
                print("设置触发事件...")
                self._trigger_event.set()
                print("收到有效触发指令")
                
                # 立即停止音乐播放（不等待，避免阻塞）
                print("立即停止音乐播放...")
                try:
                    from music_interrupt import MusicInterruptHandler
                    # 创建任务但不等待，避免阻塞后续逻辑
                    asyncio.create_task(MusicInterruptHandler.stop_all_music_immediately())
                except Exception as e:
                    print(f"停止音乐播放失败: {e}")
                
            else:
                print(f"触发被防抖过滤，距离上次触发: {now - self._last_trigger}ms")

    async def process_triggers(self):
        print("process_triggers 任务已启动，等待触发事件...")
        # 在这里启动串口监听器
        print("准备启动串口监听器...")
        self._uart_task = asyncio.create_task(self._uart_listener())
        print("串口监听器任务已创建")
        
        try:
            while True:
                print("等待触发事件...")
                await self._trigger_event.wait()
                print("触发事件已收到，开始执行handler...")
                try:
                    await self.handler()
                    print("handler执行完成")
                except Exception as e:
                    print(f"触发处理链错误: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    print("清除触发事件")
                    self._trigger_event.clear()
        except Exception as e:
            print(f"process_triggers 异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理串口监听器任务
            if self._uart_task and not self._uart_task.done():
                self._uart_task.cancel()
                try:
                    await self._uart_task
                except asyncio.CancelledError:
                    print("串口监听器任务已取消") 