#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史李大霄指数回推计算模块
Historical Li Daxiao Index Calculation Module

This module implements historical index calculation using current video data
as approximations for historical periods. All historical dates return the same
index value based on the current video portfolio, avoiding artificial growth
trends that could occur from date-based filtering.
"""

import datetime
from typing import List, Dict, Optional


class HistoricalCalculator:
    """
    历史指数计算器
    Historical index calculator using current video data as historical approximations
    """
    
    def __init__(self):
        """
        初始化历史计算器
        """
        pass
    
    def calculate_historical_index(self, videos: List[Dict], target_date: str,
                                 current_date: Optional[str] = None) -> float:
        """
        计算指定历史日期的李大霄指数
        使用当前视频数据作为历史数据近似
        
        :param videos: 当前视频数据列表
        :param target_date: 目标历史日期 (YYYY-MM-DD)
        :param current_date: 当前日期 (YYYY-MM-DD)，默认为今天 (用于验证)
        :return: 基于当前数据近似的历史指数值
        """
        from calculator import calculate_index
        
        if current_date is None:
            current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # 验证目标日期不能晚于当前日期
        current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
        target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        
        if target_dt > current_dt:
            raise ValueError(f"目标日期 {target_date} 不能晚于当前日期 {current_date}")
        
        # 历史数据近似模式：使用所有当前视频数据作为历史近似
        # 这确保所有历史日期返回相同的指数值，消除错误堆叠问题
        return calculate_index(videos)
    
    def calculate_batch_historical(self, videos: List[Dict], 
                                 date_range: List[str],
                                 current_date: Optional[str] = None) -> List[Dict]:
        """
        批量计算历史时间序列的指数值
        使用当前视频数据作为所有历史日期的近似值
        
        :param videos: 当前视频数据列表
        :param date_range: 目标日期列表 (YYYY-MM-DD)
        :param current_date: 当前日期 (YYYY-MM-DD)，默认为今天
        :return: 历史数据列表 [{"date": "YYYY-MM-DD", "index": float, "approximated": true}]
        """
        results = []
        
        for date in date_range:
            try:
                historical_index = self.calculate_historical_index(
                    videos, date, current_date
                )
                results.append({
                    "date": date,
                    "index": round(historical_index, 2),
                    "approximated": True,
                    "source": "current_data_approximation"
                })
            except Exception as e:
                results.append({
                    "date": date,
                    "index": 0.0,
                    "approximated": True,
                    "source": "current_data_approximation",
                    "error": str(e)
                })
        
        return results
    
    def generate_date_range(self, start_date: str, end_date: str) -> List[str]:
        """
        生成日期范围列表
        
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :return: 日期列表
        """
        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        dates = []
        current_dt = start_dt
        while current_dt <= end_dt:
            dates.append(current_dt.strftime("%Y-%m-%d"))
            current_dt += datetime.timedelta(days=1)
        
        return dates


def create_historical_calculator() -> HistoricalCalculator:
    """
    创建历史计算器实例
    
    :return: 历史计算器实例
    """
    return HistoricalCalculator()


# 便捷函数
def calculate_historical_index(videos: List[Dict], target_date: str,
                             current_date: Optional[str] = None) -> float:
    """
    便捷函数：计算单个历史日期的指数
    使用当前视频数据作为历史数据近似
    
    :param videos: 当前视频数据列表
    :param target_date: 目标历史日期 (YYYY-MM-DD)
    :param current_date: 当前日期，默认为今天
    :return: 基于当前数据近似的历史指数值
    """
    calculator = create_historical_calculator()
    return calculator.calculate_historical_index(videos, target_date, current_date)


def calculate_batch_historical(videos: List[Dict], date_range: List[str],
                              current_date: Optional[str] = None) -> List[Dict]:
    """
    便捷函数：批量计算历史时间序列
    使用当前视频数据作为所有历史日期的近似值
    
    :param videos: 当前视频数据列表
    :param date_range: 目标日期列表
    :param current_date: 当前日期，默认为今天
    :return: 历史数据列表
    """
    calculator = create_historical_calculator()
    return calculator.calculate_batch_historical(videos, date_range, current_date)