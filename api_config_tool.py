#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 浏览器模拟配置工具
Browser Simulation Configuration Tool

This tool helps users configure browser simulation settings to avoid 412 security control errors
and provides troubleshooting utilities.
"""

import asyncio
import sys
from crawler import configure_api_settings, get_api_troubleshooting_info, fetch_videos
from config import BILIBILI_UID, API_REQUEST_CONFIG

def print_current_config():
    """显示当前配置"""
    print("当前浏览器模拟配置:")
    print("-" * 40)
    for key, value in API_REQUEST_CONFIG.items():
        print(f"  {key}: {value}")
    print("-" * 40)

async def test_api_connection():
    """测试浏览器模拟连接"""
    print("正在测试浏览器模拟连接...")
    try:
        # 测试获取最近3天的数据
        from datetime import date, timedelta
        end_date = date.today().strftime("%Y-%m-%d")
        start_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos(BILIBILI_UID, start_date, end_date, use_fallback=False)
        print(f"✅ 浏览器模拟连接成功！获取到 {len(videos)} 个视频")
        return True
    except Exception as e:
        print(f"❌ 浏览器模拟连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("Bilibili 浏览器模拟配置工具")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # 显示帮助信息
        print("""
使用方法:
  python3 api_config_tool.py config    # 显示当前配置
  python3 api_config_tool.py test      # 测试浏览器模拟连接
  python3 api_config_tool.py safe      # 应用安全模式配置
  python3 api_config_tool.py fast      # 应用快速模式配置 (风险较高)
  python3 api_config_tool.py custom    # 自定义配置向导
  python3 api_config_tool.py help      # 显示故障排除信息

浏览器模拟特性:
- 使用真实浏览器Headers和User-Agent
- 模拟人类访问行为（随机延迟）
- 解析网页内容而非直接API调用
- 大幅降低触发安全风控的概率
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "config":
        print_current_config()
        
    elif command == "test":
        result = asyncio.run(test_api_connection())
        if not result:
            print("\n建议:")
            print("1. 使用安全模式: python3 api_config_tool.py safe")
            print("2. 检查网络连接")
            print("3. 查看故障排除信息: python3 api_config_tool.py help")
        
    elif command == "safe":
        print("应用安全模式配置...")
        configure_api_settings(
            timeout=20,
            retry_attempts=2,
            retry_delay=10,
            rate_limit_delay=5,
            enable_fallback=True
        )
        print("✅ 已应用安全模式配置 (低风险，速度较慢)")
        print_current_config()
        
    elif command == "fast":
        print("应用快速模式配置...")
        configure_api_settings(
            timeout=15,
            retry_attempts=3,
            retry_delay=3,
            rate_limit_delay=2,
            enable_fallback=True
        )
        print("✅ 已应用快速模式配置 (风险较高，速度较快)")
        print("⚠️  警告: 快速模式可能增加触发安全风控的概率")
        print_current_config()
        
    elif command == "custom":
        print("自定义配置向导")
        print("-" * 30)
        
        try:
            timeout = int(input("超时时间 (秒, 建议15-30): ") or "20")
            retry_attempts = int(input("重试次数 (建议2-3): ") or "2")
            retry_delay = int(input("重试延迟 (秒, 建议5-15): ") or "10")
            rate_limit_delay = int(input("请求间隔 (秒, 建议3-8): ") or "5")
            enable_fallback = input("启用模拟数据回退? (y/n): ").lower().startswith('y')
            
            configure_api_settings(
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_delay=retry_delay,
                rate_limit_delay=rate_limit_delay,
                enable_fallback=enable_fallback
            )
            print("✅ 已应用自定义配置")
            print_current_config()
            
        except (ValueError, KeyboardInterrupt):
            print("❌ 配置取消或输入无效")
        
    elif command == "help":
        print("故障排除信息:")
        print(get_api_troubleshooting_info())
        
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python3 api_config_tool.py' 查看帮助信息")

if __name__ == "__main__":
    main()