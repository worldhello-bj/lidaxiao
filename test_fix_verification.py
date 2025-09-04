#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证李大霄指数堆叠问题修复效果
Verify fix for Li Daxiao Index stacking issue
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(__file__))

from historical import HistoricalCalculator


def test_fix_verification():
    """验证修复效果：所有历史日期应返回相同指数值"""
    print("验证李大霄指数堆叠问题修复效果")
    print("="*50)
    
    # 创建包含日期的测试数据（这在修复前会导致堆叠问题）
    current_date = "2024-08-28"
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    # 创建30天内分布的视频数据
    mock_videos = []
    for i in range(30):
        pub_date = current_dt - datetime.timedelta(days=i+1)
        video = {
            "view": 50000 - i*500,  # 递减的播放量
            "comment": 1000 - i*10, # 递减的评论数
            "title": f"Video {i+1}",
            "pubdate": pub_date.strftime("%Y-%m-%d")
        }
        mock_videos.append(video)
    
    print(f"测试视频数据: {len(mock_videos)} 个视频")
    print(f"发布日期范围: {mock_videos[-1]['pubdate']} 到 {mock_videos[0]['pubdate']}")
    
    # 测试不同长度的历史范围
    calculator = HistoricalCalculator()
    
    test_ranges = [
        ("短期", 7),   # 1周
        ("中期", 30),  # 1个月  
        ("长期", 90)   # 3个月
    ]
    
    for range_name, days in test_ranges:
        print(f"\n{range_name}测试 ({days}天):")
        
        # 生成日期范围
        date_range = []
        for i in range(days, 0, -1):
            date = current_dt - datetime.timedelta(days=i)
            date_range.append(date.strftime("%Y-%m-%d"))
        
        # 批量计算
        results = calculator.calculate_batch_historical(mock_videos, date_range, current_date)
        indices = [r["index"] for r in results]
        
        # 分析结果
        unique_values = set(indices)
        min_idx = min(indices)
        max_idx = max(indices)
        
        print(f"  日期范围: {date_range[0]} 到 {date_range[-1]}")
        print(f"  唯一指数值数量: {len(unique_values)}")
        print(f"  指数值范围: {min_idx:.2f} - {max_idx:.2f}")
        
        if len(unique_values) == 1:
            print(f"  ✓ 所有日期指数值相同: {indices[0]:.2f}")
        else:
            print(f"  ✗ 指数值不一致，发现堆叠问题")
            return False
    
    print("\n" + "="*50)
    print("✅ 修复验证成功！")
    print("所有历史日期现在都返回相同的指数值，")
    print("完全消除了错误堆叠问题。")
    return True


def demonstrate_intended_behavior():
    """演示修复后的预期行为"""
    print("\n" + "="*50)
    print("演示修复后的预期行为")
    print("="*50)
    
    mock_videos = [
        {"view": 50000, "comment": 1000, "title": "热门视频"},
        {"view": 30000, "comment": 500, "title": "普通视频"},
    ]
    
    calculator = HistoricalCalculator()
    
    # 测试不同的历史日期
    test_dates = [
        "2024-01-01",  # 很早的日期
        "2024-06-15",  # 中等日期
        "2024-08-25",  # 最近的日期
    ]
    
    print("使用相同视频数据计算不同历史日期的指数:")
    print("（修复后：所有日期应返回相同值）")
    
    for date in test_dates:
        index = calculator.calculate_historical_index(mock_videos, date, "2024-08-28")
        print(f"  {date}: {index:.2f}")
    
    print("\n这种行为是预期的，因为:")
    print("1. 历史计算使用当前数据作为近似")
    print("2. 没有真实历史数据时，这是最合理的估算方式")
    print("3. 避免了因日期过滤导致的虚假增长趋势")


if __name__ == "__main__":
    try:
        success = test_fix_verification()
        demonstrate_intended_behavior()
        
        if success:
            print(f"\n{'='*50}")
            print("🎉 李大霄指数堆叠问题修复成功！")
            sys.exit(0)
        else:
            print(f"\n{'='*50}")
            print("❌ 修复验证失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)