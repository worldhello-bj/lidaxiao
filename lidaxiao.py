#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 (支持API和浏览器模拟两种模式)
Li Daxiao Index Calculation Program (Supports both API and Browser Simulation modes)

This program crawls Bilibili videos from a specific UP主 (UID: 2137589551),
calculates an index based on views and comments, and generates visualizations.

Supported modes:
- API mode: Fast but may trigger 412 security control errors
- Browser simulation mode: Slower but avoids anti-bot detection
- Auto mode: Tries API first, falls back to browser simulation if needed
"""

import datetime
import asyncio
import argparse

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos, get_api_troubleshooting_info
from calculator import calculate_index
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts


async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='李大霄指数计算程序')
    parser.add_argument('--mode', choices=['api', 'browser', 'auto'], default='auto',
                       help='获取模式: api(快速但可能触发412), browser(慢但稳定), auto(自动选择)')
    args = parser.parse_args()
    
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    mode_descriptions = {
        'api': '快速API模式',
        'browser': '浏览器模拟模式', 
        'auto': '智能自动模式'
    }
    
    print(f"开始计算李大霄指数 ({mode_descriptions[args.mode]})...")
    print(f"日期范围: {start_date} 至 {d}")
    
    try:
        # 爬取数据
        print("正在爬取视频数据...")
        videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d, mode=args.mode)
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
        error_msg = str(e)
        print(f"执行过程中发生错误: {error_msg}")
        
        # 提供针对性的错误处理建议
        if "412" in error_msg or "安全风控" in error_msg:
            print("\n这是Bilibili安全风控错误。解决建议:")
            print("1. 尝试浏览器模拟模式: python3 lidaxiao.py --mode browser")
            print("2. 使用安全配置: python3 api_config_tool.py safe")
            print("3. 等待一段时间后重试")
            print("4. 运行demo.py查看演示功能")
        elif "address associated with hostname" in error_msg:
            print("\n这是网络连接问题。解决建议:")
            print("1. 检查网络连接") 
            print("2. 检查防火墙设置")
            print("3. 尝试浏览器模拟模式: python3 lidaxiao.py --mode browser")
            print("4. 运行demo.py查看演示功能")
        
        print(f"\n详细故障排除信息:")
        print(get_api_troubleshooting_info())


if __name__ == "__main__":
    asyncio.run(main())