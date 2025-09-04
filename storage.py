#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据存储模块
Data Storage Module

This module handles JSON file operations for saving and loading index data.
"""

import json
import os


def save_daily_data(date, index_value):
    """
    保存单日JSON文件
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    """
    from config import DAILY_FILE_TEMPLATE
    
    filename = DAILY_FILE_TEMPLATE.format(date=date)
    with open(filename, "w", encoding='utf-8') as f:
        json.dump({"date": date, "index": index_value}, f, indent=2, ensure_ascii=False)


def update_history_data(date, index_value):
    """
    更新累积历史JSON文件
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    """
    from config import HISTORY_FILE
    
    history_data = load_history_data()
    
    # 检查是否已存在当日数据，如果存在则更新，否则添加
    updated = False
    for item in history_data:
        if item["date"] == date:
            item["index"] = index_value
            updated = True
            break
    
    if not updated:
        history_data.append({"date": date, "index": index_value})
    
    with open(HISTORY_FILE, "w", encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)


def load_history_data():
    """
    加载历史数据
    :return: 历史数据列表，如果文件不存在则返回空列表
    """
    from config import HISTORY_FILE
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    return []


def save_all_data(date, index_value):
    """
    保存所有数据（单日 + 历史更新）
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    """
    save_daily_data(date, index_value)
    update_history_data(date, index_value)