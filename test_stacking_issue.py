#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试历史长时间计算中的李大霄指数错误堆叠问题
Test for Li Daxiao Index Error Stacking in Long-term Historical Calculations
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(__file__))

from historical import HistoricalCalculator, calculate_batch_historical


def test_long_term_batch_calculation():
    """测试长时间批量历史计算是否存在堆叠问题"""
    print("Testing long-term batch calculation for stacking issues...")
    
    # 创建模拟视频数据 - 固定数据，不应该导致指数变化
    mock_videos = [
        {"view": 50000, "comment": 1000, "title": "Test Video 1"},
        {"view": 30000, "comment": 500, "title": "Test Video 2"},
        {"view": 20000, "comment": 300, "title": "Test Video 3"}
    ]
    
    # 创建长时间范围 - 过去90天
    current_date = "2024-08-28"
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    # 生成过去90天的日期范围
    date_range = []
    for i in range(90, 0, -1):  # 从90天前到昨天
        date = current_dt - datetime.timedelta(days=i)
        date_range.append(date.strftime("%Y-%m-%d"))
    
    print(f"测试日期范围: {len(date_range)} 天 (从 {date_range[0]} 到 {date_range[-1]})")
    
    # 批量计算历史指数
    calculator = HistoricalCalculator()
    results = calculator.calculate_batch_historical(mock_videos, date_range, current_date)
    
    # 分析结果
    indices = [r["index"] for r in results if "error" not in r]
    
    print(f"计算结果数量: {len(indices)}")
    print(f"最小指数值: {min(indices):.2f}")
    print(f"最大指数值: {max(indices):.2f}")
    print(f"平均指数值: {sum(indices)/len(indices):.2f}")
    
    # 检查前10天和后10天的对比
    first_10 = indices[:10]
    last_10 = indices[-10:]
    
    print(f"\n前10天指数值: {first_10}")
    print(f"后10天指数值: {last_10}")
    print(f"前10天平均: {sum(first_10)/len(first_10):.2f}")
    print(f"后10天平均: {sum(last_10)/len(last_10):.2f}")
    
    # 检查是否存在持续递增趋势
    increasing_count = 0
    for i in range(1, len(indices)):
        if indices[i] > indices[i-1]:
            increasing_count += 1
    
    increasing_percentage = (increasing_count / (len(indices) - 1)) * 100
    print(f"\n递增趋势分析:")
    print(f"递增次数: {increasing_count}/{len(indices)-1}")
    print(f"递增百分比: {increasing_percentage:.1f}%")
    
    # 检查所有值是否应该相同（因为使用相同的视频数据）
    unique_indices = set(indices)
    print(f"\n唯一指数值数量: {len(unique_indices)}")
    
    if len(unique_indices) == 1:
        print("✓ 所有指数值相同，没有堆叠问题")
        return True
    else:
        print(f"✗ 发现 {len(unique_indices)} 个不同的指数值，可能存在堆叠问题")
        print(f"不同的指数值: {sorted(unique_indices)}")
        
        # 如果递增百分比很高，说明存在堆叠问题
        if increasing_percentage > 70:
            print("✗ 检测到持续递增趋势，确认存在堆叠问题")
            return False
        else:
            print("? 指数值有变化，但未检测到明显的堆叠模式")
            return True


def test_single_vs_batch_consistency():
    """测试单个计算与批量计算的一致性"""
    print("\n" + "="*60)
    print("Testing consistency between single and batch calculations...")
    
    mock_videos = [
        {"view": 40000, "comment": 800, "title": "Video A"},
        {"view": 25000, "comment": 400, "title": "Video B"}
    ]
    
    calculator = HistoricalCalculator()
    test_dates = ["2024-08-20", "2024-08-21", "2024-08-22"]
    current_date = "2024-08-28"
    
    # 单个计算
    single_results = []
    for date in test_dates:
        index = calculator.calculate_historical_index(mock_videos, date, current_date)
        single_results.append(index)
    
    # 批量计算
    batch_results = calculator.calculate_batch_historical(mock_videos, test_dates, current_date)
    batch_indices = [r["index"] for r in batch_results]
    
    print("单个计算结果:", [f"{x:.2f}" for x in single_results])
    print("批量计算结果:", [f"{x:.2f}" for x in batch_indices])
    
    # 检查一致性
    consistency_ok = True
    for i, (single, batch) in enumerate(zip(single_results, batch_indices)):
        if abs(single - batch) > 0.01:
            print(f"✗ 日期 {test_dates[i]}: 单个={single:.2f}, 批量={batch:.2f}, 差异={abs(single-batch):.2f}")
            consistency_ok = False
    
    if consistency_ok:
        print("✓ 单个计算与批量计算结果一致")
    
    return consistency_ok


if __name__ == "__main__":
    print("="*60)
    print("李大霄指数错误堆叠问题测试")
    print("Li Daxiao Index Error Stacking Test")
    print("="*60)
    
    try:
        stacking_ok = test_long_term_batch_calculation()
        consistency_ok = test_single_vs_batch_consistency()
        
        print("\n" + "="*60)
        print("测试结果总结:")
        print(f"长期批量计算测试: {'通过' if stacking_ok else '失败'}")
        print(f"一致性测试: {'通过' if consistency_ok else '失败'}")
        
        if stacking_ok and consistency_ok:
            print("✓ 所有测试通过，未发现堆叠问题")
            sys.exit(0)
        else:
            print("✗ 检测到问题，需要进一步调查")
            sys.exit(1)
    
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)