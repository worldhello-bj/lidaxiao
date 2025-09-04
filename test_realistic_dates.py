#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试使用真实日期数据的历史指数计算
Test historical index calculation with realistic date data
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(__file__))

from historical import HistoricalCalculator


def test_with_realistic_video_dates():
    """使用真实视频发布日期测试历史计算"""
    print("Testing with realistic video publication dates...")
    
    # 创建带有发布日期的模拟视频数据
    # 模拟一个月内发布的视频
    current_date = "2024-08-28"
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    mock_videos = []
    # 生成30个视频，分布在过去30天内
    for i in range(30):
        pub_date = current_dt - datetime.timedelta(days=i+1)  # 1-30天前
        video = {
            "view": 50000 - i*1000,  # 播放量逐渐减少（模拟较新视频播放量更高）
            "comment": 1000 - i*20,  # 评论数也逐渐减少
            "title": f"Video {i+1}",
            "pubdate": pub_date.strftime("%Y-%m-%d")  # 关键：添加发布日期
        }
        mock_videos.append(video)
    
    print(f"创建了 {len(mock_videos)} 个带日期的视频")
    print(f"最早视频: {mock_videos[-1]['pubdate']}, 播放量: {mock_videos[-1]['view']}")
    print(f"最新视频: {mock_videos[0]['pubdate']}, 播放量: {mock_videos[0]['view']}")
    
    # 生成测试日期范围（过去60天）
    date_range = []
    for i in range(60, 0, -1):
        date = current_dt - datetime.timedelta(days=i)
        date_range.append(date.strftime("%Y-%m-%d"))
    
    print(f"测试日期范围: {len(date_range)} 天")
    
    # 批量计算历史指数
    calculator = HistoricalCalculator()
    results = calculator.calculate_batch_historical(mock_videos, date_range, current_date)
    
    indices = [r["index"] for r in results if "error" not in r]
    
    print(f"\n结果分析:")
    print(f"计算结果数量: {len(indices)}")
    print(f"最小指数值: {min(indices):.2f}")
    print(f"最大指数值: {max(indices):.2f}")
    print(f"平均指数值: {sum(indices)/len(indices):.2f}")
    
    # 显示前10天和后10天的详细结果
    print(f"\n前10天详细结果:")
    for i in range(min(10, len(results))):
        r = results[i]
        print(f"  {r['date']}: {r['index']:.2f}")
    
    print(f"\n后10天详细结果:")
    for i in range(max(0, len(results)-10), len(results)):
        r = results[i]
        print(f"  {r['date']}: {r['index']:.2f}")
    
    # 分析趋势
    increasing_count = 0
    for i in range(1, len(indices)):
        if indices[i] > indices[i-1]:
            increasing_count += 1
    
    increasing_percentage = (increasing_count / (len(indices) - 1)) * 100
    print(f"\n趋势分析:")
    print(f"递增次数: {increasing_count}/{len(indices)-1}")
    print(f"递增百分比: {increasing_percentage:.1f}%")
    
    # 手动验证几个关键日期的计算
    print(f"\n手动验证:")
    test_date = "2024-07-29"  # 30天前
    effective_date = datetime.datetime.strptime(test_date, "%Y-%m-%d").date() - datetime.timedelta(days=6)
    print(f"测试日期: {test_date}")
    print(f"有效计算日期（减去6天）: {effective_date}")
    
    # 手动筛选视频
    filtered_videos = []
    for video in mock_videos:
        video_date = datetime.datetime.strptime(video['pubdate'], "%Y-%m-%d").date()
        if video_date <= effective_date:
            filtered_videos.append(video)
    
    print(f"符合条件的视频数量: {len(filtered_videos)}")
    if filtered_videos:
        print(f"最新符合条件的视频: {filtered_videos[0]['pubdate']}")
        print(f"最早符合条件的视频: {filtered_videos[-1]['pubdate']}")
    
    return indices


if __name__ == "__main__":
    print("="*60)
    print("使用真实日期数据的李大霄指数计算测试")
    print("="*60)
    
    try:
        indices = test_with_realistic_video_dates()
        
        # 检查是否存在异常增长
        if len(set(indices)) > 1:
            print("\n指数值有变化，这是预期的（因为不同日期有不同的可用视频）")
            
            # 检查是否有不合理的持续增长
            max_val = max(indices)
            min_val = min(indices)
            if max_val > min_val * 2:  # 如果最大值是最小值的2倍以上
                print(f"警告: 指数变化幅度较大 (最小: {min_val:.2f}, 最大: {max_val:.2f})")
            else:
                print(f"指数变化在合理范围内 (最小: {min_val:.2f}, 最大: {max_val:.2f})")
        else:
            print("\n所有指数值相同")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)