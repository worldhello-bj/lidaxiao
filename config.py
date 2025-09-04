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

# API 请求配置 (用于处理412安全风控错误)
API_REQUEST_CONFIG = {
    "timeout": 10,              # 请求超时时间(秒)
    "retry_attempts": 3,        # 重试次数
    "retry_delay": 2,           # 重试延迟(秒)
    "rate_limit_delay": 1,      # 请求间隔(秒)
    "verify_ssl": True,         # SSL验证
    "trust_env": True,          # 信任环境代理设置
}

# 浏览器配置 (用于Playwright模式)
BROWSER_CONFIG = {
    "headless": False,           # 是否使用无头模式 (True: 后台运行, False: 显示浏览器窗口)
    "browser_type": "chromium", # 浏览器类型: chromium, firefox, webkit
}

# 历史指数计算配置 (已简化 - 不再使用数学模型)

# 历史计算支持的模式 (现在只使用当前数据近似)
HISTORICAL_APPROXIMATION_MODE = "current_data_as_historical"

# 错误消息配置
ERROR_MESSAGES = {
    "412": "触发了Bilibili安全风控策略(412错误)。建议: 1)减少请求频率 2)检查网络环境 3)使用代理",
    "network": "网络连接失败。请检查网络连接和防火墙设置",
}