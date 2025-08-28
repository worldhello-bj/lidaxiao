# 历史李大霄指数回推计算模块文档
# Historical Li Daxiao Index Calculation Module Documentation

## 概述 / Overview

历史李大霄指数回推计算模块提供了使用当前视频数据作为历史数据近似值的功能。该模块通过将当前获取的视频播放量、评论数等数据作为指定历史日期的近似值，从而计算出相应的历史李大霄指数。

The Historical Li Daxiao Index Calculation Module provides functionality to approximate historical index values using current video data. This module treats current video view counts, comments, and other statistics as approximations for specified historical dates to calculate corresponding historical Li Daxiao indices.

## 核心理念 / Core Concept

### 数据近似原理 / Data Approximation Principle

本模块的核心思想是：
- **使用当前视频数据**：获取当前时点的视频播放量、评论数等统计数据
- **作为历史数据近似**：将这些当前数据作为指定历史日期的近似值
- **计算历史指数**：基于这些近似的历史数据计算出相应日期的李大霄指数
- **累积数据存储**：将计算结果保存到累积历史数据文件中

The core idea of this module is:
- **Use current video data**: Fetch current video view counts, comments, and other statistics
- **As historical approximations**: Treat this current data as approximations for specified historical dates
- **Calculate historical indices**: Calculate Li Daxiao indices for those dates based on the approximated data
- **Accumulate data storage**: Save results to cumulative historical data files

### 实际应用场景 / Practical Use Cases

这种方法特别适用于：
1. **启动历史数据收集**：为新建立的监控系统快速建立历史数据基线
2. **数据补充**：填补历史数据收集中的空缺日期
3. **趋势分析准备**：为后续的趋势分析提供数据基础
4. **长期数据积累**：随着爬虫每日运行，逐步建立完整的历史数据集

This approach is particularly suitable for:
1. **Bootstrap historical data collection**: Quickly establish historical baselines for newly set up monitoring systems
2. **Data gap filling**: Fill missing dates in historical data collection
3. **Trend analysis preparation**: Provide data foundation for subsequent trend analysis  
4. **Long-term data accumulation**: Gradually build comprehensive historical datasets as crawlers run daily

## 核心功能 / Core Features

### 1. 历史数据近似计算 / Historical Data Approximation Calculation

#### 基本原理 (Basic Principle)
- **输入**: 当前获取的视频数据（播放量、评论数等）
- **处理**: 将当前数据作为指定历史日期的近似值
- **输出**: 基于近似数据计算的历史李大霄指数
- **存储**: 将结果保存到累积历史数据文件中

#### 适用场景 (Use Cases)
- 建立历史数据基线
- 填补历史数据空缺
- 长期数据收集的启动阶段
- 趋势分析的数据准备

### 2. 计算功能 / Calculation Functions

#### 单日期计算 (Single Date Calculation)
```python
from historical import calculate_historical_index

# 使用当前视频数据计算2024-08-20的历史指数
historical_index = calculate_historical_index(
    videos=current_videos,           # 当前视频数据
    target_date="2024-08-20",       # 目标历史日期
    current_date="2024-08-28"       # 当前日期(可选)
)
```

#### 批量计算 (Batch Calculation)
```python
from historical import calculate_batch_historical

# 批量计算过去一周的历史指数近似值
date_range = ["2024-08-21", "2024-08-22", "2024-08-23", ...]
results = calculate_batch_historical(
    videos=current_videos,
    date_range=date_range,
    current_date="2024-08-28"
)
```

### 3. 命令行接口 / Command Line Interface

#### 基本用法 (Basic Usage)
```bash
# 启用历史计算模式 - 计算过去一周的历史指数近似值
python3 lidaxiao.py --historical

# 计算特定日期的历史指数近似值
python3 lidaxiao.py --historical --target-date 2024-08-20

# 批量计算日期范围的历史指数近似值
python3 lidaxiao.py --historical --date-range 2024-08-15,2024-08-25
```

#### 参数说明 (Parameter Description)
- `--historical`: 启用历史计算模式（使用当前视频数据作为历史数据近似）
- `--target-date DATE`: 目标历史日期 (YYYY-MM-DD格式)
- `--date-range START,END`: 历史日期范围 (YYYY-MM-DD,YYYY-MM-DD格式)

### 4. 数据存储 / Data Storage

#### 累积历史数据 (Cumulative Historical Data)
- **文件**: `history.json` - 主要的累积历史数据文件
- **更新**: 每次历史计算后自动更新
- **格式**: 按日期排序的历史指数记录
- **作用**: 长期积累，形成完整的历史数据集

#### 单次计算结果文件 (Individual Calculation Result Files)
- **单日历史计算**: `historical_{date}.json`
- **批量计算结果**: `historical_batch_{start}_{end}.json`
- **默认周期数据**: `historical_week_{date}.json`

## 使用示例 / Usage Examples

### 示例1: 计算过去一周历史指数近似值
```bash
# 使用默认参数计算过去一周
python3 lidaxiao.py --historical

# 输出结果:
# ======================================
# 历史李大霄指数回推计算模式
# 使用当前视频数据作为历史数据近似
# ======================================
# 正在获取当前视频数据作为历史数据回推基础...
# 获取到 15 个视频
# 基于当前视频数据的指数: 45.50
# 说明: 将使用此数据作为历史各日期的近似值
# 
# 正在计算过去一周的历史指数近似值...
# 方法: 使用当前视频数据作为每个历史日期的近似值
# 
# 过去一周历史指数近似值:
# 日期           历史指数近似值   说明
# --------------------------------------------------
# 2024-08-22   45.50         近似值
# 2024-08-23   45.50         近似值
# 2024-08-24   45.50         近似值
# 2024-08-25   45.50         近似值
# 2024-08-26   45.50         近似值
# 2024-08-27   45.50         近似值
# 2024-08-28   45.50         当前值
```

