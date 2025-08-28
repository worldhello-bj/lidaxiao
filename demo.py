#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 - 模拟数据版本
Li Daxiao Index Calculation Program - Mock Data Version

This program demonstrates the Li Daxiao index calculation using mock data
when real API access is not available.
"""

import datetime
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Configure Chinese font support
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
import os
import random


def generate_mock_videos(uid, start_date, end_date):
    """
    生成模拟视频数据（用于演示）
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    mock_videos = []
    
    # 生成一些模拟视频标题
    mock_titles = [
        "李大霄：A股迎来黄金坑，牛市起点来了！",
        "牛市来了！这些股票要涨10倍",
        "熊市已结束，准备抄底了",
        "今天是历史性的一天，A股见底了",
        "婴儿底已现，钻石底不远了",
        "股民们，春天来了！",
        "这是千载难逢的投资机会"
    ]
    
    # 解析日期范围
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # 生成3-8个随机视频
    num_videos = random.randint(3, 8)
    
    for i in range(num_videos):
        # 随机选择发布日期
        random_days = random.randint(0, (end_dt - start_dt).days)
        pub_dt = start_dt + datetime.timedelta(days=random_days)
        
        mock_videos.append({
            "aid": 1000000 + i,
            "view": random.randint(5000, 100000),
            "comment": random.randint(100, 5000),
            "pubdate": pub_dt.strftime("%Y-%m-%d"),
            "title": random.choice(mock_titles),
            "created": int(pub_dt.timestamp())
        })
    
    print(f"[模拟数据] 生成了 {len(mock_videos)} 个视频")
    return mock_videos


def calculate_index(videos):
    """
    计算李大霄指数
    :param videos: 视频列表
    :return: 指数值 (float)
    """
    total = 0.0
    for v in videos:
        # 单个视频指数 = (播放量/10000 + 评论数/100)
        video_index = (v["view"] / 10000) + (v["comment"] / 100)
        total += video_index
    return total  # 无视频时自动返回0.0


def save_data_and_plot(d, videos, index_value):
    """
    保存数据并生成可视化图表
    :param d: 当前日期 (YYYY-MM-DD)
    :param videos: 视频列表
    :param index_value: 计算出的指数值
    """
    # 保存单日JSON文件
    with open(f"{d}.json", "w", encoding='utf-8') as f:
        json.dump({"date": d, "index": index_value}, f, indent=2, ensure_ascii=False)
    
    # 更新累积JSON文件
    history_file = "history.json"
    history_data = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding='utf-8') as f:
            history_data = json.load(f)
    
    # 检查是否已存在当日数据，如果存在则更新，否则添加
    updated = False
    for item in history_data:
        if item["date"] == d:
            item["index"] = index_value
            updated = True
            break
    
    if not updated:
        history_data.append({"date": d, "index": index_value})
    
    with open(history_file, "w", encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    # 生成历史折线图
    _plot_history_index(history_data, d)
    
    # 生成单日堆叠图
    _plot_daily_stack(videos, d, index_value)


def _plot_history_index(history_data, d):
    """生成历史折线图"""
    dates = [item["date"] for item in history_data]
    indices = [item["index"] for item in history_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, indices, marker='o', linestyle='-', color='blue')
    plt.title(f"李大霄指数历史趋势 (截至 {d})")
    plt.xlabel("日期")
    plt.ylabel("指数值")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    date_str = d.replace('-', '')
    plt.savefig(f"index_history_{date_str}.png")
    plt.close()


def _plot_daily_stack(videos, d, total_index):
    """生成单日堆叠图"""
    if not videos:
        # 无视频时的特殊处理
        plt.figure(figsize=(8, 5))
        plt.bar(["无视频"], [0], color='gray')
        plt.text(0, 0.1, "指数=0 (无视频贡献)", ha='center')
        plt.title(f"李大霄指数构成 ({d})")
        plt.ylabel("贡献值")
    else:
        # 按发布时间倒序排序 (最新视频在堆叠顶层)
        sorted_videos = sorted(
            videos, 
            key=lambda v: v["created"], 
            reverse=True
        )
        titles = [v["title"][:12] + "..." if len(v["title"]) > 12 else v["title"] 
                 for v in sorted_videos]
        contributions = [(v["view"] / 10000 + v["comment"] / 100) 
                        for v in sorted_videos]
        
        # 生成堆叠柱状图
        plt.figure(figsize=(10, 6))
        bottom = 0
        for title, contribution in zip(titles, contributions):
            plt.bar([d], [contribution], bottom=bottom, label=title)
            bottom += contribution
        
        plt.title(f"李大霄指数构成 ({d}) | 总指数: {total_index:.2f}")
        plt.ylabel("视频贡献值")
        plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
        plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    date_str = d.replace('-', '')
    plt.savefig(f"index_stack_{date_str}.png", bbox_inches='tight')
    plt.close()


def main():
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    
    print(f"开始计算李大霄指数...")
    print(f"日期范围: {start_date} 至 {d}")
    print("[注意] 使用模拟数据进行演示")
    
    try:
        # 生成模拟数据
        print("正在生成模拟视频数据...")
        videos = generate_mock_videos(uid=2137589551, start_date=start_date, end_date=d)
        print(f"获取到 {len(videos)} 个视频")
        
        # 显示视频信息
        print("\n视频详情:")
        for i, video in enumerate(videos, 1):
            video_index = (video["view"] / 10000) + (video["comment"] / 100)
            print(f"  {i}. {video['title'][:30]}...")
            print(f"     播放量: {video['view']:,} | 评论数: {video['comment']:,} | 贡献: {video_index:.2f}")
        
        # 计算指数
        print("\n正在计算指数...")
        index_value = calculate_index(videos)
        print(f"李大霄指数: {index_value:.2f}")
        
        # 保存数据并生成可视化
        print("正在保存数据并生成图表...")
        save_data_and_plot(d, videos, index_value)
        
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