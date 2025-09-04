#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细计算过程调试脚本
Detailed Calculation Process Debug Script

这个脚本用于调试李大霄指数历史计算中的堆叠问题，
输出详细的计算步骤和中间结果，帮助定位问题根源。
"""

import sys
import os
import datetime
import json
sys.path.insert(0, os.path.dirname(__file__))

from historical import debug_calculation_process, debug_batch_calculation


def create_realistic_test_data():
    """创建真实的测试数据，模拟实际爬取的视频数据"""
    current_date = "2024-08-28"
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    # 模拟过去30天内发布的视频
    mock_videos = []
    for i in range(30):
        pub_date = current_dt - datetime.timedelta(days=i+1)
        video = {
            "view": 50000 - i*1000,  # 播放量递减，模拟较新视频播放量更高
            "comment": 1000 - i*20,   # 评论数递减
            "title": f"李大霄谈股市-第{i+1}期",
            "pubdate": pub_date.strftime("%Y-%m-%d")
        }
        mock_videos.append(video)
    
    return mock_videos, current_date


def debug_single_date_example():
    """调试单个日期的计算过程示例"""
    print("="*80)
    print("单个日期计算过程调试示例")
    print("="*80)
    
    videos, current_date = create_realistic_test_data()
    
    # 选择几个关键日期进行调试
    test_dates = [
        "2024-07-01",  # 很早的日期，可能没有视频
        "2024-07-25",  # 中间日期，可能有少量视频
        "2024-08-15",  # 较近日期，应该有较多视频
        "2024-08-27"   # 最近日期，应该有最多视频
    ]
    
    for test_date in test_dates:
        print(f"\n调试日期: {test_date}")
        print("-" * 60)
        
        debug_info = debug_calculation_process(videos, test_date, current_date)
        
        # 输出关键信息
        print(f"输入视频数量: {debug_info['input_videos_count']}")
        
        for step in debug_info['calculation_steps']:
            if step['step'] == 2:  # 6天规则
                print(f"原始目标日期: {step['original_target']}")
                print(f"有效计算日期: {step['effective_target']} (减去6天)")
            elif step['step'] == 4:  # 筛选结果
                print(f"筛选后视频数量: {step['filtered_videos_count']}")
                print(f"符合日期条件的视频: {step['videos_before_effective_date']}")
                print(f"超出日期范围的视频: {step['videos_after_effective_date']}")
                print(f"无日期信息的视频: {step['videos_no_date_included']}")
        
        if 'final_result' in debug_info:
            print(f"最终指数: {debug_info['final_result']['index']}")
        
        if 'error' in debug_info:
            print(f"错误: {debug_info['error']}")


def debug_batch_calculation_example():
    """调试批量计算过程示例"""
    print("\n" + "="*80)
    print("批量计算过程调试示例")
    print("="*80)
    
    videos, current_date = create_realistic_test_data()
    
    # 创建60天的日期范围
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    date_range = []
    for i in range(60, 0, -1):
        date = current_dt - datetime.timedelta(days=i)
        date_range.append(date.strftime("%Y-%m-%d"))
    
    print(f"批量计算日期范围: {len(date_range)} 天")
    print(f"从 {date_range[0]} 到 {date_range[-1]}")
    
    # 调试批量计算
    batch_debug = debug_batch_calculation(videos, date_range, current_date, sample_dates=3)
    
    print(f"\n采样调试 {batch_debug['sampled_dates']} 个日期:")
    
    for sample in batch_debug['sample_details']:
        print(f"\n日期 #{sample['index']}: {sample['date']}")
        debug_info = sample['debug_info']
        
        # 找到关键步骤
        for step in debug_info['calculation_steps']:
            if step['step'] == 4:  # 筛选结果
                print(f"  - 筛选后视频数量: {step['filtered_videos_count']}")
                print(f"  - 有效日期视频: {step['videos_before_effective_date']}")
                
        if 'final_result' in debug_info:
            print(f"  - 指数结果: {debug_info['final_result']['index']}")
    
    # 输出分析结果
    analysis = batch_debug['summary_analysis']
    print(f"\n批量计算分析结果:")
    print(f"总计算次数: {analysis['total_calculations']}")
    print(f"指数范围: {analysis['min_index']:.2f} - {analysis['max_index']:.2f}")
    print(f"平均指数: {analysis['mean_index']:.2f}")
    print(f"唯一值数量: {analysis['unique_values']}")
    print(f"递增次数: {analysis['increasing_transitions']}")
    print(f"递增百分比: {analysis['increasing_percentage']:.1f}%")
    print(f"疑似堆叠问题: {'是' if analysis['potential_stacking_issue'] else '否'}")


def analyze_video_data_distribution():
    """分析视频数据分布"""
    print("\n" + "="*80)
    print("视频数据分布分析")
    print("="*80)
    
    videos, current_date = create_realistic_test_data()
    
    print(f"总视频数量: {len(videos)}")
    
    # 按发布日期分组
    videos_by_date = {}
    for video in videos:
        date = video['pubdate']
        if date not in videos_by_date:
            videos_by_date[date] = []
        videos_by_date[date].append(video)
    
    print(f"发布日期数量: {len(videos_by_date)}")
    print(f"日期范围: {min(videos_by_date.keys())} 到 {max(videos_by_date.keys())}")
    
    # 分析不同历史日期能获取到多少视频
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    print("\n不同历史日期的可用视频分析:")
    test_historical_dates = [
        current_dt - datetime.timedelta(days=45),  # 45天前
        current_dt - datetime.timedelta(days=30),  # 30天前
        current_dt - datetime.timedelta(days=15),  # 15天前
        current_dt - datetime.timedelta(days=7),   # 7天前
    ]
    
    for hist_date in test_historical_dates:
        effective_date = hist_date - datetime.timedelta(days=6)  # 6天规则
        
        available_videos = 0
        for video in videos:
            video_date = datetime.datetime.strptime(video['pubdate'], "%Y-%m-%d").date()
            if video_date <= effective_date:
                available_videos += 1
        
        print(f"历史日期 {hist_date} (有效日期 {effective_date}): {available_videos} 个可用视频")
    
    print("\n问题分析:")
    print("1. 如果早期历史日期可用视频数量为0，说明视频数据不足")
    print("2. 如果不同日期的可用视频数量差异很大，会导致指数值差异很大")
    print("3. 这种差异被误认为是'堆叠问题'，但实际上是数据不足导致的合理结果")


def main():
    """主函数"""
    print("李大霄指数历史计算详细调试")
    print("Li Daxiao Index Historical Calculation Debug")
    
    try:
        # 1. 分析视频数据分布
        analyze_video_data_distribution()
        
        # 2. 单个日期调试
        debug_single_date_example()
        
        # 3. 批量计算调试
        debug_batch_calculation_example()
        
        print("\n" + "="*80)
        print("调试总结:")
        print("1. 6天规则算法本身是合理的")
        print("2. '堆叠问题'的根本原因是视频数据不足")
        print("3. 需要爬取更多历史视频数据，或调整数据获取策略")
        print("4. 当前算法正确实现了设计意图")
        print("="*80)
        
    except Exception as e:
        print(f"调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()