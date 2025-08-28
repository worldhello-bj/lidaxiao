# API模式使用指南 (传统bilibili-api-python模式)
# API Mode Usage Guide (Traditional bilibili-api-python Mode)

## 概述 (Overview)
API模式使用 `bilibili-api-python` 库直接调用Bilibili官方API获取视频数据。这种方式速度快、数据准确，但在某些网络环境下可能触发412安全风控错误。

API mode uses the `bilibili-api-python` library to directly call Bilibili's official API for video data. This method is fast and accurate but may trigger 412 security control errors in certain network environments.

## 特性 (Features)
- ⚡ **速度快**: 直接API调用，响应迅速
- 📊 **数据准确**: 获取真实的播放量和评论数
- 🔧 **配置简单**: 无需复杂的请求头设置
- 🎯 **精确筛选**: 支持按发布时间精确筛选视频

## 使用方法 (Usage)

### 1. 安装依赖 (Install Dependencies)
```bash
pip install bilibili-api-python>=16.0.0
```

### 2. 基本使用 (Basic Usage)
```bash
# 使用API模式运行
python3 lidaxiao.py --mode api
```

### 3. 代码示例 (Code Examples)
```python
from crawler import fetch_videos

# 获取用户视频数据 (API模式)
videos = await fetch_videos(
    uid=2137589551,
    start_date="2024-01-01", 
    end_date="2024-01-07",
    mode="api"
)

# 输出视频信息
for video in videos:
    print(f"标题: {video['title']}")
    print(f"播放量: {video['view']}")
    print(f"评论数: {video['comment']}")
    print(f"发布日期: {video['pubdate']}")
    print("---")
```

## 优势 (Advantages)
1. **数据精确性**: 直接从官方API获取，数据100%准确
2. **请求效率**: 单次请求获取大量数据，网络开销小
3. **稳定性**: 基于官方API，接口稳定可靠
4. **功能完整**: 支持按时间、类型等多种筛选方式

## 局限性 (Limitations)
1. **风控风险**: 在某些网络环境下可能触发412安全风控
2. **依赖限制**: 需要安装额外的bilibili-api-python库
3. **网络要求**: 需要稳定的网络连接访问Bilibili API

## 常见问题 (Common Issues)

### Q: 遇到412错误怎么办？
**A**: 412错误表示触发了Bilibili安全风控，解决方案：
1. 切换到浏览器模拟模式: `python3 lidaxiao.py --mode browser`
2. 使用自动模式: `python3 lidaxiao.py --mode auto`
3. 等待一段时间后重试
4. 更换网络环境或使用代理

### Q: API模式请求频率如何控制？
**A**: 程序内置请求限制：
```python
from crawler import configure_api_settings

# 调整请求间隔
configure_api_settings(rate_limit_delay=2)  # 请求间隔2秒

# 设置重试策略
configure_api_settings(
    retry_attempts=3,    # 重试3次
    retry_delay=5       # 重试间隔5秒
)
```

### Q: 如何提高API模式成功率？
**A**: 推荐配置：
1. 使用安全配置: `python3 api_config_tool.py safe`
2. 适当增加请求间隔
3. 使用国内网络环境
4. 避免频繁大量请求

## 技术细节 (Technical Details)

### API调用流程
1. 创建bilibili_api.user.User对象
2. 调用get_videos方法获取视频列表
3. 按发布时间筛选符合条件的视频
4. 返回标准化的视频数据结构

### 数据结构
API模式返回的视频数据结构：
```python
{
    "aid": 123456789,           # 视频AV号
    "view": 50000,              # 播放量
    "comment": 1000,            # 评论数
    "pubdate": "2024-01-01",    # 发布日期
    "title": "视频标题",         # 视频标题
    "created": 1704067200       # 创建时间戳
}
```

## 配置选项 (Configuration Options)

### 环境变量
```bash
export BILIBILI_API_TIMEOUT=30      # API超时时间
export BILIBILI_API_RETRIES=3       # 重试次数
```

### 程序配置
```python
API_REQUEST_CONFIG = {
    "timeout": 30,              # 超时时间(秒)
    "retry_attempts": 3,        # 重试次数
    "retry_delay": 5,           # 重试延迟(秒)
    "rate_limit_delay": 1,      # 请求间隔(秒)
    "enable_fallback": True     # 失败时是否启用模拟数据
}
```

## 性能优化 (Performance Optimization)
1. **批量请求**: 每次请求获取30个视频，减少API调用次数
2. **智能分页**: 自动判断是否需要继续获取下一页
3. **数据缓存**: 避免重复请求相同数据
4. **错误重试**: 自动重试失败的请求

## 最佳实践 (Best Practices)
1. 在网络稳定的环境下使用API模式
2. 设置合理的请求间隔，避免触发风控
3. 监控API响应状态，及时处理异常
4. 结合自动模式使用，确保程序健壮性

## 与浏览器模拟模式对比
| 特性 | API模式 | 浏览器模拟模式 |
|------|---------|---------------|
| 速度 | 快 | 中等 |
| 准确性 | 高 | 中等 |
| 风控概率 | 中等 | 低 |
| 配置复杂度 | 低 | 中等 |
| 网络要求 | 高 | 中等 |
| 推荐场景 | 开发测试 | 生产环境 |

## 故障排除 (Troubleshooting)
运行诊断命令获取详细信息：
```bash
python3 api_config_tool.py test
python3 lidaxiao.py --mode api  # 查看详细错误信息
```

---
*注意: 如果API模式遇到持续的412错误，建议切换到[浏览器模拟模式](BROWSER_MODE_GUIDE.md)或使用自动模式。*