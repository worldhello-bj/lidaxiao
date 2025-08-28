# 历史李大霄指数回推计算模块文档
# Historical Li Daxiao Index Calculation Module Documentation

## 概述 / Overview

历史李大霄指数回推计算模块是对现有系统的扩展，提供了基于当前视频数据推算历史指数值的功能。该模块支持多种数学模型、批量计算、自定义参数和可视化展示。

The Historical Li Daxiao Index Calculation Module is an extension to the existing system that provides functionality to estimate historical index values based on current video data. The module supports multiple mathematical models, batch processing, custom parameters, and visualization.

## 核心功能 / Core Features

### 1. 支持的计算模型 / Supported Calculation Models

#### 指数衰减模型 (Exponential Decay Model)
- **公式**: `historical_value = current_value * exp(-decay_rate * days_ago)`
- **适用场景**: 视频数据呈指数增长趋势
- **默认衰减率**: 0.05
- **特点**: 历史值随时间指数递减，适合模拟病毒式传播内容

#### 线性增长模型 (Linear Growth Model)
- **公式**: `historical_value = current_value / (1 + growth_rate * days_ago)`
- **适用场景**: 视频数据呈线性稳定增长
- **默认增长率**: 0.02
- **特点**: 历史值随时间线性递减，适合模拟稳定增长内容

#### 混合模型 (Hybrid Model)
- **公式**: `weighted_combination(exponential_value, linear_value)`
- **适用场景**: 兼顾指数和线性特征的综合估算
- **默认权重**: 指数模型70%，线性模型30%
- **特点**: 平衡两种模型的优势，提供更稳健的估算

### 2. 计算功能 / Calculation Functions

#### 单日期计算 (Single Date Calculation)
```python
from historical import calculate_historical_index

# 计算2024-08-20的历史指数
historical_index = calculate_historical_index(
    videos=current_videos,           # 当前视频数据
    target_date="2024-08-20",       # 目标历史日期
    current_date="2024-08-28",      # 当前日期(可选)
    model="exponential",            # 使用的模型
    decay_rate=0.05,                # 自定义衰减率(可选)
    growth_rate=0.02                # 自定义增长率(可选)
)
```

#### 批量计算 (Batch Calculation)
```python
from historical import calculate_batch_historical

# 批量计算过去一周的历史指数
date_range = ["2024-08-21", "2024-08-22", "2024-08-23", ...]
results = calculate_batch_historical(
    videos=current_videos,
    date_range=date_range,
    current_date="2024-08-28",
    model="hybrid"
)
```

### 3. 命令行接口 / Command Line Interface

#### 基本用法 (Basic Usage)
```bash
# 启用历史计算模式
python3 lidaxiao.py --historical

# 计算特定日期的历史指数
python3 lidaxiao.py --historical --target-date 2024-08-20

# 批量计算日期范围
python3 lidaxiao.py --historical --date-range 2024-08-15,2024-08-25

# 使用不同的计算模型
python3 lidaxiao.py --historical --historical-model linear

# 自定义模型参数
python3 lidaxiao.py --historical --decay-rate 0.08 --growth-rate 0.03
```

#### 完整参数列表 (Complete Parameters)
- `--historical`: 启用历史计算模式
- `--target-date DATE`: 目标历史日期 (YYYY-MM-DD格式)
- `--date-range START,END`: 历史日期范围 (YYYY-MM-DD,YYYY-MM-DD格式)
- `--historical-model MODEL`: 计算模型 (exponential/linear/hybrid)
- `--decay-rate FLOAT`: 指数衰减率 (默认0.05)
- `--growth-rate FLOAT`: 线性增长率 (默认0.02)

### 4. 可视化功能 / Visualization Features

#### 历史趋势图 (Historical Trend Chart)
- 显示单个模型的历史估算趋势
- 文件名: `historical_estimates_{model}_{date}.png`
- 特点: 橙色曲线、当前日期红色标记

#### 模型对比图 (Model Comparison Chart)
- 对比不同模型的估算结果
- 文件名: `model_comparison_{date}.png`
- 特点: 蓝色(指数)、绿色(线性)、橙色(混合)

#### 组合趋势图 (Combined Trend Chart)
- 结合实际历史数据和估算数据
- 文件名: `combined_trend_{model}_{date}.png`
- 特点: 实际数据实线、估算数据虚线、分界线标记

## 使用示例 / Usage Examples

### 示例1: 计算过去一周历史指数
```bash
# 使用默认参数计算过去一周
python3 lidaxiao.py --historical

# 输出结果:
# 历史李大霄指数回推计算模式
# ===============================================
# 正在获取当前视频数据作为回推基础...
# 获取到 15 个视频
# 当前李大霄指数: 45.50
# 
# 正在计算过去一周的历史指数...
# 使用模型: exponential
# 
# 过去一周历史指数:
# 日期           历史指数       趋势
# -----------------------------------
# 2024-08-22   33.71      -
# 2024-08-23   35.44      ↗
# 2024-08-24   37.25      ↗
# 2024-08-25   39.16      ↗
# 2024-08-26   41.17      ↗
# 2024-08-27   43.28      ↗
# 2024-08-28   45.50      ↗
```

### 示例2: 使用不同模型进行对比
```bash
# 使用线性模型计算特定日期
python3 lidaxiao.py --historical --target-date 2024-08-15 --historical-model linear

# 使用混合模型计算日期范围
python3 lidaxiao.py --historical --date-range 2024-08-10,2024-08-20 --historical-model hybrid
```

