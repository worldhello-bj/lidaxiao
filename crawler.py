#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据爬取模块 (使用Playwright浏览器自动化)
Video Crawling Module (Using Playwright Browser Automation)

This module handles fetching video data from Bilibili using Playwright browser automation
with real browser and strongest anti-detection capabilities.
"""

import json
import datetime
import random
import asyncio
import logging
import time
import re
import traceback
from config import BROWSER_CONFIG, ERROR_MESSAGES, TIMING_CONFIG, DEBUG_CONFIG

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup4 not available, HTML parsing will be limited")

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, please install: pip install playwright && playwright install chromium")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enable_debug_logging():
    """启用调试日志模式"""
    DEBUG_CONFIG["enabled"] = True
    # 设置日志级别为DEBUG
    logging.getLogger().setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.debug("🔍 调试日志模式已启用")
    log_configuration_state()


def log_configuration_state():
    """记录当前配置状态"""
    if not DEBUG_CONFIG.get("log_configuration", False):
        return
        
    logger.debug("📋 当前配置状态:")
    logger.debug(f"  浏览器配置: {BROWSER_CONFIG}")
    logger.debug(f"  时间配置: {TIMING_CONFIG}")
    logger.debug(f"  调试配置: {DEBUG_CONFIG}")


def log_page_state(page, operation="未知操作"):
    """记录页面状态信息"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_page_states", False):
        return
        
    try:
        logger.debug(f"🌐 页面状态 ({operation}):")
        logger.debug(f"  URL: {page.url}")
        logger.debug(f"  标题: {page.title()}")
    except Exception as e:
        logger.debug(f"❌ 无法获取页面状态: {e}")


async def log_dom_snapshot(page, operation="未知操作"):
    """记录DOM快照信息"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_dom_snapshots", False):
        return
        
    try:
        html_content = await page.content()
        max_length = DEBUG_CONFIG.get("max_dom_snapshot_length", 1000)
        if len(html_content) > max_length:
            html_content = html_content[:max_length] + "..."
        logger.debug(f"📄 DOM快照 ({operation}):")
        logger.debug(f"  HTML长度: {len(html_content)} 字符")
        logger.debug(f"  内容预览: {html_content}")
    except Exception as e:
        logger.debug(f"❌ 无法获取DOM快照: {e}")


def log_selector_search(selector, elements_found, operation="选择器查找"):
    """记录选择器查找详情"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_selectors", False):
        return
        
    logger.debug(f"🔍 {operation}:")
    logger.debug(f"  选择器: {selector}")
    logger.debug(f"  找到元素数量: {elements_found}")


def log_video_parsing_details(videos, operation="视频解析"):
    """记录视频数据解析详情"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_video_parsing", False):
        return
        
    logger.debug(f"🎬 {operation}:")
    logger.debug(f"  解析到视频数量: {len(videos)}")
    
    for i, video in enumerate(videos[:3]):  # 只显示前3个作为示例
        logger.debug(f"  视频 {i+1}:")
        logger.debug(f"    标题: {video.get('title', 'N/A')}")
        logger.debug(f"    播放量: {video.get('view', 'N/A')}")
        logger.debug(f"    评论数: {video.get('comment', 'N/A')}")
        logger.debug(f"    时间戳: {video.get('created', 'N/A')}")
    
    if len(videos) > 3:
        logger.debug(f"  ... 还有 {len(videos) - 3} 个视频")


def log_retry_attempt(attempt, max_attempts, error, delay=None):
    """记录重试尝试详情"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_retries", False):
        return
        
    logger.debug(f"🔄 重试详情:")
    logger.debug(f"  当前尝试: {attempt + 1}/{max_attempts}")
    logger.debug(f"  错误信息: {error}")
    if delay:
        logger.debug(f"  等待时间: {delay} 秒")
    logger.debug(f"  错误堆栈: {traceback.format_exc()}")


def log_pagination_details(page_num, total_pages=None, has_next=None):
    """记录分页操作详情"""
    if not DEBUG_CONFIG.get("enabled", False) or not DEBUG_CONFIG.get("log_pagination", False):
        return
        
    logger.debug(f"📄 分页详情:")
    logger.debug(f"  当前页: {page_num}")
    if total_pages:
        logger.debug(f"  总页数: {total_pages}")
    if has_next is not None:
        logger.debug(f"  有下一页: {has_next}")


def log_exception_context(operation, exception, context=None):
    """记录异常和上下文信息"""
    logger.error(f"❌ 操作失败: {operation}")
    logger.error(f"  异常类型: {type(exception).__name__}")
    logger.error(f"  异常信息: {str(exception)}")
    if context:
        logger.error(f"  上下文信息: {context}")
    logger.error(f"  完整堆栈跟踪:\n{traceback.format_exc()}")


