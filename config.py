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
DEFAULT_DAYS_RANGE = 1  # 默认查询今日的数据

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

# 浏览器配置 (Playwright模式)
BROWSER_CONFIG = {
    "headless": False,           # 是否使用无头模式 (True: 后台运行, False: 显示浏览器窗口)
    "browser_type": "chromium",  # 浏览器类型: chromium, firefox, webkit
    "timeout": 10,               # 请求超时时间(秒)
    "retry_attempts": 3,         # 重试次数
    "retry_delay": 2,            # 重试延迟(秒)
    "page_delay": 1,             # 页面间隔(秒)
    "fast_mode": False,          # 快速模式：减少等待时间，提高界面响应速度
}

# 快速模式配置 - 显著减少等待时间以提高界面响应速度
FAST_MODE_CONFIG = {
    "page_load_wait": 500,       # 页面加载等待时间(毫秒) - 从2000ms减少到500ms
    "pagination_wait": 300,      # 分页点击等待时间(毫秒) - 从1000ms减少到300ms
    "post_action_wait": 800,     # 操作后等待时间(毫秒) - 从2000ms减少到800ms
    "page_interval_min": 1.0,    # 页面间最小间隔(秒) - 从3-6秒减少到1-2秒
    "page_interval_max": 2.0,    # 页面间最大间隔(秒)
    "failure_wait_min": 0.5,     # 失败后最小等待(秒) - 从2-4秒减少到0.5-1秒
    "failure_wait_max": 1.0,     # 失败后最大等待(秒)
    "network_timeout": 8000,     # 网络超时(毫秒) - 从15000ms减少到8000ms
    "element_timeout": 5000,     # 元素等待超时(毫秒) - 从15000ms减少到5000ms
}

# 历史指数计算配置 (已简化 - 不再使用数学模型)

# 历史计算支持的模式 (现在只使用当前数据近似)
HISTORICAL_APPROXIMATION_MODE = "current_data_as_historical"

# 错误消息配置
ERROR_MESSAGES = {
    "network": "网络连接失败。请检查网络连接和防火墙设置",
    "playwright": "Playwright浏览器启动失败。请确保已正确安装: pip install playwright && playwright install chromium",
}