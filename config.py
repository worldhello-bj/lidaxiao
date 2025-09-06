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
    "performance_mode": "fast",  # 性能模式: fast(快速), balanced(平衡), stable(稳定)
}

# 时间配置 - 性能优化：大幅减少等待时间提升爬取速度
TIMING_CONFIG = {
    "page_load_wait": 200,       # 页面加载等待时间(毫秒) - 减少60%等待时间
    "pagination_wait": 100,      # 分页点击等待时间(毫秒) - 减少67%等待时间
    "post_action_wait": 300,     # 操作后等待时间(毫秒) - 减少62%等待时间
    "page_interval_min": 0.3,    # 页面间最小间隔(秒) - 减少70%页面间隔
    "page_interval_max": 0.6,    # 页面间最大间隔(秒) - 减少70%页面间隔
    "failure_wait_min": 0.2,     # 失败后最小等待(秒) - 快速重试
    "failure_wait_max": 0.5,     # 失败后最大等待(秒) - 快速重试
    "network_timeout": 5000,     # 网络超时(毫秒) - 减少37%网络等待
    "element_timeout": 3000,     # 元素等待超时(毫秒) - 减少40%元素等待
}

# 性能模式配置 - 允许动态调整性能和稳定性的平衡
PERFORMANCE_MODES = {
    "fast": {
        "page_load_wait": 150,
        "pagination_wait": 50, 
        "post_action_wait": 200,
        "page_interval_min": 0.2,
        "page_interval_max": 0.4,
        "network_timeout": 4000,
        "element_timeout": 2000,
    },
    "balanced": {
        "page_load_wait": 200,
        "pagination_wait": 100,
        "post_action_wait": 300,
        "page_interval_min": 0.3,
        "page_interval_max": 0.6,
        "network_timeout": 5000,
        "element_timeout": 3000,
    },
    "stable": {
        "page_load_wait": 300,
        "pagination_wait": 200,
        "post_action_wait": 500,
        "page_interval_min": 0.5,
        "page_interval_max": 1.0,
        "network_timeout": 8000,
        "element_timeout": 5000,
    }
}

# 历史指数计算配置 (已简化 - 不再使用数学模型)

# 历史计算支持的模式 (现在只使用当前数据近似)
HISTORICAL_APPROXIMATION_MODE = "current_data_as_historical"

# 错误消息配置
ERROR_MESSAGES = {
    "network": "网络连接失败。请检查网络连接和防火墙设置",
    "playwright": "Playwright浏览器启动失败。请确保已正确安装: pip install playwright && playwright install chromium",
}

def apply_performance_mode(mode="balanced"):
    """应用性能模式配置
    
    Args:
        mode: 性能模式 - fast(快速), balanced(平衡), stable(稳定)
    """
    global TIMING_CONFIG
    if mode in PERFORMANCE_MODES:
        TIMING_CONFIG.update(PERFORMANCE_MODES[mode])
        print(f"已切换到 {mode} 性能模式")
        return True
    else:
        print(f"未知性能模式: {mode}，可用模式: {list(PERFORMANCE_MODES.keys())}")
        return False