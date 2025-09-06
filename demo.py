#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序 - 演示脚本
Li Daxiao Index Calculation Program - Demo Script

完整演示程序各种模式的使用方法和功能特性。
"""

import datetime
import asyncio
from config import BILIBILI_UID, DEFAULT_DAYS_RANGE
from crawler import fetch_videos, PLAYWRIGHT_AVAILABLE, enable_fast_mode, disable_fast_mode
from calculator import calculate_index
from storage import save_all_data, load_history_data
from visualizer import generate_all_charts

async def demo_api_mode():
    """演示API模式"""
    print("🚀 API模式演示")
    print("=" * 50)
    
    # 设置短日期范围以快速演示
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    print(f"📅 获取日期范围: {start_date} 至 {end_date}")
    print(f"👤 UP主UID: {BILIBILI_UID}")
    print()
    
    try:
        print("⚡ 启动API模式...")
        videos = await fetch_videos(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            mode="api"
        )
        
        print(f"✅ 成功获取到 {len(videos)} 个视频")
        
        # 计算指数
        index_value = calculate_index(videos)
        print(f"📊 李大霄指数: {index_value:.2f}")
        print()
        
        return True, videos, index_value
        
    except Exception as e:
        print(f"❌ API模式失败: {e}")
        print("💡 提示: 遇到412错误时请尝试Playwright模式")
        print()
        return False, [], 0.0

async def demo_playwright_mode():
    """演示Playwright模式"""
    print("🎭 Playwright模式演示")
    print("=" * 50)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright库未安装")
        print("请先安装: pip install playwright && playwright install chromium")
        print()
        return False, [], 0.0
    
    # 设置短日期范围以快速演示
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    print(f"📅 获取日期范围: {start_date} 至 {end_date}")
    print(f"👤 UP主UID: {BILIBILI_UID}")
    print()
    
    try:
        print("🌐 启动真实浏览器...")
        print("⏳ 请耐心等待，包含智能分页导航...")
        
        videos = await fetch_videos(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            mode="playwright"
        )
        
        print(f"✅ 成功获取到 {len(videos)} 个视频")
        print("🎯 Playwright模式特色功能:")
        print("  • 真实浏览器模拟，最强反检测")
        print("  • 智能分页按钮点击")
        print("  • 自动等待页面加载完成")
        print("  • 支持动态内容和JavaScript")
        
        # 计算指数
        index_value = calculate_index(videos)
        print(f"📊 李大霄指数: {index_value:.2f}")
        print()
        
        return True, videos, index_value
        
    except Exception as e:
        print(f"❌ Playwright模式失败: {e}")
        print()
        return False, [], 0.0

async def demo_full_workflow():
    """演示完整的工作流程"""
    print("🔄 完整工作流程演示")
    print("=" * 50)
    
    # 使用标准的7天范围
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=DEFAULT_DAYS_RANGE-1)).strftime("%Y-%m-%d")
    
    print(f"📅 计算日期: {end_date} (统计前{DEFAULT_DAYS_RANGE}天视频)")
    print(f"📅 数据范围: {start_date} 至 {end_date}")
    print()
    
    # 尝试自动模式
    try:
        print("🤖 使用智能自动模式...")
        videos = await fetch_videos(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            mode="auto"
        )
        
        print(f"✅ 成功获取到 {len(videos)} 个视频")
        
        # 显示视频详情
        if videos:
            print("\n📺 视频列表预览:")
            print("-" * 80)
            for i, video in enumerate(videos[:3]):  # 只显示前3个
                print(f"{i+1}. {video['title'][:40]}...")
                print(f"   📈 播放: {video['view']:,} | 💬 评论: {video['comment']:,} | 📅 发布: {video['pubdate']}")
                contribution = video['view'] / 10000 + video['comment'] / 100
                print(f"   🏆 贡献值: {contribution:.2f}")
            
            if len(videos) > 3:
                print(f"   ... 还有 {len(videos) - 3} 个视频")
            print()
        
        # 计算指数
        index_value = calculate_index(videos)
        print(f"🎯 最终李大霄指数: {index_value:.2f}")
        print()
        
        # 保存数据
        print("💾 保存数据文件...")
        save_all_data(end_date, videos, index_value)
        print("✅ 已保存JSON数据文件")
        
        # 生成图表
        print("📊 生成可视化图表...")
        try:
            history_data = load_history_data()
            generate_all_charts(end_date, videos, index_value, history_data)
            print("✅ 已生成历史趋势图和单日分析图")
        except Exception as e:
            print(f"⚠️ 图表生成警告: {e}")
        
        print(f"\n🎉 演示完成! 李大霄指数: {index_value:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ 完整流程演示失败: {e}")
        print("💡 可能的解决方案:")
        print("  1. 检查网络连接")
        print("  2. 尝试手动指定模式: --mode playwright 或 --mode api")
        print("  3. 检查Playwright是否正确安装")
        return False

async def demo_fast_mode():
    """演示快速模式"""
    print("🚀 快速模式演示")
    print("=" * 50)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright库未安装")
        print("请先安装: pip install playwright && playwright install chromium")
        print()
        return False, [], 0.0
    
    # 设置短日期范围以快速演示
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"📅 获取日期范围: {start_date} 至 {end_date}")
    print(f"👤 UP主UID: {BILIBILI_UID}")
    print("🚀 启用快速模式以提高响应速度...")
    print()
    
    try:
        # 启用快速模式
        enable_fast_mode()
        
        print("⚡ 快速模式已启用，减少等待时间...")
        print("⏳ 开始获取视频数据...")
        
        start_time = datetime.datetime.now()
        videos = await fetch_videos(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date
        )
        end_time = datetime.datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 快速模式下成功获取到 {len(videos)} 个视频")
        print(f"⏱️  耗时: {duration:.1f} 秒")
        print("🎯 快速模式特色功能:")
        print("  • 减少页面加载等待时间")
        print("  • 优化分页点击响应速度")
        print("  • 降低网络超时时间")
        print("  • 提高界面操作流畅度")
        
        # 计算指数
        index_value = calculate_index(videos)
        print(f"📊 李大霄指数: {index_value:.2f}")
        print()
        
        # 恢复标准模式
        disable_fast_mode()
        print("🔄 已恢复标准模式")
        
        return True, videos, index_value
        
    except Exception as e:
        print(f"❌ 快速模式失败: {e}")
        disable_fast_mode()
        print("🔄 已恢复标准模式")
        print()
        return False, [], 0.0


async def main():
    """主演示函数"""
    print("🌟 李大霄指数计算程序 - 功能演示")
    print("=" * 60)
    print("本演示将展示程序的各种功能和模式")
    print()
    
    # 演示不同模式
    print("📋 演示计划:")
    print("1. API模式 - 快速获取数据")
    print("2. Playwright模式 - 浏览器自动化")  
    print("3. 快速模式 - 提高界面响应速度")
    print("4. 完整工作流程 - 数据获取、计算、保存、可视化")
    print()
    
    input("按回车键开始演示...")
    print()
    
    # 1. API模式演示
    api_success, api_videos, api_index = await demo_api_mode()
    
    input("按回车键继续下一个演示...")
    print()
    
    # 2. Playwright模式演示
    playwright_success, pw_videos, pw_index = await demo_playwright_mode()
    
    input("按回车键继续快速模式演示...")
    print()
    
    # 3. 快速模式演示
    fast_success, fast_videos, fast_index = await demo_fast_mode()
    
    input("按回车键继续完整流程演示...")
    print()
    
    # 4. 完整工作流程演示
    full_success = await demo_full_workflow()
    
    # 总结
    print()
    print("📋 演示结果总结:")
    print("-" * 40)
    print(f"API模式:      {'✅ 成功' if api_success else '❌ 失败'}")
    print(f"Playwright模式: {'✅ 成功' if playwright_success else '❌ 失败'}")
    print(f"快速模式:     {'✅ 成功' if fast_success else '❌ 失败'}")
    print(f"完整流程:     {'✅ 成功' if full_success else '❌ 失败'}")
    print()
    
    if api_success or playwright_success or fast_success:
        print("🎯 推荐使用方式:")
        if fast_success:
            print("  python3 lidaxiao.py --fast            # 快速响应模式")
        if playwright_success:
            print("  python3 lidaxiao.py                   # 标准模式")
        if api_success:
            print("  python3 lidaxiao.py --mode api        # 开发调试")
        print()
        print("💡 性能优化建议:")
        print("  • 使用 --fast 参数可显著提高界面响应速度")
        print("  • 使用 --headless 参数可在后台运行以节省资源")
        print("  • 使用较小的日期范围可减少数据获取时间")
    else:
        print("💡 请检查网络连接和依赖安装后重试")

if __name__ == "__main__":
    asyncio.run(main())