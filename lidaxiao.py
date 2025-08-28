#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序
Li Daxiao Index Calculation Program

This program crawls Bilibili videos from a specific UP主 (UID: 2137589551),
calculates an index based on views and comments, and generates visualizations.
"""

import datetime
import asyncio

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos
from calculator import calculate_index
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts


async def main():
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    print(f"开始计算李大霄指数...")
    print(f"日期范围: {start_date} 至 {d}")
    
    try:
        # 爬取数据
        print("正在爬取视频数据...")
        videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d)
        print(f"获取到 {len(videos)} 个视频")
        
        # 计算指数
        print("正在计算指数...")
        index_value = calculate_index(videos)
        print(f"李大霄指数: {index_value:.2f}")
        
        # 保存数据
        print("正在保存数据...")
        save_all_data(d, index_value)
        
        # 生成可视化图表
        print("正在生成图表...")
        history_data = load_history_data()
        generate_all_charts(videos, d, index_value, history_data)
        
        print("完成！生成的文件:")
        print(f"- 单日数据: {d}.json")
        print(f"- 历史数据: history.json")
        print(f"- 历史趋势图: index_history_{d.replace('-', '')}.png")
        print(f"- 单日构成图: index_stack_{d.replace('-', '')}.png")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        print("请检查网络连接和依赖库安装情况")


if __name__ == "__main__":
    asyncio.run(main())