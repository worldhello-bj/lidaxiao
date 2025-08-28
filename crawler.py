#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据爬取模块
Video Crawling Module

This module handles fetching video data from Bilibili API and generating mock data for testing.
"""

from bilibili_api import user
import datetime
import random


async def fetch_videos(uid, start_date, end_date):
    """
    获取指定日期范围内的视频数据
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    u = user.User(uid)
    all_videos = []
    pn = 1
    
    while True:
        # 调用B站API获取分页视频列表
        res = await u.get_videos(pn=pn, order=user.VideoOrder.PUBDATE)
        if not res["list"]["vlist"]:
            break
            
        for video_info in res["list"]["vlist"]:
            pubdate = datetime.datetime.fromtimestamp(video_info["created"]).strftime("%Y-%m-%d")
            # 仅保留指定日期范围内的视频
            if start_date <= pubdate <= end_date:
                all_videos.append({
                    "aid": video_info["aid"],
                    "view": int(video_info["play"]),
                    "comment": int(video_info["comment"]),
                    "pubdate": pubdate,
                    "title": video_info["title"],
                    "created": video_info["created"]
                })
        pn += 1
        
    return all_videos


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