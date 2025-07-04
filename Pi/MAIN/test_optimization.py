#!/usr/bin/env python3
"""
优化效果测试脚本
用于测试和比较不同任务处理策略的性能
支持多模型配置测试
"""

import asyncio
import time
import json
from load_config import load_config
from silicon_ai import ask_question, parse_tasks_and_audio, process_tasks_parallel, batch_process_tasks, get_available_models
from optimization_config import performance_monitor, get_processing_strategy

class OptimizationTester:
    def __init__(self):
        self.config = load_config()
        if not self.config or "silicon" not in self.config:
            raise RuntimeError("配置加载失败或缺少silicon配置")
        
        self.api_token = self.config["silicon"]["api_token"]
        self.models = get_available_models()
        
        print("🔧 加载的模型配置:")
        for model_type, model_config in self.models.items():
            print(f"  {model_type}: {model_config.get('name', 'N/A')} - {model_config.get('description', 'N/A')}")
    
    async def test_single_task(self, intent, model_type="task_execution"):
        """测试单个任务处理"""
        print(f"\n🔍 测试单个任务: {intent} (使用模型: {model_type})")
        performance_monitor.start_timing(f"单个任务测试_{model_type}")
        
        result = ask_question(intent, self.api_token, model_type=model_type)
        
        performance_monitor.end_timing(f"单个任务测试_{model_type}")
        return result
    
    async def test_parallel_tasks(self, intents, model_type="task_execution"):
        """测试并行任务处理"""
        print(f"\n🔍 测试并行任务: {intents} (使用模型: {model_type})")
        performance_monitor.start_timing(f"并行任务测试_{model_type}")
        
        tasks = [{"intent": intent} for intent in intents]
        results = await process_tasks_parallel(tasks, self.api_token, self.config)
        
        performance_monitor.end_timing(f"并行任务测试_{model_type}")
        return results
    
    async def test_batch_tasks(self, intents, model_type="batch_processing"):
        """测试批量任务处理"""
        print(f"\n🔍 测试批量任务: {intents} (使用模型: {model_type})")
        performance_monitor.start_timing(f"批量任务测试_{model_type}")
        
        tasks = [{"intent": intent} for intent in intents]
        results = batch_process_tasks(tasks, self.api_token, model_type=model_type)
        
        performance_monitor.end_timing(f"批量任务测试_{model_type}")
        return results
    
    async def test_task_planning(self, user_input, model_type="task_planning"):
        """测试任务编排"""
        print(f"\n🔍 测试任务编排: {user_input} (使用模型: {model_type})")
        performance_monitor.start_timing(f"任务编排测试_{model_type}")
        
        plan = parse_tasks_and_audio(user_input, self.api_token, model_type=model_type)
        
        performance_monitor.end_timing(f"任务编排测试_{model_type}")
        return plan
    
    def print_results(self, results, title):
        """打印结果"""
        print(f"\n📊 {title}:")
        if isinstance(results, list):
            for i, result in enumerate(results):
                print(f"  任务 {i+1}: {result}")
        else:
            print(f"  结果: {results}")
    
    async def test_model_comparison(self):
        """测试不同模型的性能对比"""
        print("\n🔬 模型性能对比测试")
        print("="*50)
        
        test_input = "调高音量并随机播放一首歌，再推荐一部动作片"
        
        # 测试任务编排模型
        print("\n📋 任务编排模型测试:")
        plan = await self.test_task_planning(test_input, "task_planning")
        self.print_results(plan, "任务编排结果")
        
        if plan and 'tasks' in plan:
            tasks = plan['tasks']
            print(f"\n分解出 {len(tasks)} 个子任务:")
            for i, task in enumerate(tasks):
                print(f"  {i+1}. {task.get('intent', '')}")
            
            # 测试子任务执行模型
            print("\n🔧 子任务执行模型测试:")
            for i, task in enumerate(tasks):
                intent = task.get('intent', '')
                result = await self.test_single_task(intent, "task_execution")
                self.print_results(result, f"子任务 {i+1} 执行结果")
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始优化效果综合测试")
        print("="*60)
        
        # 测试用例
        test_cases = [
            {
                "name": "单个简单任务",
                "input": "调高音量",
                "type": "single"
            },
            {
                "name": "多个相关任务",
                "input": "调高音量并随机播放一首歌",
                "type": "planning"
            },
            {
                "name": "复杂多任务",
                "input": "调高音量并随机播放一首歌，再推荐一部动作片，还要一个酷酷的表情",
                "type": "planning"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🎯 测试用例: {test_case['name']}")
            print(f"输入: {test_case['input']}")
            
            if test_case['type'] == 'single':
                result = await self.test_single_task(test_case['input'], "task_execution")
                self.print_results(result, "单个任务结果")
            
            elif test_case['type'] == 'planning':
                plan = await self.test_task_planning(test_case['input'], "task_planning")
                self.print_results(plan, "任务编排结果")
                
                if plan and 'tasks' in plan:
                    tasks = plan['tasks']
                    print(f"\n📋 分解出 {len(tasks)} 个子任务:")
                    for i, task in enumerate(tasks):
                        print(f"  {i+1}. {task.get('intent', '')}")
                    
                    # 测试不同处理策略
                    if len(tasks) == 1:
                        print("\n🔄 使用直接处理策略...")
                        result = await self.test_single_task(tasks[0].get('intent', ''), "task_execution")
                        self.print_results(result, "直接处理结果")
                    
                    elif len(tasks) <= 3:
                        print("\n🔄 使用并行处理策略...")
                        intents = [task.get('intent', '') for task in tasks]
                        results = await self.test_parallel_tasks(intents, "task_execution")
                        self.print_results(results, "并行处理结果")
                    
                    else:
                        print("\n🔄 使用批量处理策略...")
                        intents = [task.get('intent', '') for task in tasks]
                        results = await self.test_batch_tasks(intents, "batch_processing")
                        self.print_results(results, "批量处理结果")
        
        # 打印性能统计
        print("\n" + "="*60)
        print("📈 性能统计报告")
        print("="*60)
        print(performance_monitor.get_timing_summary())
        
        # 性能分析
        timings = performance_monitor.timings
        if timings:
            print("\n📊 性能分析:")
            total_time = 0
            for operation, timing in timings.items():
                if 'duration' in timing:
                    total_time += timing['duration']
                    print(f"  {operation}: {timing['duration']:.2f}秒")
            
            print(f"\n⏱️ 总耗时: {total_time:.2f}秒")
            
            # 找出最耗时的操作
            slowest_operation = max(
                [(op, timing['duration']) for op, timing in timings.items() if 'duration' in timing],
                key=lambda x: x[1]
            )
            print(f"🐌 最耗时操作: {slowest_operation[0]} ({slowest_operation[1]:.2f}秒)")
    
    async def test_scalability(self):
        """测试可扩展性"""
        print("\n🔬 可扩展性测试")
        print("="*40)
        
        # 测试不同任务数量的性能
        task_counts = [1, 2, 3, 5, 8]
        test_intents = [
            "调高音量",
            "播放音乐", 
            "推荐电影",
            "发送表情",
            "调节音量",
            "播放随机歌曲",
            "推荐动作片",
            "发送酷酷表情"
        ]
        
        for count in task_counts:
            print(f"\n📊 测试 {count} 个任务:")
            intents = test_intents[:count]
            
            performance_monitor.start_timing(f"可扩展性测试_{count}任务")
            
            if count == 1:
                await self.test_single_task(intents[0], "task_execution")
            elif count <= 3:
                await self.test_parallel_tasks(intents, "task_execution")
            else:
                await self.test_batch_tasks(intents, "batch_processing")
            
            performance_monitor.end_timing(f"可扩展性测试_{count}任务")
    
    async def test_model_configuration(self):
        """测试模型配置"""
        print("\n⚙️ 模型配置测试")
        print("="*40)
        
        # 测试不同模型类型的配置
        model_types = ["task_planning", "task_execution", "batch_processing"]
        
        for model_type in model_types:
            if model_type in self.models:
                model_config = self.models[model_type]
                print(f"\n📋 {model_type} 模型配置:")
                print(f"  模型名称: {model_config.get('name', 'N/A')}")
                print(f"  描述: {model_config.get('description', 'N/A')}")
                print(f"  温度: {model_config.get('temperature', 'N/A')}")
                print(f"  最大令牌: {model_config.get('max_tokens', 'N/A')}")
                print(f"  启用思考: {model_config.get('enable_thinking', 'N/A')}")
                
                # 测试该模型的基本功能
                if model_type == "task_planning":
                    print(f"  🧪 测试任务编排功能...")
                    await self.test_task_planning("调高音量", model_type)
                elif model_type == "task_execution":
                    print(f"  🧪 测试任务执行功能...")
                    await self.test_single_task("调高音量", model_type)
                elif model_type == "batch_processing":
                    print(f"  🧪 测试批量处理功能...")
                    await self.test_batch_tasks(["调高音量", "播放音乐"], model_type)

async def main():
    try:
        tester = OptimizationTester()
        
        # 运行模型配置测试
        await tester.test_model_configuration()
        
        # 运行模型性能对比测试
        await tester.test_model_comparison()
        
        # 运行综合测试
        await tester.run_comprehensive_test()
        
        # 运行可扩展性测试
        await tester.test_scalability()
        
        print("\n✅ 优化效果测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 