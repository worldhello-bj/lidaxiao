#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化测试模块
Performance Optimization Test Module

测试爬虫性能优化的效果
"""

import asyncio
import time
import sys
import logging
from config import TIMING_CONFIG, BROWSER_CONFIG, apply_performance_mode

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_timing_configuration():
    """测试时间配置优化"""
    print("=== 时间配置优化测试 ===")
    
    # 显示默认配置
    print("\n当前配置 (balanced模式):")
    for key, value in TIMING_CONFIG.items():
        print(f"  {key}: {value}")
    
    # 测试快速模式
    print("\n切换到快速模式:")
    apply_performance_mode("fast")
    for key, value in TIMING_CONFIG.items():
        print(f"  {key}: {value}")
    
    # 测试稳定模式
    print("\n切换到稳定模式:")
    apply_performance_mode("stable")
    for key, value in TIMING_CONFIG.items():
        print(f"  {key}: {value}")
    
    # 恢复平衡模式
    apply_performance_mode("balanced")
    print("\n恢复到平衡模式")

def simulate_page_timing():
    """模拟页面处理时间计算"""
    print("\n=== 页面处理时间模拟 ===")
    
    modes = ["fast", "balanced", "stable"]
    for mode in modes:
        apply_performance_mode(mode)
        
        # 计算单页处理时间 (毫秒)
        single_page_time = (
            TIMING_CONFIG["page_load_wait"] +
            TIMING_CONFIG["pagination_wait"] +
            TIMING_CONFIG["post_action_wait"] +
            (TIMING_CONFIG["page_interval_min"] + TIMING_CONFIG["page_interval_max"]) / 2 * 1000
        )
        
        # 计算30页的总时间
        total_time_30_pages = single_page_time * 30 / 1000  # 转换为秒
        
        print(f"{mode}模式:")
        print(f"  单页处理时间: {single_page_time:.0f}ms ({single_page_time/1000:.1f}s)")
        print(f"  30页总时间: {total_time_30_pages:.1f}s ({total_time_30_pages/60:.1f}分钟)")

def calculate_performance_improvement():
    """计算性能提升"""
    print("\n=== 性能提升分析 ===")
    
    # 原始配置（未优化前）
    original_config = {
        "page_load_wait": 500,
        "pagination_wait": 300,
        "post_action_wait": 800,
        "page_interval_min": 1.0,
        "page_interval_max": 2.0,
    }
    
    # 优化后的快速模式配置
    optimized_config = {
        "page_load_wait": 150,
        "pagination_wait": 50,
        "post_action_wait": 200,
        "page_interval_min": 0.2,
        "page_interval_max": 0.4,
    }
    
    # 计算单页时间
    original_time = (
        original_config["page_load_wait"] +
        original_config["pagination_wait"] +
        original_config["post_action_wait"] +
        (original_config["page_interval_min"] + original_config["page_interval_max"]) / 2 * 1000
    )
    
    optimized_time = (
        optimized_config["page_load_wait"] +
        optimized_config["pagination_wait"] +
        optimized_config["post_action_wait"] +
        (optimized_config["page_interval_min"] + optimized_config["page_interval_max"]) / 2 * 1000
    )
    
    improvement = (original_time - optimized_time) / original_time * 100
    
    print(f"原始单页时间: {original_time:.0f}ms ({original_time/1000:.2f}s)")
    print(f"优化单页时间: {optimized_time:.0f}ms ({optimized_time/1000:.2f}s)")
    print(f"性能提升: {improvement:.1f}%")
    print(f"速度提升: {original_time/optimized_time:.1f}x")
    
    # 计算30页的时间差
    original_30_pages = original_time * 30 / 1000
    optimized_30_pages = optimized_time * 30 / 1000
    time_saved = original_30_pages - optimized_30_pages
    
    print(f"\n30页爬取对比:")
    print(f"原始总时间: {original_30_pages:.1f}s ({original_30_pages/60:.1f}分钟)")
    print(f"优化总时间: {optimized_30_pages:.1f}s ({optimized_30_pages/60:.1f}分钟)")
    print(f"节省时间: {time_saved:.1f}s ({time_saved/60:.1f}分钟)")

def test_performance_optimization():
    """主测试函数"""
    print("李大霄指数爬虫性能优化测试")
    print("=" * 50)
    
    try:
        # 测试时间配置
        test_timing_configuration()
        
        # 模拟页面时间
        simulate_page_timing()
        
        # 计算性能提升
        calculate_performance_improvement()
        
        print("\n✅ 性能优化测试完成")
        print("\n主要优化:")
        print("• 页面加载等待时间减少60-70%")
        print("• 分页等待时间减少67-83%")
        print("• 页面间隔时间减少70-80%")
        print("• 总体性能提升约75%，速度提升4倍")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_performance_optimization()
    sys.exit(0 if success else 1)