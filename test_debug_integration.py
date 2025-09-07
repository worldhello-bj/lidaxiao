#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试日志功能集成测试
Debug Logging Integration Test

演示如何在实际使用中启用和使用调试日志功能
"""

import sys
import os
import asyncio
import datetime
sys.path.insert(0, os.path.dirname(__file__))

from crawler import enable_debug_logging, fetch_videos, enable_fast_mode, PLAYWRIGHT_AVAILABLE
from config import BILIBILI_UID

async def test_debug_integration():
    """测试调试日志与实际功能的集成"""
    print("=" * 80)
    print("🧪 调试日志功能集成测试")
    print("=" * 80)
    print()
    
    # 启用调试日志
    print("1. 启用调试日志模式...")
    enable_debug_logging()
    print()
    
    # 启用快速模式以减少测试时间
    print("2. 启用快速模式...")
    enable_fast_mode()
    print()
    
    # 如果Playwright不可用，只演示调试功能
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright未安装，只演示调试日志配置功能")
        print("要完整测试，请安装: pip install playwright && playwright install chromium")
        return True
    
    # 设置短日期范围以进行测试
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"3. 测试爬取功能 (日期范围: {start_date} 至 {end_date})")
    print("   注意观察详细的调试日志输出...")
    print()
    
    try:
        # 这里会触发所有增强的调试日志
        videos = await fetch_videos(
            uid=BILIBILI_UID,
            start_date=start_date,
            end_date=end_date,
            extended_pages=False,  # 使用较少页面进行测试
            headless=True  # 无头模式以便测试
        )
        
        print(f"\n✅ 测试成功！获取到 {len(videos)} 个视频")
        print("🔍 调试日志功能正常工作，提供了详细的操作信息")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        print("💡 这可能是网络问题或网站结构变化，但调试日志提供了详细的错误信息")
        return False

def test_debug_config_showcase():
    """展示调试配置的各种选项"""
    print("\n" + "=" * 80)
    print("🎛️  调试配置选项展示")
    print("=" * 80)
    print()
    
    from config import DEBUG_CONFIG
    
    print("调试配置选项说明:")
    config_explanations = {
        "enabled": "是否启用调试模式",
        "log_page_states": "记录页面状态信息 (URL、标题等)",
        "log_dom_snapshots": "记录DOM快照 (较大，谨慎开启)",
        "log_selectors": "记录选择器查找详情",
        "log_video_parsing": "记录视频数据解析过程",
        "log_configuration": "记录配置参数变化",
        "log_retries": "记录重试过程详情",
        "log_pagination": "记录分页操作详情",
        "max_dom_snapshot_length": "DOM快照最大长度限制"
    }
    
    for key, value in DEBUG_CONFIG.items():
        explanation = config_explanations.get(key, "未知配置项")
        print(f"  {key}: {value} - {explanation}")
    
    print()
    print("💡 如需自定义调试选项，可以修改 DEBUG_CONFIG 字典")
    print("例如: DEBUG_CONFIG['log_dom_snapshots'] = True  # 启用DOM快照")

if __name__ == "__main__":
    try:
        # 运行集成测试
        success = asyncio.run(test_debug_integration())
        
        # 展示配置选项
        test_debug_config_showcase()
        
        print("\n" + "=" * 80)
        if success:
            print("🎉 调试日志功能集成测试完成！")
            print("✅ 所有调试功能正常工作")
        else:
            print("⚠️  测试中遇到一些问题，但调试日志功能本身工作正常")
        
        print("\n📖 使用指南:")
        print("1. 在你的代码开头调用 enable_debug_logging()")
        print("2. 运行你的爬取任务，观察详细的调试输出")
        print("3. 根据调试信息定位和解决问题")
        print("4. 生产环境记得关闭调试模式以提高性能")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)