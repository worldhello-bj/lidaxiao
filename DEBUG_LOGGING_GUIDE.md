# 增强调试日志功能使用指南

## 概述

本项目实现了全面的调试日志功能，可以输出详细的debug信息，帮助开发者快速定位和解决复杂问题。

## 功能特性

### ✅ 已实现的调试功能

1. **Playwright操作详细记录**
   - 每一步操作前后的页面状态（URL、标题等）
   - DOM快照信息（可选，文件较大时谨慎启用）
   - 页面加载、导航、点击等操作的详细时序

2. **选择器查找调试**
   - 记录每个选择器的查找结果
   - 显示找到的元素数量
   - 便于定位选择器失效问题

3. **分页和导航过程详情**
   - 当前页、总页数、是否有下一页
   - 分页按钮查找和点击过程
   - 页面间导航的详细步骤

4. **异常和错误完整上下文**
   - 完整的堆栈跟踪信息
   - 操作类型和失败时的上下文
   - 重试机制的详细记录

5. **视频数据解析中间结果**
   - 每个视频的解析详情
   - 播放量、评论数、时间戳的提取过程
   - 视频过滤和筛选的逐步记录

6. **配置参数实时追踪**
   - 所有配置变更的前后对比
   - 快速模式/稳定模式切换的详细记录
   - 运行时配置的实时状态

## 使用方法

### 1. 基本启用

```python
from crawler import enable_debug_logging

# 在代码开头启用调试日志
enable_debug_logging()

# 然后正常运行你的爬取代码
```

### 2. 完整示例

```python
import asyncio
from crawler import enable_debug_logging, fetch_videos, enable_fast_mode
from config import BILIBILI_UID

async def main():
    # 启用调试日志
    enable_debug_logging()
    
    # 可选：启用快速模式
    enable_fast_mode()
    
    # 执行爬取任务 - 将输出详细的调试信息
    videos = await fetch_videos(
        uid=BILIBILI_UID,
        start_date="2024-01-01",
        end_date="2024-01-02",
        extended_pages=False,
        headless=True
    )
    
    print(f"获取到 {len(videos)} 个视频")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 配置调试详细程度

```python
from config import DEBUG_CONFIG

# 启用所有调试功能
DEBUG_CONFIG.update({
    "log_page_states": True,      # 页面状态
    "log_selectors": True,        # 选择器查找
    "log_video_parsing": True,    # 视频解析
    "log_pagination": True,       # 分页操作
    "log_retries": True,          # 重试过程
    "log_configuration": True,    # 配置变更
    "log_dom_snapshots": False,   # DOM快照（谨慎启用）
})

# 启用调试模式
enable_debug_logging()
```

## 调试配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `enabled` | `False` | 是否启用调试模式 |
| `log_page_states` | `True` | 记录页面状态信息 |
| `log_dom_snapshots` | `False` | 记录DOM快照（文件较大） |
| `log_selectors` | `True` | 记录选择器查找详情 |
| `log_video_parsing` | `True` | 记录视频数据解析过程 |
| `log_configuration` | `True` | 记录配置参数变化 |
| `log_retries` | `True` | 记录重试过程详情 |
| `log_pagination` | `True` | 记录分页操作详情 |
| `max_dom_snapshot_length` | `1000` | DOM快照最大长度 |

## 调试日志示例

### 页面状态记录
```
DEBUG:crawler:🌐 页面状态 (首页导航完成):
DEBUG:crawler:  URL: https://space.bilibili.com/2137589551/video?tid=0&keyword=&order=pubdate
DEBUG:crawler:  标题: 李大霄的个人空间_哔哩哔哩_bilibili
```

### 选择器查找详情
```
DEBUG:crawler:🔍 视频列表加载检查:
DEBUG:crawler:  选择器: .small-item, .bili-video-card
DEBUG:crawler:  找到元素数量: 15
```

### 视频解析结果
```
DEBUG:crawler:🎬 第1页解析结果:
DEBUG:crawler:  解析到视频数量: 15
DEBUG:crawler:  视频 1:
DEBUG:crawler:    标题: 李大霄：市场底部信号显现，投资机会来了！
DEBUG:crawler:    播放量: 82000
DEBUG:crawler:    评论数: 1200
DEBUG:crawler:    时间戳: 1704067200
```

### 分页操作详情
```
DEBUG:crawler:📄 分页详情:
DEBUG:crawler:  当前页: 2
DEBUG:crawler:  总页数: 10
DEBUG:crawler:  有下一页: True
```

### 异常上下文记录
```
ERROR:crawler:❌ 操作失败: 第1页导航
ERROR:crawler:  异常类型: TimeoutError
ERROR:crawler:  异常信息: 页面加载超时
ERROR:crawler:  上下文信息: {'page_num': 1, 'url': 'https://space.bilibili.com/...'}
ERROR:crawler:  完整堆栈跟踪:
Traceback (most recent call last):
  ...
```

## 最佳实践

### 1. 开发阶段
- 启用所有调试功能
- 使用较短的日期范围进行测试
- 关注选择器和分页相关的调试信息

### 2. 问题排查
- 遇到问题时立即启用调试模式
- 查看异常上下文和完整堆栈
- 分析页面状态和选择器查找结果

### 3. 性能调优
- 使用配置变更日志跟踪性能设置
- 观察重试和等待时间的影响
- 根据调试信息调整时间配置

### 4. 生产环境
- 关闭调试模式以提高性能
- 保留基本的error和warning日志
- 在出现问题时才临时启用

## 注意事项

⚠️ **重要提醒**

1. **性能影响**: 调试模式会产生大量日志，影响运行速度
2. **磁盘空间**: 详细日志会占用更多磁盘空间
3. **DOM快照**: 默认关闭，开启前请确保有足够存储空间
4. **敏感信息**: 注意日志中可能包含的敏感信息

## 故障排除

### 常见问题

1. **调试日志没有显示**
   - 确保调用了 `enable_debug_logging()`
   - 检查日志级别设置
   - 确认 `DEBUG_CONFIG['enabled']` 为 `True`

2. **日志过多**
   - 关闭不需要的调试选项
   - 减少 `max_dom_snapshot_length`
   - 使用较小的日期范围测试

3. **性能下降**
   - 在生产环境关闭调试模式
   - 只在问题排查时临时启用
   - 调整调试配置的详细程度

## 演示脚本

项目包含以下演示脚本：

1. `demo_debug_logging.py` - 基本功能演示
2. `test_debug_integration.py` - 集成测试演示

运行方式：
```bash
python3 demo_debug_logging.py
python3 test_debug_integration.py
```

## 技术实现

调试功能基于以下技术实现：

- **配置驱动**: 通过 `DEBUG_CONFIG` 灵活控制调试级别
- **最小侵入**: 增强现有日志系统，不破坏原有结构
- **上下文感知**: 记录操作发生时的完整上下文信息
- **性能友好**: 可完全关闭，不影响生产环境性能

调试功能已完全集成到主要的爬取流程中，包括：
- `fetch_videos_playwright()` - 主要爬取函数
- `PlaywrightBrowserSimulator` - 浏览器操作类
- 配置管理函数 - `enable_fast_mode()`, `enable_stable_mode()` 等

---

通过这套完整的调试日志系统，开发者可以轻松定位和解决各种复杂的爬取问题。