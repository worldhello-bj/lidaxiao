#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 - 演示版本
Li Daxiao Index Calculation Program - Demo Version

This program demonstrates the Li Daxiao index calculation using real data.
If data cannot be fetched, it will show proper error messages instead of using mock data.
"""

import datetime
import asyncio

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos
from calculator import calculate_index, get_video_details
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts


async def main():
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    print(f"开始计算李大霄指数...")
    print(f"日期范围: {start_date} 至 {d}")
    print("[注意] 使用真实数据进行计算")
    
    try:
        # 获取真实数据 - 尝试使用Playwright模式，失败则回退到browser模式
        print("正在获取视频数据...")
        try:
            videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d, mode="playwright")
            print(f"✅ Playwright模式获取到 {len(videos)} 个视频")
        except Exception as e:
            print(f"⚠️ Playwright模式失败: {e}")
            print("🔄 回退到浏览器模拟模式...")
            videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d, mode="browser")
            print(f"✅ 浏览器模拟模式获取到 {len(videos)} 个视频")
        
        if not videos:
            print("❌ 未获取到任何视频数据")
            print("可能的原因:")
            print("1. 网络连接问题")
            print("2. B站访问限制")
            print("3. 日期范围内没有发布视频")
            print("4. 解析页面结构失败")
            return
        
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
        
        print("\n✅ 完成！生成的文件:")
        print(f"- 单日数据: {d}.json")
        print(f"- 历史数据: history.json")
        print(f"- 历史趋势图: index_history_{d.replace('-', '')}.png")
        print(f"- 单日构成图: index_stack_{d.replace('-', '')}.png")
        
    except Exception as e:
        import traceback
        print(f"❌ 执行过程中发生错误: {e}")
        print("\n建议解决方案:")
        print("1. 检查网络连接")
        print("2. 稍后重试")
        print("3. 使用API配置工具: python3 api_config_tool.py safe")
        print("4. 查看详细错误信息:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())