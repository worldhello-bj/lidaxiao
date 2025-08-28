#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 双模式配置工具
Dual Mode Configuration Tool

This tool helps users configure both API and browser simulation settings
to avoid 412 security control errors and provides troubleshooting utilities.
"""

import asyncio
import sys
from crawler import configure_api_settings, get_api_troubleshooting_info, fetch_videos
from config import BILIBILI_UID, API_REQUEST_CONFIG

def print_current_config():
    """显示当前配置"""
    print("当前程序配置 (适用于API和浏览器模拟两种模式):")
    print("-" * 50)
    for key, value in API_REQUEST_CONFIG.items():
        print(f"  {key}: {value}")
    print("-" * 50)

async def test_connection(mode="auto"):
    """测试指定模式的连接"""
    mode_names = {"api": "API模式", "browser": "浏览器模拟模式", "auto": "自动模式"}
    print(f"正在测试{mode_names.get(mode, mode)}连接...")
    
    try:
        # 测试获取最近3天的数据
        from datetime import date, timedelta
        end_date = date.today().strftime("%Y-%m-%d")
        start_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        videos = await fetch_videos(BILIBILI_UID, start_date, end_date, mode=mode, use_fallback=False)
        print(f"✅ {mode_names.get(mode, mode)}连接成功！获取到 {len(videos)} 个视频")
        return True
    except Exception as e:
        print(f"❌ {mode_names.get(mode, mode)}连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("Bilibili 双模式配置工具 (API模式 + 浏览器模拟模式)")
    print("=" * 60)
    
    if len(sys.argv) == 1:
        # 显示帮助信息
        print("""
使用方法:
  python3 api_config_tool.py config         # 显示当前配置
  python3 api_config_tool.py test [mode]    # 测试连接 (mode: api/browser/auto)
  python3 api_config_tool.py safe          # 应用安全配置 (推荐生产环境)
  python3 api_config_tool.py fast          # 应用快速配置 (API模式优化)
  python3 api_config_tool.py proxy <url>   # 设置代理
  python3 api_config_tool.py custom        # 自定义配置向导
  python3 api_config_tool.py help          # 显示详细故障排除信息

模式说明:
  - API模式: 快速但可能触发412错误，适合开发测试
  - 浏览器模拟模式: 稳定避免风控，适合生产环境
  - 自动模式: 智能选择，兼顾速度和稳定性

示例:
  python3 api_config_tool.py test browser  # 测试浏览器模拟模式
  python3 api_config_tool.py test api      # 测试API模式
  python3 api_config_tool.py safe          # 应用安全配置后推荐使用浏览器模式
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "config":
        print_current_config()
        
    elif command == "test":
        # 支持指定测试模式
        mode = "auto"
        if len(sys.argv) > 2:
            mode = sys.argv[2].lower()
            if mode not in ["api", "browser", "auto"]:
                print(f"❌ 不支持的模式: {mode}")
                print("支持的模式: api, browser, auto")
                return
        
        result = asyncio.run(test_connection(mode))
        if not result:
            print(f"\n{mode}模式连接失败的建议:")
            if mode == "api":
                print("1. 切换到浏览器模拟模式: python3 lidaxiao.py --mode browser")
                print("2. 使用自动模式: python3 lidaxiao.py --mode auto") 
                print("3. 应用安全配置: python3 api_config_tool.py safe")
            elif mode == "browser":
                print("1. 检查网络连接")
                print("2. 等待一段时间后重试")
                print("3. 尝试使用代理")
            else:  # auto mode
                print("1. 使用浏览器模拟模式: python3 lidaxiao.py --mode browser")
                print("2. 应用安全配置: python3 api_config_tool.py safe")
            print("4. 查看故障排除信息: python3 api_config_tool.py help")
        
    elif command == "safe":
        print("应用安全模式配置 (推荐用于浏览器模拟模式)...")
        configure_api_settings(
            timeout=20,
            retry_attempts=2,
            retry_delay=10,
            rate_limit_delay=5,
            enable_fallback=True
        )
        print("✅ 已应用安全模式配置 (低风险，速度较慢)")
        print("💡 建议配合浏览器模拟模式使用: python3 lidaxiao.py --mode browser")
        print_current_config()
        
    elif command == "fast":
        print("应用快速模式配置 (适合API模式)...")
        configure_api_settings(
            timeout=15,
            retry_attempts=3,
            retry_delay=3,
            rate_limit_delay=2,
            enable_fallback=True
        )
        print("✅ 已应用快速模式配置 (风险较高，速度较快)")
        print("⚠️  警告: 快速模式可能增加触发安全风控的概率")
        print("💡 建议配合API模式使用: python3 lidaxiao.py --mode api")
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