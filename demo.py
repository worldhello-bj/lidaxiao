#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 - 模拟数据版本
Li Daxiao Index Calculation Program - Mock Data Version

This program demonstrates the Li Daxiao index calculation using mock data
when real API access is not available.
"""

import datetime

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import generate_mock_videos
from calculator import calculate_index, get_video_details
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts


def main():
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    print(f"开始计算李大霄指数...")
    print(f"日期范围: {start_date} 至 {d}")
    print("[注意] 使用模拟数据进行演示")
    
    try:
        # 生成模拟数据
        print("正在生成模拟视频数据...")
        videos = generate_mock_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d)
        print(f"获取到 {len(videos)} 个视频")
        
        # 显示视频信息
        print("\n视频详情:")
        detailed_videos = get_video_details(videos)
        for i, video in enumerate(detailed_videos, 1):
            print(f"  {i}. {video['title'][:30]}...")
            print(f"     播放量: {video['view']:,} | 评论数: {video['comment']:,} | 贡献: {video['contribution']:.2f}")
        
        # 计算指数
        print("\n正在计算指数...")
        index_value = calculate_index(videos)
        print(f"李大霄指数: {index_value:.2f}")
        
        # 保存数据
        print("正在保存数据...")
        save_all_data(d, index_value)
        
        # 生成可视化图表
        print("正在生成图表...")
        history_data = load_history_data()
        generate_all_charts(videos, d, index_value, history_data)
        
        print("\n完成！生成的文件:")
        print(f"- 单日数据: {d}.json")
        print(f"- 历史数据: history.json")
        print(f"- 历史趋势图: index_history_{d.replace('-', '')}.png")
        print(f"- 单日构成图: index_stack_{d.replace('-', '')}.png")
        
    except Exception as e:
        import traceback
        print(f"执行过程中发生错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()


if __name__ == "__main__":
    main()