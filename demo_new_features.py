#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新功能演示脚本
Demo script for the new features

演示新的默认计算方式（今日）和详细报告功能
Demonstrates the new default calculation method (today only) and detailed reporting
"""

import sys
import os
import datetime
sys.path.insert(0, '/home/runner/work/lidaxiao/lidaxiao')

from config import DEFAULT_DAYS_RANGE
from calculator import calculate_index, get_video_details

def demo_new_default_calculation():
    """演示新的默认计算方式"""
    print("=" * 80)
    print("🆕 新功能演示：默认计算方式更改")
    print("=" * 80)
    print()
    
    print("📅 计算日期范围变化：")
    print(f"   旧版本：默认计算过去 7 天")
    print(f"   新版本：默认计算今日（{DEFAULT_DAYS_RANGE} 天）")
    print()
    
    # 模拟旧版本的计算逻辑
    today = datetime.date.today()
    old_start_date = (today - datetime.timedelta(days=7-1))  # 旧版本的7天
    new_start_date = (today - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1))  # 新版本的1天
    
    print("📊 日期计算对比：")
    print(f"   今日：{today}")
    print(f"   旧版本开始日期：{old_start_date} (计算 {(today - old_start_date).days + 1} 天)")
    print(f"   新版本开始日期：{new_start_date} (计算 {(today - new_start_date).days + 1} 天)")
    print(f"   ✅ 新版本确实只计算今日：{new_start_date == today}")
    print()

def demo_detailed_calculation():
    """演示详细计算功能"""
    print("=" * 80)
    print("🆕 新功能演示：详细计算日志")
    print("=" * 80)
    print()
    
    # 模拟今日的视频数据
    today_videos = [
        {
            "title": "李大霄：市场底部信号显现，投资机会来了！",
            "view": 82000,
            "comment": 1200,
            "pubdate": datetime.date.today().strftime("%Y-%m-%d")
        },
        {
            "title": "A股三大指数分析：科技股领涨预期",
            "view": 65000,
            "comment": 890,
            "pubdate": datetime.date.today().strftime("%Y-%m-%d")
        },
        {
            "title": "股市早评：关注这些板块机会",
            "view": 48000,
            "comment": 650,
            "pubdate": datetime.date.today().strftime("%Y-%m-%d")
        }
    ]
    
    print(f"📺 今日视频数据示例（{len(today_videos)} 个视频）：")
    print()
    
    total_views = sum(v['view'] for v in today_videos)
    total_comments = sum(v['comment'] for v in today_videos)
    
    print("📈 基础统计：")
    print(f"   总播放量：{total_views:,}")
    print(f"   总评论数：{total_comments:,}")
    print(f"   平均播放量：{total_views // len(today_videos):,}")
    print(f"   平均评论数：{total_comments // len(today_videos):,}")
    print()
    
    # 计算指数
    index_value = calculate_index(today_videos)
    print(f"🎯 李大霄指数：{index_value:.2f}")
    print()
    
    # 详细分解
    print("🔍 详细计算分解：")
    print("   计算公式：李大霄指数 = Σ(播放量/10000 + 评论数/100)")
    print()
    
    detailed_videos = get_video_details(today_videos)
    for i, video in enumerate(detailed_videos, 1):
        view_contrib = video['view'] / 10000
        comment_contrib = video['comment'] / 100
        print(f"   视频 {i}：{video['title'][:50]}")
        print(f"      播放量：{video['view']:,} ÷ 10000 = {view_contrib:.2f}")
        print(f"      评论数：{video['comment']:,} ÷ 100 = {comment_contrib:.2f}")
        print(f"      该视频贡献：{video['contribution']:.2f}")
        print()
    
    print("💡 report.py 使用说明：")
    print("   python3 report.py                    # 生成今日详细报告")
    print("   python3 report.py --date 2024-01-15  # 生成指定日期报告")
    print("   python3 report.py --mode playwright  # 使用指定爬取模式")
    print()

def demo_usage_comparison():
    """演示使用方式对比"""
    print("=" * 80)
    print("📋 使用方式对比")
    print("=" * 80)
    print()
    
    print("🔄 主程序使用（默认行为已更改）：")
    print("   旧版本：python3 lidaxiao.py        # 计算过去7天")
    print("   新版本：python3 lidaxiao.py        # 计算今日")
    print("   如需7天：python3 lidaxiao.py --historical --date-range start,end")
    print()
    
    print("📊 新增报告功能：")
    print("   python3 report.py                  # 今日详细报告")
    print("   python3 report.py --date 2024-01-15 # 历史日期详细报告")
    print()
    
    print("✨ 主要改进：")
    print("   ✅ 默认计算更加精准（今日数据）")
    print("   ✅ 新增详细计算日志功能")
    print("   ✅ 保持向后兼容性")
    print("   ✅ 提供丰富的调试信息")
    print()

if __name__ == "__main__":
    demo_new_default_calculation()
    demo_detailed_calculation()
    demo_usage_comparison()
    
    print("=" * 80)
    print("✅ 新功能演示完成！")
    print("✅ 所有更改已生效，默认计算今日数据，可使用 report.py 生成详细日志")
    print("=" * 80)