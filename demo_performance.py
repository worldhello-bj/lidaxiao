#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化演示脚本
Performance improvement demonstration script

用法 (Usage):
  python3 demo_performance.py           # 标准模式演示
  python3 demo_performance.py --fast    # 快速模式演示
"""

import asyncio
import time
import argparse
from config import BROWSER_CONFIG


def simulate_page_operations():
    """模拟页面操作以展示性能差异"""
    from crawler import get_timing_config
    
    timing = get_timing_config()
    mode_name = "快速模式" if BROWSER_CONFIG.get("fast_mode", False) else "标准模式"
    
    print(f"🎯 {mode_name}性能演示")
    print("=" * 40)
    print(f"当前配置:")
    print(f"  • 页面加载等待: {timing['page_load_wait']}ms")
    print(f"  • 分页点击等待: {timing['pagination_wait']}ms")
    print(f"  • 操作后等待: {timing['post_action_wait']}ms")
    print(f"  • 页面间隔: {timing['page_interval_min']}-{timing['page_interval_max']}s")
    print(f"  • 网络超时: {timing['network_timeout']}ms")
    print()
    
    return timing


async def simulate_video_crawling(timing):
    """模拟视频爬取流程"""
    total_start = time.time()
    
    print("📋 模拟视频爬取流程:")
    
    # 1. 页面加载
    print("  1. 页面加载中...", end=" ", flush=True)
    start = time.time()
    await asyncio.sleep(timing["page_load_wait"] / 1000)
    duration = time.time() - start
    print(f"耗时 {duration:.2f}s")
    
    # 2. 获取视频列表
    print("  2. 获取视频列表...", end=" ", flush=True)
    start = time.time()
    await asyncio.sleep(timing["post_action_wait"] / 1000)
    duration = time.time() - start
    print(f"耗时 {duration:.2f}s")
    
    # 3. 分页操作 (模拟3页)
    page_count = 3
    for page in range(2, page_count + 1):
        print(f"  3.{page-1} 点击第{page}页...", end=" ", flush=True)
        start = time.time()
        
        # 分页点击等待
        await asyncio.sleep(timing["pagination_wait"] / 1000)
        # 页面加载等待
        await asyncio.sleep(timing["post_action_wait"] / 1000)
        # 页面间隔
        interval = (timing["page_interval_min"] + timing["page_interval_max"]) / 2
        await asyncio.sleep(interval)
        
        duration = time.time() - start
        print(f"耗时 {duration:.2f}s")
    
    total_duration = time.time() - total_start
    print(f"\n📊 总耗时: {total_duration:.2f}s")
    
    return total_duration


def compare_modes():
    """比较标准模式和快速模式的性能"""
    print("⚡ 性能对比分析")
    print("=" * 40)
    
    # 标准模式时间
    standard_times = {
        "page_load_wait": 2000,
        "pagination_wait": 1000,
        "post_action_wait": 2000,
        "page_interval_avg": 4500,  # (3000 + 6000) / 2
    }
    
    # 快速模式时间
    fast_times = {
        "page_load_wait": 500,
        "pagination_wait": 300,
        "post_action_wait": 800,
        "page_interval_avg": 1500,  # (1000 + 2000) / 2
    }
    
    # 计算单页操作时间 (点击分页 + 页面加载 + 页面间隔)
    standard_per_page = (standard_times["pagination_wait"] + 
                        standard_times["post_action_wait"] + 
                        standard_times["page_interval_avg"]) / 1000
    
    fast_per_page = (fast_times["pagination_wait"] + 
                    fast_times["post_action_wait"] + 
                    fast_times["page_interval_avg"]) / 1000
    
    # 计算3页总时间 (初始页面加载 + 2次翻页)
    standard_total = (standard_times["page_load_wait"] + 
                     standard_times["post_action_wait"]) / 1000 + 2 * standard_per_page
    
    fast_total = (fast_times["page_load_wait"] + 
                 fast_times["post_action_wait"]) / 1000 + 2 * fast_per_page
    
    improvement = (standard_total - fast_total) / standard_total * 100
    
    print(f"标准模式预计时间: {standard_total:.1f}s")
    print(f"快速模式预计时间: {fast_total:.1f}s")
    print(f"性能提升: {improvement:.1f}%")
    print(f"时间节省: {standard_total - fast_total:.1f}s")
    print()


async def main():
    """主演示函数"""
    parser = argparse.ArgumentParser(description='性能优化演示')
    parser.add_argument('--fast', action='store_true', help='启用快速模式')
    args = parser.parse_args()
    
    print("🚀 李大霄指数程序性能优化演示")
    print("=" * 50)
    
    if args.fast:
        from crawler import enable_fast_mode
        enable_fast_mode()
        print("✅ 已启用快速模式")
    else:
        print("📋 使用标准模式")
    
    print()
    
    # 显示对比分析
    compare_modes()
    
    # 模拟操作
    timing = simulate_page_operations()
    actual_duration = await simulate_video_crawling(timing)
    
    print("\n💡 使用建议:")
    if args.fast:
        print("  • 快速模式适合日常使用和界面操作")
        print("  • 显著提高响应速度和用户体验")
        print("  • 命令行使用: python3 lidaxiao.py --fast")
    else:
        print("  • 标准模式提供最强的反检测能力")
        print("  • 适合需要稳定性的批量操作")
        print("  • 可通过 --fast 参数启用快速模式")
    
    print("\n🎯 快速启用方法:")
    print("  python3 lidaxiao.py --fast        # 命令行启用")
    print("  crawler.enable_fast_mode()        # 代码中启用")


if __name__ == "__main__":
    asyncio.run(main())