### 示例3: 程序化调用
```python
from historical import HistoricalCalculator
from calculator import calculate_index

# 创建历史计算器
calculator = HistoricalCalculator(decay_rate=0.08, growth_rate=0.03)

# 模拟视频数据
mock_videos = [
    {"view": 50000, "comment": 1000},
    {"view": 30000, "comment": 500},
]

# 计算当前指数
current_index = calculate_index(mock_videos)
print(f"当前指数: {current_index:.2f}")

# 计算历史指数
hist_index = calculator.calculate_historical_index(
    mock_videos, "2024-08-15", "2024-08-28", "exponential"
)
print(f"历史指数: {hist_index:.2f}")

# 批量计算
date_list = calculator.generate_date_range("2024-08-20", "2024-08-28")
results = calculator.calculate_batch_historical(mock_videos, date_list)
for result in results:
    print(f"{result['date']}: {result['index']:.2f}")
```

## 输出文件 / Output Files

### JSON数据文件 (JSON Data Files)
1. **单日历史计算**: `historical_{date}.json`
2. **批量计算结果**: `historical_batch_{start}_{end}.json`
3. **默认周期数据**: `historical_week_{date}.json`

### 可视化图表 (Visualization Charts)
1. **历史趋势图**: `historical_estimates_{model}_{date}.png`
2. **模型对比图**: `model_comparison_{date}.png`
3. **组合趋势图**: `combined_trend_{model}_{date}.png`

### 数据格式 (Data Format)
```json
{
  "date": "2024-08-20",
  "index": 35.42,
  "model": "exponential",
  "estimated": true
}
```

## 配置参数 / Configuration Parameters

### 默认配置 (Default Configuration)
```python
# config.py中的默认设置
HISTORICAL_DECAY_RATE = 0.05     # 指数衰减率
HISTORICAL_GROWTH_RATE = 0.02    # 线性增长率
HISTORICAL_MODELS = ["exponential", "linear", "hybrid"]  # 支持的模型
```

### 参数调优建议 (Parameter Tuning Recommendations)

#### 衰减率选择 (Decay Rate Selection)
- **0.02-0.05**: 适合病毒式传播内容
- **0.05-0.08**: 适合一般流行内容  
- **0.08-0.12**: 适合快速增长内容

#### 增长率选择 (Growth Rate Selection)
- **0.01-0.02**: 适合稳定增长内容
- **0.02-0.05**: 适合中等增长内容
- **0.05-0.10**: 适合快速增长内容

## 技术实现 / Technical Implementation

### 核心算法 (Core Algorithms)
1. **时间差计算**: `days_ago = (current_date - target_date).days`
2. **指数衰减**: `math.exp(-decay_rate * days_ago)`
3. **线性增长**: `1 / (1 + growth_rate * days_ago)`
4. **混合权重**: `exp_weight * exp_value + (1-exp_weight) * linear_value`

### 错误处理 (Error Handling)
- 日期格式验证
- 参数范围检查
- 数据完整性验证
- 计算异常捕获

### 扩展性设计 (Extensibility Design)
- 模块化架构，易于添加新模型
- 配置文件驱动，支持动态参数调整
- 插件式可视化，支持自定义图表类型
- 数据接口标准化，支持外部数据源集成

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
- ✅ 指数衰减模型测试
- ✅ 线性增长模型测试
- ✅ 混合模型测试
- ✅ 单日期计算测试
- ✅ 批量计算测试
- ✅ 日期范围生成测试
- ✅ 可视化功能测试

## 故障排除 / Troubleshooting

### 常见问题 (Common Issues)

#### 1. 日期格式错误
**错误**: `ValueError: time data '2024/08/20' does not match format '%Y-%m-%d'`
**解决**: 确保日期格式为 `YYYY-MM-DD`

#### 2. 参数超出范围
**错误**: 衰减率或增长率为负数
**解决**: 确保衰减率和增长率为正数

#### 3. 目标日期晚于当前日期
**错误**: `ValueError: 目标日期 2024-08-30 不能晚于当前日期 2024-08-28`
**解决**: 确保目标日期早于或等于当前日期

#### 4. 中文字体显示问题
**警告**: `UserWarning: Glyph missing from font(s)`
**说明**: 这是正常的字体警告，不影响功能，图表仍会正常生成

## 最佳实践 / Best Practices

### 1. 模型选择建议
- **内容类型分析**: 分析视频内容类型选择合适模型
- **历史数据验证**: 如有实际历史数据，用于验证模型准确性
- **多模型对比**: 使用模型对比图选择最合适的模型

### 2. 参数调优策略
- **小样本测试**: 先用少量数据测试参数效果
- **交叉验证**: 使用已知历史数据验证参数准确性
- **分段调优**: 不同时间段可能需要不同参数

### 3. 结果解释原则
- **相对趋势**: 重点关注趋势变化而非绝对数值
- **误差范围**: 认识到估算存在固有误差
- **多重验证**: 结合多种模型和数据源进行验证

## 未来发展 / Future Development

### 计划功能 (Planned Features)
- 机器学习模型集成
- 外部数据源支持(微博、抖音等)
- 实时数据流处理
- 预测精度评估指标
- 多维度影响因子分析

### 扩展方向 (Extension Directions)
- 时间序列分析模型(ARIMA, LSTM)
- 社交媒体情感分析
- 市场事件关联分析
- 个性化模型参数学习

---

**版本**: v1.0.0  
**更新日期**: 2024-08-28  
**作者**: Li Daxiao Index Team  
**许可**: 遵循项目主许可协议