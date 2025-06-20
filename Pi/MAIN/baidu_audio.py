import json
import time
import binascii
import tty
import requests
import asyncio
import uuid
import subprocess
import wave
import numpy as np

# 配置音频采样率与设备ID
audiorate = 16000
# 树莓派下用uuid生成唯一ID
try:
    dev_cuid = uuid.getnode()
    dev_cuid = hex(dev_cuid)[2:]
except Exception:
    dev_cuid = "raspberrypi"

global_token = None
token_expiration_time = 0

def fetch_token(API_Key, Secret_Key):
    start_time = time.time()
    url = f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers)
    print(f"获取 token 耗时: {time.time() - start_time:.2f} 秒")
    response_data = response.json()
    access_token = response_data.get("access_token")
    expires_in = response_data.get("expires_in", 0)
    expiration_time = time.time() + expires_in
    return access_token, expiration_time

def get_token(API_Key, Secret_Key):
    global global_token, token_expiration_time
    if not global_token or time.time() >= token_expiration_time:
        print("Token 不存在或已过期，正在重新获取...")
        global_token, token_expiration_time = fetch_token(API_Key, Secret_Key)
    return global_token

def recongize(apikey, sercretkey, audiofile, dev_pid=80001, chunk_size=4096):
    token = get_token(apikey, sercretkey)
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={token}'
    headers = {
        'Content-Type': 'audio/pcm;rate=16000',
    }
    start_time = time.time()
    response = None
    try:
        with open(audiofile, 'rb') as f:
            response = requests.post(url, data=f, headers=headers)
        print(f"上传音频耗时: {time.time() - start_time:.2f} 秒")
        response_text = response.text
        print(f"原始响应文本: {response_text}")
        results = json.loads(response_text)
        print(f"返回数据: {results}")
        if not results:
            raise ValueError("返回数据为空")
        if results.get("err_no") == 0:
            if "result" in results and results["result"]:
                result_text = "".join(results["result"])
                return result_text
            else:
                raise ValueError("返回数据中没有识别结果")
        else:
            error_msg = results.get("err_msg", "未知错误")
            error_no = results.get("err_no", "未知错误码")
            raise ValueError(f"识别错误: {error_msg}, 错误码: {error_no}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应文本: {response_text}")
        raise ValueError(f"JSON解析错误: {e}")
    except ValueError as e:
        print(f"处理错误: {e}")
        raise
    except Exception as e:
        print(f"请求异常: {str(e)}")
        raise
    finally:
        if response:
            response.close()

async def speech_tts(apikey, sercretkey, text_tts, play_on_i2s=True, aue=6, audio_ctrl='{"sampling_rate":16000}'):
    token = get_token(apikey, sercretkey)
    text = binascii.hexlify(text_tts.encode('utf-8')).decode("utf-8")
    text_urlencode = ''
    for i in range(0, len(text)):
        if i % 2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    tts_url = (
        f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={token}'
        f'&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111'
        f'&aue={aue}&audio_ctrl={audio_ctrl}'
    )
    try:
        response = requests.get(tts_url, stream=True)
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("audio"):
            print("TTS合成失败，返回内容：")
            print(response.text)
            return
        # 根据aue决定后缀
        ext = ".wav" if aue == 6 else ".mp3" if aue == 3 else ".pcm"
        filename = f"tts_output{ext}"
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"TTS音频已保存为 {filename}")
        if play_on_i2s and aue == 6:
            play_wav_on_i2s(filename)
        elif play_on_i2s and aue == 4:
            print("如需播放pcm请先转换为wav")
    except Exception as e:
        print(f"TTS处理异常: {str(e)}")
        raise
    finally:
        if response:
            response.close()

def play_wav_on_i2s(filename):
    # 检查声道数，如果是单声道，自动转为双声道
    with wave.open(filename, 'rb') as wf:
        channels = wf.getnchannels()
        if channels == 1:
            # 读取音频数据
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            # 复制为双声道
            stereo = np.column_stack((audio, audio)).flatten().astype(np.int16)
            # 保存为临时双声道文件
            outname = filename.replace('.wav', '_2ch.wav')
            with wave.open(outname, 'wb') as outwf:
                outwf.setnchannels(2)
                outwf.setsampwidth(wf.getsampwidth())
                outwf.setframerate(wf.getframerate())
                outwf.writeframes(stereo.tobytes())
            filename = outname
    cmd = [
        "aplay",
        "-D", "hw:0,0",
        "-f", "S16_LE",
        "-r", "16000",
        "-c", "2",
        filename
    ]
    print(f"[I2S] 正在播放: {filename}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    play_wav_on_i2s("tts_output.wav")
    #apikey = "your_api_key"
    #sercretkey = "your_secret_key"
    #try:
    #    recognized_text = recongize(apikey, sercretkey, "recording.wav")
    #    print(f"识别结果: {recognized_text}")
    #except ValueError as e:
    #    print(f"语音识别错误: {e}")
    #try:
    #    asyncio.run(speech_tts(apikey, sercretkey, "你好，世界！"))
    #except Exception as e:
    #    print(f"语音合成错误: {e}") 