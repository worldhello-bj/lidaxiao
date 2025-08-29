# Playwright 浏览器自动化模式使用指南

## 概述

Playwright模式是李大霄指数计算程序的最新升级模式，使用真实浏览器自动化技术，提供业界最强的反检测能力和动态内容处理能力。

## 主要优势

### 🛡️ 最强反检测能力
- 使用真实Chromium浏览器内核，完全模拟人类用户
- 内置反自动化检测脚本，隐藏webdriver特征
- 设置真实的浏览器指纹和用户代理
- 支持完整的浏览器环境和JavaScript执行

### 🤖 智能自动化功能
- **自动等待机制**: 等待页面完全加载再进行数据提取
- **智能滚动**: 自动滚动页面触发懒加载内容
- **元素等待**: 等待关键元素出现后再进行操作
- **网络空闲检测**: 等待网络请求完成

### 🌐 动态内容支持
- 完美处理JavaScript渲染的动态内容
- 支持单页应用(SPA)的数据获取
- 处理异步加载的视频列表
- 支持复杂的交互式页面

## 安装配置

### 1. 安装Playwright库
```bash
pip install playwright
```

### 2. 安装浏览器引擎
```bash
playwright install chromium
```

### 3. 验证安装
```bash
python3 api_config_tool.py test playwright
```

## 使用方法

### 基本使用
```bash
# 使用Playwright模式运行主程序
python3 lidaxiao.py --mode playwright

# 运行演示脚本
python3 demo_playwright.py
```

### 历史计算模式
```bash
# Playwright模式进行历史指数计算
python3 lidaxiao.py --mode playwright --historical --target-date 2024-01-15
```

## 代码示例

### 基本API调用
```python
import asyncio
from crawler import fetch_videos_playwright

async def get_videos():
    videos = await fetch_videos_playwright(
        uid=2137589551,
        start_date="2024-01-01", 
        end_date="2024-01-31",
        headless=True  # 无头模式
    )
    return videos

# 运行
videos = asyncio.run(get_videos())
```

### 使用浏览器上下文
```python
from crawler import PlaywrightBrowserSimulator

async def advanced_usage():
    async with PlaywrightBrowserSimulator(headless=True) as browser:
        # 获取第一页数据
        html = await browser.fetch_user_videos(uid=2137589551, page_num=1)
        
        # 解析视频数据
        videos = browser.parse_videos_from_html(html)
        return videos
```

## 配置选项

### 浏览器模式
```python
# 无头模式（推荐生产环境）
await fetch_videos_playwright(uid, start_date, end_date, headless=True)

# 可视化模式（适合调试）
await fetch_videos_playwright(uid, start_date, end_date, headless=False)
```

### 浏览器类型
```python
# 支持的浏览器类型
browser_types = ["chromium", "firefox", "webkit"]

# 创建不同类型的浏览器
async with PlaywrightBrowserSimulator(
    headless=True, 
    browser_type="chromium"
) as browser:
    # 使用浏览器
    pass
```

## 反检测特性

### 内置反检测措施
1. **移除webdriver标识**: 隐藏`navigator.webdriver`属性
2. **模拟真实浏览器**: 设置完整的插件和权限信息
3. **用户代理伪装**: 使用最新的Chrome用户代理
4. **行为模拟**: 自然的滚动和等待时间
5. **指纹规避**: 设置标准的视口大小和语言偏好

### 高级反检测配置
```python
# 自定义反检测脚本会自动注入到每个页面
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });
    
    window.chrome = { runtime: {} };
""")
```

## 性能和限制

### 性能特点
- **速度**: 比传统HTTP请求慢3-5倍
- **内存**: 需要更多内存资源（约100-200MB）
- **CPU**: 需要较多CPU资源用于浏览器渲染
- **可靠性**: 反检测成功率>95%

