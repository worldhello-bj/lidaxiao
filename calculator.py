#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数计算模块
Index Calculation Module

This module handles the calculation of Li Daxiao index based on video data.
"""


def calculate_index(videos):
    """
    计算李大霄指数
    :param videos: 视频列表
    :return: 指数值 (float)
    """
    from config import VIEW_DIVISOR, COMMENT_DIVISOR
    
    total = 0.0
    for v in videos:
        # 单个视频指数 = (播放量/10000 + 评论数/100)
        video_index = (v["view"] / VIEW_DIVISOR) + (v["comment"] / COMMENT_DIVISOR)
        total += video_index
    return total  # 无视频时自动返回0.0


def calculate_video_contribution(video):
    """
    计算单个视频的指数贡献
    :param video: 单个视频数据
    :return: 该视频的指数贡献值 (float)
    """
    from config import VIEW_DIVISOR, COMMENT_DIVISOR
    
    return (video["view"] / VIEW_DIVISOR) + (video["comment"] / COMMENT_DIVISOR)


def get_video_details(videos):
    """
    获取视频详细信息，包括每个视频的贡献值
    :param videos: 视频列表
    :return: 包含贡献值的视频详细信息列表
    """
    detailed_videos = []
    for video in videos:
        contribution = calculate_video_contribution(video)
        detailed_videos.append({
            **video,
            "contribution": contribution
        })
    return detailed_videos