#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界情况和边缘案例测试
Boundary conditions and edge cases test
"""

import datetime
from historical import HistoricalCalculator


def test_edge_case_1():
    """测试案例1：目标日期前后刚好有视频"""
    print("=" * 60)
    print("边界案例1: 目标日期前后刚好有视频")
    print("Edge case 1: Videos exactly before and after target range")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    videos = [
        {"view": 10000, "comment": 100, "title": "Day before range", "pubdate": "2024-08-21"},  # 应该被排除
        {"view": 20000, "comment": 200, "title": "First day of range", "pubdate": "2024-08-22"},  # 应该被包含
        {"view": 30000, "comment": 300, "title": "Last day of range", "pubdate": "2024-08-28"},  # 应该被包含
        {"view": 40000, "comment": 400, "title": "Day after range", "pubdate": "2024-08-29"},  # 应该被排除
    ]
    
    debug_info = calculator.debug_calculation_process(videos, "2024-08-28")
    result = debug_info["final_result"]["index"]
    
    # 期望结果：只包含2024-08-22和2024-08-28的视频
    expected = ((20000 / 10000) + (200 / 100)) + ((30000 / 10000) + (300 / 100))
    
    print(f"结果: {result}, 期望: {expected}")
    print(f"包含的视频数量: {debug_info['calculation_steps'][3]['filtered_videos_count']}")
    
    success = abs(result - expected) < 0.01
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


def test_edge_case_2():
    """测试案例2：空视频列表"""
    print("\n" + "=" * 60)
    print("边界案例2: 空视频列表")
    print("Edge case 2: Empty video list")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    result = calculator.calculate_historical_index([], "2024-08-28")
    
    print(f"结果: {result}, 期望: 0.0")
    success = result == 0.0
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


def test_edge_case_3():
    """测试案例3：只有日期范围外的视频"""
    print("\n" + "=" * 60)
    print("边界案例3: 只有日期范围外的视频")
    print("Edge case 3: Videos only outside date range")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    videos = [
        {"view": 10000, "comment": 100, "title": "Too early", "pubdate": "2024-08-20"},
        {"view": 20000, "comment": 200, "title": "Too late", "pubdate": "2024-08-30"},
    ]
    
    result = calculator.calculate_historical_index(videos, "2024-08-28")
    
    print(f"结果: {result}, 期望: 0.0")
    success = result == 0.0
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


def test_edge_case_4():
    """测试案例4：跨月份边界"""
    print("\n" + "=" * 60)
    print("边界案例4: 跨月份边界")
    print("Edge case 4: Cross-month boundary")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    # 目标日期是9月3日，范围应该是8月28日到9月3日
    videos = [
        {"view": 10000, "comment": 100, "title": "Aug 27", "pubdate": "2024-08-27"},  # 排除
        {"view": 20000, "comment": 200, "title": "Aug 28", "pubdate": "2024-08-28"},  # 包含
        {"view": 30000, "comment": 300, "title": "Sep 1", "pubdate": "2024-09-01"},   # 包含
        {"view": 40000, "comment": 400, "title": "Sep 3", "pubdate": "2024-09-03"},   # 包含
        {"view": 50000, "comment": 500, "title": "Sep 4", "pubdate": "2024-09-04"},   # 排除
    ]
    
    debug_info = calculator.debug_calculation_process(videos, "2024-09-03")
    result = debug_info["final_result"]["index"]
    
    # 期望：包含8-28, 9-1, 9-3的视频
    expected = ((20000 / 10000) + (200 / 100)) + ((30000 / 10000) + (300 / 100)) + ((40000 / 10000) + (400 / 100))
    
    print(f"目标日期: 2024-09-03")
    print(f"期望日期范围: [2024-08-28, 2024-09-03]")
    print(f"包含的视频数量: {debug_info['calculation_steps'][3]['filtered_videos_count']}")
    print(f"结果: {result}, 期望: {expected}")
    
    success = abs(result - expected) < 0.01
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


def test_edge_case_5():
    """测试案例5：闰年2月边界"""
    print("\n" + "=" * 60)
    print("边界案例5: 闰年2月边界")
    print("Edge case 5: Leap year February boundary")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    # 2024年是闰年，2月有29天
    videos = [
        {"view": 10000, "comment": 100, "title": "Feb 23", "pubdate": "2024-02-23"},  # 排除
        {"view": 20000, "comment": 200, "title": "Feb 24", "pubdate": "2024-02-24"},  # 包含
        {"view": 30000, "comment": 300, "title": "Feb 29", "pubdate": "2024-02-29"},  # 包含（闰年）
        {"view": 40000, "comment": 400, "title": "Mar 1", "pubdate": "2024-03-01"},   # 包含
        {"view": 50000, "comment": 500, "title": "Mar 2", "pubdate": "2024-03-02"},   # 包含
        {"view": 60000, "comment": 600, "title": "Mar 3", "pubdate": "2024-03-03"},   # 排除
    ]
    
    debug_info = calculator.debug_calculation_process(videos, "2024-03-02")
    result = debug_info["final_result"]["index"]
    
    # 期望：包含2-25, 2-29, 3-1, 3-2的视频（2-24应该被排除）
    expected = ((30000 / 10000) + (300 / 100)) + ((40000 / 10000) + (400 / 100)) + ((50000 / 10000) + (500 / 100))
    
    print(f"目标日期: 2024-03-02")
    print(f"期望日期范围: [2024-02-25, 2024-03-02] (包含闰年2月29日)")
    print(f"包含的视频数量: {debug_info['calculation_steps'][3]['filtered_videos_count']}")
    print(f"结果: {result}, 期望: {expected}")
    print(f"注意: 2024-02-24的视频应该被排除，因为不在7天范围内")
    
    success = abs(result - expected) < 0.01
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


def test_edge_case_6():
    """测试案例6：视频没有日期信息"""
    print("\n" + "=" * 60)
    print("边界案例6: 视频没有日期信息")
    print("Edge case 6: Videos without date information")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    videos = [
        {"view": 10000, "comment": 100, "title": "With date", "pubdate": "2024-08-25"},
        {"view": 20000, "comment": 200, "title": "No date", "created": None},  # 无日期信息
        {"view": 30000, "comment": 300, "title": "Invalid date", "pubdate": "invalid-date"},  # 无效日期
    ]
    
    debug_info = calculator.debug_calculation_process(videos, "2024-08-28")
    result = debug_info["final_result"]["index"]
    
    print(f"包含的视频数量: {debug_info['calculation_steps'][3]['filtered_videos_count']}")
    print(f"结果: {result}")
    
    # 应该包含：有效日期的视频 + 无日期信息的视频（向后兼容）
    # 无效日期格式的视频应该被排除
    expected = ((10000 / 10000) + (100 / 100)) + ((20000 / 10000) + (200 / 100))
    
    success = abs(result - expected) < 0.01
    print(f"期望结果: {expected} (包含1个有效日期视频 + 1个无日期信息视频，1个无效日期视频被排除)")
    print(f"✅ 测试通过" if success else f"❌ 测试失败")
    return success


if __name__ == "__main__":
    print("开始边界情况和边缘案例测试")
    print("Starting boundary conditions and edge cases tests")
    
    test_results = [
        test_edge_case_1(),
        test_edge_case_2(),
        test_edge_case_3(),
        test_edge_case_4(),
        test_edge_case_5(),
        test_edge_case_6(),
    ]
    
    print("\n" + "=" * 60)
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print(f"🎉 所有 {total} 个边界测试都通过了！")
        print("🎉 All boundary tests passed!")
    else:
        print(f"❌ {total - passed}/{total} 个测试失败")
        print("❌ Some boundary tests failed")
    print("=" * 60)