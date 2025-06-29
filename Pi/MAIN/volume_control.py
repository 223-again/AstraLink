import subprocess
import re
import asyncio
from typing import Optional

class VolumeController:
    def __init__(self):
        self.current_volume = 50  # 默认音量50%
        
    async def get_current_volume(self) -> int:
        """获取当前系统音量"""
        try:
            # 使用amixer获取当前音量
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
            )
            
            if result.returncode == 0:
                output = result.stdout
                # 解析音量百分比
                match = re.search(r'\[(\d+)%\]', output)
                if match:
                    self.current_volume = int(match.group(1))
                    return self.current_volume
        except Exception as e:
            print(f"获取音量失败: {e}")
        
        return self.current_volume
    
    async def set_volume(self, volume_percent: int) -> bool:
        """设置系统音量"""
        try:
            # 确保音量在0-100范围内
            volume_percent = max(0, min(100, volume_percent))
            
            # 使用amixer设置音量
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(["amixer", "set", "Master", f"{volume_percent}%"], capture_output=True, text=True)
            )
            
            if result.returncode == 0:
                self.current_volume = volume_percent
                print(f"音量已设置为: {volume_percent}%")
                return True
            else:
                print(f"设置音量失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"设置音量异常: {e}")
            return False
    
    async def increase_volume(self, increment: int = 10) -> bool:
        """增加音量"""
        current = await self.get_current_volume()
        new_volume = min(100, current + increment)
        return await self.set_volume(new_volume)
    
    async def decrease_volume(self, decrement: int = 10) -> bool:
        """降低音量"""
        current = await self.get_current_volume()
        new_volume = max(0, current - decrement)
        return await self.set_volume(new_volume)

# 全局音量控制器实例
volume_controller = VolumeController()

async def handle_volume_command(command: str) -> str:
    """处理音量控制命令"""
    try:
        if command == "volume_up":
            success = await volume_controller.increase_volume(10)
            return "音量已调高" if success else "音量调节失败"
        elif command == "volume_down":
            success = await volume_controller.decrease_volume(10)
            return "音量已调低" if success else "音量调节失败"
        elif command.startswith("volume_set_"):
            # 格式: volume_set_50 (设置音量为50%)
            try:
                volume = int(command.split("_")[-1])
                success = await volume_controller.set_volume(volume)
                return f"音量已设置为{volume}%" if success else "音量设置失败"
            except ValueError:
                return "音量设置格式错误"
        else:
            return "未知的音量控制命令"
    except Exception as e:
        print(f"音量控制异常: {e}")
        return "音量控制出现异常"

if __name__ == "__main__":
    # 测试音量控制功能
    async def test():
        controller = VolumeController()
        
        print("测试音量控制功能...")
        
        # 获取当前音量
        current = await controller.get_current_volume()
        print(f"当前音量: {current}%")
        
        # 测试增加音量
        await controller.increase_volume(5)
        
        # 测试降低音量
        await controller.decrease_volume(5)
        
        # 测试设置特定音量
        await controller.set_volume(60)
        
        print("测试完成")
    
    asyncio.run(test()) 