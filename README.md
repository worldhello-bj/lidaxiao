# lidaxiao
# 李大霄指数计算程序需求框架

## 1. 爬虫部分实现

```python
from bilibili_api import user
import datetime

def fetch_videos(uid, start_date, end_date):
    """
    获取指定日期范围内的视频数据
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    u = user.User(uid)
    all_videos = []
    page = 1
    
    while True:
        # 调用B站API获取分页视频列表
        res = u.get_videos(page=page, order=user.Order.PUBDATE)
        if not res["list"]["vlist"]:
            break
            
        for video_info in res["list"]["vlist"]:
            pubdate = datetime.datetime.fromtimestamp(video_info["created"]).strftime("%Y-%m-%d")
            # 仅保留指定日期范围内的视频
            if start_date <= pubdate <= end_date:
                all_videos.append({
                    "aid": video_info["aid"],
                    "view": int(video_info["play"]),
                    "comment": int(video_info["comment"]),
                    "pubdate": pubdate,
                    "title": video_info["title"],
                    "created": video_info["created"]
                })
        page += 1
        
    return all_videos
```

**实现要点**：
- 使用 `bilibili-api-python` 库直接调用B站官方API
- 按发布时间排序获取视频 (`order=user.Order.PUBDATE`)
- 仅保留 `[start_date, end_date]` 范围内的视频
- 处理分页逻辑，确保获取所有符合条件的视频
- 返回包含必要字段的视频列表（播放量、评论数、标题、时间戳等）

## 2. 数据分析部分实现

```python
def calculate_index(videos):
    """
    计算李大霄指数
    :param videos: 视频列表
    :return: 指数值 (float)
    """
    total = 0.0
    for v in videos:
        # 单个视频指数 = (播放量/10000 + 评论数/100)
        video_index = (v["view"] / 10000) + (v["comment"] / 100)
        total += video_index
    return total  # 无视频时自动返回0.0
```

**实现要点**：
- 严格使用公式：`(播放量/10000 + 评论数/100)`
- 遍历所有符合条件的视频，累加单个视频指数
- 无视频时自动返回0.0（符合"无视频指数=0"要求）
- 不进行任何额外计算或修正

## 3. 数据存储与可视化实现

```python
import json
import matplotlib.pyplot as plt
import os
import datetime

def save_data_and_plot(d, videos, index_value):
    """
    保存数据并生成可视化图表
    :param d: 当前日期 (YYYY-MM-DD)
    :param videos: 视频列表
    :param index_value: 计算出的指数值
    """
    # 保存单日JSON文件
    with open(f"{d}.json", "w") as f:
        json.dump({"date": d, "index": index_value}, f, indent=2)
    
    # 更新累积JSON文件
    history_file = "history.json"
    history_data = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history_data = json.load(f)
    history_data.append({"date": d, "index": index_value})
    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=2)
    
    # 生成历史折线图
    _plot_history_index(history_data, d)
    
    # 生成单日堆叠图
    _plot_daily_stack(videos, d, index_value)

def _plot_history_index(history_data, d):
    """生成历史折线图"""
    dates = [item["date"] for item in history_data]
    indices = [item["index"] for item in history_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, indices, marker='o', linestyle='-', color='blue')
    plt.title(f"李大霄指数历史趋势 (截至 {d})")
    plt.xlabel("日期")
    plt.ylabel("指数值")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    date_str = d.replace('-', '')
    plt.savefig(f"index_history_{date_str}.png")
    plt.close()

def _plot_daily_stack(videos, d, total_index):
    """生成单日堆叠图"""
    if not videos:
        # 无视频时的特殊处理
        plt.figure(figsize=(8, 5))
        plt.bar(["无视频"], [0], color='gray')
        plt.text(0, 0.1, "指数=0 (无视频贡献)", ha='center')
        plt.title(f"李大霄指数构成 ({d})")
        plt.ylabel("贡献值")
    else:
        # 按发布时间倒序排序 (最新视频在堆叠顶层)
        sorted_videos = sorted(
            videos, 
            key=lambda v: v["created"], 
            reverse=True
        )
        titles = [v["title"][:12] + "..." if len(v["title"]) > 12 else v["title"] 
                 for v in sorted_videos]
        contributions = [(v["view"] / 10000 + v["comment"] / 100) 
                        for v in sorted_videos]
        
        # 生成堆叠柱状图
        plt.figure(figsize=(10, 6))
        bottom = 0
        for title, contribution in zip(titles, contributions):
            plt.bar([d], [contribution], bottom=bottom, label=title)
            bottom += contribution
        
        plt.title(f"李大霄指数构成 ({d}) | 总指数: {total_index:.2f}")
        plt.ylabel("视频贡献值")
        plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
        plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    date_str = d.replace('-', '')
    plt.savefig(f"index_stack_{date_str}.png", bbox_inches='tight')
    plt.close()
```

**实现要点**：
- **数据存储**：
  - 单日JSON：`{YYYY-MM-DD}.json`（格式：`{"date":"...","index":数值}`）
  - 累积JSON：`history.json`（追加模式，列表结构）
- **历史折线图**：
  - 文件名：`index_history_YYYYMMDD.png`
  - 内容：仅展示历史指数趋势（X轴=日期，Y轴=指数值）
  - 包含网格线和日期旋转，确保可读性
- **单日堆叠图**：
  - 文件名：`index_stack_YYYYMMDD.png`
  - 内容：单柱堆叠图，展示当日各视频贡献
  - 堆叠顺序：按发布时间倒序（最新视频在顶层）
  - 图例置于右侧避免重叠
  - 无视频时显示明确提示

## 4. 主程序流程

```python
if __name__ == "__main__":
    # 获取当前日期
    d = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    
    # 爬取数据
    videos = fetch_videos(uid=2137589551, start_date=start_date, end_date=d)
    
    # 计算指数
    index_value = calculate_index(videos)
    
    # 保存数据并生成可视化
    save_data_and_plot(d, videos, index_value)
```

**执行流程**：
1. 确定日期范围：`[D-6, D]`（D=当前日期）
2. 调用爬虫获取指定日期范围内的视频数据
3. 计算李大霄指数（前7天视频指数之和）
4. 保存单日和历史JSON数据
5. 生成两张独立图表：
   - 历史趋势折线图
   - 单日贡献堆叠图

**依赖库**：
- `bilibili-api-python`（爬虫）
- `matplotlib`（可视化）
- 标准库：`json`, `os`, `datetime`
