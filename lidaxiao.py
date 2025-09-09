#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 (使用Playwright浏览器自动化)
Li Daxiao Index Calculation Program (Using Playwright Browser Automation)

This program crawls Bilibili videos from a specific UP主 (UID: 2137589551),
calculates an index based on views and comments, and generates visualizations.

Uses Playwright browser automation with strongest anti-detection capabilities.
"""

import datetime
import asyncio
import argparse

from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos, get_troubleshooting,enable_debug
from calculator import calculate_index
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts, generate_historical_charts
from historical import calc_historical_index, calc_batch_historical, HistoricalCalculator



def calc_effective_date(target_date):
    """
    计算显示用的有效目标日期，减去6天（仅用于展示）
    
    注意：历史指数计算现在使用当前数据近似，不再根据此日期过滤视频
    
    :param target_date: 原始目标日期
    :return: 有效目标日期（减去6天后，仅用于显示）
    """
    if isinstance(target_date, str):
        target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        target_dt = target_date
    
    # 计算显示用的有效日期（减去6天）
    effective_target = target_dt - datetime.timedelta(days=6)
    return effective_target


def calc_data_range(effective_target_date, current_date):
    """
    基于有效目标日期动态计算所需的视频数据范围
    使用连续函数而非离散分类
    
    :param effective_target_date: 有效目标日期（已减去6天）
    :param current_date: 当前日期
    :return: 包含数据范围天数和是否扩展爬取的字典
    """
    if isinstance(current_date, str):
        current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    else:
        current_dt = current_date
        
    if isinstance(effective_target_date, str):
        effective_target_dt = datetime.datetime.strptime(effective_target_date, "%Y-%m-%d").date()
    else:
        effective_target_dt = effective_target_date
    
    # 计算有效目标日期距离当前的天数
    days_ago = (current_dt - effective_target_dt).days
    
    # 使用连续函数计算数据范围，而非离散分类
    # 基本原则：目标日期越久远，需要更大的数据范围来确保数据充足
    if days_ago <= 0:
        # 未来日期或当天，使用最小范围
        data_range_days = 30
        fetch_all_pages = False
    elif days_ago <= 45:
        # 近期日期，数据范围随天数线性增长
        data_range_days = max(30, days_ago + 15)
        fetch_all_pages = False
    elif days_ago <= 120:
        # 中期日期，需要更多数据和扩展爬取
        data_range_days = max(60, int(days_ago * 1.2))
        fetch_all_pages = True
    else:
        # 远期日期，使用最大范围确保数据充足
        data_range_days = max(180, int(days_ago * 1.5))
        fetch_all_pages = True
    
    # 确保数据范围不超过实际可用天数
    max_available_days = (current_dt - datetime.date(2020, 1, 1)).days  # 假设2020年开始有数据
    data_range_days = min(data_range_days, max_available_days)
    
    return {
        "data_range_days": data_range_days,
        "fetch_all_pages": fetch_all_pages,
        "days_ago": days_ago,
        "effective_target_date": effective_target_dt
    }


def determine_fetch_range(args, current_date):
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
        # 默认过去一周（从今天开始往前推7天）
        earliest_target_date = current_dt - datetime.timedelta(days=6)
    
    # 计算有效目标日期（减去6天）
    effective_target_date = calc_effective_date(earliest_target_date)
    
    # 基于有效目标日期动态计算数据范围
    range_info = calc_data_range(effective_target_date, current_dt)
    data_range_days = range_info["data_range_days"]
    fetch_all_pages = range_info["fetch_all_pages"]
    days_ago = range_info["days_ago"]
    
    # 计算视频数据获取的开始日期
    start_date = (current_dt - datetime.timedelta(days=data_range_days - 1)).strftime("%Y-%m-%d")
    
    print(f"目标历史日期: {earliest_target_date}")
    print(f"有效计算日期: {effective_target_date} (减去6天)")
    print(f"距离当前: {days_ago} 天")
    print(f"视频数据范围: {data_range_days} 天 ({'扩展爬取' if fetch_all_pages else '标准爬取'})")
    
    return {
        "start_date": start_date,
        "end_date": current_date,
        "fetch_all_pages": fetch_all_pages,
        "days_ago": days_ago,
        "effective_target_date": effective_target_date.strftime("%Y-%m-%d"),
        "data_range_days": data_range_days
    }


def validate_video_data(videos, args):
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
        print("- 尝试使用Playwright模式: --mode playwright")
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
    enable_debug()
    parser = argparse.ArgumentParser(description='李大霄指数计算程序 (使用Playwright浏览器自动化)')
    parser.add_argument('--headless', action='store_true', default=None,
                       help='强制使用无头模式 (后台运行浏览器，用于服务器环境)')
    parser.add_argument('--no-headless', action='store_true', default=None,
                       help='强制使用有头模式 (显示浏览器窗口，用于调试和测试)')
    
    # 历史计算功能参数
    parser.add_argument('--historical', action='store_true',
                       help='启用历史指数回推计算模式 (使用当前视频数据作为历史数据近似)')
    parser.add_argument('--target-date', 
                       help='目标历史日期 (YYYY-MM-DD)')
    parser.add_argument('--date-range',
                       help='历史日期范围，格式: start_date,end_date (YYYY-MM-DD,YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 处理headless模式参数
    headless_mode = None
    if args.headless and args.no_headless:
        print("错误: --headless 和 --no-headless 不能同时使用")
        return
    elif args.headless:
        headless_mode = True
    elif args.no_headless:
        headless_mode = False
    # 如果都没有指定，将使用配置文件中的默认值 (headless_mode = None)
    
    # 历史计算模式
    if args.historical:
        await run_historical_mode(args, headless=headless_mode)
        return
    
    # 原有的当前指数计算模式
    await run_current_mode(args, headless=headless_mode)


def validate_dates(args, current_date):
    """
    验证历史日期参数，确保不是未来日期
    
    历史指数计算使用7天窗口，当前日期可以使用（单日数据不完整不影响7天窗口计算）
    
    :param args: 命令行参数
    :param current_date: 当前日期字符串
    :raises ValueError: 如果目标日期是未来日期
    """
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    if args.target_date:
        target_dt = datetime.datetime.strptime(args.target_date, "%Y-%m-%d").date()
        if target_dt > current_dt:
            raise ValueError(f"目标日期 {args.target_date} 不能晚于当前日期 {current_date}")
    
    if args.date_range:
        start_date_str, end_date_str = args.date_range.split(',')
        start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        if start_dt > current_dt:
            raise ValueError(f"开始日期 {start_date_str} 不能晚于当前日期 {current_date}")
        if end_dt > current_dt:
            raise ValueError(f"结束日期 {end_date_str} 不能晚于当前日期 {current_date}")


async def run_historical_mode(args, headless=None):
    """历史指数计算模式 - 使用当前视频数据作为历史数据近似"""
    print("=" * 50)
    print("历史李大霄指数回推计算模式")
    print("使用当前视频数据作为历史数据近似")
    print("=" * 50)
    
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # 验证历史日期参数，防止未来日期
    try:
        validate_dates(args, current_date)
    except ValueError as e:
        print(f"❌ 日期验证失败: {e}")
        print("\n💡 提示:")
        print("- 历史指数计算只能计算过去的日期")
        print("- 请检查目标日期是否正确，确保不是未来日期")
        print("- 日期格式应为 YYYY-MM-DD，例如: 2025-09-05")
        print("- 当前日期可以使用（7天窗口计算不受单日数据不完整影响）")
        return
    
    # 根据目标历史日期动态确定视频获取范围，确保有足够的历史数据
    video_fetch_range = determine_fetch_range(args, current_date)
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
                                  extended_pages=fetch_all_pages, headless=headless)
        print(f"获取到 {len(videos)} 个视频")
        
        # 验证视频数据是否足够
        if not validate_video_data(videos, args):
            return
        
        # 计算当前指数
        current_index = calculate_index(videos)
        print(f"基于当前视频数据的指数: {current_index:.2f}")
        print("说明: 将使用此数据作为历史各日期的近似值")
        
        # 处理不同的历史计算请求
        if args.target_date:
            # 单个日期计算
            await calc_single_date(videos, args, current_date, current_index)
        elif args.date_range:
            # 批量日期计算
            await calc_batch_dates(videos, args, current_date, current_index)
        else:
            # 默认计算过去一周的历史数据
            await calc_default_range(videos, args, current_date, current_index)
            
    except Exception as e:
        print(f"历史计算过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


async def calc_single_date(videos, args, current_date, current_index):
    """计算单个历史日期"""
    target_date = args.target_date
    effective_date = calc_effective_date(target_date)
    
    print(f"\n正在计算 {target_date} 的历史指数...")
    print("方法: 使用当前视频数据作为历史数据近似")
    print(f"李大霄指数计算规则: 基于 {effective_date.strftime('%Y-%m-%d')} (往回倒6天) 的数据")
    
    try:
        historical_index = calc_historical_index(
            videos, target_date, current_date
        )
        
        days_diff = (datetime.datetime.strptime(current_date, "%Y-%m-%d").date() - 
                    datetime.datetime.strptime(target_date, "%Y-%m-%d").date()).days
        
        effective_days_diff = (datetime.datetime.strptime(current_date, "%Y-%m-%d").date() - 
                              effective_date).days
        
        print(f"\n计算结果:")
        print(f"- 显示日期: {target_date} ({days_diff}天前)")
        print(f"- 有效计算日期: {effective_date.strftime('%Y-%m-%d')} ({effective_days_diff}天前)")
        print(f"- 当前指数: {current_index:.2f}")
        print(f"- 历史指数近似值: {historical_index:.2f}")
        print(f"- 说明: 使用当前视频数据作为 {effective_date.strftime('%Y-%m-%d')} 的近似值")
        
        # 将历史数据保存到累积数据中
        from storage import update_history_data
        update_history_data(target_date, historical_index)
        print(f"- 已将历史数据保存到累积数据文件 (基于当前数据近似计算)")
        
        # 生成历史指数图表
        try:
            from storage import load_history_data
            from visualizer import generate_historical_charts
            
            history_data = load_history_data()
            if history_data:
                print("- 正在生成历史趋势图表...")
                generated_files = generate_historical_charts(
                    videos, current_date, 
                    [{"date": target_date, "index": historical_index, "estimated": True}],
                    target_date
                )
                if generated_files:
                    print("- 生成的图表文件:")
                    for file in generated_files:
                        print(f"  * {file}")
                else:
                    print("- 图表生成完成")
            else:
                print("- 跳过图表生成 (无历史数据)")
                
        except Exception as chart_error:
            print(f"- 图表生成失败: {chart_error}")
        
    except Exception as e:
        print(f"计算失败: {e}")


async def calc_batch_dates(videos, args, current_date, current_index):
    """批量计算历史日期"""
    date_range_str = args.date_range
    start_date, end_date = date_range_str.split(',')
    
    print(f"\n正在批量计算 {start_date} 至 {end_date} 的历史指数...")
    print("方法: 使用当前视频数据作为每个历史日期的近似值")
    print("历史指数计算规则: 所有历史日期使用相同的当前数据进行计算")
    
    try:
        calculator = HistoricalCalculator()
        date_list = calculator.generate_date_range(start_date, end_date)
        
        results = calc_batch_historical(
            videos, date_list, current_date
        )
        
        print(f"\n批量计算结果:")
        print(f"{'显示日期':<12} {'有效计算日期':<15} {'历史指数近似值':<15} {'状态'}")
        print("-" * 65)
        
        for result in results:
            display_date = result['date']
            effective_date = calc_effective_date(display_date).strftime("%Y-%m-%d")
            status = "✓ 成功" if "error" not in result else "✗ 失败"
            print(f"{display_date:<12} {effective_date:<15} {result['index']:<15.2f} {status}")
        
        # 保存批量结果到累积历史数据
        from storage import update_history_data
        success_count = 0
        for result in results:
            if "error" not in result:
                update_history_data(result['date'], result['index'])
                success_count += 1
        
        # 生成批量历史趋势图表
        try:
            print("\n正在生成历史趋势图表...")
            from visualizer import plot_historical_estimates, generate_historical_charts
            
            # 准备用于图表生成的数据格式
            chart_data = [{"date": r["date"], "index": r["index"], "estimated": True} 
                         for r in results if "error" not in r]
            
            if chart_data:
                # 生成历史估算趋势图
                filename = plot_historical_estimates(chart_data, current_date, "batch_historical")
                if filename:
                    print(f"✓ 批量历史趋势图已生成: {filename}")
                
                # 尝试生成其他历史图表
                generated_files = generate_historical_charts(
                    videos, current_date, chart_data, 
                    target_date=start_date
                )
                if generated_files:
                    print("✓ 其他历史图表文件:")
                    for file in generated_files:
                        print(f"  * {file}")
            else:
                print("✗ 无有效数据用于图表生成")
                
        except Exception as chart_error:
            print(f"✗ 图表生成失败: {chart_error}")
            import traceback
            traceback.print_exc()
        
        # 同时保存批量结果到单独文件
        filename = f"historical_batch_{start_date}_{end_date}.json"
        import json
        
        # 添加元数据说明历史计算方法
        output_data = {
            "calculation_rule": "历史指数计算规则：使用当前视频数据作为所有历史日期的近似值",
            "explanation": "所有历史日期返回相同的指数值，基于当前可获取的视频数据计算，避免了时间序列中的虚假增长趋势",
            "date_range": f"{start_date} 至 {end_date}",
            "results": results
        }
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n批量结果已保存到: {filename}")
        print(f"已将 {success_count} 条历史数据保存到累积数据文件")
        print(f"注意: 所有历史日期使用相同的当前视频数据进行近似计算")
        
    except Exception as e:
        print(f"批量计算失败: {e}")


async def calc_default_range(videos, args, current_date, current_index):
    """计算默认历史范围(过去一周)"""
    print(f"\n正在计算过去一周的历史指数近似值...")
    print("方法: 使用当前视频数据作为每个历史日期的近似值")
    print("注意: 李大霄指数计算规则为往回倒6天")
    
    try:
        current_dt = datetime.date.today()
        # 计算默认范围：从今天开始往前推7天，但要考虑6天偏移
        raw_end_date = current_dt
        raw_start_date = current_dt - datetime.timedelta(days=6)  # 过去7天
        
        # 应用6天偏移规则：实际计算时每个日期都要减去6天
        effective_end_date = calc_effective_date(raw_end_date)
        effective_start_date = calc_effective_date(raw_start_date)
        
        calculator = HistoricalCalculator()
        # 使用原始日期范围生成日期列表（用户看到的日期）
        date_list = calculator.generate_date_range(
            raw_start_date.strftime("%Y-%m-%d"), 
            raw_end_date.strftime("%Y-%m-%d")
        )
        
        results = calc_batch_historical(
            videos, date_list, current_date
        )
        
        print(f"\n过去一周历史指数近似值:")
        print(f"{'显示日期':<12} {'有效计算日期':<15} {'历史指数近似值':<15} {'说明'}")
        print("-" * 70)
        
        for i, result in enumerate(results):
            display_date = result['date']
            effective_date = calc_effective_date(display_date).strftime("%Y-%m-%d")
            
            if i == len(results) - 1:  # 今天
                description = "当前值"
            else:
                description = "近似值"
            
            print(f"{display_date:<12} {effective_date:<15} {result['index']:<15.2f} {description}")
        
        # 保存批量结果到累积历史数据
        from storage import update_history_data
        success_count = 0
        for result in results:
            if "error" not in result:
                # 使用显示日期保存，但备注这是基于6天前数据计算的
                update_history_data(result['date'], result['index'])
                success_count += 1
        
        # 生成默认历史范围图表
        try:
            print("\n正在生成过去一周历史趋势图表...")
            from visualizer import plot_historical_estimates, generate_historical_charts
            
            # 准备用于图表生成的数据格式
            chart_data = [{"date": r["date"], "index": r["index"], "estimated": True} 
                         for r in results if "error" not in r]
            
            if chart_data:
                # 生成历史估算趋势图
                filename = plot_historical_estimates(chart_data, current_date, "weekly_historical")
                if filename:
                    print(f"✓ 过去一周历史趋势图已生成: {filename}")
                
                # 尝试生成其他历史图表
                generated_files = generate_historical_charts(
                    videos, current_date, chart_data, 
                    target_date=raw_start_date.strftime("%Y-%m-%d")
                )
                if generated_files:
                    print("✓ 其他历史图表文件:")
                    for file in generated_files:
                        print(f"  * {file}")
            else:
                print("✗ 无有效数据用于图表生成")
                
        except Exception as chart_error:
            print(f"✗ 图表生成失败: {chart_error}")
            import traceback
            traceback.print_exc()
        
        # 保存默认结果到单独文件
        filename = f"historical_week_{current_date}.json"
        import json
        
        # 添加元数据说明历史计算方法
        output_data = {
            "calculation_rule": "历史指数计算规则：使用当前视频数据作为所有历史日期的近似值",
            "explanation": "所有历史日期返回相同的指数值，基于当前可获取的视频数据计算，避免了时间序列中的虚假增长趋势",
            "results": results
        }
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n历史数据已保存到: {filename}")
        print(f"已将 {success_count} 条历史数据保存到累积数据文件")
        print(f"注意: 所有历史日期使用相同的当前视频数据进行近似计算")
        
    except Exception as e:
        print(f"默认历史计算失败: {e}")


async def run_current_mode(args, headless=None):
    """原有的当前指数计算模式"""
    
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    print(f"开始计算李大霄指数 (Playwright浏览器自动化模式)...")
    print(f"日期范围: {start_date} 至 {d}")
    print("💡 提示：如果爬取速度慢，可使用 crawler.enable_fast_mode() 获得4倍速度提升")
    print()
    
    try:
        # 爬取数据
        print("正在爬取视频数据...")
        videos = await fetch_videos(uid=BILIBILI_UID, start_date=start_date, end_date=d, headless=headless)
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
        if "address associated with hostname" in error_msg:
            print("\n这是网络连接问题。解决建议:")
            print("1. 检查网络连接") 
            print("2. 检查防火墙设置")
            print("3. 尝试无头模式: python3 lidaxiao.py --headless")
            print("4. 运行demo.py查看演示功能")
        elif "Playwright" in error_msg:
            print("\n这是Playwright相关问题。解决建议:")
            print("1. 确保Playwright已安装: pip install playwright")
            print("2. 安装浏览器: playwright install chromium")
            print("3. 检查系统兼容性")
            print("4. 运行demo.py查看演示功能")
        
        print(f"\n详细故障排除信息:")
        print(get_troubleshooting())


if __name__ == "__main__":
    asyncio.run(main())