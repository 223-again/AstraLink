import subprocess
import re

def find_usb_mic_device():
    """
    自动查找USB麦克风的录音设备号。
    返回 'plughw:X,0' 格式的字符串，如果找不到则返回 None。
    """
    try:
        output = subprocess.check_output(['arecord', '-l'], stderr=subprocess.STDOUT).decode('utf-8')
        for line in output.splitlines():
            # 查找包含 'usb' 和 'audio' 的行，更通用
            if 'usb' in line.lower() and 'audio' in line.lower():
                match = re.search(r'card (\d+):', line)
                if match:
                    card_number = match.group(1)
                    device_string = f'plughw:{card_number},0'
                    print(f"成功找到USB麦克风: {device_string}")
                    return device_string
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 'arecord' 命令执行失败或未找到。请确保 alsa-utils 已安装。")
        return None
    print("未找到USB麦克风。")
    return None

def find_i2s_dac_device():
    """
    自动查找I2S DAC的播放设备号。
    驱动名可能包含 'hifiberry', 'dac', 'adafruit', 'amp', 'rpi-dac' 等。
    返回 'hw:X,0' 格式的字符串，如果找不到则返回 None。
    """
    try:
        output = subprocess.check_output(['aplay', '-l'], stderr=subprocess.STDOUT).decode('utf-8')
        # 扩展关键词列表以包含新的驱动名
        keywords = ['hifiberry', 'dac', 'adafruit', 'amp', 'rpi-dac', 'rpidac']
        for line in output.splitlines():
            # 查找包含关键词的声卡
            if any(keyword in line.lower() for keyword in keywords):
                match = re.search(r'card (\d+):', line)
                if match:
                    card_number = match.group(1)
                    device_string = f'hw:{card_number},0'
                    print(f"成功找到I2S DAC设备: {device_string}")
                    return device_string
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 'aplay' 命令执行失败或未找到。请确保 alsa-utils 已安装。")
        return None
    print("未找到I2S DAC设备。")
    return None

if __name__ == "__main__":
    print("--- 正在测试设备查找功能 ---")
    
    # 测试录音设备
    mic_device = find_usb_mic_device()
    if mic_device:
        print(f"录音设备名: {mic_device}")
    else:
        print("查找录音设备失败。")
        
    print("\n" + "-"*20 + "\n")

    # 测试播放设备
    dac_device = find_i2s_dac_device()
    if dac_device:
        print(f"I2S播放设备名: {dac_device}")
    else:
        print("查找I2S播放设备失败。") 