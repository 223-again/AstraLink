import subprocess

class AudioRecorder:
    def __init__(self, sample_rate=16000, sample_size_in_bits=16, channels=1, buffer_length_in_bytes=4096):
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_SIZE_IN_BITS = sample_size_in_bits
        self.CHANNELS = channels
        self.BUFFER_LENGTH_IN_BYTES = buffer_length_in_bytes

    def record_audio(self, duration, filename, device="plughw:3,0"):
        print(f"[arecord] 开始录音 {duration} 秒...")
        cmd = [
            "arecord",
            "-D", device,
            "-f", "S16_LE",
            "-r", "16000",
            "-d", str(duration),
            filename
        ]
        subprocess.run(cmd, check=True)
        print(f"[arecord] 录音完成，文件已保存为 {filename}")

    def record_audio_pcm(self, duration, filename, device="plughw:3,0"):
        """
        录制原始PCM音频，推荐参数：
        - 格式：pcm
        - 采样率：16000
        - 通道数：1
        """
        print(f"[arecord] 开始录制 PCM {duration} 秒...")
        cmd = [
            "arecord",
            "-D", device,
            "-f", "S16_LE",
            "-r", "16000",
            "-c", "1",
            "-d", str(duration),
            "-t", "raw",
            filename
        ]
        subprocess.run(cmd, check=True)
        print(f"[arecord] PCM录音完成，文件已保存为 {filename}")

    def deinit(self):
        pass

# 测试代码
if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record_audio(5, "test.pcm", device="plughw:2,0")
    recorder.record_audio_pcm(5, "recording.pcm")
    recorder.deinit() 