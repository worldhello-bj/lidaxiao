#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 双模式配置工具
Dual Mode Configuration Tool

This tool helps users configure both API and Playwright settings
to avoid 412 security control errors and provides troubleshooting utilities.
"""

import asyncio
import sys
from crawler import configure_api_settings, get_api_troubleshooting_info, fetch_videos
from config import BILIBILI_UID, API_REQUEST_CONFIG

def print_current_config():
    """显示当前配置"""
    print("当前程序配置 (适用于API和Playwright两种模式):")
    print("-" * 50)
    for key, value in API_REQUEST_CONFIG.items():
        print(f"  {key}: {value}")
    print("-" * 50)

async def test_connection(mode="auto"):
    """测试指定模式的连接"""
    mode_names = {"api": "API模式", "playwright": "Playwright模式", "auto": "自动模式"}
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
    print("Bilibili 双模式配置工具 (API模式 + Playwright模式)")
    print("=" * 60)
    
    if len(sys.argv) == 1:
        # 显示帮助信息
        print("""
使用方法:
  python3 api_config_tool.py config         # 显示当前配置
  python3 api_config_tool.py test [mode]    # 测试连接 (mode: api/playwright/auto)
  python3 api_config_tool.py safe          # 应用安全配置 (推荐生产环境)
  python3 api_config_tool.py fast          # 应用快速配置 (API模式优化)
  python3 api_config_tool.py proxy <url>   # 设置代理
  python3 api_config_tool.py custom        # 自定义配置向导
  python3 api_config_tool.py help          # 显示详细故障排除信息

模式说明:
  - API模式: 快速但可能触发412错误，适合开发测试
  - Playwright模式: 真实浏览器自动化，最强反检测能力
  - 自动模式: 智能选择，兼顾速度和稳定性

示例:
  python3 api_config_tool.py test playwright # 测试Playwright模式
  python3 api_config_tool.py test api        # 测试API模式
  python3 api_config_tool.py safe            # 应用安全配置后推荐使用Playwright模式
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
            if mode not in ["api", "playwright", "auto"]:
                print(f"❌ 不支持的模式: {mode}")
                print("支持的模式: api, playwright, auto")
                print("注意: browser模式已移除，请使用playwright模式替代")
                return
        
        result = asyncio.run(test_connection(mode))
        if not result:
            print(f"\n{mode}模式连接失败的建议:")
            if mode == "api":
                print("1. 切换到Playwright模式: python3 lidaxiao.py --mode playwright")
                print("2. 使用自动模式: python3 lidaxiao.py --mode auto") 
                print("3. 应用安全配置: python3 api_config_tool.py safe")
            elif mode == "playwright":
                print("1. 检查Playwright是否正确安装: playwright install chromium")
                print("2. 检查网络连接")
                print("3. 等待一段时间后重试")
            else:  # auto mode
                print("1. 使用Playwright模式: python3 lidaxiao.py --mode playwright")
                print("2. 应用安全配置: python3 api_config_tool.py safe")
            print("4. 查看故障排除信息: python3 api_config_tool.py help")
        
    elif command == "safe":
        print("应用安全模式配置 (推荐用于Playwright模式)...")
        configure_api_settings(
            timeout=20,
            retry_attempts=2,
            retry_delay=10,
            rate_limit_delay=5
        )
        print("✅ 已应用安全模式配置 (低风险，速度较慢)")
        print("💡 建议配合Playwright模式使用: python3 lidaxiao.py --mode playwright")
        print_current_config()
        
    elif command == "fast":
        print("应用快速模式配置 (适合API模式)...")
        configure_api_settings(
            timeout=15,
            retry_attempts=3,
            retry_delay=3,
            rate_limit_delay=2
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
            
            configure_api_settings(
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_delay=retry_delay,
                rate_limit_delay=rate_limit_delay
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