# Li Daxiao Index Calculator / 李大霄指数计算程序

This project implements a Li Daxiao Index calculation program that crawls Bilibili videos, calculates an index based on views and comments, and generates visualizations. **The program supports both API mode and Browser Simulation mode to handle different network environments.**

这个项目实现了李大霄指数计算程序，爬取Bilibili视频，基于播放量和评论数计算指数，并生成可视化图表。**程序同时支持API模式和浏览器模拟模式以适应不同的网络环境。**

## Supported Modes / 支持的模式

### 🚀 API Mode (快速模式)
- **Speed**: Fast / 速度快
- **Accuracy**: High / 准确性高  
- **Risk**: May trigger 412 errors / 可能触发412错误
- **Use case**: Development and testing / 开发测试环境
- **Documentation**: [API Mode Guide](API_MODE_GUIDE.md) / [API模式指南](API_MODE_GUIDE.md)

### 🛡️ Browser Simulation Mode (稳定模式)  
- **Speed**: Medium / 速度中等
- **Accuracy**: Medium-High / 准确性中-高
- **Risk**: Low security control trigger / 低风控概率
- **Use case**: Production environments / 生产环境
- **Documentation**: [Browser Mode Guide](BROWSER_MODE_GUIDE.md) / [浏览器模式指南](BROWSER_MODE_GUIDE.md)

### 🔄 Historical Calculation Mode (历史回推模式)
- **Speed**: Medium / 速度中等
- **Purpose**: Estimate historical index values from current data / 从当前数据估算历史指数值
- **Models**: Exponential decay, Linear growth, Hybrid / 指数衰减、线性增长、混合模型
- **Use case**: Historical analysis and trend prediction / 历史分析和趋势预测
- **Documentation**: [Historical Calculation Guide](HISTORICAL_GUIDE.md) / [历史计算指南](HISTORICAL_GUIDE.md)

## Features / 功能特性

- **Dual Mode Support**: Choose between API and browser simulation modes / 双模式支持：API模式和浏览器模拟模式
- **Video Crawling**: Fetches videos from a specific Bilibili UP主 (UID: 2137589551) for the past 7 days / 视频爬取：获取指定UP主近7天视频
- **Index Calculation**: Calculates Li Daxiao Index using formula: `(views/10000 + comments/100)` for each video / 指数计算：播放量/10000 + 评论数/100
- **Data Storage**: Saves daily and historical data in JSON format / 数据存储：保存日史数据为JSON格式
- **Visualization**: Generates two types of charts / 可视化：生成两种类型图表
  - Historical trend line chart / 历史趋势线图
  - Daily contribution stack chart / 日贡献堆叠图
- **Security Control Avoidance**: Browser simulation mode avoids 412 errors / 安全风控规避：浏览器模拟模式避免412错误

## Installation / 安装

1. Clone the repository:
```bash
git clone <repository-url>
cd lidaxiao
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Quick Start / 快速开始
```bash
# Auto mode (recommended) / 自动模式（推荐）
python3 lidaxiao.py

# API mode (fast but may encounter 412 errors) / API模式（快但可能遇到412错误）
python3 lidaxiao.py --mode api

# Browser simulation mode (stable, avoids security control) / 浏览器模拟模式（稳定，避免安全风控）
python3 lidaxiao.py --mode browser
```

### Configuration / 配置

For users experiencing 412 errors, use the configuration tool:
```bash
# Apply safe configuration (recommended for production) / 应用安全配置（生产环境推荐）
python3 api_config_tool.py safe

# Test connection / 测试连接
python3 api_config_tool.py test

# Set proxy if needed / 如需要设置代理
python3 api_config_tool.py proxy http://your-proxy:port

# Custom configuration wizard / 自定义配置向导
python3 api_config_tool.py custom
```

### Demo Version / 演示版本
```bash
# Use mock data for testing / 使用模拟数据测试
python3 demo.py

# Historical calculation demo / 历史计算功能演示  
python3 demo_historical.py

# Visualization demo / 可视化功能演示
python3 demo_visualization.py
```

### Historical Calculation Mode / 历史计算模式
```bash
# Enable historical calculation mode / 启用历史计算模式
python3 lidaxiao.py --historical

# Calculate specific historical date / 计算特定历史日期
python3 lidaxiao.py --historical --target-date 2024-08-20

# Batch calculation for date range / 批量计算日期范围
python3 lidaxiao.py --historical --date-range 2024-08-15,2024-08-25

# Use different models / 使用不同模型
python3 lidaxiao.py --historical --historical-model linear
python3 lidaxiao.py --historical --historical-model hybrid