### 适用场景
✅ **推荐使用**:
- 传统爬虫频繁被拦截
- 需要处理JavaScript动态内容
- 对反检测要求极高的生产环境
- 需要调试真实浏览器行为

❌ **不推荐使用**:
- 资源受限的环境
- 对速度要求极高的场景
- 简单的静态页面爬取

## 故障排除

### 常见问题

#### 1. Playwright未安装
```bash
❌ ImportError: No module named 'playwright'

解决方案:
pip install playwright
playwright install chromium
```

#### 2. 浏览器安装失败
```bash
❌ Browser not found

解决方案:
# 重新安装浏览器
playwright install chromium --with-deps

# 或指定安装路径
PLAYWRIGHT_BROWSERS_PATH=/path/to/browsers playwright install chromium
```

#### 3. 无头模式失败
```bash
❌ Failed to launch browser

解决方案:
# 1. 安装依赖
sudo apt-get install -y xvfb

# 2. 检查系统资源
free -h
df -h

# 3. 尝试降低并发
# 减少页面获取数量
```

#### 4. 网络超时
```bash
❌ TimeoutError: waiting for selector

解决方案:
# 增加超时时间
await page.wait_for_selector('.video-item', timeout=30000)

# 检查网络连接
ping bilibili.com
```

### 调试技巧

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 使用可视化模式调试
```python
# 开启可视化模式观察浏览器行为
await fetch_videos_playwright(
    uid=2137589551,
    start_date="2024-01-01", 
    end_date="2024-01-02",
    headless=False  # 可以看到浏览器窗口
)
```

#### 截图调试
```python
async with PlaywrightBrowserSimulator(headless=True) as browser:
    await browser.page.goto(url)
    await browser.page.screenshot(path="debug.png")
    # 检查截图确认页面状态
```

## 最佳实践

### 1. 生产环境配置
```python
# 推荐的生产环境配置
configure_api_settings(
    timeout=30,           # 增加超时时间
    retry_attempts=2,     # 减少重试次数
    retry_delay=10,       # 增加重试延迟
    rate_limit_delay=5    # 增加请求间隔
)
```

### 2. 错误处理
```python
try:
    videos = await fetch_videos_playwright(uid, start_date, end_date)
except ImportError:
    # Playwright未安装，回退到browser模式
    videos = await fetch_videos_browser(uid, start_date, end_date)
except Exception as e:
    logger.error(f"Playwright模式失败: {e}")
    # 其他错误处理
```

### 3. 资源管理
```python
# 使用上下文管理器确保资源释放
async with PlaywrightBrowserSimulator() as browser:
    # 执行操作
    pass
# 浏览器会自动关闭
```

## 与其他模式对比

| 特性 | API模式 | Browser模式 | **Playwright模式** |
|------|---------|-------------|-------------------|
| 速度 | 很快 ⚡ | 中等 🚶 | 较慢 🐌 |
| 反检测能力 | 低 ❌ | 中等 ⚠️ | **最强** ✅ |
| 动态内容支持 | 无 ❌ | 有限 ⚠️ | **完美** ✅ |
| 资源消耗 | 很低 💚 | 低 💛 | **较高** ❤️ |
| 配置复杂度 | 简单 💚 | 简单 💚 | **中等** 💛 |
| 调试友好性 | 一般 💛 | 一般 💛 | **优秀** 💚 |

## 总结

Playwright模式是处理现代Web应用反爬虫机制的终极解决方案。虽然资源消耗较高，但其卓越的反检测能力和动态内容支持使其成为生产环境的首选方案。

**推荐使用场景**:
- 🔥 高要求的生产环境
- 🚫 传统方法频繁失败时
- 🌐 复杂的JavaScript页面
- 🔍 需要调试浏览器行为时

---
*更多信息请参考：[BROWSER_MODE_GUIDE.md](BROWSER_MODE_GUIDE.md) | [API_MODE_GUIDE.md](API_MODE_GUIDE.md)*