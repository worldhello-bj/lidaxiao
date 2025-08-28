#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块
Configuration Module

This module contains all configuration constants and settings for the Li Daxiao index program.
"""

# UP主 UID (李大霄的B站账号)
BILIBILI_UID = 2137589551

# 时间设置
DEFAULT_DAYS_RANGE = 7  # 默认查询过去7天的数据

# 指数计算相关常数
VIEW_DIVISOR = 10000    # 播放量除数
COMMENT_DIVISOR = 100   # 评论数除数

# 文件名配置
HISTORY_FILE = "history.json"
DAILY_FILE_TEMPLATE = "{date}.json"
HISTORY_CHART_TEMPLATE = "index_history_{date_str}.png"
DAILY_CHART_TEMPLATE = "index_stack_{date_str}.png"

# 图表配置
CHART_FIGSIZE_HISTORY = (10, 6)
CHART_FIGSIZE_DAILY = (10, 6)
CHART_FIGSIZE_NO_VIDEO = (8, 5)

# 视频标题截断长度
TITLE_TRUNCATE_LENGTH = 12