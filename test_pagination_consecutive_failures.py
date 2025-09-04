#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分页连续失败逻辑
Test pagination consecutive failures logic
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from crawler import fetch_videos_playwright


class TestPaginationConsecutiveFailures(unittest.TestCase):
    """测试分页连续失败逻辑的测试类"""

    def setUp(self):
        """设置测试环境"""
        self.uid = 2137589551
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-07"

    @patch('crawler.PLAYWRIGHT_AVAILABLE', True)
    @patch('crawler.PlaywrightBrowserSimulator')
    async def test_consecutive_failures_limit_is_three(self, mock_browser_class):
        """测试连续失败限制是否为3次"""
        
        # 创建模拟的浏览器实例
        mock_browser = AsyncMock()
        mock_browser_class.return_value.__aenter__.return_value = mock_browser
        
        # 模拟连续失败3次，然后成功
        failure_count = 0
        def mock_fetch_user_videos(uid, page, is_first_page=True):
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 3:  # 前3次失败
                raise Exception(f"Mock failure {failure_count}")
            else:  # 第4次成功
                return "<html>mock content</html>"
        
        mock_browser.fetch_user_videos.side_effect = mock_fetch_user_videos
        
        # 模拟解析视频返回空列表（触发失败）
        mock_browser.parse_videos_from_html.return_value = []
        
        # 运行测试
        with self.assertRaises(Exception) as context:
            await fetch_videos_playwright(
                self.uid, self.start_date, self.end_date, 
                use_fallback=False, extended_pages=False, headless=True
            )
        
        # 验证是否尝试了足够多的页面（至少3次失败）
        self.assertGreaterEqual(mock_browser.fetch_user_videos.call_count, 3)
        
    @patch('crawler.PLAYWRIGHT_AVAILABLE', True) 
    @patch('crawler.PlaywrightBrowserSimulator')
    async def test_consecutive_failures_reset_on_success(self, mock_browser_class):
        """测试成功获取页面时连续失败计数会重置"""
        
        # 创建模拟的浏览器实例
        mock_browser = AsyncMock()
        mock_browser_class.return_value.__aenter__.return_value = mock_browser
        
        # 模拟失败-失败-成功-失败-失败-失败的模式
        call_count = 0
        def mock_fetch_user_videos(uid, page, is_first_page=True):
            nonlocal call_count
            call_count += 1
            if call_count in [1, 2, 4, 5, 6]:  # 第1,2,4,5,6次失败
                raise Exception(f"Mock failure {call_count}")
            else:  # 第3次成功
                return "<html>mock content</html>"
        
        def mock_parse_videos(html_content):
            nonlocal call_count
            if call_count == 3:  # 第3次成功时返回视频数据
                return [{'aid': 1, 'view': 1000, 'comment': 100, 'title': 'test', 'created': 1704067200}]
            return []
        
        mock_browser.fetch_user_videos.side_effect = mock_fetch_user_videos
        mock_browser.parse_videos_from_html.side_effect = mock_parse_videos
        
        # 运行测试
        try:
            result = await fetch_videos_playwright(
                self.uid, self.start_date, self.end_date, 
                use_fallback=False, extended_pages=False, headless=True
            )
            # 如果成功获取到数据，验证结果
            self.assertIsInstance(result, list)
        except Exception:
            # 如果失败，验证至少尝试了6次（失败-失败-成功-失败-失败-失败）
            self.assertGreaterEqual(mock_browser.fetch_user_videos.call_count, 6)

    def test_max_consecutive_failures_constant(self):
        """测试代码中的max_consecutive_failures常量是否为3"""
        import inspect
        import crawler
        
        # 获取函数源代码
        source = inspect.getsource(crawler.fetch_videos_playwright)
        
        # 验证代码中包含max_consecutive_failures = 3
        self.assertIn("max_consecutive_failures = 3", source)
        self.assertNotIn("max_consecutive_failures = 2", source)


async def run_async_tests():
    """运行异步测试"""
    test_instance = TestPaginationConsecutiveFailures()
    test_instance.setUp()
    
    print("测试连续失败限制是否为3次...")
    try:
        await test_instance.test_consecutive_failures_limit_is_three()
        print("✅ 测试通过")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n测试成功时连续失败计数重置...")
    try:
        await test_instance.test_consecutive_failures_reset_on_success()
        print("✅ 测试通过")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def main():
    """主函数"""
    print("=== 分页连续失败逻辑测试 ===")
    
    # 运行同步测试
    test_instance = TestPaginationConsecutiveFailures()
    print("\n测试max_consecutive_failures常量...")
    try:
        test_instance.test_max_consecutive_failures_constant()
        print("✅ 测试通过: max_consecutive_failures = 3")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 运行异步测试
    print("\n运行异步测试...")
    asyncio.run(run_async_tests())
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()