"""
优化配置文件
用于管理任务处理的性能优化策略
"""

# 任务处理策略配置
TASK_PROCESSING_STRATEGIES = {
    "single_task": {
        "threshold": 1,  # 任务数量阈值
        "method": "direct",  # 直接处理
        "description": "单个任务直接处理"
    },
    "parallel_processing": {
        "threshold": 3,  # 任务数量阈值
        "method": "parallel",  # 并行处理
        "description": "少量任务并行处理"
    },
    "batch_processing": {
        "threshold": float('inf'),  # 无上限
        "method": "batch",  # 批量处理
        "description": "多个任务批量处理"
    }
}

# API调用优化配置
API_OPTIMIZATION = {
    "timeout": {
        "single_request": 10,  # 单个请求超时时间
        "batch_request": 15,   # 批量请求超时时间
        "parallel_request": 12  # 并行请求超时时间
    },
    "retry": {
        "max_attempts": 2,     # 最大重试次数
        "retry_delay": 1,      # 重试延迟（秒）
    },
    "concurrent_limit": {
        "max_parallel_tasks": 5,  # 最大并行任务数
        "max_batch_size": 8       # 最大批量处理大小
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

def get_processing_strategy(task_count):
    """
    根据任务数量返回处理策略
    """
    for strategy_name, config in TASK_PROCESSING_STRATEGIES.items():
        if task_count <= config["threshold"]:
            return config["method"], config["description"]
    
    # 默认返回批量处理
    return "batch", "默认批量处理"

def should_use_batch_processing(task_count):
    """
    判断是否应该使用批量处理
    """
    return task_count > TASK_PROCESSING_STRATEGIES["parallel_processing"]["threshold"]

def get_api_timeout(method):
    """
    根据处理方法获取API超时时间
    """
    return API_OPTIMIZATION["timeout"].get(method, 10)

def get_max_parallel_tasks():
    """
    获取最大并行任务数
    """
    return API_OPTIMIZATION["concurrent_limit"]["max_parallel_tasks"]

def get_max_batch_size():
    """
    获取最大批量处理大小
    """
    return API_OPTIMIZATION["concurrent_limit"]["max_batch_size"]

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