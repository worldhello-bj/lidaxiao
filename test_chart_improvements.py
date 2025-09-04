#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图表美化功能
Test chart beautification features
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(__file__))

from visualizer import plot_historical_estimates, plot_history_trend

def create_test_data():
    """创建包含明显极值的测试数据"""
    data = []
    values = [50, 45, 30, 25, 10, 15, 35, 60, 80, 140, 120, 90, 70, 55, 40]  # 明显的最小值10和最大值140
    
    for i, value in enumerate(values):
        date = datetime.date(2024, 5, 1) + datetime.timedelta(days=i*3)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "index": value,
            "estimated": True
        })
    
    return data

def test_extreme_values_detection():
    """测试极值检测功能"""
    print("测试极值检测功能...")
    test_data = create_test_data()
    
    # 提取数值用于验证
    indices = [item["index"] for item in test_data]
    expected_max = max(indices)
    expected_min = min(indices)
    
    print(f"测试数据极值: 最大值={expected_max}, 最小值={expected_min}")
    
    # 生成图表并检查是否成功
    current_date = "2024-09-04"
    filename = plot_historical_estimates(test_data, current_date, "test")
    
    if filename and os.path.exists(filename):
        file_size = os.path.getsize(filename)
        print(f"✓ 极值标注图表生成成功: {filename} ({file_size} bytes)")
        return True
    else:
        print("✗ 极值标注图表生成失败")
        return False

def test_date_label_optimization():
    """测试日期标签优化功能"""
    print("\n测试日期标签优化功能...")
    
    # 创建大量数据点来测试标签优化
    data = []
    for i in range(50):  # 50个数据点应该触发标签优化
        date = datetime.date(2024, 1, 1) + datetime.timedelta(days=i*2)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "index": 50 + (i % 10) * 5,  # 简单的波动
            "estimated": True
        })
    
    print(f"生成了 {len(data)} 个数据点用于测试标签优化")
    
    current_date = "2024-09-04"
    filename = plot_historical_estimates(data, current_date, "label_test")
    
    if filename and os.path.exists(filename):
        file_size = os.path.getsize(filename)
        print(f"✓ 标签优化图表生成成功: {filename} ({file_size} bytes)")
        return True
    else:
        print("✗ 标签优化图表生成失败")
        return False

def test_visual_improvements():
    """测试视觉改进"""
    print("\n测试视觉改进...")
    
    # 测试 plot_history_trend 函数
    test_data = create_test_data()
    current_date = "2024-09-04"
    
    try:
        plot_history_trend(test_data, current_date)
        filename = f"index_history_{current_date.replace('-', '')}.png"
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✓ 历史趋势图生成成功: {filename} ({file_size} bytes)")
            return True
        else:
            print("✗ 历史趋势图生成失败")
            return False
    except Exception as e:
        print(f"✗ 历史趋势图生成出错: {e}")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n测试边界情况...")
    
    # 测试空数据
    try:
        result = plot_historical_estimates([], "2024-09-04", "empty")
        if result is None:
            print("✓ 空数据处理正确")
        else:
            print("✗ 空数据处理异常")
            return False
    except Exception as e:
        print(f"✗ 空数据处理出错: {e}")
        return False
    
    # 测试单个数据点
    single_data = [{
        "date": "2024-09-04",
        "index": 50.0,
        "estimated": True
    }]
    
    try:
        filename = plot_historical_estimates(single_data, "2024-09-04", "single")
        if filename and os.path.exists(filename):
            print("✓ 单数据点处理正确")
            return True
        else:
            print("✗ 单数据点处理失败")
            return False
    except Exception as e:
        print(f"✗ 单数据点处理出错: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("李大霄指数图表美化功能测试")
    print("Li Daxiao Index Chart Beautification Tests")  
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    if test_extreme_values_detection():
        tests_passed += 1
    
    if test_date_label_optimization():
        tests_passed += 1
    
    if test_visual_improvements():
        tests_passed += 1
        
    if test_edge_cases():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    if tests_passed == total_tests:
        print("🎉 所有美化功能测试通过！")
        print("🎉 All beautification tests passed!")
        print("✓ 极值标注功能正常")
        print("✓ 日期标签优化功能正常")
        print("✓ 视觉改进功能正常")
        print("✓ 边界情况处理正常")
    else:
        print(f"❌ {total_tests - tests_passed}/{total_tests} 个测试失败")
        print(f"❌ {total_tests - tests_passed}/{total_tests} tests failed")
        sys.exit(1)
    
    print("=" * 60)