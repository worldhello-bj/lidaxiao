#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细计算日志输出模块
Detailed Calculation Log Output Module

This module generates comprehensive calculation reports for the Li Daxiao index,
showing detailed calculation steps and intermediate results.
"""

import datetime
import json
import sys
import os
import asyncio
import argparse

# 添加当前目录到路径，确保可以导入其他模块
sys.path.insert(0, os.path.dirname(__file__))

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos
from calculator import calculate_index, get_video_details, calculate_video_contribution
from historical import HistoricalCalculator, debug_calculation_process


def print_separator(title, width=80):
    """打印分隔符"""
    print("=" * width)
    print(f" {title} ".center(width))
    print("=" * width)


def print_subsection(title, width=60):
    """打印子节分隔符"""
    print("-" * width)
    print(f" {title} ")
    print("-" * width)


async def generate_detailed_report(target_date=None):
    """
    生成详细的计算报告
    
    :param target_date: 目标日期，如果为None则使用今天
    """
    if target_date is None:
        target_date = datetime.date.today().strftime("%Y-%m-%d")
    else:
        # 验证日期格式
        try:
            datetime.datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            print(f"错误: 日期格式不正确，应为 YYYY-MM-DD，收到: {target_date}")
            return
    
    print_separator("李大霄指数详细计算报告")
    print(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标日期: {target_date}")
    print(f"爬取模式: Playwright浏览器自动化")
    print(f"默认天数范围: {DEFAULT_DAYS_RANGE}")
    print()
    
    try:
        # 1. 计算数据爬取的日期范围
        target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        start_date = (target_dt - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
        
        print_subsection("第一步: 数据爬取设置")
        print(f"开始日期: {start_date}")
        print(f"结束日期: {target_date}")
        print(f"爬取天数: {DEFAULT_DAYS_RANGE}")
        print(f"UP主UID: {BILIBILI_UID}")
        print()
        
        # 2. 爬取视频数据
        print_subsection("第二步: 视频数据爬取")
        print("正在爬取视频数据...")
        videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=target_date)
        print(f"成功获取 {len(videos)} 个视频")
        print()
        
        # 3. 视频数据概览
        print_subsection("第三步: 视频数据概览")
        if videos:
            total_views = sum(v.get('view', 0) for v in videos)
            total_comments = sum(v.get('comment', 0) for v in videos)
            avg_views = total_views / len(videos) if videos else 0
            avg_comments = total_comments / len(videos) if videos else 0
            
            print(f"视频总数: {len(videos)}")
            print(f"总播放量: {total_views:,}")
            print(f"总评论数: {total_comments:,}")
            print(f"平均播放量: {avg_views:,.0f}")
            print(f"平均评论数: {avg_comments:,.0f}")
            print()
            
            # 显示前10个视频的详细信息
            print("前10个视频详情:")
            for i, video in enumerate(videos[:10]):
                contribution = calculate_video_contribution(video)
                print(f"  {i+1:2d}. {video.get('title', 'Unknown')[:40]:<40} "
                      f"播放: {video.get('view', 0):>8,} "
                      f"评论: {video.get('comment', 0):>6,} "
                      f"贡献: {contribution:>6.2f}")
            
            if len(videos) > 10:
                print(f"  ... 还有 {len(videos) - 10} 个视频")
        else:
            print("未获取到任何视频数据")
        print()
        
        # 4. 指数计算详情
        print_subsection("第四步: 指数计算详情")
        if videos:
            detailed_videos = get_video_details(videos)
            index_value = calculate_index(videos)
            
            print("计算公式: 李大霄指数 = Σ(播放量/10000 + 评论数/100)")
            print(f"最终指数: {index_value:.2f}")
            print()
            
            print("各视频贡献度分解:")
            for i, video in enumerate(detailed_videos):
                view_contribution = video['view'] / 10000
                comment_contribution = video['comment'] / 100
                print(f"  {i+1:2d}. {video.get('title', 'Unknown')[:30]:<30} "
                      f"播放贡献: {view_contribution:>6.2f} "
                      f"评论贡献: {comment_contribution:>6.2f} "
                      f"总贡献: {video['contribution']:>6.2f}")
        else:
            print("无视频数据，指数为 0.00")
        print()
        
        # 5. 如果是历史计算，提供详细的调试信息
        if target_date != datetime.date.today().strftime("%Y-%m-%d"):
            print_subsection("第五步: 历史计算调试信息")
            debug_info = debug_calculation_process(videos, target_date)
            
            print("历史计算详细步骤:")
            for step in debug_info.get('calculation_steps', []):
                step_num = step.get('step', 0)
                description = step.get('description', 'Unknown')
                print(f"  步骤 {step_num}: {description}")
                
                if step_num == 1:  # 日期验证
                    print(f"    目标日期: {step.get('target_date_parsed', 'N/A')}")
                    print(f"    当前日期: {step.get('current_date_parsed', 'N/A')}")
                    print(f"    日期有效: {step.get('date_valid', False)}")
                
                elif step_num == 2:  # 7天规则
                    print(f"    计算范围: {step.get('start_date', 'N/A')} 到 {step.get('end_date', 'N/A')}")
                    print(f"    总天数: {step.get('total_days', 0)}")
                
                elif step_num == 4:  # 视频筛选
                    print(f"    输入视频数: {step.get('total_input_videos', 0)}")
                    print(f"    筛选后数量: {step.get('filtered_videos_count', 0)}")
                
                elif step_num == 5:  # 指数计算
                    print(f"    最终指数: {step.get('total_index', 0.0)}")
                    
            if 'final_result' in debug_info:
                result = debug_info['final_result']
                print(f"\n历史计算最终结果: {result.get('index', 0.0)}")
                print(f"计算成功: {result.get('success', False)}")
        
        # 6. 总结
        print_subsection("计算总结")
        print(f"计算完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据日期范围: {start_date} 至 {target_date}")
        print(f"处理视频数量: {len(videos)}")
        if videos:
            print(f"李大霄指数: {calculate_index(videos):.2f}")
        else:
            print("李大霄指数: 0.00")
        
        print()
        print("报告生成完成！")
        
    except Exception as e:
        print_separator("错误信息")
        print(f"生成报告时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='李大霄指数详细计算报告生成器 (使用Playwright浏览器自动化)')
    parser.add_argument('--date', 
                       help='目标日期 (YYYY-MM-DD)，不指定则使用今天')
    
    args = parser.parse_args()
    
    try:
        await generate_detailed_report(target_date=args.date)
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"执行报告生成时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())