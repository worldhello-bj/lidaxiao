#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili API 配置工具
API Configuration Tool

This tool helps users configure API settings to avoid 412 security control errors
and provides troubleshooting utilities.
"""

import asyncio
import sys
from crawler import configure_api_settings, get_api_troubleshooting_info, fetch_videos
from config import BILIBILI_UID, API_REQUEST_CONFIG

def print_current_config():
    """显示当前配置"""
    print("当前API配置:")
    print("-" * 40)
    for key, value in API_REQUEST_CONFIG.items():
        print(f"  {key}: {value}")
    print("-" * 40)

async def test_api_connection():
    """测试API连接"""
    print("正在测试API连接...")
    try:
        # 测试获取最近3天的数据
        from datetime import date, timedelta
        end_date = date.today().strftime("%Y-%m-%d")
        start_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos(BILIBILI_UID, start_date, end_date, use_fallback=False)
        print(f"✅ API连接成功！获取到 {len(videos)} 个视频")
        return True
    except Exception as e:
        print(f"❌ API连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("Bilibili API 配置工具")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # 显示帮助信息
        print("""
使用方法:
  python3 api_config_tool.py config    # 显示当前配置
  python3 api_config_tool.py test      # 测试API连接  
  python3 api_config_tool.py safe      # 应用安全配置(降低风控概率)
  python3 api_config_tool.py fast      # 应用快速配置(可能触发风控)
  python3 api_config_tool.py proxy <url> # 设置代理
  python3 api_config_tool.py help      # 显示故障排除信息

示例:
  python3 api_config_tool.py safe
  python3 api_config_tool.py proxy http://127.0.0.1:8080
  python3 api_config_tool.py test
""")
        return
    
    command = sys.argv[1].lower()
    
    if command == "config":
        print_current_config()
        
    elif command == "test":
        asyncio.run(test_api_connection())
        
    elif command == "safe":
        print("应用安全配置 (降低412风控概率)...")
        configure_api_settings(
            timeout=15,
            retry_attempts=2,
            retry_delay=5, 
            rate_limit_delay=3,
            enable_fallback=True
        )
        print("✅ 安全配置已应用")
        print_current_config()
        
    elif command == "fast":
        print("应用快速配置 (可能触发风控)...")
        configure_api_settings(
            timeout=5,
            retry_attempts=5,
            retry_delay=1,
            rate_limit_delay=0.5,
            enable_fallback=True
        )
        print("✅ 快速配置已应用")
        print_current_config()
        
    elif command == "proxy":
        if len(sys.argv) < 3:
            print("❌ 请提供代理URL")
            print("示例: python3 api_config_tool.py proxy http://127.0.0.1:8080")
            return
        proxy_url = sys.argv[2]
        configure_api_settings(proxy=proxy_url)
        print(f"✅ 代理已设置: {proxy_url}")
        
    elif command == "help":
        print(get_api_troubleshooting_info())
        
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python3 api_config_tool.py' 查看帮助")

if __name__ == "__main__":
    main()