### 示例2: 计算特定历史日期
```bash
# 计算特定日期的历史指数近似值
python3 lidaxiao.py --historical --target-date 2024-08-15

# 计算日期范围的历史指数近似值
python3 lidaxiao.py --historical --date-range 2024-08-10,2024-08-20
```

### 示例3: 程序化调用
```python
from historical import HistoricalCalculator
from calculator import calculate_index

# 创建历史计算器
calculator = HistoricalCalculator()

# 模拟视频数据
mock_videos = [
    {"view": 50000, "comment": 1000},
    {"view": 30000, "comment": 500},
]

# 计算当前指数
current_index = calculate_index(mock_videos)
print(f"当前指数: {current_index:.2f}")

# 计算历史指数近似值
hist_index = calculator.calculate_historical_index(
    mock_videos, "2024-08-15", "2024-08-28"
)
print(f"2024-08-15 历史指数近似值: {hist_index:.2f}")

# 批量计算
date_list = calculator.generate_date_range("2024-08-20", "2024-08-28")
results = calculator.calculate_batch_historical(mock_videos, date_list)
for result in results:
    print(f"{result['date']}: {result['index']:.2f} (近似值)")
```

## 输出文件 / Output Files

### JSON数据文件 (JSON Data Files)
1. **累积历史数据**: `history.json` - 主要的历史数据文件，持续累积
2. **单日历史计算**: `historical_{date}.json` - 单次日期计算结果
3. **批量计算结果**: `historical_batch_{start}_{end}.json` - 批量日期范围计算结果
4. **默认周期数据**: `historical_week_{date}.json` - 默认一周计算结果

### 数据格式 (Data Format)
```json
{
  "date": "2024-08-20",
  "index": 45.50,
  "approximated": true,
  "source": "current_data_approximation"
}
```

## 技术实现 / Technical Implementation

### 核心算法 (Core Algorithm)
```python
def calculate_historical_index(videos, target_date, current_date=None):
    """
    使用当前视频数据计算历史指数近似值
    """
    # 1. 验证日期有效性
    validate_dates(target_date, current_date)
    
    # 2. 直接使用当前视频数据计算指数
    historical_index = calculate_index(videos)
    
    # 3. 返回结果作为历史近似值
    return historical_index
```

### 设计原理 (Design Principles)
1. **简单直接**: 不使用复杂的数学模型，直接使用当前数据
2. **数据积累**: 每次计算都保存到累积历史数据中
3. **日期验证**: 确保目标日期不晚于当前日期
4. **批量处理**: 支持一次计算多个历史日期

### 错误处理 (Error Handling)
- 日期格式验证
- 目标日期不能晚于当前日期的验证
- 视频数据有效性检查
- 计算异常捕获

### 扩展性设计 (Extensibility Design)
- 简洁的模块化架构
- 标准化的数据接口
- 可配置的日期范围生成
- 与现有存储系统的无缝集成

## 演示和测试 / Demo and Testing

### 运行演示 (Running Demos)
```bash
# 功能演示
python3 demo_historical.py

# 可视化演示
python3 demo_visualization.py

# 单元测试
python3 test_historical.py
```

### 测试覆盖 (Test Coverage)
- ✅ 历史数据近似计算测试
- ✅ 单日期计算测试
- ✅ 批量计算测试
- ✅ 日期范围生成测试
- ✅ 日期验证测试
- ✅ 数据存储集成测试

## 故障排除 / Troubleshooting

### 常见问题 (Common Issues)

#### 1. 日期格式错误
**错误**: `ValueError: time data '2024/08/20' does not match format '%Y-%m-%d'`
**解决**: 确保日期格式为 `YYYY-MM-DD`

#### 2. 目标日期晚于当前日期
**错误**: `ValueError: 目标日期 2024-08-30 不能晚于当前日期 2024-08-28`
**解决**: 确保目标日期早于或等于当前日期

#### 3. 视频数据为空
**错误**: 计算结果为 0.0
**解决**: 检查视频数据获取是否成功，确保有足够的视频数据

## 最佳实践 / Best Practices

### 1. 数据收集策略
- **定期运行**: 每日运行爬虫，逐步积累真实的历史数据
- **数据验证**: 定期检查累积的历史数据的完整性
- **备份策略**: 定期备份 `history.json` 文件

### 2. 使用建议
- **理解局限性**: 认识到这是基于当前数据的近似，不是真实历史数据
- **趋势观察**: 重点关注长期趋势而非单日绝对值
- **数据补充**: 随着系统长期运行，用真实数据逐步替换近似值

### 3. 结果解释
- **相对参考**: 将结果作为相对参考而非绝对真实值
- **基线建立**: 用于建立分析基线，为后续真实数据收集做准备
- **趋势启发**: 为趋势分析和模式识别提供初始数据点

## 未来发展 / Future Development

### 计划功能 (Planned Features)
- 真实历史数据收集与近似值的智能融合
- 数据质量评估和置信度指标
- 多数据源整合（微博、抖音等平台）
- 自动化的数据验证和清洗功能

### 扩展方向 (Extension Directions)
- 与实际历史数据的对比分析功能
- 数据准确性的持续改进机制
- 跨平台数据源的统一处理
- 历史数据的可视化和分析工具

---

**版本**: v2.0.0 (简化版)  
**更新日期**: 2024-08-28  
**作者**: Li Daxiao Index Team  
**许可**: 遵循项目主许可协议