from gpiozero import OutputDevice
from time import sleep

# --- 电机参数与引脚定义 ---
TOTAL_TRAVEL_STEPS = 6000      # 从底部到顶部的总行程步数（已根据用户实际调整）
DEFAULT_SPEED_DELAY = 0.001    # 默认速度延时，值越小速度越快

# BCM 引脚编号
_IN1 = OutputDevice(24)
_IN2 = OutputDevice(23)
_IN3 = OutputDevice(22)
_IN4 = OutputDevice(27)

# "向上"的步进序列
_UP_SEQUENCE = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]

# --- 底层控制函数 ---
def _set_step(w1, w2, w3, w4):
    (_IN1.on if w1 else _IN1.off)()
    (_IN2.on if w2 else _IN2.off)()
    (_IN3.on if w3 else _IN3.off)()
    (_IN4.on if w4 else _IN4.off)()

# --- 公共控制函数 ---
def stop_motor():
    """
    立刻停止电机并断电。
    """
    _set_step(0, 0, 0, 0)

def move_motor(steps, delay=DEFAULT_SPEED_DELAY):
    """
    移动电机指定的步数。
    :param steps: 移动的步数。正数为向上，负数为向下。
    :param delay: 每一步的延时（秒）。
    """
    # 根据步数的正负决定方向
    if steps > 0: # 向上
        sequence = _UP_SEQUENCE
    else: # 向下
        sequence = _UP_SEQUENCE[::-1] # 反转序列即为反向

    # 执行移动
    for _ in range(abs(steps)):
        for step in sequence:
            _set_step(*step)
            sleep(delay)
            
    stop_motor() # 移动完成后停止电机 