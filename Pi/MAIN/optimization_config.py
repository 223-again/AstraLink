"""
优化配置文件
用于管理性能监控和优化策略
"""

# API调用优化配置
API_OPTIMIZATION = {
    "timeout": {
        "default": 15,  # 默认请求超时时间
        "short": 10,    # 短请求超时时间
        "long": 30      # 长请求超时时间
    },
    "retry": {
        "max_attempts": 2,     # 最大重试次数
        "retry_delay": 1,      # 重试延迟（秒）
    }
}

# 缓存配置
CACHE_CONFIG = {
    "enable_cache": True,      # 是否启用缓存
    "cache_ttl": 300,          # 缓存生存时间（秒）
    "max_cache_size": 100      # 最大缓存条目数
}

# 性能监控配置
PERFORMANCE_MONITORING = {
    "enable_timing": True,     # 是否启用时间统计
    "log_slow_operations": True,  # 是否记录慢操作
    "slow_operation_threshold": 5.0  # 慢操作阈值（秒）
}

def get_api_timeout(timeout_type="default"):
    """
    获取API超时时间
    """
    return API_OPTIMIZATION["timeout"].get(timeout_type, 15)

# 性能统计类
class PerformanceMonitor:
    def __init__(self):
        self.timings = {}
        self.slow_operations = []
    
    def start_timing(self, operation_name):
        """开始计时"""
        if PERFORMANCE_MONITORING["enable_timing"]:
            import time
            self.timings[operation_name] = {"start": time.time()}
    
    def end_timing(self, operation_name):
        """结束计时"""
        if PERFORMANCE_MONITORING["enable_timing"]:
            import time
            if operation_name in self.timings:
                duration = time.time() - self.timings[operation_name]["start"]
                self.timings[operation_name]["duration"] = duration
                
                # 记录慢操作
                if PERFORMANCE_MONITORING["log_slow_operations"] and \
                   duration > PERFORMANCE_MONITORING["slow_operation_threshold"]:
                    self.slow_operations.append({
                        "operation": operation_name,
                        "duration": duration,
                        "timestamp": time.time()
                    })
                    print(f"⚠️ 慢操作警告: {operation_name} 耗时 {duration:.2f} 秒")
                
                return duration
        return 0
    
    def get_timing_summary(self):
        """获取计时摘要"""
        if not PERFORMANCE_MONITORING["enable_timing"]:
            return "性能监控已禁用"
        
        summary = "性能统计:\n"
        for operation, timing in self.timings.items():
            if "duration" in timing:
                summary += f"  {operation}: {timing['duration']:.2f}秒\n"
        
        if self.slow_operations:
            summary += "\n慢操作记录:\n"
            for op in self.slow_operations[-5:]:  # 只显示最近5个
                summary += f"  {op['operation']}: {op['duration']:.2f}秒\n"
        
        return summary

# 全局性能监控实例
performance_monitor = PerformanceMonitor() 