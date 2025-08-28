#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史李大霄指数回推计算模块
Historical Li Daxiao Index Calculation Module

This module implements algorithms to estimate historical index values from current video data.
Supports exponential decay, linear regression, and custom growth models.
"""

import datetime
import math
from typing import List, Dict, Union, Optional


class HistoricalCalculator:
    """
    历史指数计算器
    Historical index calculator with multiple estimation models
    """
    
    def __init__(self, decay_rate: float = 0.05, growth_rate: float = 0.02):
        """
        初始化历史计算器
        :param decay_rate: 指数衰减率 (默认 0.05)
        :param growth_rate: 线性增长率 (默认 0.02)
        """
        self.decay_rate = decay_rate
        self.growth_rate = growth_rate
    
    def exponential_decay_model(self, current_value: float, days_ago: int) -> float:
        """
        指数衰减模型: historical_value = current_value * exp(-decay_rate * days_ago)
        适用于假设视频数据随时间指数增长的场景
        
        :param current_value: 当前值
        :param days_ago: 距离当前的天数
        :return: 估算的历史值
        """
        if days_ago <= 0:
            return current_value
        return current_value * math.exp(-self.decay_rate * days_ago)
    
    def linear_growth_model(self, current_value: float, days_ago: int) -> float:
        """
        线性增长模型: historical_value = current_value / (1 + growth_rate * days_ago)
        适用于假设视频数据线性增长的场景
        
        :param current_value: 当前值
        :param days_ago: 距离当前的天数
        :return: 估算的历史值
        """
        if days_ago <= 0:
            return current_value
        return current_value / (1 + self.growth_rate * days_ago)
    
    def hybrid_model(self, current_value: float, days_ago: int, 
                    exp_weight: float = 0.7) -> float:
        """
        混合模型: 结合指数衰减和线性增长
        
        :param current_value: 当前值
        :param days_ago: 距离当前的天数
        :param exp_weight: 指数模型权重 (0-1)
        :return: 估算的历史值
        """
        if days_ago <= 0:
            return current_value
            
        exp_value = self.exponential_decay_model(current_value, days_ago)
        linear_value = self.linear_growth_model(current_value, days_ago)
        
        return exp_weight * exp_value + (1 - exp_weight) * linear_value
    
    def calculate_historical_index(self, videos: List[Dict], target_date: str,
                                 current_date: Optional[str] = None,
                                 model: str = "exponential") -> float:
        """
        计算指定历史日期的李大霄指数
        
        :param videos: 当前视频数据列表
        :param target_date: 目标历史日期 (YYYY-MM-DD)
        :param current_date: 当前日期 (YYYY-MM-DD)，默认为今天
        :param model: 使用的模型 ("exponential", "linear", "hybrid")
        :return: 估算的历史指数值
        """
        from calculator import calculate_index
        
        if current_date is None:
            current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # 计算当前指数
        current_index = calculate_index(videos)
        
        # 计算天数差
        current_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
        target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        days_ago = (current_dt - target_dt).days
        
        if days_ago < 0:
            raise ValueError(f"目标日期 {target_date} 不能晚于当前日期 {current_date}")
        
        # 根据选择的模型计算历史值
        if model == "exponential":
            return self.exponential_decay_model(current_index, days_ago)
        elif model == "linear":
            return self.linear_growth_model(current_index, days_ago)
        elif model == "hybrid":
            return self.hybrid_model(current_index, days_ago)
        else:
            raise ValueError(f"不支持的模型: {model}. 支持的模型: exponential, linear, hybrid")
    
    def calculate_batch_historical(self, videos: List[Dict], 
                                 date_range: List[str],
                                 current_date: Optional[str] = None,
                                 model: str = "exponential") -> List[Dict]:
        """
        批量计算历史时间序列的指数值
        
        :param videos: 当前视频数据列表
        :param date_range: 目标日期列表 (YYYY-MM-DD)
        :param current_date: 当前日期 (YYYY-MM-DD)，默认为今天
        :param model: 使用的模型 ("exponential", "linear", "hybrid")
        :return: 历史数据列表 [{"date": "YYYY-MM-DD", "index": float}]
        """
        results = []
        
        for date in date_range:
            try:
                historical_index = self.calculate_historical_index(
                    videos, date, current_date, model
                )
                results.append({
                    "date": date,
                    "index": round(historical_index, 2),
                    "model": model,
                    "estimated": True
                })
            except Exception as e:
                results.append({
                    "date": date,
                    "index": 0.0,
                    "model": model,
                    "estimated": True,
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


def create_historical_calculator(decay_rate: Optional[float] = None,
                               growth_rate: Optional[float] = None) -> HistoricalCalculator:
    """
    创建历史计算器实例，使用配置文件中的默认参数
    
    :param decay_rate: 指数衰减率，覆盖默认值
    :param growth_rate: 线性增长率，覆盖默认值
    :return: 历史计算器实例
    """
    from config import HISTORICAL_DECAY_RATE, HISTORICAL_GROWTH_RATE
    
    actual_decay = decay_rate if decay_rate is not None else HISTORICAL_DECAY_RATE
    actual_growth = growth_rate if growth_rate is not None else HISTORICAL_GROWTH_RATE
    
    return HistoricalCalculator(actual_decay, actual_growth)


# 便捷函数
def calculate_historical_index(videos: List[Dict], target_date: str,
                             current_date: Optional[str] = None,
                             model: str = "exponential",
                             decay_rate: Optional[float] = None,
                             growth_rate: Optional[float] = None) -> float:
    """
    便捷函数：计算单个历史日期的指数
    
    :param videos: 当前视频数据列表
    :param target_date: 目标历史日期 (YYYY-MM-DD)
    :param current_date: 当前日期，默认为今天
    :param model: 使用的模型
    :param decay_rate: 自定义衰减率
    :param growth_rate: 自定义增长率
    :return: 估算的历史指数值
    """
    calculator = create_historical_calculator(decay_rate, growth_rate)
    return calculator.calculate_historical_index(videos, target_date, current_date, model)


def calculate_batch_historical(videos: List[Dict], date_range: List[str],
                              current_date: Optional[str] = None,
                              model: str = "exponential",
                              decay_rate: Optional[float] = None,
                              growth_rate: Optional[float] = None) -> List[Dict]:
    """
    便捷函数：批量计算历史时间序列
    
    :param videos: 当前视频数据列表
    :param date_range: 目标日期列表
    :param current_date: 当前日期，默认为今天
    :param model: 使用的模型
    :param decay_rate: 自定义衰减率
    :param growth_rate: 自定义增长率
    :return: 历史数据列表
    """
    calculator = create_historical_calculator(decay_rate, growth_rate)
    return calculator.calculate_batch_historical(videos, date_range, current_date, model)