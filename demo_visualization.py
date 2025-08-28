#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史指数可视化功能演示
Historical Index Visualization Demo

This script demonstrates the historical index visualization functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from historical import calculate_batch_historical, HistoricalCalculator
from visualizer import plot_historical_estimates, plot_model_comparison, plot_combined_trend
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


def demo_historical_trend_chart():
    """演示历史趋势图表生成"""
    print("=" * 60)
    print("历史趋势图表生成演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    
    # 生成过去两周的历史数据
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range("2024-08-14", "2024-08-28")
    
    # 使用混合模型计算历史数据
    results = calculate_batch_historical(
        mock_videos, date_list, current_date, "hybrid"
    )
    
    print(f"生成 {len(results)} 个数据点的历史趋势图...")
    filename = plot_historical_estimates(results, current_date, "hybrid")
    print(f"✓ 历史趋势图已保存: {filename}")
    
    return results


def demo_model_comparison_chart():
    """演示模型对比图表生成"""
    print("\n" + "=" * 60)
    print("模型对比图表生成演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    target_date = "2024-08-20"
    
    print(f"生成从 {target_date} 到 {current_date} 的模型对比图...")
    filename = plot_model_comparison(mock_videos, target_date, current_date)
    print(f"✓ 模型对比图已保存: {filename}")
    
    # 生成仅指数模型和线性模型的对比
    filename2 = plot_model_comparison(
        mock_videos, target_date, current_date, 
        models=["exponential", "linear"]
    )
    print(f"✓ 双模型对比图已保存: {filename2}")


def demo_combined_trend_chart():
    """演示实际数据与估算数据组合图表"""
    print("\n" + "=" * 60)
    print("组合趋势图表生成演示")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    
    # 模拟一些实际历史数据
    actual_history = [
        {"date": "2024-08-20", "index": 35.2},
        {"date": "2024-08-21", "index": 36.8},
        {"date": "2024-08-22", "index": 38.1},
        {"date": "2024-08-23", "index": 39.5},
    ]
    
    # 生成估算数据
    calculator = HistoricalCalculator()
    est_dates = calculator.generate_date_range("2024-08-24", "2024-08-28")
    estimated_history = calculate_batch_historical(
        mock_videos, est_dates, current_date, "hybrid"
    )
    
    print(f"实际数据点: {len(actual_history)} 个")
    print(f"估算数据点: {len(estimated_history)} 个")
    
    filename = plot_combined_trend(
        actual_history, estimated_history, current_date, 
        split_date="2024-08-23", model_name="hybrid"
    )
    print(f"✓ 组合趋势图已保存: {filename}")


def demo_visualization_integration():
    """演示与主程序的集成"""
    print("\n" + "=" * 60)
    print("可视化功能集成演示")
    print("=" * 60)
    
    from visualizer import generate_historical_charts
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    target_date = "2024-08-15"
    
    # 生成历史数据
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range(target_date, current_date)
    
    results = calculate_batch_historical(
        mock_videos, date_list, current_date, "exponential"
    )
    
    print(f"使用集成函数生成历史图表...")
    chart_files = generate_historical_charts(
        mock_videos, current_date, results, target_date=target_date
    )
    
    print(f"✓ 生成了 {len(chart_files)} 个图表文件:")
    for i, chart_file in enumerate(chart_files, 1):
        print(f"  {i}. {chart_file}")


def create_sample_data_for_testing():
    """创建用于测试的样本数据文件"""
    print("\n" + "=" * 60)
    print("创建测试样本数据")
    print("=" * 60)
    
    mock_videos = create_mock_videos()
    current_date = "2024-08-28"
    
    # 生成一个月的历史数据
    calculator = HistoricalCalculator()
    date_list = calculator.generate_date_range("2024-07-28", "2024-08-28")
    
    # 生成三种模型的数据
    models_data = {}
    for model in ["exponential", "linear", "hybrid"]:
        results = calculate_batch_historical(
            mock_videos, date_list, current_date, model
        )
        models_data[model] = results
    
    # 保存综合测试数据
    test_data = {
        "meta": {
            "description": "李大霄指数历史回推计算测试数据",
            "current_date": current_date,
            "date_range": f"{date_list[0]} 至 {date_list[-1]}",
            "data_points": len(date_list),
            "current_index": calculate_index(mock_videos),
            "mock_videos": len(mock_videos)
        },
        "models": models_data,
        "videos": mock_videos
    }
    
    filename = "historical_test_data.json"
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 测试数据已保存: {filename}")
    print(f"  - 数据点数量: {len(date_list)}")
    print(f"  - 模型数量: {len(models_data)}")
    print(f"  - 当前指数: {test_data['meta']['current_index']:.2f}")


def main():
    """主演示函数"""
    print("📊 李大霄指数历史回推可视化功能演示")
    print("生成各种图表展示历史数据趋势和模型对比\n")
    
    try:
        # 演示各种可视化功能
        historical_data = demo_historical_trend_chart()
        demo_model_comparison_chart()
        demo_combined_trend_chart()
        demo_visualization_integration()
        create_sample_data_for_testing()
        
        print("\n" + "=" * 60)
        print("🎉 可视化演示完成！")
        print("=" * 60)
        print("生成的图表文件:")
        
        import glob
        chart_files = glob.glob("*.png")
        for i, chart_file in enumerate(sorted(chart_files), 1):
            print(f"  {i}. {chart_file}")
        
        print(f"\n生成的数据文件:")
        json_files = glob.glob("*.json")
        for i, json_file in enumerate(sorted(json_files), 1):
            print(f"  {i}. {json_file}")
        
        print("\n可视化功能特性:")
        print("✓ 历史趋势图 - 显示单个模型的历史估算趋势")
        print("✓ 模型对比图 - 对比不同模型的估算结果")
        print("✓ 组合趋势图 - 结合实际数据和估算数据")
        print("✓ 集成接口 - 与主程序无缝集成")
        print("✓ 自定义参数 - 支持灵活的参数配置")
        
    except Exception as e:
        print(f"可视化演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)