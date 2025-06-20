import serial
import asyncio
import time

class TriggerManager:
    def __init__(self, handler, uart_num=1, baudrate=9600, rx_pin=None, serial_port='/dev/ttyUSB0'):
        # serial_port需根据实际树莓派串口设备名调整
        self.ser = serial.Serial(serial_port, baudrate=baudrate, timeout=0.1)
        self._trigger_event = asyncio.Event()
        self.debounce_ms = 500
        self._last_trigger = 0
        self.handler = handler
        asyncio.create_task(self._uart_listener())

    async def _uart_listener(self):
        buffer = b''
        while True:
            await asyncio.sleep(0.01)
            while self.ser.in_waiting > 0:
                buffer += self.ser.read(1)
                try:
                    message = buffer.decode('utf-8')
                    if '\n' in message:
                        line, rest = message.split('\n', 1)
                        await self._process_command(line.strip())
                        buffer = rest.encode('utf-8')
                except UnicodeDecodeError:
                    buffer = b''

    async def _process_command(self, cmd):
        if cmd == "TRIGGER":
            now = int(time.time() * 1000)
            if now - self._last_trigger > self.debounce_ms:
                self._last_trigger = now
                self._trigger_event.set()
                print("收到有效触发指令")

    async def process_triggers(self):
        while True:
            await self._trigger_event.wait()
            try:
                await self.handler()
            except Exception as e:
                print(f"触发处理链错误: {e}")
            finally:
                self._trigger_event.clear() 