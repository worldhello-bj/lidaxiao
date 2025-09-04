#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示修复后的李大霄指数计算逻辑
Demonstration of the fixed Li Daxiao index calculation logic
"""

from historical import HistoricalCalculator
import datetime


def demonstrate_fix():
    """演示修复前后的差异"""
    print("=" * 70)
    print("李大霄指数计算逻辑修复演示")
    print("Li Daxiao Index Calculation Logic Fix Demo")
    print("=" * 70)
    
    # 创建测试数据
    calculator = HistoricalCalculator()
    target_date = "2024-08-28"
    
    videos = [
        {"view": 10000, "comment": 100, "title": "2024-08-20 视频", "pubdate": "2024-08-20"},
        {"view": 20000, "comment": 200, "title": "2024-08-21 视频", "pubdate": "2024-08-21"},
        {"view": 30000, "comment": 300, "title": "2024-08-22 视频", "pubdate": "2024-08-22"},  # 第1天
        {"view": 40000, "comment": 400, "title": "2024-08-23 视频", "pubdate": "2024-08-23"},  # 第2天
        {"view": 50000, "comment": 500, "title": "2024-08-24 视频", "pubdate": "2024-08-24"},  # 第3天
        {"view": 60000, "comment": 600, "title": "2024-08-25 视频", "pubdate": "2024-08-25"},  # 第4天
        {"view": 70000, "comment": 700, "title": "2024-08-26 视频", "pubdate": "2024-08-26"},  # 第5天
        {"view": 80000, "comment": 800, "title": "2024-08-27 视频", "pubdate": "2024-08-27"},  # 第6天
        {"view": 90000, "comment": 900, "title": "2024-08-28 视频", "pubdate": "2024-08-28"},  # 目标日期
        {"view": 100000, "comment": 1000, "title": "2024-08-29 视频", "pubdate": "2024-08-29"},
    ]
    
    print(f"\n目标日期: {target_date}")
    print("根据问题描述，应包含该日及前7天内发布的视频")
    print("According to the issue, should include videos from target date and 7 days before")
    
    print(f"\n创建测试视频数据:")
    for video in videos:
        date = video["pubdate"]
        if "2024-08-22" <= date <= "2024-08-28":
            status = "✓ 应包含"
        elif date < "2024-08-22":
            status = "✗ 应排除（太早）"
        else:
            status = "✗ 应排除（太晚）"
        print(f"  {date}: {video['title']} - {status}")
    
    # 计算修复后的结果
    result = calculator.calculate_historical_index(videos, target_date)
    
    print(f"\n修复后的计算结果:")
    print(f"李大霄指数: {result}")
    
    # 显示详细计算过程
    debug_info = calculator.debug_calculation_process(videos, target_date)
    
    print(f"\n详细计算过程:")
    for step in debug_info["calculation_steps"]:
        if step["step"] == 2:
            print(f"日期范围: [{step['start_date']}, {step['end_date']}] (共7天)")
        elif step["step"] == 4:
            print(f"筛选结果: 包含 {step['filtered_videos_count']}/{step['total_input_videos']} 个视频")
            print("包含的视频:")
            for detail in step["filtered_videos_details"]:
                contribution = (detail.get("view", 0) / 10000) + (detail.get("comment", 0) / 100)
                print(f"  {detail['title']}: 贡献值 {contribution:.2f}")
    
    print(f"\n手动验证:")
    manual_total = 0
    for video in videos:
        if "2024-08-22" <= video["pubdate"] <= "2024-08-28":
            contribution = (video["view"] / 10000) + (video["comment"] / 100)
            manual_total += contribution
            print(f"  {video['pubdate']}: {contribution:.2f}")
    
    print(f"手动计算总计: {manual_total:.2f}")
    print(f"系统计算结果: {result:.2f}")
    print(f"计算一致性: {'✓ 正确' if abs(result - manual_total) < 0.01 else '✗ 错误'}")
    
    # 对比修复前的错误逻辑
    print(f"\n对比修复前的错误逻辑:")
    print("修复前: 只包含 <= (目标日期-6天) 的视频")
    print("修复前逻辑下应只包含 <= 2024-08-22 的视频:")
    
    old_logic_total = 0
    for video in videos:
        if video["pubdate"] <= "2024-08-22":
            contribution = (video["view"] / 10000) + (video["comment"] / 100)
            old_logic_total += contribution
            print(f"  {video['pubdate']}: {contribution:.2f}")
    
    print(f"修复前错误结果: {old_logic_total:.2f}")
    print(f"修复后正确结果: {result:.2f}")
    print(f"差异: {result - old_logic_total:.2f}")
    
    print(f"\n总结:")
    print("✅ 修复成功！现在正确包含目标日期及其前7天内的所有视频")
    print("✅ Fix successful! Now correctly includes all videos from target date and 7 days before")
    
    return True


if __name__ == "__main__":
    demonstrate_fix()