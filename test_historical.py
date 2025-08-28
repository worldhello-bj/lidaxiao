#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史指数计算模块测试
Historical Index Calculation Module Tests

Simple tests to validate the historical calculation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from historical import HistoricalCalculator, calculate_historical_index, calculate_batch_historical
import datetime


def test_exponential_decay_model():
    """测试指数衰减模型"""
    print("Testing exponential decay model...")
    calculator = HistoricalCalculator(decay_rate=0.1)
    
    current_value = 100.0
    
    # 测试当前值 (0天前)
    assert abs(calculator.exponential_decay_model(current_value, 0) - 100.0) < 0.01
    print("✓ 当前值测试通过")
    
    # 测试历史值 (1天前)
    days_1_ago = calculator.exponential_decay_model(current_value, 1)
    expected_1 = 100.0 * 0.904837  # exp(-0.1 * 1) ≈ 0.904837
    assert abs(days_1_ago - expected_1) < 0.01
    print("✓ 1天前值测试通过")
    
    # 测试历史值应该小于当前值
    days_10_ago = calculator.exponential_decay_model(current_value, 10)
    assert days_10_ago < current_value
    print("✓ 历史值小于当前值测试通过")
    
    print("Exponential decay model tests passed!")


def test_linear_growth_model():
    """测试线性增长模型"""
    print("\nTesting linear growth model...")
    calculator = HistoricalCalculator(growth_rate=0.02)
    
    current_value = 100.0
    
    # 测试当前值
    assert abs(calculator.linear_growth_model(current_value, 0) - 100.0) < 0.01
    print("✓ 当前值测试通过")
    
    # 测试历史值 (10天前)
    days_10_ago = calculator.linear_growth_model(current_value, 10)
    expected_10 = 100.0 / (1 + 0.02 * 10)  # 100 / 1.2 = 83.33
    assert abs(days_10_ago - expected_10) < 0.01
    print("✓ 10天前值测试通过")
    
    # 测试历史值应该小于当前值
    assert days_10_ago < current_value
    print("✓ 历史值小于当前值测试通过")
    
    print("Linear growth model tests passed!")


def test_hybrid_model():
    """测试混合模型"""
    print("\nTesting hybrid model...")
    calculator = HistoricalCalculator()
    
    current_value = 100.0
    days_ago = 5
    
    hybrid_value = calculator.hybrid_model(current_value, days_ago)
    exp_value = calculator.exponential_decay_model(current_value, days_ago)
    linear_value = calculator.linear_growth_model(current_value, days_ago)
    
    # 混合值应该在指数值和线性值之间
    min_val = min(exp_value, linear_value)
    max_val = max(exp_value, linear_value)
    assert min_val <= hybrid_value <= max_val
    print("✓ 混合值在合理范围内")
    
    print("Hybrid model tests passed!")


def test_historical_index_calculation():
    """测试历史指数计算"""
    print("\nTesting historical index calculation...")
    
    # 创建模拟视频数据
    mock_videos = [
        {"view": 50000, "comment": 1000, "title": "Test Video 1"},
        {"view": 30000, "comment": 500, "title": "Test Video 2"},
    ]
    
    current_date = "2024-01-10"
    target_date = "2024-01-05"  # 5天前
    
    # 测试不同模型
    for model in ["exponential", "linear", "hybrid"]:
        historical_index = calculate_historical_index(
            mock_videos, target_date, current_date, model
        )
        print(f"✓ {model} 模型计算结果: {historical_index:.2f}")
        assert historical_index > 0
        assert historical_index < 100  # 合理范围
    
    print("Historical index calculation tests passed!")


def test_batch_calculation():
    """测试批量计算"""
    print("\nTesting batch calculation...")
    
    mock_videos = [
        {"view": 50000, "comment": 1000, "title": "Test Video 1"},
        {"view": 30000, "comment": 500, "title": "Test Video 2"},
    ]
    
    current_date = "2024-01-10"
    date_range = ["2024-01-08", "2024-01-09", "2024-01-10"]
    
    results = calculate_batch_historical(
        mock_videos, date_range, current_date, "exponential"
    )
    
    assert len(results) == 3
    print("✓ 批量计算结果数量正确")
    
    for result in results:
        assert "date" in result
        assert "index" in result
        assert "model" in result
        assert result["index"] > 0
        print(f"✓ 日期 {result['date']}: 指数 {result['index']}")
    
    print("Batch calculation tests passed!")


def test_date_range_generation():
    """测试日期范围生成"""
    print("\nTesting date range generation...")
    
    calculator = HistoricalCalculator()
    dates = calculator.generate_date_range("2024-01-01", "2024-01-05")
    
    expected_dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    assert dates == expected_dates
    print("✓ 日期范围生成正确")
    
    print("Date range generation tests passed!")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("运行历史指数计算模块测试")
    print("=" * 50)
    
    try:
        test_exponential_decay_model()
        test_linear_growth_model() 
        test_hybrid_model()
        test_historical_index_calculation()
        test_batch_calculation()
        test_date_range_generation()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)