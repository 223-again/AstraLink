# 迁移自Esp32/mic.py
# 需检查MicroPython相关内容并适配为标准Python
# 其余功能结构和流程保持不变

# ... existing code ... 

# 迁移自Esp32/mic.py，适配树莓派标准Python
# 使用sounddevice进行录音，scipy.io.wavfile写入wav文件
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class AudioRecorder:
    def __init__(self, sample_rate=16000, sample_size_in_bits=16, channels=1, buffer_length_in_bytes=4096):
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_SIZE_IN_BITS = sample_size_in_bits
        self.CHANNELS = channels
        self.BUFFER_LENGTH_IN_BYTES = buffer_length_in_bytes

    def generate_wav_header(self, sample_rate, sample_size_in_bits, channels, num_samples):
        # 标准Python下无需手动生成wav头，由scipy.io.wavfile自动处理
        pass

    def record_audio(self, duration, filename):
        print(f"开始录音 {duration} 秒...")
        audio = sd.rec(int(duration * self.SAMPLE_RATE), samplerate=self.SAMPLE_RATE, channels=self.CHANNELS, dtype='int16')
        sd.wait()  # 等待录音结束
        write(filename, self.SAMPLE_RATE, audio)
        print(f"录音完成，文件已保存为 {filename}")

    def deinit(self):
        # 标准Python下无需特殊释放
        pass

# 测试代码
if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record_audio(3, "recording.wav")
    recorder.deinit() 