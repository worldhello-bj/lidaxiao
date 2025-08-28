#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史指数计算功能演示
Historical Index Calculation Demo

This script demonstrates the historical index calculation functionality 
without requiring actual Bilibili API access.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from historical import calculate_historical_index, calculate_batch_historical, HistoricalCalculator
from calculator import calculate_index
import json


def create_mock_videos():
    """创建模拟视频数据"""
    return [
        {
            "aid": 123456789,
            "view": 50000,
            "comment": 1000, 
            "pubdate": "2024-08-25",
            "title": "李大霄：今日股市分析",
            "created": 1724611200
        },
        {
            "aid": 123456790,
            "view": 30000,
            "comment": 500,
            "pubdate": "2024-08-24", 
            "title": "李大霄：市场趋势预测",
            "created": 1724524800
        },
        {
            "aid": 123456791,
            "view": 75000,
            "comment": 1500,
            "pubdate": "2024-08-23",
            "title": "李大霄：投资策略分享", 
            "created": 1724438400
        }
    ]


def demo_basic_calculation():
    """演示基本计算功能"""
    print("=" * 60)
    print("基本历史指数计算演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_index = calculate_index(mock_videos)
    
    print(f"模拟视频数据：{len(mock_videos)} 个视频")
    print(f"当前李大霄指数：{current_index:.2f}")
    print()
    
    # 计算不同历史日期的指数
    historical_dates = ["2024-08-20", "2024-08-15", "2024-08-10", "2024-08-01"]
    current_date = "2024-08-28"
    
    for model in ["exponential", "linear", "hybrid"]:
        print(f"使用 {model} 模型的历史计算结果:")
        print(f"{'日期':<12} {'历史指数':<10} {'天数差':<8} {'变化率'}")
        print("-" * 50)
        
        for date in historical_dates:
            try:
                hist_index = calculate_historical_index(
                    mock_videos, date, current_date, model
                )
                
                import datetime
                days_diff = (datetime.datetime.strptime(current_date, "%Y-%m-%d").date() - 
                           datetime.datetime.strptime(date, "%Y-%m-%d").date()).days
                
                change_rate = ((current_index - hist_index) / hist_index * 100) if hist_index > 0 else 0
                
                print(f"{date:<12} {hist_index:<10.2f} {days_diff:<8} {change_rate:+.1f}%")
                
            except Exception as e:
                print(f"{date:<12} {'错误':<10} {'--':<8} {str(e)}")
        
        print()


def demo_batch_calculation():
    """演示批量计算功能"""
    print("=" * 60)
    print("批量历史指数计算演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    
    # 生成日期范围
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range("2024-08-20", "2024-08-28")
    
    print(f"计算日期范围: 2024-08-20 至 2024-08-28 ({len(date_list)} 天)")
    
    for model in ["exponential", "linear", "hybrid"]:
        print(f"\n{model.upper()} 模型批量计算结果:")
        
        results = calculate_batch_historical(
            mock_videos, date_list, current_date, model
        )
        
        print(f"{'日期':<12} {'指数':<8} {'趋势':<6} {'状态'}")
        print("-" * 40)
        
        for i, result in enumerate(results):
            # 计算趋势
            if i == 0:
                trend = "--"
            else:
                prev_index = results[i-1]['index']
                curr_index = result['index']
                if curr_index > prev_index:
                    trend = "↗ 上升"
                elif curr_index < prev_index:
                    trend = "↘ 下降"
                else:
                    trend = "→ 平稳"
            
            status = "✓" if "error" not in result else "✗"
            print(f"{result['date']:<12} {result['index']:<8.2f} {trend:<6} {status}")
        
        # 保存结果到文件
        filename = f"demo_batch_{model}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {filename}")


def demo_custom_parameters():
    """演示自定义参数功能"""
    print("\n" + "=" * 60)
    print("自定义参数演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    target_date = "2024-08-15"  # 13天前
    
    print(f"目标日期: {target_date} (13天前)")
    print(f"当前指数: {calculate_index(mock_videos):.2f}")
    print()
    
    # 测试不同的衰减率和增长率
    parameters = [
        {"decay_rate": 0.02, "growth_rate": 0.01, "name": "低衰减/低增长"},
        {"decay_rate": 0.05, "growth_rate": 0.02, "name": "默认参数"},
        {"decay_rate": 0.10, "growth_rate": 0.05, "name": "高衰减/高增长"},
    ]
    
    print(f"{'参数设置':<15} {'指数模型':<8} {'线性模型':<8} {'混合模型':<8}")
    print("-" * 50)
    
    for param in parameters:
        exp_result = calculate_historical_index(
            mock_videos, target_date, current_date, "exponential",
            decay_rate=param["decay_rate"], growth_rate=param["growth_rate"]
        )
        
        linear_result = calculate_historical_index(
            mock_videos, target_date, current_date, "linear",
            decay_rate=param["decay_rate"], growth_rate=param["growth_rate"]
        )
        
        hybrid_result = calculate_historical_index(
            mock_videos, target_date, current_date, "hybrid",
            decay_rate=param["decay_rate"], growth_rate=param["growth_rate"]
        )
        
        print(f"{param['name']:<15} {exp_result:<8.2f} {linear_result:<8.2f} {hybrid_result:<8.2f}")


def demo_visualization_data():
    """为可视化准备数据"""
    print("\n" + "=" * 60)
    print("可视化数据准备")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    
    # 生成过去一个月的历史数据
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range("2024-07-28", "2024-08-28")
    
    results = calculate_batch_historical(
        mock_videos, date_list, current_date, "hybrid"
    )
    
    # 保存可视化数据
    viz_data = {
        "title": "李大霄指数历史趋势 (演示数据)",
        "current_date": current_date,
        "model": "hybrid",
        "current_index": calculate_index(mock_videos),
        "historical_data": results
    }
    
    filename = "demo_visualization_data.json"
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(viz_data, f, indent=2, ensure_ascii=False)
    
    print(f"可视化数据已生成: {filename}")
    print(f"数据点数量: {len(results)}")
    print(f"日期范围: {date_list[0]} 至 {date_list[-1]}")
    
    # 显示趋势概要
    min_index = min(r['index'] for r in results)
    max_index = max(r['index'] for r in results)
    avg_index = sum(r['index'] for r in results) / len(results)
    
    print(f"指数统计:")
    print(f"- 最小值: {min_index:.2f}")
    print(f"- 最大值: {max_index:.2f}")
    print(f"- 平均值: {avg_index:.2f}")


def main():
    """主演示函数"""
    print("🎯 李大霄指数历史回推计算功能演示")
    print("使用模拟数据，无需实际网络请求\n")
    
    try:
        demo_basic_calculation()
        demo_batch_calculation() 
        demo_custom_parameters()
        demo_visualization_data()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("=" * 60)
        print("功能特性总结:")
        print("✓ 支持指数衰减、线性增长、混合三种模型")
        print("✓ 支持单个日期和批量日期计算")
        print("✓ 支持自定义衰减率和增长率参数")
        print("✓ 支持结果导出为JSON格式")
        print("✓ 支持趋势分析和可视化数据准备")
        print("\n生成的文件:")
        print("- demo_batch_exponential.json")
        print("- demo_batch_linear.json") 
        print("- demo_batch_hybrid.json")
        print("- demo_visualization_data.json")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)