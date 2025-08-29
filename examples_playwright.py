#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright模式使用示例
Examples for using Playwright browser automation mode

此文件展示了如何在代码中使用新的Playwright模式
This file demonstrates how to use the new Playwright mode in code
"""

import asyncio
import datetime
from crawler import fetch_videos, fetch_videos_playwright, PlaywrightBrowserSimulator, PLAYWRIGHT_AVAILABLE

async def example_basic_usage():
    """基本用法示例"""
    print("=== 基本用法示例 ===")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright未安装，请先安装: pip install playwright && playwright install chromium")
        return
    
    try:
        # 获取最近7天的视频数据
        end_date = datetime.date.today().strftime("%Y-%m-%d")
        start_date = (datetime.date.today() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos(
            uid=2137589551,  # 李大霄UP主ID
            start_date=start_date,
            end_date=end_date,
            mode="playwright"  # 使用Playwright模式
        )
        
        print(f"✅ 获取到 {len(videos)} 个视频")
        return videos
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return []

async def example_with_custom_settings():
    """自定义设置示例"""
    print("\n=== 自定义设置示例 ===")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright未安装")
        return
    
    try:
        # 使用自定义设置的Playwright模式
        end_date = datetime.date.today().strftime("%Y-%m-%d")
        start_date = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos_playwright(
            uid=2137589551,
            start_date=start_date,
            end_date=end_date,
            headless=True,      # 无头模式
            extended_pages=False # 标准页数
        )
        
        print(f"✅ 自定义设置获取到 {len(videos)} 个视频")
        return videos
        
    except Exception as e:
        print(f"❌ 自定义设置失败: {e}")
        return []

async def example_browser_context():
    """浏览器上下文管理示例"""
    print("\n=== 浏览器上下文管理示例 ===")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright未安装")
        return
    
    try:
        # 使用上下文管理器确保资源正确释放
        async with PlaywrightBrowserSimulator(headless=True) as browser:
            # 获取多页数据
            all_videos = []
            for page_num in range(1, 4):  # 获取前3页
                print(f"正在获取第 {page_num} 页...")
                
                html_content = await browser.fetch_user_videos(
                    uid=2137589551, 
                    page_num=page_num,
                    is_first_page=(page_num == 1)
                )
                
                page_videos = browser.parse_videos_from_html(html_content)
                all_videos.extend(page_videos)
                
                print(f"第 {page_num} 页获取到 {len(page_videos)} 个视频")
                
                # 页面间延迟
                await asyncio.sleep(2)
        
        print(f"✅ 总共获取到 {len(all_videos)} 个视频")
        return all_videos
        
    except Exception as e:
        print(f"❌ 上下文管理失败: {e}")
        return []

async def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    try:
        # 尝试Playwright模式，失败时回退到其他模式
        end_date = datetime.date.today().strftime("%Y-%m-%d")
        start_date = (datetime.date.today() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        
        videos = None
        
        # 首选Playwright模式
        try:
            print("🎭 尝试Playwright模式...")
            videos = await fetch_videos(
                uid=2137589551,
                start_date=start_date,
                end_date=end_date,
                mode="playwright"
            )
            print(f"✅ Playwright模式成功：{len(videos)} 个视频")
            
        except Exception as e:
            print(f"⚠️ Playwright模式失败: {e}")
            
            # 回退到浏览器模拟模式
            try:
                print("🌐 回退到浏览器模拟模式...")
                videos = await fetch_videos(
                    uid=2137589551,
                    start_date=start_date,
                    end_date=end_date,
                    mode="api"  # 改为使用api模式作为对比
                )
                print(f"✅ 浏览器模拟模式成功：{len(videos)} 个视频")
                
            except Exception as e2:
                print(f"❌ 浏览器模拟模式也失败: {e2}")
                print("💡 建议检查网络连接或稍后重试")
                
        return videos or []
        
    except Exception as e:
        print(f"❌ 整体错误处理失败: {e}")
        return []

def example_configuration():
    """配置示例"""
    print("\n=== 配置示例 ===")
    
    from crawler import configure_api_settings
    
    # Playwright模式推荐配置
    configure_api_settings(
        timeout=30,           # 增加超时时间，适应浏览器启动
        retry_attempts=2,     # 减少重试次数，避免过度重试
        retry_delay=10,       # 增加重试延迟
        rate_limit_delay=5    # 增加请求间隔，模拟人类行为
    )
    
    print("✅ 已应用Playwright模式推荐配置")
    
    # 查看当前配置
    from crawler import API_REQUEST_CONFIG
    print("当前配置:")
    for key, value in API_REQUEST_CONFIG.items():
        print(f"  {key}: {value}")

async def main():
    """主函数"""
    print("🎭 Playwright模式使用示例")
    print("=" * 50)
    
    # 配置示例
    example_configuration()
    
    # 基本用法
    await example_basic_usage()
    
    # 自定义设置（如果第一个成功的话）
    # await example_custom_settings()
    
    # 浏览器上下文管理（资源密集型，谨慎使用）
    # await example_browser_context()
    
    # 错误处理
    await example_error_handling()
    
    print("\n🎉 示例完成！")
    print("\n📚 更多信息:")
    print("- 详细文档: PLAYWRIGHT_MODE_GUIDE.md")
    print("- 完整演示: python3 demo_playwright.py")
    print("- 故障排除: python3 api_config_tool.py help")

if __name__ == "__main__":
    asyncio.run(main())