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
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
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
    plt.plot(dates, indices, marker='o', linestyle='-', color='blue')
    plt.title(f"李大霄指数历史趋势 (截至 {current_date})")
    plt.xlabel("日期")
    plt.ylabel("指数值")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    date_str = current_date.replace('-', '')
    filename = HISTORY_CHART_TEMPLATE.format(date_str=date_str)
    plt.savefig(filename)
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