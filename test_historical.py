#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史指数计算模块测试
Historical Index Calculation Module Tests

Simple tests to validate the historical calculation functionality using current data approximation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from historical import HistoricalCalculator, calc_historical_index, calc_batch_historical
import datetime


def test_historical_calculator_initialization():
    """测试历史计算器初始化"""
    print("Testing historical calculator initialization...")
    calculator = HistoricalCalculator()
    assert calculator is not None
    print("✓ 历史计算器初始化测试通过")


def test_single_date_calculation():
    """测试单日期历史计算"""
    print("\nTesting single date historical calculation...")
    
    # 模拟视频数据
    mock_videos = [
        {"view": 50000, "comment": 1000, "title": "Test Video 1"},
        {"view": 30000, "comment": 500, "title": "Test Video 2"},
        {"view": 20000, "comment": 300, "title": "Test Video 3"}
    ]
    
    calculator = HistoricalCalculator()
    
    # 计算历史指数（应该等于当前指数）
    historical_index = calculator.calc_historical_index(
        mock_videos, "2024-08-20", "2024-08-28"
    )
    
    # 验证计算结果是否合理
    assert historical_index > 0, "Historical index should be positive"
    assert isinstance(historical_index, float), "Historical index should be a float"
    
    print(f"✓ 历史指数计算结果: {historical_index:.2f}")
    print("✓ 单日期历史计算测试通过")


def test_batch_calculation():
    """测试批量历史计算"""
    print("\nTesting batch historical calculation...")
    
    # 模拟视频数据
    mock_videos = [
        {"view": 40000, "comment": 800, "title": "Test Video A"},
        {"view": 25000, "comment": 400, "title": "Test Video B"}
    ]
    
    calculator = HistoricalCalculator()
    date_range = ["2024-08-20", "2024-08-21", "2024-08-22"]
    
    # 批量计算
    results = calculator.calc_batch_historical(mock_videos, date_range, "2024-08-28")
    
    # 验证结果
    assert len(results) == 3, "Should return 3 results"
    
    for result in results:
        assert "date" in result, "Result should contain date"
        assert "index" in result, "Result should contain index"
        assert "approximated" in result, "Result should contain approximated flag"
        assert result["approximated"] is True, "All results should be approximated"
        assert result["index"] > 0, "Index should be positive"
    
    # 验证所有日期的指数值应该相同（因为使用相同的当前数据）
    indices = [r["index"] for r in results]
    assert all(abs(idx - indices[0]) < 0.01 for idx in indices), "All indices should be the same"
    
    print(f"✓ 批量计算结果数量: {len(results)}")
    print(f"✓ 所有日期的近似指数值: {indices[0]:.2f}")
    print("✓ 批量历史计算测试通过")


def test_date_validation():
    """测试日期验证"""
    print("\nTesting date validation...")
    
    mock_videos = [{"view": 10000, "comment": 100, "title": "Test Video"}]
    calculator = HistoricalCalculator()
    
    # 测试未来日期应该抛出异常
    try:
        calculator.calc_historical_index(mock_videos, "2025-01-01", "2024-08-28")
        assert False, "Should raise exception for future date"
    except ValueError as e:
        print(f"✓ 正确捕获未来日期错误: {str(e)}")
    
    # 测试有效日期应该成功
    try:
        result = calculator.calc_historical_index(mock_videos, "2024-08-15", "2024-08-28")
        assert result > 0, "Valid date should return positive result"
        print("✓ 有效日期计算成功")
    except Exception as e:
        assert False, f"Valid date should not raise exception: {e}"
    
    print("✓ 日期验证测试通过")


def test_date_range_generation():
    """测试日期范围生成"""
    print("\nTesting date range generation...")
    
    calculator = HistoricalCalculator()
    
    # 生成日期范围
    date_range = calculator.generate_date_range("2024-08-20", "2024-08-25")
    
    expected_dates = [
        "2024-08-20", "2024-08-21", "2024-08-22", 
        "2024-08-23", "2024-08-24", "2024-08-25"
    ]
    
    assert date_range == expected_dates, f"Expected {expected_dates}, got {date_range}"
    print(f"✓ 日期范围生成正确: {date_range}")
    print("✓ 日期范围生成测试通过")


def test_convenience_functions():
    """测试便捷函数"""
    print("\nTesting convenience functions...")
    
    mock_videos = [
        {"view": 60000, "comment": 1200, "title": "Convenience Test Video"}
    ]
    
    # 测试单日期便捷函数
    result1 = calc_historical_index(mock_videos, "2024-08-20", "2024-08-28")
    assert result1 > 0, "Convenience function should return positive result"
    print(f"✓ 单日期便捷函数结果: {result1:.2f}")
    
    # 测试批量便捷函数
    date_range = ["2024-08-20", "2024-08-21"]
    results = calc_batch_historical(mock_videos, date_range, "2024-08-28")
    assert len(results) == 2, "Should return 2 results"
    print(f"✓ 批量便捷函数结果数量: {len(results)}")
    
    print("✓ 便捷函数测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("历史指数计算模块测试")
    print("Historical Index Calculation Module Tests")
    print("=" * 50)
    
    try:
        test_historical_calculator_initialization()
        test_single_date_calculation()
        test_batch_calculation()
        test_date_validation()
        test_date_range_generation()
        test_convenience_functions()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！All tests passed!")
        print("历史指数计算模块工作正常")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
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
        historical_index = calc_historical_index(
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
    
    results = calc_batch_historical(
        mock_videos, date_range, current_date
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