#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日期范围修复
Test for date range calculation fix
"""

import datetime
from historical import HistoricalCalculator


def create_test_videos():
    """创建测试用视频数据，覆盖多个日期"""
    videos = []
    base_date = datetime.date(2024, 8, 28)  # 目标日期
    
    # 创建从8月20日到8月30日的视频数据
    for i in range(-8, 3):  # 8月20日到8月30日
        date = base_date + datetime.timedelta(days=i)
        videos.append({
            "view": 10000 * (i + 10),  # 不同播放量以便区分
            "comment": 100 * (i + 10),
            "title": f"Video on {date}",
            "pubdate": date.strftime("%Y-%m-%d")
        })
    
    return videos


def test_current_wrong_behavior():
    """测试当前错误的行为"""
    print("=" * 60)
    print("测试当前日期范围计算逻辑")
    print("Testing current date range calculation logic")
    print("=" * 60)
    
    videos = create_test_videos()
    calculator = HistoricalCalculator()
    target_date = "2024-08-28"
    
    print(f"\n目标日期: {target_date}")
    print("期望包含视频日期范围: 2024-08-22 到 2024-08-28 (7天)")
    print("Expected video date range: 2024-08-22 to 2024-08-28 (7 days)")
    
    # 显示所有测试视频
    print(f"\n测试视频数据 ({len(videos)} 个视频):")
    for video in videos:
        print(f"  {video['pubdate']}: 播放量={video['view']}, 评论={video['comment']}")
    
    # 使用debug模式查看当前计算过程
    debug_info = calculator.debug_calculation_process(videos, target_date)
    
    print(f"\n调试信息:")
    for step in debug_info["calculation_steps"]:
        if step["step"] == 2:  # 7天规则步骤
            print(f"  新逻辑: 目标日期 {step['target_date']} -> 日期范围 [{step['start_date']}, {step['end_date']}] (7天)")
        elif step["step"] == 4:  # 视频筛选步骤
            print(f"  筛选结果: 符合条件视频 {step['filtered_videos_count']}/{step['total_input_videos']}")
            print(f"  范围内视频: {step['videos_in_range']}")
            print(f"  范围前视频: {step['videos_before_range']}")
            print(f"  范围后视频: {step['videos_after_range']}")
            
            # 显示实际包含的视频
            if step.get("filtered_videos_details"):
                print("  实际包含的视频:")
                for detail in step["filtered_videos_details"][:5]:  # 只显示前5个
                    print(f"    {detail['title']}: {detail['reason']}")
    
    result_index = debug_info["final_result"]["index"]
    print(f"\n当前计算结果: {result_index}")
    
    # 手动验证期望的结果
    expected_videos = [v for v in videos if "2024-08-22" <= v["pubdate"] <= "2024-08-28"]
    expected_index = sum((v["view"] / 10000) + (v["comment"] / 100) for v in expected_videos)
    
    print(f"\n期望结果验证:")
    print(f"  期望包含视频数量: {len(expected_videos)}")
    print(f"  期望包含的日期:")
    for video in expected_videos:
        contribution = (video["view"] / 10000) + (video["comment"] / 100)
        print(f"    {video['pubdate']}: 贡献值 {contribution:.2f}")
    print(f"  期望指数值: {expected_index:.2f}")
    
    # 检查是否存在问题
    if abs(result_index - expected_index) > 0.01:
        print(f"\n❌ 发现问题: 当前结果 {result_index} != 期望结果 {expected_index:.2f}")
        print("当前逻辑只包含有效日期前的视频，遗漏了目标日期及其前6天的视频")
        return False
    else:
        print(f"\n✅ 结果正确: 当前结果 {result_index} = 期望结果 {expected_index:.2f}")
        return True


def test_boundary_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试边界情况")
    print("Testing boundary cases")
    print("=" * 60)
    
    calculator = HistoricalCalculator()
    
    # 测试案例1: 目标日期正好有视频
    videos_case1 = [
        {"view": 10000, "comment": 100, "title": "Target date video", "pubdate": "2024-08-28"},
        {"view": 20000, "comment": 200, "title": "6 days before", "pubdate": "2024-08-22"},
        {"view": 15000, "comment": 150, "title": "7 days before", "pubdate": "2024-08-21"},  # 应该被排除
    ]
    
    print("\n案例1: 目标日期正好有视频")
    debug1 = calculator.debug_calculation_process(videos_case1, "2024-08-28")
    result1 = debug1["final_result"]["index"]
    
    # 期望: 包含2024-08-28和2024-08-22的视频，排除2024-08-21
    expected1 = ((10000 / 10000) + (100 / 100)) + ((20000 / 10000) + (200 / 100))
    
    print(f"  当前结果: {result1}")
    print(f"  期望结果: {expected1} (包含8-28和8-22的视频)")
    
    if abs(result1 - expected1) > 0.01:
        print("  ❌ 边界情况失败")
        return False
    else:
        print("  ✅ 边界情况正确")
    
    return True


if __name__ == "__main__":
    print("开始测试日期范围计算修复")
    print("Starting date range calculation fix tests")
    
    success = test_current_wrong_behavior()
    boundary_success = test_boundary_cases()
    
    print("\n" + "=" * 60)
    if success and boundary_success:
        print("🎉 所有测试通过！当前逻辑正确。")
        print("🎉 All tests passed! Current logic is correct.")
    else:
        print("❌ 发现问题需要修复")
        print("❌ Issues found that need to be fixed")
    print("=" * 60)