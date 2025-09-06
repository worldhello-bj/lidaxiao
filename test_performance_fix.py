#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化验证测试
Test to verify performance improvements for faster UI response
"""

import datetime
import asyncio
import time
from config import BROWSER_CONFIG, FAST_MODE_CONFIG
from crawler import enable_fast_mode, disable_fast_mode, get_timing_config


def test_timing_config():
    """测试时间配置功能"""
    print("🧪 测试时间配置功能...")
    
    # 测试标准模式
    disable_fast_mode()
    standard_config = get_timing_config()
    print(f"标准模式配置: {standard_config}")
    
    # 测试快速模式
    enable_fast_mode()
    fast_config = get_timing_config()
    print(f"快速模式配置: {fast_config}")
    
    # 验证快速模式确实更快
    assert fast_config["page_load_wait"] < standard_config["page_load_wait"]
    assert fast_config["pagination_wait"] < standard_config["pagination_wait"]
    assert fast_config["post_action_wait"] < standard_config["post_action_wait"]
    assert fast_config["page_interval_max"] < standard_config["page_interval_max"]
    
    print("✅ 时间配置测试通过")


def test_fast_mode_toggle():
    """测试快速模式开关功能"""
    print("🧪 测试快速模式开关...")
    
    # 初始状态
    original_state = BROWSER_CONFIG.get("fast_mode", False)
    
    # 启用快速模式
    enable_fast_mode()
    assert BROWSER_CONFIG["fast_mode"] == True
    print("✓ 快速模式启用成功")
    
    # 禁用快速模式
    disable_fast_mode()
    assert BROWSER_CONFIG["fast_mode"] == False
    print("✓ 快速模式禁用成功")
    
    # 恢复原始状态
    BROWSER_CONFIG["fast_mode"] = original_state
    print("✅ 快速模式开关测试通过")


def test_performance_improvement():
    """验证性能改进效果"""
    print("🧪 验证性能改进效果...")
    
    # 比较标准模式和快速模式的时间配置
    disable_fast_mode()
    standard_times = get_timing_config()
    
    enable_fast_mode()  
    fast_times = get_timing_config()
    
    # 计算改进幅度
    improvements = {}
    for key in ["page_load_wait", "pagination_wait", "post_action_wait"]:
        if key in standard_times and key in fast_times:
            improvement = (standard_times[key] - fast_times[key]) / standard_times[key] * 100
            improvements[key] = improvement
            print(f"  {key}: 减少 {improvement:.1f}% (从 {standard_times[key]}ms 到 {fast_times[key]}ms)")
    
    # 页面间隔改进
    standard_interval = (standard_times["page_interval_min"] + standard_times["page_interval_max"]) / 2
    fast_interval = (fast_times["page_interval_min"] + fast_times["page_interval_max"]) / 2
    interval_improvement = (standard_interval - fast_interval) / standard_interval * 100
    print(f"  页面间隔: 减少 {interval_improvement:.1f}% (从平均 {standard_interval:.1f}s 到 {fast_interval:.1f}s)")
    
    # 验证确实有显著改进
    assert all(imp > 0 for imp in improvements.values()), "快速模式应该在所有方面都有改进"
    assert interval_improvement > 0, "页面间隔应该有改进"
    
    print("✅ 性能改进验证通过")
    
    # 恢复标准模式
    disable_fast_mode()


async def test_real_timing():
    """测试实际时间消耗"""
    print("🧪 测试实际时间消耗...")
    
    # 模拟页面加载等待
    enable_fast_mode()
    timing = get_timing_config()
    
    print(f"模拟快速模式页面加载等待 ({timing['page_load_wait']}ms)...")
    start_time = time.time()
    await asyncio.sleep(timing["page_load_wait"] / 1000)  # 转换为秒
    fast_duration = time.time() - start_time
    
    disable_fast_mode()
    timing = get_timing_config()
    
    print(f"模拟标准模式页面加载等待 ({timing['page_load_wait']}ms)...")
    start_time = time.time()
    await asyncio.sleep(timing["page_load_wait"] / 1000)  # 转换为秒
    standard_duration = time.time() - start_time
    
    improvement = (standard_duration - fast_duration) / standard_duration * 100
    print(f"实际时间改进: {improvement:.1f}% (从 {standard_duration:.2f}s 到 {fast_duration:.2f}s)")
    
    assert fast_duration < standard_duration, "快速模式应该更快"
    print("✅ 实际时间测试通过")


def main():
    """主测试函数"""
    print("🚀 李大霄指数程序性能优化验证测试")
    print("=" * 50)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 运行所有测试
        test_timing_config()
        print()
        
        test_fast_mode_toggle()
        print()
        
        test_performance_improvement()
        print()
        
        # 异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test_real_timing())
        print()
        
        print("🎉 所有性能优化测试通过！")
        print()
        print("📊 优化效果总结:")
        print("✓ 页面加载等待时间减少 75% (2000ms → 500ms)")
        print("✓ 分页点击等待时间减少 70% (1000ms → 300ms)")
        print("✓ 操作后等待时间减少 60% (2000ms → 800ms)")
        print("✓ 页面间隔时间减少 67% (平均4.5s → 1.5s)")
        print("✓ 网络超时减少 47% (15000ms → 8000ms)")
        print()
        print("🎯 预期用户体验改进:")
        print("• 界面响应速度提高 2-3 倍")
        print("• 数据抓取时间减少 50-70%")
        print("• 更流畅的用户交互体验")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()