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
from visualizer import generate_all_charts, generate_historical_charts
from historical import calculate_historical_index, calculate_batch_historical, HistoricalCalculator


def determine_video_fetch_range(args, current_date):
    """
    根据历史计算需求动态确定视频获取范围
    
    :param args: 命令行参数
    :param current_date: 当前日期字符串
    :return: 包含开始日期、结束日期和是否启用扩展爬取的字典
    """
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    # 确定最早的目标历史日期
    earliest_target_date = None
    
    if args.target_date:
        earliest_target_date = datetime.datetime.strptime(args.target_date, "%Y-%m-%d").date()
    elif args.date_range:
        start_date_str, _ = args.date_range.split(',')
        earliest_target_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        # 默认过去一周
        earliest_target_date = current_dt - datetime.timedelta(days=6)
    
    # 根据目标日期的远近程度确定视频获取策略
    days_ago = (current_dt - earliest_target_date).days
    
    if days_ago <= 30:  # 最近30天内
        # 使用标准范围：过去30天
        start_date = (current_dt - datetime.timedelta(days=29)).strftime("%Y-%m-%d")
        fetch_all_pages = False
        print(f"目标历史日期在最近30天内，使用标准视频获取策略")
    elif days_ago <= 90:  # 最近90天内
        # 使用扩展范围：过去90天，增加爬取页数
        start_date = (current_dt - datetime.timedelta(days=89)).strftime("%Y-%m-%d")
        fetch_all_pages = True
        print(f"目标历史日期在最近90天内，使用扩展视频获取策略")
    else:  # 90天以前
        # 使用最大范围：过去180天，最大爬取页数
        start_date = (current_dt - datetime.timedelta(days=179)).strftime("%Y-%m-%d")
        fetch_all_pages = True
        print(f"目标历史日期在90天前，使用最大范围视频获取策略")
    
    return {
        "start_date": start_date,
        "end_date": current_date,
        "fetch_all_pages": fetch_all_pages,
        "days_ago": days_ago
    }


def validate_video_data_sufficiency(videos, args):
    """
    验证视频数据是否足够进行历史指数计算
    
    :param videos: 视频数据列表
    :param args: 命令行参数
    :return: 是否有足够数据
    """
    if not videos:
        print("⚠️  错误: 没有获取到任何视频数据！")
        print("可能的原因:")
        print("1. 网络连接问题")
        print("2. Bilibili访问限制")
        print("3. UP主在指定时间范围内没有发布视频")
        print("解决建议:")
        print("- 检查网络连接")
        print("- 尝试使用浏览器模式: --mode browser")
        print("- 稍后重试")
        return False
    
    # 根据不同的历史计算模式设置最小视频数量要求
    if args.target_date:
        min_required = 10  # 单日期计算最少需要10个视频
        context = "单日期历史指数计算"
    elif args.date_range:
        min_required = 20  # 批量计算最少需要20个视频
        context = "批量历史指数计算"
    else:
        min_required = 15  # 默认过去一周计算最少需要15个视频
        context = "默认历史指数计算"
    
    if len(videos) < min_required:
        print(f"⚠️  警告: 视频数据可能不足！")
        print(f"当前获取到 {len(videos)} 个视频，{context}建议至少需要 {min_required} 个视频")
        print("这可能导致历史指数计算不够准确，建议:")
        print("1. 扩大视频获取时间范围")
        print("2. 尝试不同的爬取模式")
        print("3. 检查UP主在相关时间段的视频发布情况")
        
        # 询问用户是否继续
        try:
            user_input = input("是否仍要继续计算? (y/n): ").lower().strip()
            if user_input not in ['y', 'yes', '是', '继续']:
                print("已取消历史指数计算")
                return False
        except (EOFError, KeyboardInterrupt):
            # 在非交互环境中，默认继续执行但给出警告
            print("检测到非交互环境，将继续执行但数据可能不够准确")
            pass
    
    print(f"✓ 视频数据验证通过: {len(videos)} 个视频足够进行{context}")
    return True


