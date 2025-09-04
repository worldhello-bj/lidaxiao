#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化模块
Data Visualization Module

This module handles chart generation for Li Daxiao index data.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt

# Configure Chinese font support
plt.rcParams['font.sans-serif'] = [ 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_history_trend(history_data, current_date):
    """
    生成历史趋势折线图
    :param history_data: 历史数据列表
    :param current_date: 当前日期 (YYYY-MM-DD)
    """
    from config import CHART_FIGSIZE_HISTORY, HISTORY_CHART_TEMPLATE
    
    dates = [item["date"] for item in history_data]
    indices = [item["index"] for item in history_data]
    
    plt.figure(figsize=CHART_FIGSIZE_HISTORY)
    plt.plot(dates, indices, marker='o', linestyle='-', color='#1f77b4',
             linewidth=2.5, markersize=3, alpha=0.9)
    
    # 找出极值点并标注
    if indices:
        max_index = max(indices)
        min_index = min(indices)
        max_date = dates[indices.index(max_index)]
        min_date = dates[indices.index(min_index)]
        
        # 标记最大值点
        plt.scatter([max_date], [max_index], color='red', s=120, 
                   zorder=6, marker='^', label=f'最大值: {max_index:.1f}')
        plt.annotate(f'{max_index:.1f}', 
                    xy=(max_date, max_index), xytext=(10, 15),
                    textcoords='offset points', fontsize=10, color='red',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1))
        
        # 标记最小值点
        plt.scatter([min_date], [min_index], color='green', s=120, 
                   zorder=6, marker='v', label=f'最小值: {min_index:.1f}')
        plt.annotate(f'{min_index:.1f}', 
                    xy=(min_date, min_index), xytext=(10, -25),
                    textcoords='offset points', fontsize=10, color='green',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', color='green', lw=1))
    
    plt.title(f"李大霄指数历史趋势 (截至 {current_date})", fontsize=14, pad=20)
    plt.xlabel("日期", fontsize=12)
    plt.ylabel("指数值", fontsize=12)
    
    # 改善X轴标签重叠问题
    total_points = len(dates)
    if total_points > 20:
        step = max(1, total_points // 15)
        selected_indices = list(range(0, total_points, step))
        if selected_indices[-1] != total_points - 1:
            selected_indices.append(total_points - 1)
        
        selected_dates = [dates[i] for i in selected_indices]
        plt.xticks(selected_dates, rotation=45, ha='right')
    else:
        plt.xticks(rotation=45, ha='right')
    
    # 改善图例和网格
    if indices and len(set(indices)) > 1:  # Only show legend if there are extreme values marked
        plt.legend(loc='upper left', bbox_to_anchor=(0, 1), framealpha=0.9)
    
    plt.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
    plt.grid(True, alpha=0.2, linestyle=':', linewidth=0.3, which='minor')
    plt.tight_layout()
    
    date_str = current_date.replace('-', '')
    filename = HISTORY_CHART_TEMPLATE.format(date_str=date_str)
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close()


def plot_daily_stack(videos, current_date, total_index):
    """
    生成单日视频贡献堆叠图
    :param videos: 视频列表
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param total_index: 总指数值
    """
    from config import (CHART_FIGSIZE_DAILY, CHART_FIGSIZE_NO_VIDEO, 
                       DAILY_CHART_TEMPLATE, TITLE_TRUNCATE_LENGTH,
                       VIEW_DIVISOR, COMMENT_DIVISOR)
    
    if not videos:
        # 无视频时的特殊处理
        plt.figure(figsize=CHART_FIGSIZE_NO_VIDEO)
        plt.bar(["无视频"], [0], color='gray')
        plt.text(0, 0.1, "指数=0 (无视频贡献)", ha='center')
        plt.title(f"李大霄指数构成 ({current_date})")
        plt.ylabel("贡献值")
    else:
        # 按发布时间倒序排序 (最新视频在堆叠顶层)
        sorted_videos = sorted(
            videos, 
            key=lambda v: v["created"], 
            reverse=True
        )
        titles = [v["title"][:TITLE_TRUNCATE_LENGTH] + "..." 
                 if len(v["title"]) > TITLE_TRUNCATE_LENGTH else v["title"] 
                 for v in sorted_videos]
        contributions = [(v["view"] / VIEW_DIVISOR + v["comment"] / COMMENT_DIVISOR) 
                        for v in sorted_videos]
        
        # 生成堆叠柱状图
        plt.figure(figsize=CHART_FIGSIZE_DAILY)
        bottom = 0
        for title, contribution in zip(titles, contributions):
            plt.bar([current_date], [contribution], bottom=bottom, label=title)
            bottom += contribution
        
        plt.title(f"李大霄指数构成 ({current_date}) | 总指数: {total_index:.2f}")
        plt.ylabel("视频贡献值")
        plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
        plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    date_str = current_date.replace('-', '')
    filename = DAILY_CHART_TEMPLATE.format(date_str=date_str)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


def plot_historical_estimates(historical_data, current_date, model_name="hybrid"):
    """
    生成历史指数估算趋势图
    :param historical_data: 历史估算数据列表 [{"date": "YYYY-MM-DD", "index": float, "estimated": True}]
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param model_name: 使用的模型名称
    """
    from config import CHART_FIGSIZE_HISTORY
    import numpy as np
    
    if not historical_data:
        return
    
    dates = [item["date"] for item in historical_data]
    indices = [item["index"] for item in historical_data]
    
    plt.figure(figsize=CHART_FIGSIZE_HISTORY)
    
    # 绘制历史估算曲线
    plt.plot(dates, indices, marker='o', linestyle='-', color='#1f77b4', 
             linewidth=2.5, markersize=3, alpha=0.9, label=f'历史估算 ({model_name}模型)')
    
    # 找出极值点并标注
    max_index = max(indices)
    min_index = min(indices)
    max_date = dates[indices.index(max_index)]
    min_date = dates[indices.index(min_index)]
    
    # 标记最大值点
    plt.scatter([max_date], [max_index], color='red', s=120, 
               zorder=6, marker='^', label=f'最大值: {max_index:.1f}')
    plt.annotate(f'{max_index:.1f}', 
                xy=(max_date, max_index), xytext=(10, 15),
                textcoords='offset points', fontsize=10, color='red',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='red', lw=1))
    
    # 标记最小值点
    plt.scatter([min_date], [min_index], color='green', s=120, 
               zorder=6, marker='v', label=f'最小值: {min_index:.1f}')
    plt.annotate(f'{min_index:.1f}', 
                xy=(min_date, min_index), xytext=(10, -25),
                textcoords='offset points', fontsize=10, color='green',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='green', lw=1))
    
    # 标记当前日期
    current_index = None
    for item in historical_data:
        if item["date"] == current_date:
            current_index = item["index"]
            break
    
    if current_index:
        plt.scatter([current_date], [current_index], color='orange', s=150, 
                   zorder=5, label='当前日期', marker='*')
    
    plt.title(f"李大霄指数历史回推趋势 (截至 {current_date})", fontsize=14, pad=20)
    plt.xlabel("日期", fontsize=12)
    plt.ylabel("指数值", fontsize=12)
    
    # 改善X轴标签重叠问题 - 智能选择显示的日期标签
    total_points = len(dates)
    if total_points > 20:
        # 计算合适的步长，确保标签不会太密集
        step = max(1, total_points // 15)  # 最多显示15个标签
        selected_indices = list(range(0, total_points, step))
        # 确保包含最后一个点
        if selected_indices[-1] != total_points - 1:
            selected_indices.append(total_points - 1)
        
        selected_dates = [dates[i] for i in selected_indices]
        plt.xticks(selected_dates, rotation=45, ha='right')
    else:
        plt.xticks(rotation=45, ha='right')
    
    # 改善图例位置，避免重叠
    plt.legend(loc='upper left', bbox_to_anchor=(0, 1), framealpha=0.9)
    
    # 改善网格样式
    plt.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
    plt.grid(True, alpha=0.2, linestyle=':', linewidth=0.3, which='minor')
    
    plt.tight_layout()
    
    date_str = current_date.replace('-', '')
    filename = f"historical_estimates_{model_name}_{date_str}.png"
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close()
    
    return filename


def plot_model_comparison(videos, target_date, current_date, models=None):
    """
    生成不同模型的历史估算对比图
    :param videos: 视频数据列表
    :param target_date: 目标历史日期 (YYYY-MM-DD)
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param models: 要比较的模型列表，默认为所有模型
    """
    from config import CHART_FIGSIZE_HISTORY
    from historical import HistoricalCalculator, calculate_batch_historical
    
    if models is None:
        models = ["exponential", "linear", "hybrid"]
    
    # 生成日期范围
    import datetime
    target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range(target_date, current_date)
    
    plt.figure(figsize=CHART_FIGSIZE_HISTORY)
    
    colors = {'exponential': 'blue', 'linear': 'green', 'hybrid': 'orange'}
    model_names = {
        'exponential': '指数衰减模型',
        'linear': '线性增长模型', 
        'hybrid': '混合模型'
    }
    
    for model in models:
        results = calculate_batch_historical(videos, date_list, current_date)
        dates = [r["date"] for r in results]
        indices = [r["index"] for r in results]
        
        plt.plot(dates, indices, marker='o', linestyle='-', 
                color=colors.get(model, 'gray'), 
                linewidth=2, markersize=3, alpha=0.8,
                label=model_names.get(model, model))
    
    plt.title(f"历史指数回推模型对比 ({target_date} 至 {current_date})")
    plt.xlabel("日期")
    plt.ylabel("指数值")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    date_str = current_date.replace('-', '')
    filename = f"model_comparison_{date_str}.png"
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    
    return filename


def plot_combined_trend(actual_history, estimated_history, current_date, 
                       split_date=None, model_name="hybrid"):
    """
    生成实际历史数据和估算数据的组合趋势图
    :param actual_history: 实际历史数据 [{"date": "YYYY-MM-DD", "index": float}]
    :param estimated_history: 估算历史数据 [{"date": "YYYY-MM-DD", "index": float, "estimated": True}]
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param split_date: 实际数据和估算数据的分界日期
    :param model_name: 估算模型名称
    """
    from config import CHART_FIGSIZE_HISTORY
    
    plt.figure(figsize=CHART_FIGSIZE_HISTORY)
    
    all_dates = []
    all_indices = []
    
    # 绘制实际历史数据
    if actual_history:
        actual_dates = [item["date"] for item in actual_history]
        actual_indices = [item["index"] for item in actual_history]
        plt.plot(actual_dates, actual_indices, marker='o', linestyle='-', 
                color='#1f77b4', linewidth=2.5, markersize=3, 
                label='实际历史数据')
        all_dates.extend(actual_dates)
        all_indices.extend(actual_indices)
    
    # 绘制估算历史数据
    if estimated_history:
        est_dates = [item["date"] for item in estimated_history]
        est_indices = [item["index"] for item in estimated_history]
        plt.plot(est_dates, est_indices, marker='s', linestyle='--', 
                color='orange', linewidth=2.5, markersize=3, alpha=0.8,
                label=f'估算数据 ({model_name}模型)')
        all_dates.extend(est_dates)
        all_indices.extend(est_indices)
    
    # 标记全局极值
    if all_indices:
        max_index = max(all_indices)
        min_index = min(all_indices)
        max_date = all_dates[all_indices.index(max_index)]
        min_date = all_dates[all_indices.index(min_index)]
        
        plt.scatter([max_date], [max_index], color='red', s=120, 
                   zorder=6, marker='^', label=f'最大值: {max_index:.1f}')
        plt.scatter([min_date], [min_index], color='green', s=120, 
                   zorder=6, marker='v', label=f'最小值: {min_index:.1f}')
    
    # 添加分界线
    if split_date and actual_history and estimated_history:
        plt.axvline(x=split_date, color='red', linestyle=':', alpha=0.7, 
                   label='实际/估算分界')
    
    plt.title(f"李大霄指数趋势对比 (截至 {current_date})", fontsize=14, pad=20)
    plt.xlabel("日期", fontsize=12)
    plt.ylabel("指数值", fontsize=12)
    
    # 改善X轴标签重叠问题
    total_points = len(set(all_dates))
    if total_points > 20:
        # 从合并的数据中选择显示的日期
        unique_dates = sorted(set(all_dates))
        step = max(1, len(unique_dates) // 15)
        selected_dates = unique_dates[::step]
        if unique_dates[-1] not in selected_dates:
            selected_dates.append(unique_dates[-1])
        plt.xticks(selected_dates, rotation=45, ha='right')
    else:
        plt.xticks(rotation=45, ha='right')
    
    plt.legend(loc='upper left', bbox_to_anchor=(0, 1), framealpha=0.9)
    plt.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
    plt.grid(True, alpha=0.2, linestyle=':', linewidth=0.3, which='minor')
    plt.tight_layout()
    
    date_str = current_date.replace('-', '')
    filename = f"combined_trend_{model_name}_{date_str}.png"
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close()
    
    return filename


def generate_historical_charts(videos, current_date, historical_data, 
                             target_date=None, models=None):
    """
    生成历史计算相关的所有图表
    :param videos: 视频数据列表
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param historical_data: 历史估算数据
    :param target_date: 目标历史日期，用于模型对比
    :param models: 要对比的模型列表
    :return: 生成的文件名列表
    """
    generated_files = []
    
    try:
        # 生成历史估算趋势图
        if historical_data:
            model_name = historical_data[0].get("model", "hybrid") if historical_data else "hybrid"
            filename = plot_historical_estimates(historical_data, current_date, model_name)
            if filename:
                generated_files.append(filename)
        
        # 生成模型对比图
        if target_date and videos:
            filename = plot_model_comparison(videos, target_date, current_date, models)
            if filename:
                generated_files.append(filename)
        
    except Exception as e:
        print(f"生成历史图表时发生错误: {e}")
    
    return generated_files


def generate_all_charts(videos, current_date, total_index, history_data):
    """
    生成所有图表
    :param videos: 视频列表
    :param current_date: 当前日期 (YYYY-MM-DD)
    :param total_index: 总指数值
    :param history_data: 历史数据列表
    """
    plot_history_trend(history_data, current_date)
    plot_daily_stack(videos, current_date, total_index)
