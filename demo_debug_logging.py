#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示增强的调试日志功能
Demo Enhanced Debug Logging Features

这个脚本演示了新增的调试日志功能，包括:
- Playwright每一步操作前后的页面状态
- 关键选择器查找、元素数量和内容
- 分页、滚动、延迟、重试等过程的详细信息
- 异常和catch分支的详细堆栈和上下文
- 抓取到的视频数据中间结果
- 配置参数的实时输出
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crawler import (
    enable_debug_logging, 
    log_configuration_state,
    configure_browser_settings,
    enable_fast_mode,
    enable_stable_mode,
    log_video_parsing_details,
    log_pagination_details,
    log_selector_search,
    log_exception_context
)

def demo_debug_configuration():
    """演示调试配置功能"""
    print("=" * 80)
    print("🔍 调试日志功能演示")
    print("=" * 80)
    print()
    
    print("1. 启用调试日志模式:")
    enable_debug_logging()
    print()
    
    print("2. 演示配置更新和记录:")
    configure_browser_settings(headless=True, page_load_wait=200, network_timeout=5000)
    print()
    
    print("3. 演示快速模式配置变更:")
    enable_fast_mode()
    print()
    
    print("4. 演示稳定模式配置变更:")
    enable_stable_mode()
    print()

def demo_debug_utilities():
    """演示调试工具函数"""
    print("5. 演示视频解析调试信息:")
    mock_videos = [
        {
            "aid": 123456,
            "title": "李大霄：市场底部信号显现，投资机会来了！",
            "view": 82000,
            "comment": 1200,
            "created": 1704067200
        },
        {
            "aid": 123457,
            "title": "A股三大指数分析：科技股领涨预期",
            "view": 65000,
            "comment": 890,
            "created": 1704153600
        }
    ]
    log_video_parsing_details(mock_videos, "模拟解析结果")
    print()
    
    print("6. 演示分页调试信息:")
    log_pagination_details(page_num=2, total_pages=10, has_next=True)
    print()
    
    print("7. 演示选择器查找调试信息:")
    log_selector_search(".bili-video-card", 15, "视频卡片查找")
    log_selector_search(".pagination-btn", 0, "分页按钮查找")
    print()
    
    print("8. 演示异常上下文记录:")
    try:
        # 模拟一个异常
        raise ValueError("模拟的网络连接错误")
    except Exception as e:
        log_exception_context("模拟操作", e, {"page": 1, "retry": 2})
    print()

def demo_debug_benefits():
    """演示调试功能的优势"""
    print("=" * 80)
    print("🎯 调试功能优势总结")
    print("=" * 80)
    print()
    
    benefits = [
        "✅ 详细的页面状态记录 - 可追踪每一步操作前后的页面URL、标题等",
        "✅ 选择器查找调试 - 记录每个选择器找到的元素数量，便于定位选择器问题",
        "✅ 分页过程详情 - 记录当前页、总页数、是否有下一页等分页状态",
        "✅ 完整的异常上下文 - 包含操作类型、完整堆栈跟踪和上下文信息",
        "✅ 视频解析中间结果 - 显示每个视频的解析详情，包括标题、播放量、评论数等",
        "✅ 配置参数实时记录 - 跟踪所有配置变更，便于调试配置问题",
        "✅ 重试过程详情 - 记录每次重试的原因、等待时间和错误信息",
        "✅ DOM快照支持 - 可选择性记录页面DOM状态（谨慎启用，文件较大）"
    ]
    
    for benefit in benefits:
        print(benefit)
    print()
    
    print("🔧 使用方法:")
    print("1. 在代码中调用 enable_debug_logging() 启用调试模式")
    print("2. 通过 DEBUG_CONFIG 配置调整调试详细程度")
    print("3. 查看详细的DEBUG级别日志输出")
    print()
    
    print("⚠️  注意事项:")
    print("- 调试模式会产生大量日志，仅在需要时启用")
    print("- DOM快照功能默认关闭，如需要请谨慎启用")
    print("- 生产环境建议关闭调试模式以提高性能")
    print()

if __name__ == "__main__":
    try:
        demo_debug_configuration()
        demo_debug_utilities()
        demo_debug_benefits()
        
        print("🎉 调试日志功能演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)