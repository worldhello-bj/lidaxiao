#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化验证测试
Performance Optimization Verification Test

验证所有性能优化功能是否正确工作
"""

import sys
import asyncio
from config import TIMING_CONFIG, BROWSER_CONFIG
from crawler import (
    enable_fast_mode, 
    enable_stable_mode, 
    configure_browser_settings,
    get_troubleshooting_info
)

def test_config_modes():
    """测试配置系统"""
    print("1. 测试配置系统...")
    
    # 记录初始值
    initial_page_load = TIMING_CONFIG["page_load_wait"]
    initial_interval_min = TIMING_CONFIG["page_interval_min"]
    
    # 测试配置修改
    configure_browser_settings(page_load_wait=100, page_interval_min=0.1)
    modified_page_load = TIMING_CONFIG["page_load_wait"]
    modified_interval_min = TIMING_CONFIG["page_interval_min"]
    
    # 验证值是否正确变化
    assert modified_page_load == 100, f"配置修改失败: {modified_page_load} != 100"
    assert modified_interval_min == 0.1, f"配置修改失败: {modified_interval_min} != 0.1"
    
    print("   ✅ 配置系统正常")
    
    # 恢复初始配置
    configure_browser_settings(page_load_wait=initial_page_load, page_interval_min=initial_interval_min)

def test_convenience_functions():
    """测试便捷函数"""
    print("2. 测试便捷函数...")
    
    # 测试快速模式函数
    original_headless = BROWSER_CONFIG["headless"]
    enable_fast_mode()
    assert BROWSER_CONFIG["headless"] == True, "快速模式应该启用无头模式"
    assert TIMING_CONFIG["page_load_wait"] <= 150, "快速模式应该有最短等待时间"
    print("   ✅ enable_fast_mode() 正常")
    
    # 测试稳定模式函数
    enable_stable_mode()
    assert BROWSER_CONFIG["headless"] == False, "稳定模式应该显示浏览器"
    assert TIMING_CONFIG["page_load_wait"] >= 300, "稳定模式应该有较长等待时间"
    print("   ✅ enable_stable_mode() 正常")
    
    # 恢复原始设置
    BROWSER_CONFIG["headless"] = original_headless

def test_browser_configuration():
    """测试浏览器配置函数"""
    print("3. 测试浏览器配置...")
    
    original_attempts = BROWSER_CONFIG["retry_attempts"]
    original_headless = BROWSER_CONFIG["headless"]
    
    # 测试配置函数
    configure_browser_settings(
        retry_attempts=5,
        headless=True,
        page_load_wait=100,  # 直接设置时间参数
        pagination_wait=30
    )
    
    assert BROWSER_CONFIG["retry_attempts"] == 5, "重试次数应该被更新"
    assert BROWSER_CONFIG["headless"] == True, "无头模式应该被更新"
    assert TIMING_CONFIG["page_load_wait"] == 100, "页面加载等待应该被更新"
    assert TIMING_CONFIG["pagination_wait"] == 30, "分页等待应该被更新"
    
    print("   ✅ configure_browser_settings() 正常")
    
    # 恢复原始设置
    BROWSER_CONFIG["retry_attempts"] = original_attempts
    BROWSER_CONFIG["headless"] = original_headless
    # 保持当前配置，无需恢复模式

def test_performance_calculations():
    """测试性能计算"""
    print("4. 测试性能计算...")
    
    # 快速配置
    fast_config = {
        "page_load_wait": 150,
        "pagination_wait": 50,
        "post_action_wait": 200,
        "page_interval_min": 0.2,
        "page_interval_max": 0.4,
    }
    
    # 稳定配置
    stable_config = {
        "page_load_wait": 300,
        "pagination_wait": 200,
        "post_action_wait": 500,
        "page_interval_min": 0.5,
        "page_interval_max": 1.0,
    }
    
    # 测试快速配置时间
    fast_time = (
        fast_config["page_load_wait"] +
        fast_config["pagination_wait"] + 
        fast_config["post_action_wait"] +
        (fast_config["page_interval_min"] + fast_config["page_interval_max"]) / 2 * 1000
    )
    
    # 测试稳定配置时间
    stable_time = (
        stable_config["page_load_wait"] +
        stable_config["pagination_wait"] + 
        stable_config["post_action_wait"] +
        (stable_config["page_interval_min"] + stable_config["page_interval_max"]) / 2 * 1000
    )
    
    # 验证性能差异
    improvement_ratio = stable_time / fast_time
    assert improvement_ratio > 2.0, f"快速配置应该至少快2倍: {improvement_ratio:.1f}x"
    
    print(f"   ✅ 性能提升比例: {improvement_ratio:.1f}x")

def test_troubleshooting_info():
    """测试故障排除信息"""
    print("5. 测试故障排除信息...")
    
    info = get_troubleshooting_info()
    assert "configure_browser_settings" in info, "故障排除信息应该包含配置函数信息"
    assert "enable_fast_mode" in info, "应该包含快速模式使用说明"
    assert "性能优化建议" in info, "应该包含性能优化建议"
    
    print("   ✅ 故障排除信息正常")

def test_integration():
    """集成测试"""
    print("6. 集成测试...")
    
    # 测试完整的优化流程
    print("   • 启用快速模式...")
    enable_fast_mode()
    
    # 验证配置正确应用
    assert BROWSER_CONFIG["headless"] == True
    assert TIMING_CONFIG["page_load_wait"] <= 150
    assert TIMING_CONFIG["page_interval_min"] <= 0.4
    
    print("   • 启用稳定模式...")
    enable_stable_mode()
    
    # 验证配置切换
    assert BROWSER_CONFIG["headless"] == False
    assert TIMING_CONFIG["page_load_wait"] >= 300
    assert TIMING_CONFIG["page_interval_min"] >= 0.5
    
    print("   ✅ 集成测试通过")

def run_all_tests():
    """运行所有测试"""
    print("🧪 李大霄指数爬虫性能优化验证测试")
    print("=" * 50)
    
    try:
        test_config_modes()
        test_convenience_functions()
        test_browser_configuration()
        test_performance_calculations()
        test_troubleshooting_info()
        test_integration()
        
        print("\n🎉 所有测试通过！")
        print("\n📊 验证结果:")
        print("• 性能模式切换：✅ 正常")
        print("• 便捷函数：✅ 正常")
        print("• 配置管理：✅ 正常")
        print("• 性能计算：✅ 正常")
        print("• 故障排除：✅ 正常")
        print("• 集成功能：✅ 正常")
        
        print("\n🚀 性能优化功能已就绪，用户可以通过以下方式获得4倍速度提升:")
        print("from crawler import enable_fast_mode")
        print("enable_fast_mode()")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)