async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='李大霄指数计算程序')
    parser.add_argument('--mode', choices=['api', 'browser', 'auto'], default='auto',
                       help='获取模式: api(快速但可能触发412), browser(慢但稳定), auto(自动选择)')
    
    # 历史计算功能参数
    parser.add_argument('--historical', action='store_true',
                       help='启用历史指数回推计算模式 (使用当前视频数据作为历史数据近似)')
    parser.add_argument('--target-date', 
                       help='目标历史日期 (YYYY-MM-DD)')
    parser.add_argument('--date-range',
                       help='历史日期范围，格式: start_date,end_date (YYYY-MM-DD,YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 历史计算模式
    if args.historical:
        await run_historical_mode(args)
        return
    
    # 原有的当前指数计算模式
    await run_current_mode(args)


async def run_historical_mode(args):
    """历史指数计算模式 - 使用当前视频数据作为历史数据近似"""
    print("=" * 50)
    print("历史李大霄指数回推计算模式")
    print("使用当前视频数据作为历史数据近似")
    print("=" * 50)
    
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # 根据目标历史日期动态确定视频获取范围，确保有足够的历史数据
    video_fetch_range = determine_video_fetch_range(args, current_date)
    start_date = video_fetch_range["start_date"]
    end_date = video_fetch_range["end_date"]
    fetch_all_pages = video_fetch_range["fetch_all_pages"]
    
    print(f"视频数据获取范围: {start_date} 至 {end_date}")
    if fetch_all_pages:
        print("启用扩展爬取模式以确保获取足够的历史数据")
    
    try:
        # 获取当前视频数据作为基础
        print("正在获取视频数据作为历史数据回推基础...")
        videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=end_date, 
                                  mode=args.mode, extended_pages=fetch_all_pages)
        print(f"获取到 {len(videos)} 个视频")
        
        # 验证视频数据是否足够
        if not validate_video_data_sufficiency(videos, args):
            return
        
        # 计算当前指数
        current_index = calculate_index(videos)
        print(f"基于当前视频数据的指数: {current_index:.2f}")
        print("说明: 将使用此数据作为历史各日期的近似值")
        
        # 处理不同的历史计算请求
        if args.target_date:
            # 单个日期计算
            await calculate_single_historical_date(videos, args, current_date, current_index)
        elif args.date_range:
            # 批量日期计算
            await calculate_batch_historical_dates(videos, args, current_date, current_index)
        else:
            # 默认计算过去一周的历史数据
            await calculate_default_historical_range(videos, args, current_date, current_index)
            
    except Exception as e:
        print(f"历史计算过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


async def calculate_single_historical_date(videos, args, current_date, current_index):
    """计算单个历史日期"""
    target_date = args.target_date
    
    print(f"\n正在计算 {target_date} 的历史指数...")
    print("方法: 使用当前视频数据作为历史数据近似")
    
    try:
        historical_index = calculate_historical_index(
            videos, target_date, current_date
        )
        
        days_diff = (datetime.datetime.strptime(current_date, "%Y-%m-%d").date() - 
                    datetime.datetime.strptime(target_date, "%Y-%m-%d").date()).days
        
        print(f"\n计算结果:")
        print(f"- 目标日期: {target_date} ({days_diff}天前)")
        print(f"- 当前指数: {current_index:.2f}")
        print(f"- 历史指数近似值: {historical_index:.2f}")
        print(f"- 说明: 使用当前视频数据作为 {target_date} 的近似值")
        
        # 将历史数据保存到累积数据中
        from storage import update_history_data
        update_history_data(target_date, historical_index)
        print(f"- 已将历史数据保存到累积数据文件")
        
    except Exception as e:
        print(f"计算失败: {e}")


async def calculate_batch_historical_dates(videos, args, current_date, current_index):
    """批量计算历史日期"""
    date_range_str = args.date_range
    start_date, end_date = date_range_str.split(',')
    
    print(f"\n正在批量计算 {start_date} 至 {end_date} 的历史指数...")
    print("方法: 使用当前视频数据作为每个历史日期的近似值")
    
    try:
        calculator = HistoricalCalculator()
        date_list = calculator.generate_date_range(start_date, end_date)
        
        results = calculate_batch_historical(
            videos, date_list, current_date
        )
        
        print(f"\n批量计算结果:")
        print(f"{'日期':<12} {'历史指数近似值':<15} {'状态'}")
        print("-" * 40)
        
        for result in results:
            status = "✓ 成功" if "error" not in result else "✗ 失败"
            print(f"{result['date']:<12} {result['index']:<15.2f} {status}")
        
        # 保存批量结果到累积历史数据
        from storage import update_history_data
        success_count = 0
        for result in results:
            if "error" not in result:
                update_history_data(result['date'], result['index'])
                success_count += 1
        
        # 同时保存批量结果到单独文件
        filename = f"historical_batch_{start_date}_{end_date}.json"
        import json
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n批量结果已保存到: {filename}")
        print(f"已将 {success_count} 条历史数据保存到累积数据文件")
        
    except Exception as e:
        print(f"批量计算失败: {e}")


async def calculate_default_historical_range(videos, args, current_date, current_index):
    """计算默认历史范围(过去一周)"""
    print(f"\n正在计算过去一周的历史指数近似值...")
    print("方法: 使用当前视频数据作为每个历史日期的近似值")
    
    try:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=6)  # 过去7天
        
        calculator = HistoricalCalculator()
        date_list = calculator.generate_date_range(
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        results = calculate_batch_historical(
            videos, date_list, current_date
        )
        
        print(f"\n过去一周历史指数近似值:")
        print(f"{'日期':<12} {'历史指数近似值':<15} {'说明'}")
        print("-" * 50)
        
        for i, result in enumerate(results):
            if i == len(results) - 1:  # 今天
                description = "当前值"
            else:
                description = "近似值"
            
            print(f"{result['date']:<12} {result['index']:<15.2f} {description}")
        
        # 保存批量结果到累积历史数据
        from storage import update_history_data
        success_count = 0
        for result in results:
            if "error" not in result:
                update_history_data(result['date'], result['index'])
                success_count += 1
        
        # 保存默认结果到单独文件
        filename = f"historical_week_{current_date}.json"
        import json
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n历史数据已保存到: {filename}")
        print(f"已将 {success_count} 条历史数据保存到累积数据文件")
        
    except Exception as e:
        print(f"默认历史计算失败: {e}")


async def run_current_mode(args):
    """原有的当前指数计算模式"""
    
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