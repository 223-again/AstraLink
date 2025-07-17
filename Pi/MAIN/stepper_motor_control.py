from gpiozero import OutputDevice
import time
import threading

# --- 电机参数与引脚定义 ---
TOTAL_TRAVEL_STEPS = 1200      # 从底部到顶部的总行程步数（根据实际调整）
DEFAULT_SPEED_DELAY = 0.001    # 默认速度延时，值越小速度越快（已调快）

# BCM 引脚编号
_IN1 = OutputDevice(24)
_IN2 = OutputDevice(23)
_IN3 = OutputDevice(22)
_IN4 = OutputDevice(27)

# "向上"的步进序列
_UP_SEQUENCE = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]

# "向下"的步进序列
_DOWN_SEQUENCE = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 1, 0)]

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

def cleanup():
    """
    清理GPIO连接
    """
    try:
        stop_motor()
        _IN1.close()
        _IN2.close()
        _IN3.close()
        _IN4.close()
        print("✅ GPIO已清理")
    except:
        pass

def move_motor(steps, delay=DEFAULT_SPEED_DELAY):
    """
    移动电机指定的步数。
    :param steps: 移动的步数。正数为向上，负数为向下。
    :param delay: 每一步的延时（秒）。
    """
    print(f"🔧 开始移动电机: {steps}步, 延时: {delay}秒")
    
    # 根据步数的正负决定方向
    if steps > 0: # 向上
        sequence = _UP_SEQUENCE
        direction = "向上"
    else: # 向下
        sequence = _DOWN_SEQUENCE # 使用明确的向下序列
        direction = "向下"

    print(f"📈 移动方向: {direction}")
    print(f"🔧 使用序列: {sequence}")
    
    # 执行移动
    total_steps = abs(steps)
    for i in range(total_steps):
        for step in sequence:
            _set_step(*step)
            time.sleep(delay)
        
        # 每100步打印一次进度
        if (i + 1) % 100 == 0:
            print(f"  进度: {i + 1}/{total_steps} 步")
            
    print(f"✅ 电机移动完成: {total_steps}步")
    stop_motor() # 移动完成后停止电机

def move_to_top_and_bottom(delay=DEFAULT_SPEED_DELAY):
    """
    向上移动到顶部，然后向下移动到底部
    :param delay: 每一步的延时（秒）
    """
    print(f"🚀 开始完整行程测试: 向上到顶({TOTAL_TRAVEL_STEPS}步) -> 向下到底({TOTAL_TRAVEL_STEPS}步)")
    print(f"⏱️ 延时设置: {delay}秒")
    
    try:
        # 向上移动到顶部
        print("📈 第一阶段: 向上移动到顶部...")
        move_motor(TOTAL_TRAVEL_STEPS, delay)
        
        # 等待2秒
        print("⏳ 在顶部等待2秒...")
        time.sleep(2)
        
        # 向下移动到底部
        print("📉 第二阶段: 向下移动到底部...")
        move_motor(-TOTAL_TRAVEL_STEPS, delay)
        
        print("✅ 完整行程测试完成！")
        
    except Exception as e:
        print(f"❌ 完整行程测试失败: {e}")
        stop_motor()

def send_pulse_sequence(sequence, pulse_count, pulse_delay, direction="向上"):
    """
    发送固定脉冲序列
    :param sequence: 脉冲序列，如 _UP_SEQUENCE 或 _DOWN_SEQUENCE
    :param pulse_count: 发送的脉冲数量
    :param pulse_delay: 每个脉冲的延时（秒）
    :param direction: 移动方向描述
    """
    print(f"⚡ 发送脉冲: {pulse_count}个, 延时: {pulse_delay}s, 方向: {direction}")
    
    try:
        for i in range(pulse_count):
            for step in sequence:
                _set_step(*step)
                time.sleep(pulse_delay)
            
            # 每100个脉冲打印一次进度
            if (i + 1) % 100 == 0:
                print(f"  进度: {i + 1}/{pulse_count} 脉冲")
        
        stop_motor()
        print(f"✅ 脉冲序列发送完成: {pulse_count}个脉冲")
        
    except Exception as e:
        print(f"❌ 脉冲序列发送失败: {e}")
        stop_motor()

