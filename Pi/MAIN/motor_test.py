import stepper_motor_control as motor
from time import sleep

def homing_procedure():
    """
    手动触底（归位）流程。
    """
    print("--- 步骤 1: 手动归位 ---")
    print("电机将持续下降。当到达最底部时，请按 Ctrl+C 停止。")
    sleep(2)
    
    try:
        # 持续发送向下移动一小步的指令，直到被中断
        while True:
            motor.move_motor(steps=-1, delay=0.002) # 每次移动-1步，提供更平滑的连续运动
    except KeyboardInterrupt:
        motor.stop_motor()
        print("\n归位完成！当前位置已设为底部。\n")

def test_raising():
    """
    测试从底部上升到顶部。
    """
    print(f"--- 步骤 2: 上升测试 ---")
    print(f"将从底部向上移动 {motor.TOTAL_TRAVEL_STEPS} 步。")
    input("按 Enter 键开始上升...")
    
    motor.move_motor(motor.TOTAL_TRAVEL_STEPS)
    
    print("已到达顶部。\n")

def test_lowering():
    """
    测试从顶部下降到底部。
    """
    print(f"--- 步骤 3: 下降测试 ---")
    print(f"将从顶部向下移动 {motor.TOTAL_TRAVEL_STEPS} 步。")
    input("按 Enter 键开始下降...")
    
    # 使用负数来向下移动
    motor.move_motor(-motor.TOTAL_TRAVEL_STEPS)
    
    print("已回到部。")

if __name__ == '__main__':
    try:
        # 执行完整的测试流程
        #homing_procedure()
        test_raising()
        test_lowering()
        print("\n--- 所有测试完成 ---")
        
    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        motor.stop_motor()
        print("程序退出，电机已停止。") 