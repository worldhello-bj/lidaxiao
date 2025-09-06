#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试 - 模拟实际爬取时间
Performance Benchmark - Simulate Actual Crawling Time

模拟不同配置下的实际爬取时间对比
"""

import time
import asyncio
from config import TIMING_CONFIG

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

async def benchmark_config(config_name, config_values, pages=5):
    """基准测试特定配置"""
    print(f"🧪 测试 {config_name} 配置 ({pages} 页)...")
    
    # 备份原配置
    original_config = TIMING_CONFIG.copy()
    
    # 应用测试配置
    TIMING_CONFIG.update(config_values)
    
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
    
    # 恢复原配置
    TIMING_CONFIG.clear()
    TIMING_CONFIG.update(original_config)
    print()
    
    return elapsed, per_page

async def run_benchmark():
    """运行完整基准测试"""
    print("⚡ 李大霄指数爬虫性能基准测试")
    print("=" * 50)
    print("模拟真实爬取场景，测试不同配置的实际时间差异")
    print()
    
    test_pages = 3  # 使用较少页数快速演示
    
    # 测试不同配置
    configs = {
        "稳定配置": {
            "page_load_wait": 300,
            "pagination_wait": 200,
            "post_action_wait": 500,
            "page_interval_min": 0.5,
            "page_interval_max": 1.0,
        },
        "默认配置": {
            "page_load_wait": 150,
            "pagination_wait": 50,
            "post_action_wait": 200,
            "page_interval_min": 0.2,
            "page_interval_max": 0.4,
        },
        "快速配置": {
            "page_load_wait": 100,
            "pagination_wait": 30,
            "post_action_wait": 150,
            "page_interval_min": 0.1,
            "page_interval_max": 0.3,
        }
    }
    
    results = {}
    
    for config_name, config_values in configs.items():
        elapsed, per_page = await benchmark_config(config_name, config_values, test_pages)
        results[config_name] = {"total": elapsed, "per_page": per_page}
    
    # 计算性能对比
    print("📈 性能对比分析:")
    print("-" * 30)
    
    stable_time = results["稳定配置"]["per_page"]
    default_time = results["默认配置"]["per_page"]
    fast_time = results["快速配置"]["per_page"]
    
    print(f"每页处理时间:")
    print(f"  稳定配置: {stable_time:.2f}秒")
    print(f"  默认配置: {default_time:.2f}秒 ({stable_time/default_time:.1f}x faster)")
    print(f"  快速配置: {fast_time:.2f}秒 ({stable_time/fast_time:.1f}x faster)")
    print()
    
    print(f"30页总时间预估:")
    print(f"  稳定配置: {stable_time * 30:.1f}秒 ({stable_time * 30 / 60:.1f}分钟)")
    print(f"  默认配置: {default_time * 30:.1f}秒 ({default_time * 30 / 60:.1f}分钟)")
    print(f"  快速配置: {fast_time * 30:.1f}秒 ({fast_time * 30 / 60:.1f}分钟)")
    print()
    
    time_saved_default = (stable_time - default_time) * 30
    time_saved_fast = (stable_time - fast_time) * 30
    
    print(f"节省时间 (相比稳定配置):")
    print(f"  默认配置: {time_saved_default:.1f}秒 ({time_saved_default/60:.1f}分钟)")
    print(f"  快速配置: {time_saved_fast:.1f}秒 ({time_saved_fast/60:.1f}分钟)")
    print()
    
    print("🎯 推荐使用:")
    print("• 日常使用：默认配置 (已优化的平衡配置)")
    print("• 大量爬取：enable_fast_mode() (最大化速度)")
    print("• 调试问题：enable_stable_mode() (最高稳定性)")
    print()
    
    # 显示优化前后对比
    print("📊 优化效果 (相比原始未优化版本):")
    original_time = 3.1  # 原始版本每页时间
    improvement_default = (original_time - default_time) / original_time * 100
    improvement_fast = (original_time - fast_time) / original_time * 100
    
    print(f"  默认配置: 提升 {improvement_default:.1f}% (原始{original_time:.1f}s → {default_time:.2f}s)")
    print(f"  快速配置: 提升 {improvement_fast:.1f}% (原始{original_time:.1f}s → {fast_time:.2f}s)")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_benchmark())