# Custom parameters / 自定义参数
python3 lidaxiao.py --historical --decay-rate 0.08 --growth-rate 0.03
```

## Mode Selection Guide / 模式选择指南

### When to use API Mode / 何时使用API模式
- ✅ Development and testing environments / 开发测试环境
- ✅ Stable network with good Bilibili access / 网络稳定且Bilibili访问良好
- ✅ Need highest data accuracy / 需要最高数据准确性
- ✅ Want fastest execution speed / 需要最快执行速度

### When to use Browser Simulation Mode / 何时使用浏览器模拟模式
- ✅ Production environments / 生产环境
- ✅ Frequently encountering 412 errors / 经常遇到412错误
- ✅ Restricted network environments / 受限网络环境
- ✅ Want to avoid anti-bot detection / 希望避免反机器人检测

### 🤖 Auto Mode (智能模式)
- **Behavior**: Tries API first, falls back to browser simulation / 优先API，失败时切换到浏览器模拟
- **Use case**: General usage / 通用场景

### When to use Historical Calculation Mode / 何时使用历史回推模式
- ✅ Need to estimate historical index values / 需要估算历史指数值
- ✅ Historical trend analysis / 历史趋势分析  
- ✅ Model comparison and validation / 模型对比和验证
- ✅ Research and academic studies / 研究和学术分析

## Generated Files / 生成文件

### Standard Mode Files / 标准模式文件
- `YYYY-MM-DD.json`: Daily index data / 单日指数数据
- `history.json`: Historical index data / 历史指数数据  
- `index_history_YYYYMMDD.png`: Historical trend chart / 历史趋势图
- `index_stack_YYYYMMDD.png`: Daily contribution chart / 单日贡献图

### Historical Calculation Mode Files / 历史计算模式文件
- `historical_batch_START_END.json`: Batch calculation results / 批量计算结果
- `historical_week_DATE.json`: Weekly historical data / 周期历史数据
- `historical_estimates_MODEL_DATE.png`: Historical trend chart / 历史趋势图
- `model_comparison_DATE.png`: Model comparison chart / 模型对比图
- `combined_trend_MODEL_DATE.png`: Combined trend chart / 组合趋势图

## Dependencies / 依赖库

```text
# Required for all modes / 所有模式必需
matplotlib>=3.5.0
httpx>=0.27.0
requests>=2.25.0
beautifulsoup4>=4.9.0

# Required only for API mode / 仅API模式需要
bilibili-api-python>=16.0.0
```

## Index Formula / 指数计算公式

For each video: `Single Video Index = (View Count / 10000) + (Comment Count / 100)`

Total Li Daxiao Index = Sum of all video indices in the past 7 days

每个视频：`单视频指数 = (播放量 / 10000) + (评论数 / 100)`

李大霄总指数 = 过去7天所有视频指数之和

## Troubleshooting / 故障排除

### 412 Security Control Errors / 412安全风控错误
```bash
# Try browser simulation mode / 尝试浏览器模拟模式
python3 lidaxiao.py --mode browser

# Apply safe configuration / 应用安全配置
python3 api_config_tool.py safe

# Use demo data / 使用演示数据
python3 demo.py
```

### Network Connection Issues / 网络连接问题
```bash
# Test connection / 测试连接
python3 api_config_tool.py test

# Try with proxy / 尝试使用代理
python3 api_config_tool.py proxy http://your-proxy:port
```

### Performance Issues / 性能问题
- API mode is faster but less stable / API模式更快但稳定性较差
- Browser simulation mode is slower but more reliable / 浏览器模拟模式较慢但更可靠
- Auto mode provides the best balance / 自动模式提供最佳平衡

## Detailed Documentation / 详细文档

- **[API Mode Guide](API_MODE_GUIDE.md)**: Complete guide for API mode usage / API模式完整使用指南
- **[Browser Mode Guide](BROWSER_MODE_GUIDE.md)**: Complete guide for browser simulation mode / 浏览器模拟模式完整使用指南  
- **[Historical Calculation Guide](HISTORICAL_GUIDE.md)**: Complete guide for historical index calculation / 历史指数计算完整使用指南
- **[Configuration Tool Guide](BILIBILI_412_SOLUTION.md)**: Configuration and troubleshooting / 配置和故障排除指南

## Notes / 注意事项

- Chinese characters in charts may show font warnings but functionality works correctly / 图表中的中文字符可能显示字体警告但功能正常
- The demo version uses mock data for testing purposes / 演示版本使用模拟数据用于测试
- All dates are processed in `YYYY-MM-DD` format / 所有日期都以`YYYY-MM-DD`格式处理
- Browser simulation mode includes random delays to mimic human behavior / 浏览器模拟模式包含随机延迟以模拟人类行为

## Contributing / 贡献

When contributing, please consider both API and browser simulation modes to ensure compatibility across different environments.

贡献代码时，请考虑API模式和浏览器模拟模式，确保在不同环境下的兼容性。