#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright模式演示脚本
Demo script for Playwright browser automation mode
"""

import asyncio
import datetime
from config import BILIBILI_UID
from crawler import fetch_videos_playwright, PLAYWRIGHT_AVAILABLE

async def demo_playwright_mode():
    """演示Playwright模式的基本用法"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright库未安装")
        print("请先安装: pip install playwright && playwright install chromium")
        return False
    
    print("🎭 Playwright模式演示")
    print("=" * 50)
    
    # 设置日期范围（最近3天）
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    print(f"📅 获取日期范围: {start_date} 至 {end_date}")
    print(f"👤 UP主UID: {BILIBILI_UID}")
    print()
    
    try:
        print("🚀 启动Playwright浏览器...")
        print("⏳ 请耐心等待，首次运行可能需要较长时间...")
        
        # 使用headless模式
        videos = await fetch_videos_playwright(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            headless=True
        )
        
        print(f"✅ 成功获取到 {len(videos)} 个视频")
        print()
        
        # 显示前几个视频的详细信息
        print("📺 视频列表预览:")
        print("-" * 50)
        
        for i, video in enumerate(videos[:3]):  # 只显示前3个
            print(f"{i+1}. {video['title']}")
            print(f"   播放量: {video['view']:,}")
            print(f"   评论数: {video['comment']:,}")
            print(f"   发布日期: {video.get('pubdate', '未知')}")
            print()
        
        if len(videos) > 3:
            print(f"   ... 还有 {len(videos) - 3} 个视频")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已正确安装Playwright:")
        print("1. pip install playwright")
        print("2. playwright install chromium")
        return False
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查网络连接")
        print("2. 确认Playwright浏览器已安装")
        print("3. 尝试非无头模式（观察浏览器行为）")
        print("4. 稍后重试")
        return False

async def demo_playwright_with_headful():
    """演示非无头模式（可见浏览器窗口）"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright库未安装")
        return False
    
    print("\n🖥️  非无头模式演示（浏览器窗口可见）")
    print("=" * 50)
    print("⚠️  注意：此模式将打开真实浏览器窗口")
    
    # 询问用户是否继续
    try:
        # 在自动化环境中，我们跳过交互式输入
        print("📱 正在启动可视化浏览器模式...")
        
        end_date = datetime.date.today().strftime("%Y-%m-%d")
        start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos_playwright(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            headless=False  # 非无头模式
        )
        
        print(f"✅ 可视化模式成功获取到 {len(videos)} 个视频")
        return True
        
    except Exception as e:
        print(f"❌ 可视化模式失败: {e}")
        print("💡 提示：在无GUI环境中，请使用无头模式")
        return False

def show_playwright_features():
    """显示Playwright模式的特性"""
    print("\n🌟 Playwright模式特性")
    print("=" * 50)
    
    features = [
        "🛡️  最强反检测能力 - 使用真实浏览器内核",
        "🤖 智能等待机制 - 自动等待页面加载完成",
        "🌐 动态内容支持 - 完美处理JavaScript渲染内容",
        "📱 真实用户行为 - 模拟真实用户的浏览行为",
        "🔒 会话状态保持 - 维护完整的浏览器状态",
        "⚡ 懒加载支持 - 自动滚动触发内容加载",
        "🎯 精确元素定位 - 等待元素出现再进行操作",
        "🔧 灵活配置选项 - 支持无头/可视化模式切换"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📖 使用场景:")
    scenarios = [
        "🚫 传统爬虫被频繁拦截时",
        "🌍 需要处理复杂的JavaScript页面时", 
        "🔐 对反检测要求极高的生产环境",
        "🧪 需要调试和观察真实浏览器行为时",
        "📊 需要获取动态加载的数据时"
    ]
    
    for scenario in scenarios:
        print(f"  {scenario}")

async def main():
    """主函数"""
    print("🎭 李大霄指数 - Playwright模式演示")
    print("=" * 60)
    
    # 显示特性介绍
    show_playwright_features()
    
    # 演示无头模式
    success = await demo_playwright_mode()
    
    if success:
        print("\n🎉 演示完成！")
        print("\n📝 使用说明:")
        print("1. 在生产环境中推荐使用无头模式")
        print("2. 如需调试，可使用非无头模式观察浏览器行为")
        print("3. Playwright模式比传统方法慢，但反检测能力更强")
        print("\n🚀 在主程序中使用:")
        print("   python3 lidaxiao.py --mode playwright")
    else:
        print("\n❌ 演示失败，请检查Playwright安装")

if __name__ == "__main__":
    asyncio.run(main())