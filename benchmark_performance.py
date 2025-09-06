#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试 - 模拟实际爬取时间
Performance Benchmark - Simulate Actual Crawling Time

模拟不同配置下的实际爬取时间对比
"""

import time
import asyncio
from config import apply_performance_mode, TIMING_CONFIG

async def simulate_page_crawl():
    """模拟单页爬取过程，包含所有等待时间"""
    
    # 模拟页面加载等待
    await asyncio.sleep(TIMING_CONFIG["page_load_wait"] / 1000)
    
    # 模拟分页等待
    await asyncio.sleep(TIMING_CONFIG["pagination_wait"] / 1000)
    
    # 模拟操作后等待
    await asyncio.sleep(TIMING_CONFIG["post_action_wait"] / 1000)
    
    # 模拟页面间隔（使用平均值）
    avg_interval = (TIMING_CONFIG["page_interval_min"] + TIMING_CONFIG["page_interval_max"]) / 2
    await asyncio.sleep(avg_interval)

async def benchmark_mode(mode_name, pages=5):
    """基准测试特定模式"""
    print(f"🧪 测试 {mode_name} 模式 ({pages} 页)...")
    
    apply_performance_mode(mode_name)
    
    start_time = time.time()
    
    for page in range(1, pages + 1):
        print(f"  • 处理第 {page} 页...", end="", flush=True)
        await simulate_page_crawl()
        print(" ✅")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    per_page = elapsed / pages
    
    print(f"  📊 总时间: {elapsed:.2f}秒")
    print(f"  📊 每页: {per_page:.2f}秒")
    print(f"  📊 预估30页: {per_page * 30:.1f}秒 ({per_page * 30 / 60:.1f}分钟)")
    print()
    
    return elapsed, per_page

async def run_benchmark():
    """运行完整基准测试"""
    print("⚡ 李大霄指数爬虫性能基准测试")
    print("=" * 50)
    print("模拟真实爬取场景，测试不同性能模式的实际时间差异")
    print()
    
    test_pages = 3  # 使用较少页数快速演示
    
    # 测试所有模式
    results = {}
    
    for mode in ["stable", "balanced", "fast"]:
        elapsed, per_page = await benchmark_mode(mode, test_pages)
        results[mode] = {"total": elapsed, "per_page": per_page}
    
    # 计算性能对比
    print("📈 性能对比分析:")
    print("-" * 30)
    
    stable_time = results["stable"]["per_page"]
    balanced_time = results["balanced"]["per_page"]
    fast_time = results["fast"]["per_page"]
    
    print(f"每页处理时间:")
    print(f"  stable:   {stable_time:.2f}秒")
    print(f"  balanced: {balanced_time:.2f}秒 ({stable_time/balanced_time:.1f}x faster)")
    print(f"  fast:     {fast_time:.2f}秒 ({stable_time/fast_time:.1f}x faster)")
    print()
    
    print(f"30页总时间预估:")
    print(f"  stable:   {stable_time * 30:.1f}秒 ({stable_time * 30 / 60:.1f}分钟)")
    print(f"  balanced: {balanced_time * 30:.1f}秒 ({balanced_time * 30 / 60:.1f}分钟)")
    print(f"  fast:     {fast_time * 30:.1f}秒 ({fast_time * 30 / 60:.1f}分钟)")
    print()
    
    time_saved_balanced = (stable_time - balanced_time) * 30
    time_saved_fast = (stable_time - fast_time) * 30
    
    print(f"节省时间 (相比stable模式):")
    print(f"  balanced: {time_saved_balanced:.1f}秒 ({time_saved_balanced/60:.1f}分钟)")
    print(f"  fast:     {time_saved_fast:.1f}秒 ({time_saved_fast/60:.1f}分钟)")
    print()
    
    print("🎯 推荐使用:")
    print("• 日常使用：balanced 模式 (平衡性能和稳定性)")
    print("• 大量爬取：fast 模式 (最大化速度)")
    print("• 调试问题：stable 模式 (最高稳定性)")
    print()
    
    # 显示优化前后对比
    print("📊 优化效果 (相比原始未优化版本):")
    original_time = 3.1  # 原始版本每页时间
    improvement_balanced = (original_time - balanced_time) / original_time * 100
    improvement_fast = (original_time - fast_time) / original_time * 100
    
    print(f"  balanced模式: 提升 {improvement_balanced:.1f}% (原始{original_time:.1f}s → {balanced_time:.2f}s)")
    print(f"  fast模式:     提升 {improvement_fast:.1f}% (原始{original_time:.1f}s → {fast_time:.2f}s)")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_benchmark())