def send_single_pulse(direction="向上", pulse_delay=0.002):
    """
    发送单个脉冲
    :param direction: "向上" 或 "向下"
    :param pulse_delay: 脉冲延时（秒）
    """
    if direction == "向上":
        sequence = _UP_SEQUENCE
    else:
        sequence = _DOWN_SEQUENCE
    
    print(f"⚡ 发送单个脉冲: 方向={direction}, 延时={pulse_delay}秒")
    
    try:
        for step in sequence:
            _set_step(*step)
            time.sleep(pulse_delay)
        
        stop_motor()
        print("✅ 单个脉冲发送完成")
        
    except Exception as e:
        print(f"❌ 单个脉冲发送失败: {e}")
        stop_motor()

# --- 最终方案函数 ---
def move_up():
    """
    向上移动 - 最终方案：4000个脉冲，0.001秒延时
    """
    print("📈 开始向上移动 (4000脉冲, 0.001秒延时)")
    send_pulse_sequence(_UP_SEQUENCE, 4000, 0.001, "向上")

def move_down():
    """
    向下移动 - 最终方案：4000个脉冲，0.001秒延时
    """
    print("📉 开始向下移动 (4000脉冲, 0.001秒延时)")
    send_pulse_sequence(_DOWN_SEQUENCE, 4000, 0.001, "向下")

def business_cycle():
    """
    业务循环：向上到顶 -> 等待3秒 -> 向下到底
    在独立线程中运行
    """
    print("🚀 开始业务循环：向上到顶 -> 等待3秒 -> 向下到底")
    
    try:
        # 第一阶段：向上移动到顶部
        print("📈 第一阶段：向上移动到顶部...")
        send_pulse_sequence(_UP_SEQUENCE, 4000, 0.001, "向上")
        
        # 第二阶段：在顶部等待3秒
        print("⏳ 第二阶段：在顶部等待3秒...")
        time.sleep(3)
        
        # 第三阶段：向下移动到底部
        print("📉 第三阶段：向下移动到底部...")
        send_pulse_sequence(_DOWN_SEQUENCE, 4000, 0.001, "向下")
        
        print("✅ 业务循环完成！")
        
    except Exception as e:
        print(f"❌ 业务循环执行失败: {e}")
        stop_motor()

def start_business_cycle_thread():
    """
    启动业务循环线程
    """
    print("🔄 启动业务循环线程...")
    business_thread = threading.Thread(target=business_cycle, daemon=True)
    business_thread.start()
    print("✅ 业务循环线程已启动")
    return business_thread

def test_business_cycle():
    """
    测试业务循环功能
    """
    print("🧪 开始测试业务循环功能...")
    print("📋 测试流程：向上到顶 -> 等待3秒 -> 向下到底")
    
    try:
        # 确保电机停止
        stop_motor()
        time.sleep(1)
        
        # 启动业务循环线程
        print("🔄 启动业务循环线程...")
        business_thread = start_business_cycle_thread()
        
        # 等待业务循环完成
        print("⏳ 等待业务循环完成...")
        business_thread.join()
        
        print("✅ 业务循环测试完成！")
        
    except Exception as e:
        print(f"❌ 业务循环测试失败: {e}")
        stop_motor()

if __name__ == "__main__":
    print("步进电机控制 - gpiozero兼容模式")
    print("向上/向下移动：4000个脉冲，0.001秒延时")
    print("按 Ctrl+C 退出")
    
    # 全局变量跟踪业务线程
    business_thread = None
    
    try:
        while True:
            print("\n选择操作:")
            print("1. 向上移动")
            print("2. 向下移动")
            print("3. 停止电机")
            print("4. 启动业务循环 (线程)")
            print("5. 检查业务线程状态")
            print("6. 测试业务循环 (等待完成)")
            
            choice = input("请选择 (1-6): ").strip()
            
            if choice == "1":
                move_up()
            elif choice == "2":
                move_down()
            elif choice == "3":
                stop_motor()
                print("✅ 电机已停止")
            elif choice == "4":
                if business_thread and business_thread.is_alive():
                    print("⚠️ 业务线程正在运行中，请等待完成")
                else:
                    business_thread = start_business_cycle_thread()
            elif choice == "5":
                if business_thread and business_thread.is_alive():
                    print("🔄 业务线程正在运行中")
                else:
                    print("⏹️ 业务线程未运行或已完成")
            elif choice == "6":
                test_business_cycle()
            else:
                print("❌ 无效选择")
                
    except KeyboardInterrupt:
        print("\n👋 程序退出")
        stop_motor()
        cleanup() 