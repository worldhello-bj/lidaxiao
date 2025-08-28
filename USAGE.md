# Li Daxiao Index Calculator / 李大霄指数计算程序

This project implements a Li Daxiao Index calculation program that crawls Bilibili videos, calculates an index based on views and comments, and generates visualizations.

## Features / 功能特性

- **Video Crawling**: Fetches videos from a specific Bilibili UP主 (UID: 2137589551) for the past 7 days
- **Index Calculation**: Calculates Li Daxiao Index using formula: `(views/10000 + comments/100)` for each video
- **Data Storage**: Saves daily and historical data in JSON format
- **Visualization**: Generates two types of charts:
  - Historical trend line chart
  - Daily contribution stack chart

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

### Production Version (Real API)
```bash
python3 lidaxiao.py
```

### Demo Version (Mock Data)
```bash
python3 demo.py
```

### API Configuration Tool (For 412 Errors)
```bash
# Apply safe configuration to reduce 412 errors
python3 api_config_tool.py safe

# Set proxy if needed
python3 api_config_tool.py proxy http://your-proxy:port

# Test API connection
python3 api_config_tool.py test
```

## Generated Files / 生成文件

- `YYYY-MM-DD.json`: Daily index data / 单日指数数据
- `history.json`: Historical index data / 历史指数数据  
- `index_history_YYYYMMDD.png`: Historical trend chart / 历史趋势图
- `index_stack_YYYYMMDD.png`: Daily contribution chart / 单日贡献图

## Dependencies / 依赖库

- `bilibili-api-python>=16.0.0`: For Bilibili API access
- `matplotlib>=3.5.0`: For data visualization
- `httpx>=0.27.0`: HTTP client for API requests

## Index Formula / 指数计算公式

For each video: `Single Video Index = (View Count / 10000) + (Comment Count / 100)`

Total Li Daxiao Index = Sum of all video indices in the past 7 days

## Notes / 注意事项

- The production version requires network access to Bilibili API
- **412 Security Control Error**: If you encounter Bilibili 412 errors, use `python3 api_config_tool.py safe` to apply safe configurations
- Chinese characters in charts may show font warnings but the functionality works correctly
- The demo version uses mock data for testing purposes
- All dates are processed in `YYYY-MM-DD` format
- See `BILIBILI_412_SOLUTION.md` for detailed troubleshooting of API access issues