class PlaywrightBrowserSimulator:
    """使用Playwright进行真实浏览器自动化的模拟器"""
    
    def __init__(self, headless=None, browser_type=None):
        # 如果未指定参数，使用配置文件中的设置
        self.headless = headless if headless is not None else BROWSER_CONFIG["headless"]
        self.browser_type = browser_type if browser_type is not None else BROWSER_CONFIG["browser_type"]
        self.browser = None
        self.context = None
        self.page = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
        
    async def start(self):
        """启动浏览器"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright库不可用，请安装: pip install playwright && playwright install chromium")
            
        self.playwright = await async_playwright().start()
        
        # 启动浏览器
        if self.browser_type == "chromium":
            browser_launcher = self.playwright.chromium
        elif self.browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif self.browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
            
        self.browser = await browser_launcher.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
            }
        )
        
        # 设置反检测脚本
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' }),
                }),
            });
        """)
        
        self.page = await self.context.new_page()
        
    async def close(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def fetch_user_videos(self, uid, page_num=1, is_first_page=True):
        """获取用户视频页面内容"""
        logger.debug(f"🔄 开始获取用户 {uid} 第 {page_num} 页视频内容")
        
        if is_first_page:
            # 首页直接导航
            url = f"https://space.bilibili.com/{uid}/video?tid=0&keyword=&order=pubdate"
            logger.debug(f"🌐 导航到首页: {url}")
            
            try:
                # 修复：避免使用networkidle，改用domcontentloaded提高速度
                await self.page.goto(url, wait_until='domcontentloaded', timeout=TIMING_CONFIG["network_timeout"])
                log_page_state(self.page, "首页导航完成")
                
                # 短暂等待确保关键元素加载完成
                await self.page.wait_for_timeout(300)
                logger.debug(f"⏱️ 页面加载等待完成: 300ms")
            except Exception as e:
                log_exception_context("首页导航", e, {"url": url, "uid": uid})
                raise
        else:
            # 非首页通过点击分页按钮导航
            logger.debug(f"📄 准备导航到第 {page_num} 页")
            try:
                success = await self.navigate_to_next_page(page_num)
                if not success:
                    logger.warning(f"无法找到或点击第{page_num}页的分页按钮")
                    return None
                log_page_state(self.page, f"第{page_num}页导航完成")
            except Exception as e:
                log_exception_context("分页导航", e, {"page_num": page_num, "uid": uid})
                raise
        
        try:
            # 等待视频列表加载，使用优化的超时时间但降低要求
            selector = '.small-item, .bili-video-card'
            logger.debug(f"🔍 等待视频列表选择器: {selector}")
            await self.page.wait_for_selector(selector, timeout=TIMING_CONFIG["element_timeout"])
            
            # 检查找到的视频元素数量
            video_elements = await self.page.query_selector_all(selector)
            log_selector_search(selector, len(video_elements), "视频列表加载检查")
            
            # 优化：使用异步滚动，避免阻塞
            logger.debug("📜 执行页面滚动以触发懒加载")
            await self.page.evaluate("""
                () => {
                    // 快速异步滚动到页面底部触发懒加载
                    window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'});
                    // 快速回到顶部确保所有内容可见
                    setTimeout(() => window.scrollTo({top: 0, behavior: 'instant'}), 50);
                }
            """)
            
            # 减少等待时间：只等待必要的内容加载时间
            wait_time = TIMING_CONFIG["page_load_wait"]
            logger.debug(f"⏱️ 等待页面内容加载: {wait_time}ms")
            await self.page.wait_for_timeout(wait_time)
            
            # 获取页面内容
            content = await self.page.content()
            logger.debug(f"📄 获取到页面内容，长度: {len(content)} 字符")
            
            # 记录DOM快照（如果启用）
            await log_dom_snapshot(self.page, f"第{page_num}页内容获取")
            
            return content
            
        except Exception as e:
            log_exception_context("获取页面内容", e, {"page_num": page_num, "uid": uid})
            raise

    async def check_pagination_info(self):
        """检查分页信息，返回当前页和总页数"""
        logger.debug("🔍 开始检查分页信息")
        try:
            # 优化：使用更短的分页等待时间
            selector = '.vui_pagenation, .page-wrap, .bili-pager'
            logger.debug(f"🔍 等待分页选择器: {selector}")
            await self.page.wait_for_selector(selector, timeout=TIMING_CONFIG["element_timeout"])
            
            # 尝试获取当前页信息
            current_page = 1
            total_pages = 1
            has_next = False
            
            # 查找当前页指示器
            current_page_selectors = [
                '.vui_button.vui_pagenation--btn-num.active',
                '.page-item.active',
                '.current-page',
                '.bili-pager-btn.current'
            ]
            
            logger.debug(f"🔍 查找当前页指示器，尝试选择器: {current_page_selectors}")
            for selector in current_page_selectors:
                try:
                    element = await self.page.locator(selector).first.text_content()
                    if element and element.isdigit():
                        current_page = int(element)
                        logger.debug(f"✅ 找到当前页: {current_page}，选择器: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"❌ 选择器 {selector} 未找到当前页: {e}")
                    continue
            
            # 查找下一页按钮是否可用
            next_button_selectors = [
                '.vui_button.vui_pagenation--btn-side:has-text("下一页"):not([disabled])',
                '.page-item.next:not(.disabled)',
                'button:has-text("下一页"):not([disabled])',
                '.bili-pager-next:not([disabled])'
            ]
            
            logger.debug(f"🔍 查找下一页按钮，尝试选择器: {next_button_selectors}")
            for selector in next_button_selectors:
                try:
                    button = self.page.locator(selector).first
                    if await button.count() > 0 and await button.is_enabled():
                        has_next = True
                        logger.debug(f"✅ 找到可用的下一页按钮，选择器: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"❌ 下一页选择器 {selector} 不可用: {e}")
                    continue
            
            # 尝试获取总页数
            total_page_selectors = [
                '.vui_pagenation .vui_button.vui_pagenation--btn-num:last-of-type',
                '.page-wrap .page-item:nth-last-child(2)',
                '.bili-pager-btn:not(.next):not(.prev):last-of-type'
            ]
            
            logger.debug(f"🔍 查找总页数，尝试选择器: {total_page_selectors}")
            for selector in total_page_selectors:
                try:
                    element = await self.page.locator(selector).text_content()
                    if element and element.isdigit():
                        total_pages = max(total_pages, int(element))
                        logger.debug(f"✅ 找到总页数: {total_pages}，选择器: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"❌ 总页数选择器 {selector} 失败: {e}")
                    continue
            
            log_pagination_details(current_page, total_pages, has_next)
            logger.debug(f"分页信息: 当前页={current_page}, 总页数={total_pages}, 有下一页={has_next}")
            return {
                'current_page': current_page,
                'total_pages': total_pages,
                'has_next': has_next
            }
            
        except Exception as e:
            log_exception_context("获取分页信息", e)
            logger.debug(f"获取分页信息失败: {e}")
            return {
                'current_page': 1,
                'total_pages': 1,
                'has_next': False
            }

    async def navigate_to_next_page(self, target_page_num):
        """通过点击分页按钮导航到目标页面"""
        logger.debug(f"📄 开始导航到第 {target_page_num} 页")
        try:
            # 等待分页区域加载，使用动态超时
            pager_selector = '.vui_pagenation, .page-wrap, .bili-pager'
            logger.debug(f"🔍 等待分页区域加载: {pager_selector}")
            await self.page.wait_for_selector(pager_selector, timeout=TIMING_CONFIG["element_timeout"])
            
            # 尝试多种分页按钮选择器
            pagination_selectors = [
                f'.vui_button.vui_pagenation--btn-num:has-text("{target_page_num}")',
                f'.page-item:has-text("{target_page_num}")',
                f'button:has-text("{target_page_num}")',
                f'a:has-text("{target_page_num}")'
            ]
            
            button_found = False
            logger.debug(f"🔍 查找第 {target_page_num} 页按钮，尝试选择器: {pagination_selectors}")
            for selector in pagination_selectors:
                try:
                    # 检查按钮是否存在
                    button = self.page.locator(selector).first
                    button_count = await button.count()
                    log_selector_search(selector, button_count, f"第{target_page_num}页按钮查找")
                    
                    if button_count > 0:
                        logger.info(f"找到分页按钮，使用选择器: {selector}")
                        
                        # 优化：减少不必要的等待时间
                        logger.debug("📜 滚动到按钮位置")
                        await button.scroll_into_view_if_needed()
                        
                        wait_time = TIMING_CONFIG["pagination_wait"]
                        logger.debug(f"⏱️ 分页等待: {wait_time}ms")
                        await self.page.wait_for_timeout(wait_time)
                        
                        # 点击按钮
                        logger.debug(f"🖱️ 点击第 {target_page_num} 页按钮")
                        await button.click()
                        
                        # 修复：避免使用networkidle，改用domcontentloaded提高速度
                        logger.debug("⏳ 等待页面加载完成")
                        await self.page.wait_for_load_state('domcontentloaded', timeout=TIMING_CONFIG["network_timeout"])
                        
                        post_wait = TIMING_CONFIG["post_action_wait"]
                        logger.debug(f"⏱️ 操作后等待: {post_wait}ms")
                        await self.page.wait_for_timeout(post_wait)
                        
                        button_found = True
                        logger.info(f"成功点击第{target_page_num}页分页按钮")
                        log_page_state(self.page, f"第{target_page_num}页点击完成")
                        break
                        
                except Exception as e:
                    logger.debug(f"选择器 {selector} 未找到按钮: {e}")
                    continue
            
            if not button_found:
                # 如果没找到具体页码按钮，尝试点击"下一页"按钮
                next_button_selectors = [
                    '.vui_button.vui_pagenation--btn-side:has-text("下一页")',
                    '.page-item.next',
                    'button:has-text("下一页")',
                    '.bili-pager-next'
                ]
                
                logger.debug(f"🔍 未找到具体页码按钮，尝试下一页按钮: {next_button_selectors}")
                for selector in next_button_selectors:
                    try:
                        button = self.page.locator(selector).first
                        button_count = await button.count()
                        is_enabled = await button.is_enabled() if button_count > 0 else False
                        
                        log_selector_search(selector, button_count, "下一页按钮查找")
                        logger.debug(f"🔍 下一页按钮状态 - 数量: {button_count}, 可用: {is_enabled}")
                        
                        if button_count > 0 and is_enabled:
                            logger.info(f"点击下一页按钮，选择器: {selector}")
                            
                            # 优化：减少下一页按钮的等待时间
                            logger.debug("📜 滚动到下一页按钮位置")
                            await button.scroll_into_view_if_needed()
                            
                            wait_time = TIMING_CONFIG["pagination_wait"]
                            logger.debug(f"⏱️ 分页等待: {wait_time}ms")
                            await self.page.wait_for_timeout(wait_time)
                            
                            logger.debug("🖱️ 点击下一页按钮")
                            await button.click()
                            
                            # 修复：避免使用networkidle，改用domcontentloaded提高速度
                            logger.debug("⏳ 等待下一页加载完成")
                            await self.page.wait_for_load_state('domcontentloaded', timeout=TIMING_CONFIG["network_timeout"])
                            
                            post_wait = TIMING_CONFIG["post_action_wait"]
                            logger.debug(f"⏱️ 操作后等待: {post_wait}ms")
                            await self.page.wait_for_timeout(post_wait)
                            
                            button_found = True
                            logger.info(f"成功点击下一页按钮")
                            log_page_state(self.page, "下一页点击完成")
                            break
                            
                    except Exception as e:
                        logger.debug(f"下一页选择器 {selector} 不可用: {e}")
                        continue
            
            log_pagination_details(target_page_num, None, button_found)
            return button_found
            
        except Exception as e:
            log_exception_context(f"导航到第{target_page_num}页", e, {"target_page": target_page_num})
            logger.error(f"导航到第{target_page_num}页失败: {e}")
            return False
            
    def check_videos_too_old(self, page_videos, start_date):
        """检查页面中的视频是否都太旧，超出了日期范围"""
        if not page_videos:
            return False
            
        # 转换start_date为时间戳
        start_timestamp = datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        
        # 检查页面中是否有视频在日期范围内
        valid_videos = 0
        for video in page_videos:
            if video.get('created', 0) >= start_timestamp:
                valid_videos += 1
        
        # 如果没有视频在日期范围内，说明视频太旧了
        too_old = valid_videos == 0
        if too_old:
            logger.info(f"页面中所有 {len(page_videos)} 个视频都早于起始日期 {start_date}，停止翻页")
        
        return too_old

    def parse_videos_from_html(self, html_content):
        """解析HTML内容获取视频数据 - 性能优化版本"""
        logger.info("🎬 开始解析HTML内容获取视频数据")
        if not BS4_AVAILABLE:
            logger.error("BeautifulSoup4 not available, cannot parse HTML content")
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info(f"📄 HTML内容长度: {len(html_content)} 字符")
        
        # 性能优化：直接调用优化后的解析函数
        videos = self._parse_videos_from_html_elements(soup)
        
        # 只在调试模式启用时记录详细的视频解析信息
        if DEBUG_CONFIG.get("enabled", False) and DEBUG_CONFIG.get("log_video_parsing", False):
            log_video_parsing_details(videos, "HTML解析完成")
            
        return videos
    
    def _parse_videos_from_html_elements(self, soup):
        """从HTML元素解析视频数据 - 性能优化版本，减少日志开销"""
        videos = []
        logger.info("🔍 开始从HTML元素解析视频数据")
        
        # 优化：使用更精确的选择器，减少查找时间
        video_cards = soup.select('.small-item, .bili-video-card')
        logger.info(f"📄 找到 {len(video_cards)} 个视频卡片元素")
        
        # 性能优化：批量处理，减少单个视频的日志开销
        parsed_count = 0
        failed_count = 0
        
        for i, card in enumerate(video_cards):
            try:
                # 优化：直接查找a标签，减少条件判断
                link = card.find('a', href=True)
                if not link:
                    failed_count += 1
                    continue
                    
                href = link['href']
                aid = 0
                
                # 优化：使用更快的字符串匹配
                if '/video/av' in href:
                    aid_match = re.search(r'/video/av(\d+)', href)
                    if aid_match:
                        aid = int(aid_match.group(1))
                elif '/video/BV' in href:
                    # 优化：简化BV号处理
                    bv_match = re.search(r'/video/(BV\w+)', href)
                    if bv_match:
                        aid = abs(hash(bv_match.group(1))) % (10**9)
                
                # 优化：简化标题提取
                title = link.get('title', '') or link.get_text(strip=True) or ''
                
                # 优化：提取播放量和评论数 - 使用更精确的选择器
                view_count = 0
                comment_count = 0
                
                # 优化：使用select查找统计数据，更快
                stats_spans = card.select('.bili-video-card__stats span, .stats span, .count span')
                
                if len(stats_spans) >= 2:
                    view_text = stats_spans[0].get_text(strip=True)
                    comment_text = stats_spans[1].get_text(strip=True)
                    
                    view_count = self._parse_stats_number(view_text)
                    comment_count = self._parse_stats_number(comment_text)
                
                # 优化：简化时间戳提取
                created_timestamp = self._extract_publish_timestamp_fast(card)
                
                if aid > 0:
                    video_data = {
                        'aid': aid,
                        'view': view_count,
                        'comment': comment_count,
                        'title': title,
                        'created': created_timestamp
                    }
                    videos.append(video_data)
                    parsed_count += 1
                    
                    # 只在调试模式下输出详细信息，并且只输出前3个视频作为示例
                    if DEBUG_CONFIG.get("enabled", False) and DEBUG_CONFIG.get("log_video_parsing", False) and parsed_count <= 3:
                        logger.debug(f"🎬 视频 {parsed_count}: {title[:30]}{'...' if len(title) > 30 else ''}, AID={aid}, 播放={view_count}, 评论={comment_count}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                # 只在调试模式下输出解析错误的详细信息
                if DEBUG_CONFIG.get("enabled", False):
                    log_exception_context(f"解析第{i+1}个视频卡片", e, {"card_index": i})
                continue
        
        logger.info(f"从HTML元素解析到 {len(videos)} 个视频，成功 {parsed_count} 个，失败 {failed_count} 个")
        
        # 在调试模式下输出更多详细信息
        if DEBUG_CONFIG.get("enabled", False) and DEBUG_CONFIG.get("log_video_parsing", False):
            logger.debug(f"📊 解析统计 - 总卡片: {len(video_cards)}, 成功解析: {parsed_count}, 解析失败: {failed_count}")
            if parsed_count > 3:
                logger.debug(f"... 还有 {parsed_count - 3} 个视频已成功解析（详细信息已省略以提高性能）")
        
        return videos
    
    def _parse_stats_number(self, text):
        """解析统计数字，支持中文数字格式"""
        if not text:
            return 0
            
        # 移除非数字字符，保留数字、小数点和中文单位
        text = re.sub(r'[^\d.\u4e00-\u9fff万千百十亿]', '', text)
        
        try:
            # 处理中文数字单位
            if '万' in text:
                num_str = text.replace('万', '')
                if num_str:
                    return int(float(num_str) * 10000)
            elif '千' in text:
                num_str = text.replace('千', '')
                if num_str:
                    return int(float(num_str) * 1000)
            elif '百' in text:
                num_str = text.replace('百', '')
                if num_str:
                    return int(float(num_str) * 100)
            elif '亿' in text:
                num_str = text.replace('亿', '')
                if num_str:
                    return int(float(num_str) * 100000000)
            else:
                # 纯数字
                num_match = re.search(r'[\d.]+', text)
                if num_match:
                    return int(float(num_match.group()))
        except (ValueError, AttributeError):
            pass
            
        return 0

    def _extract_publish_timestamp_fast(self, card):
        """快速提取发布时间戳 - 性能优化版本，减少日志开销"""
        try:
            # 优化：只检查最常见的时间选择器
            time_selectors = [
                '.bili-video-card__subtitle',
                'span[title]',
                '.time',
            ]
            
            for selector in time_selectors:
                time_elements = card.select(selector)
                for elem in time_elements:
                    # 检查元素的时间属性
                    for attr in ['title', 'data-time', 'datetime']:
                        time_str = elem.get(attr, '')
                        if time_str:
                            timestamp = self._parse_time_string(time_str)
                            if timestamp > 0:
                                return timestamp
                    
                    # 检查元素文本内容
                    text = elem.get_text(strip=True)
                    if text:
                        timestamp = self._parse_time_string(text)
                        if timestamp > 0:
                            return timestamp
        except Exception:
            # 性能优化：移除不必要的调试日志，减少IO开销
            pass
        
        return 0

    def _extract_publish_timestamp(self, card):
        """从视频卡片提取发布时间戳"""
        try:
            # 优先使用B站具体的时间显示位置选择器
            bilibili_time_selectors = [
                # B站视频卡片的subtitle区域（用户提供的具体选择器）
                '.bili-video-card__subtitle',
                '.bili-video-card__details .bili-video-card__subtitle',
                # 其他常见的时间选择器
                'span[title]',  # 带title属性的span
                '.time',        # class包含time的元素
                '.date',        # class包含date的元素
                '.pubdate',     # 发布日期类
                '.upload-time', # 上传时间类
                'time',         # time标签
                '[data-time]',  # 带data-time属性的元素
            ]
            
            # 遍历时间选择器寻找时间信息
            for selector in bilibili_time_selectors:
                time_elements = card.select(selector)
                for elem in time_elements:
                    # 检查title属性
                    title_text = elem.get('title', '')
                    if title_text:
                        timestamp = self._parse_time_string(title_text)
                        if timestamp > 0:
                            logger.debug(f"从title属性提取时间戳: {title_text} -> {timestamp}")
                            return timestamp
                    
                    # 检查data-time属性
                    data_time = elem.get('data-time', '')
                    if data_time:
                        try:
                            timestamp = int(data_time)
                            logger.debug(f"从data-time属性提取时间戳: {data_time}")
                            return timestamp
                        except ValueError:
                            pass
                    
                    # 检查元素文本内容
                    text_content = elem.get_text(strip=True)
                    if text_content:
                        timestamp = self._parse_time_string(text_content)
                        if timestamp > 0:
                            logger.debug(f"从文本内容提取时间戳: {text_content} -> {timestamp}")
                            return timestamp
            
            # 如果没有找到具体时间，在整个卡片中搜索时间模式
            time_patterns = [
                # B站时间格式模式（处理格式不统一问题）
                r'(\d+小时前)',               # X小时前（24小时内）
                r'(\d+分钟前)',               # X分钟前
                r'(\d+天前)',                 # X天前
                r'(\d{1,2}-\d{1,2})',        # MM-DD format（24小时外）
                r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD format
                r'(\d{4}/\d{1,2}/\d{1,2})',  # YYYY/MM/DD format
                r'(\d{1,2}/\d{1,2})',        # MM/DD format
                r'(\d+个月前)',               # X个月前
                r'(\d+年前)',                 # X年前
            ]
            
            card_text = card.get_text()
            for pattern in time_patterns:
                match = re.search(pattern, card_text)
                if match:
                    timestamp = self._parse_time_string(match.group(1))
                    if timestamp > 0:
                        logger.debug(f"从卡片文本提取时间戳: {match.group(1)} -> {timestamp}")
                        return timestamp
            
        except Exception as e:
            logger.debug(f"提取时间戳失败: {e}")
        
        # 如果无法提取时间戳，返回当前时间作为fallback
        logger.debug("无法从HTML提取发布时间，使用当前时间作为fallback")
        return int(time.time())
    
    def _parse_time_string(self, time_str):
        """
        解析时间字符串为时间戳
        处理B站时间显示的格式不统一问题：
        - 24小时内：显示小时格式（如"2小时前"）
        - 24小时外：显示日期格式（如"01-15"）
        """
        try:
            current_time = datetime.datetime.now()
            time_str = time_str.strip()
            
            # 处理相对时间格式（24小时内常见）
            if '小时前' in time_str:
                hours_match = re.search(r'(\d+)小时前', time_str)
                if hours_match:
                    hours = int(hours_match.group(1))
                    target_time = current_time - datetime.timedelta(hours=hours)
                    return int(target_time.timestamp())
            elif '分钟前' in time_str:
                minutes_match = re.search(r'(\d+)分钟前', time_str)
                if minutes_match:
                    minutes = int(minutes_match.group(1))
                    target_time = current_time - datetime.timedelta(minutes=minutes)
                    return int(target_time.timestamp())
            elif '天前' in time_str:
                days_match = re.search(r'(\d+)天前', time_str)
                if days_match:
                    days = int(days_match.group(1))
                    target_time = current_time - datetime.timedelta(days=days)
                    return int(target_time.timestamp())
            elif '个月前' in time_str:
                months_match = re.search(r'(\d+)个月前', time_str)
                if months_match:
                    months = int(months_match.group(1))
                    target_time = current_time - datetime.timedelta(days=months * 30)  # 近似处理
                    return int(target_time.timestamp())
            elif '年前' in time_str:
                years_match = re.search(r'(\d+)年前', time_str)
                if years_match:
                    years = int(years_match.group(1))
                    target_time = current_time - datetime.timedelta(days=years * 365)  # 近似处理
                    return int(target_time.timestamp())
            
            # 处理绝对时间格式（24小时外常见，格式不统一问题的核心）
            date_formats = [
                # B站常见的日期格式
                '%Y-%m-%d %H:%M:%S',  # 2024-01-01 12:00:00
                '%Y-%m-%d %H:%M',     # 2024-01-01 12:00
                '%Y-%m-%d',           # 2024-01-01
                '%Y/%m/%d %H:%M:%S',  # 2024/01/01 12:00:00
                '%Y/%m/%d %H:%M',     # 2024/01/01 12:00
                '%Y/%m/%d',           # 2024/01/01
                # 只有月日的格式（B站24小时外常用）
                '%m-%d %H:%M',        # 01-15 12:00 (当年)
                '%m-%d',              # 01-15 (当年，B站常见格式)
                '%m/%d %H:%M',        # 01/15 12:00 (当年)
                '%m/%d',              # 01/15 (当年)
            ]
            
            for fmt in date_formats:
                try:
                    if '%Y' not in fmt:
                        # 处理没有年份的格式（B站格式不统一的重点）
                        # 假设是当年，但需要考虑跨年情况
                        if '%m-%d' in fmt:
                            # 处理 "01-15" 格式
                            parsed_time = datetime.datetime.strptime(f"{current_time.year}-{time_str}", f"%Y-{fmt}")
                        elif '%m/%d' in fmt:
                            # 处理 "01/15" 格式
                            parsed_time = datetime.datetime.strptime(f"{current_time.year}-{time_str.replace('/', '-')}", f"%Y-%m-%d")
                        else:
                            parsed_time = datetime.datetime.strptime(time_str, fmt)
                        
                        # 如果解析的日期是未来的日期，那么应该是去年的
                        if parsed_time > current_time:
                            parsed_time = parsed_time.replace(year=current_time.year - 1)
                        
                    else:
                        parsed_time = datetime.datetime.strptime(time_str, fmt)
                    
                    return int(parsed_time.timestamp())
                except ValueError:
                    continue
            
            # 尝试提取纯数字日期格式
            date_match = re.search(r'(\d{1,2})-(\d{1,2})', time_str)
            if date_match:
                month, day = int(date_match.group(1)), int(date_match.group(2))
                try:
                    parsed_time = datetime.datetime(current_time.year, month, day)
                    # 如果是未来日期，则认为是去年
                    if parsed_time > current_time:
                        parsed_time = parsed_time.replace(year=current_time.year - 1)
                    return int(parsed_time.timestamp())
                except ValueError:
                    pass
                    
        except Exception as e:
            logger.debug(f"解析时间字符串失败 '{time_str}': {e}")
        
        return 0


async def fetch_videos(uid, start_date, end_date, extended_pages=False, headless=None):
    """
    获取指定日期范围内的视频数据 (使用Playwright浏览器自动化)
    
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param extended_pages: 是否启用扩展页数爬取 (用于历史数据计算，获取更多视频)
    :param headless: 是否使用无头模式 (None: 使用配置文件设置, True/False: 覆盖配置)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright库不可用，请安装: pip install playwright && playwright install chromium")
    
    logger.info(f"开始使用Playwright模式获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
    return await fetch_videos_playwright(uid, start_date, end_date, extended_pages, headless)




async def fetch_videos_playwright(uid, start_date, end_date, extended_pages=False, headless=None):
    """
    使用Playwright真实浏览器获取视频数据
    
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param extended_pages: 是否启用扩展页数爬取 (获取更多视频数据，用于历史计算)
    :param headless: 是否使用无头模式 (None: 使用配置文件设置, True/False: 覆盖配置)
    :return: 视频列表
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright库不可用，请安装: pip install playwright && playwright install chromium")
    
    # 记录函数调用参数
    logger.debug(f"🎬 Playwright模式参数:")
    logger.debug(f"  UID: {uid}")
    logger.debug(f"  日期范围: {start_date} 至 {end_date}")
    logger.debug(f"  扩展页数: {extended_pages}")
    logger.debug(f"  无头模式: {headless}")
    
    # 如果未指定headless参数，使用配置文件中的设置
    if headless is None:
        headless = BROWSER_CONFIG["headless"]
        logger.debug(f"  使用配置文件中的无头模式设置: {headless}")
    
    # 记录当前配置状态
    log_configuration_state()
    
    all_videos = []
    
    for attempt in range(BROWSER_CONFIG["retry_attempts"]):
        try:
            log_retry_attempt(attempt, BROWSER_CONFIG["retry_attempts"], "开始尝试", None)
            logger.info(f"Playwright模式 - 第 {attempt + 1} 次尝试获取视频数据...")
            
            async with PlaywrightBrowserSimulator(headless=headless) as browser:
                page = 1
                consecutive_failures = 0  # 连续失败页数
                max_consecutive_failures = 2  # 允许的最大连续失败页数
                consecutive_empty_pages = 0  # 连续空页数（没有符合日期范围的视频）
                max_consecutive_empty = 3  # 允许的最大连续空页数
                
                # 优化：减少最大页数限制，提高爬取效率
                if extended_pages:
                    max_pages = 30  # 扩展模式：减少页数限制，依赖智能停止
                    logger.info("启用扩展爬取模式，使用智能分页检测获取更多视频数据")
                    logger.debug(f"📄 扩展模式最大页数: {max_pages}")
                else:
                    max_pages = 15  # 标准模式：减少页数限制，依赖智能停止
                    logger.info("使用智能分页检测获取视频数据")
                    logger.debug(f"📄 标准模式最大页数: {max_pages}")
                
                while page <= max_pages:
                    try:
                        logger.info(f"正在获取第 {page} 页数据...")
                        logger.debug(f"📄 当前页面状态 - 页数: {page}/{max_pages}, 连续失败: {consecutive_failures}, 连续空页: {consecutive_empty_pages}")
                        
                        # 首页直接导航，后续页面通过点击分页按钮导航
                        is_first_page = (page == 1)
                        html_content = await browser.fetch_user_videos(uid, page, is_first_page=is_first_page)
                        
                        # 如果获取内容失败（比如点击按钮失败），停止翻页
                        if html_content is None:
                            logger.info(f"第 {page} 页无法获取内容（可能没有更多页面），停止翻页")
                            break
                        
                        logger.debug(f"📄 第 {page} 页HTML内容长度: {len(html_content) if html_content else 0} 字符")
                        
                        # 检查分页信息
                        pagination_info = await browser.check_pagination_info()
                        logger.debug(f"📄 第 {page} 页分页信息: {pagination_info}")
                        
                        # 解析视频数据
                        page_videos = browser.parse_videos_from_html(html_content)
                        log_video_parsing_details(page_videos, f"第{page}页解析结果")
                        
                        if not page_videos:
                            logger.info(f"第 {page} 页没有更多视频数据，停止翻页")
                            break
                        
                        logger.info(f"第 {page} 页成功解析到 {len(page_videos)} 个视频")
                        
                        # 检查视频是否太旧
                        if browser.check_videos_too_old(page_videos, start_date):
                            logger.info("检测到视频太旧，停止翻页")
                            break
                        
                        # 筛选指定日期范围内的视频
                        valid_videos_count = 0
                        for video in page_videos:
                            if video['created'] > 0:
                                pubdate = datetime.datetime.fromtimestamp(video['created']).strftime("%Y-%m-%d")
                                if start_date <= pubdate <= end_date:
                                    video['pubdate'] = pubdate
                                    all_videos.append(video)
                                    valid_videos_count += 1
                        
                        logger.info(f"第 {page} 页有 {valid_videos_count} 个视频符合日期范围 {start_date} 至 {end_date}")
                        
                        # 智能停止条件
                        if valid_videos_count == 0:
                            consecutive_empty_pages += 1
                            logger.info(f"连续 {consecutive_empty_pages} 页没有符合条件的视频")
                            if consecutive_empty_pages >= max_consecutive_empty:
                                logger.info("连续多页没有符合条件的视频，停止翻页")
                                break
                        else:
                            consecutive_empty_pages = 0  # 重置连续空页计数
                        
                        # 检查是否还有下一页
                        if not pagination_info['has_next']:
                            logger.info("检测到没有下一页，停止翻页")
                            break
                        
                        # 如果当前页已经是总页数，也停止
                        if pagination_info['total_pages'] > 1 and page >= pagination_info['total_pages']:
                            logger.info(f"已到达最后一页（{pagination_info['total_pages']}），停止翻页")
                            break
                        
                        # 重置连续失败计数
                        consecutive_failures = 0
                        page += 1
                        
                        # 添加页面间隔，避免被检测为爬虫 - 使用动态时间配置
                        await asyncio.sleep(random.uniform(TIMING_CONFIG["page_interval_min"], TIMING_CONFIG["page_interval_max"]))
                        
                    except Exception as e:
                        consecutive_failures += 1
                        logger.error(f"获取第 {page} 页数据失败 (连续失败 {consecutive_failures} 次): {e}")
                        
                        # 如果连续失败次数超过阈值，停止翻页
                        if consecutive_failures >= max_consecutive_failures:
                            logger.error(f"连续 {consecutive_failures} 页解析失败，停止翻页")
                            break
                        
                        # 否则继续下一页
                        page += 1
                        await asyncio.sleep(random.uniform(TIMING_CONFIG["failure_wait_min"], TIMING_CONFIG["failure_wait_max"]))
                
                
                if all_videos:
                    logger.info(f"Playwright模式成功获取到 {len(all_videos)} 个符合条件的视频 (日期范围: {start_date} 至 {end_date})")
                    # 添加时间戳验证日志
                    valid_timestamps = sum(1 for video in all_videos if video.get('created', 0) > 0)
                    logger.info(f"其中 {valid_timestamps} 个视频有有效的时间戳信息")
                    return all_videos
                else:
                    raise Exception(f"未获取到符合日期范围 {start_date} 至 {end_date} 的任何视频数据")
                    
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"第 {attempt + 1} 次尝试失败: {error_msg}")
            
            if attempt < BROWSER_CONFIG["retry_attempts"] - 1:
                # 使用动态重试延迟
                delay = BROWSER_CONFIG["retry_delay"] * (1.5 ** attempt)
                logger.info(f"将在 {delay} 秒后重试...")
                await asyncio.sleep(delay)
            else:
                logger.error("所有重试尝试均失败")
    
    # 如果所有重试尝试均失败，抛出最终错误
    logger.error("所有重试尝试均失败")
    raise Exception("无法获取视频数据")


def configure_browser_settings(**kwargs):
    """
    配置浏览器设置
    
    可用参数:
    - timeout: 超时时间
    - retry_attempts: 重试次数
    - retry_delay: 重试延迟
    - page_delay: 页面间隔
    - headless: 是否无头模式
    - browser_type: 浏览器类型
    
    时间配置参数:
    - page_load_wait: 页面加载等待时间(毫秒)
    - pagination_wait: 分页点击等待时间(毫秒)
    - post_action_wait: 操作后等待时间(毫秒)
    - page_interval_min: 页面间最小间隔(秒)
    - page_interval_max: 页面间最大间隔(秒)
    - network_timeout: 网络超时(毫秒)
    - element_timeout: 元素等待超时(毫秒)
    """
    global TIMING_CONFIG
    
    logger.debug(f"🔧 配置浏览器设置，参数: {kwargs}")
    
    # 处理浏览器配置
    for key, value in kwargs.items():
        if key in BROWSER_CONFIG:
            old_value = BROWSER_CONFIG[key]
            BROWSER_CONFIG[key] = value
            logger.info(f"已更新浏览器配置 {key} = {value}")
            logger.debug(f"  原值: {old_value} -> 新值: {value}")
        elif key in TIMING_CONFIG:
            old_value = TIMING_CONFIG[key]
            TIMING_CONFIG[key] = value
            logger.info(f"已更新时间配置 {key} = {value}")
            logger.debug(f"  原值: {old_value} -> 新值: {value}")
        else:
            logger.warning(f"未知配置项: {key}")
    
    # 记录更新后的配置状态
    if DEBUG_CONFIG.get("enabled", False):
        log_configuration_state()


def enable_fast_mode():
    """启用快速模式 - 一键优化性能"""
    logger.debug("⚡ 启用快速模式，更新配置...")
    
    old_timing = TIMING_CONFIG.copy()
    old_headless = BROWSER_CONFIG["headless"]
    
    TIMING_CONFIG.update({
        "page_load_wait": 150,
        "pagination_wait": 50,
        "post_action_wait": 200,
        "page_interval_min": 0.2,
        "page_interval_max": 0.4,
        "network_timeout": 4000,
        "element_timeout": 2000,
    })
    BROWSER_CONFIG["headless"] = True  # 启用无头模式提高速度
    
    logger.info("已启用快速模式：无头浏览器 + 最短等待时间")
    
    if DEBUG_CONFIG.get("enabled", False):
        logger.debug("📊 快速模式配置变更:")
        for key, new_value in TIMING_CONFIG.items():
            old_value = old_timing.get(key, "N/A")
            if old_value != new_value:
                logger.debug(f"  {key}: {old_value} -> {new_value}")
        logger.debug(f"  headless: {old_headless} -> {BROWSER_CONFIG['headless']}")


def enable_stable_mode():
    """启用稳定模式 - 确保最大兼容性"""
    logger.debug("🛡️ 启用稳定模式，更新配置...")
    
    old_timing = TIMING_CONFIG.copy()
    old_headless = BROWSER_CONFIG["headless"]
    
    TIMING_CONFIG.update({
        "page_load_wait": 300,
        "pagination_wait": 200,
        "post_action_wait": 500,
        "page_interval_min": 0.5,
        "page_interval_max": 1.0,
        "network_timeout": 8000,
        "element_timeout": 5000,
    })
    BROWSER_CONFIG["headless"] = False  # 显示浏览器便于调试
    
    logger.info("已启用稳定模式：显示浏览器 + 较长等待时间")
    
    if DEBUG_CONFIG.get("enabled", False):
        logger.debug("📊 稳定模式配置变更:")
        for key, new_value in TIMING_CONFIG.items():
            old_value = old_timing.get(key, "N/A")
            if old_value != new_value:
                logger.debug(f"  {key}: {old_value} -> {new_value}")
        logger.debug(f"  headless: {old_headless} -> {BROWSER_CONFIG['headless']}")


def get_troubleshooting_info():
    """
    返回故障排除信息
    """
    info = [
        "=== 李大霄指数计算程序故障排除信息 ===",
        f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Playwright可用: {'是' if PLAYWRIGHT_AVAILABLE else '否'}",
        "",
        "获取模式: Playwright浏览器自动化 (最强反检测能力)",
        "",
        "当前配置:",
        f"- 超时时间: {BROWSER_CONFIG.get('timeout', 'N/A')} 秒",
        f"- 重试次数: {BROWSER_CONFIG.get('retry_attempts', 'N/A')} 次",
        f"- 重试延迟: {BROWSER_CONFIG.get('retry_delay', 'N/A')} 秒",
        f"- 页面间隔: {BROWSER_CONFIG.get('page_delay', 'N/A')} 秒",
        f"- 无头模式: {BROWSER_CONFIG.get('headless', 'N/A')}",
        f"- 浏览器类型: {BROWSER_CONFIG.get('browser_type', 'N/A')}",
        "",
        "时间配置:",
        f"- 页面加载等待: {TIMING_CONFIG.get('page_load_wait', 'N/A')} 毫秒",
        f"- 分页等待: {TIMING_CONFIG.get('pagination_wait', 'N/A')} 毫秒",
        f"- 网络超时: {TIMING_CONFIG.get('network_timeout', 'N/A')} 毫秒",
        f"- 性能配置: 页面加载等待={TIMING_CONFIG.get('page_load_wait', 'N/A')}ms, 网络超时={TIMING_CONFIG.get('network_timeout', 'N/A')}ms",
        "",
        "性能优化建议:",
        "• 使用快速模式: 在代码中调用 enable_fast_mode()",
        "• 使用无头模式: python3 lidaxiao.py --headless",
        "• 减少页面数: 使用较小的日期范围",
        "• 直接配置时间: 修改 TIMING_CONFIG 中的参数",
        "",
        "快速优化方法:",
        "1. 导入: from crawler import enable_fast_mode",
        "2. 调用: enable_fast_mode()  # 启用4倍速度优化",
        "3. 或者: configure_browser_settings(page_load_wait=100, network_timeout=3000)",
        "",
        "推荐解决方案:",
        "1. 检查网络连接和防火墙设置",
        "2. 确保Playwright已正确安装: pip install playwright && playwright install chromium",
        "3. 根据需要调整config.py中的时间配置",
        "4. 运行demo.py查看演示功能",
    ]
    return "\n".join(info)