#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据爬取模块 (支持API和Playwright两种模式)
Video Crawling Module (Supports both API and Playwright modes)

This module handles fetching video data from Bilibili using either:
1. Direct API calls (bilibili-api-python library) - faster but may trigger 412 errors  
2. Playwright browser automation - real browser with strongest anti-detection capabilities
"""

import json
import datetime
import random
import asyncio
import logging
import time
import re
from config import API_REQUEST_CONFIG, ERROR_MESSAGES, BROWSER_CONFIG

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup4 not available, HTML parsing will be limited")

try:
    from bilibili_api import user
    API_MODE_AVAILABLE = True
except ImportError:
    API_MODE_AVAILABLE = False
    logging.warning("bilibili-api-python not available, only playwright mode will work")

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, playwright mode disabled")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





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
        if is_first_page:
            # 首页直接导航
            url = f"https://space.bilibili.com/{uid}/video?tid=0&keyword=&order=pubdate"
            
            try:
                # 导航到页面
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                logger.error(f"Playwright导航到页面失败: {e}")
                raise
        else:
            # 非首页通过点击分页按钮导航
            try:
                success = await self.navigate_to_next_page(page_num)
                if not success:
                    logger.warning(f"无法找到或点击第{page_num}页的分页按钮")
                    return None
            except Exception as e:
                logger.error(f"点击分页按钮失败: {e}")
                raise
        
        try:
            # 等待视频列表加载
            await self.page.wait_for_selector('.small-item, .bili-video-card', timeout=15000)
            
            # 滚动页面以触发懒加载
            await self.page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let totalHeight = 0;
                        let distance = 100;
                        let timer = setInterval(() => {
                            let scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if(totalHeight >= scrollHeight){
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            
            # 等待一段时间让内容完全加载
            await self.page.wait_for_timeout(2000)
            
            # 获取页面内容
            content = await self.page.content()
            return content
            
        except Exception as e:
            logger.error(f"Playwright获取页面内容失败: {e}")
            raise

    async def navigate_to_next_page(self, target_page_num):
        """通过点击分页按钮导航到目标页面"""
        try:
            # 等待分页区域加载
            await self.page.wait_for_selector('.vui_pagenation, .page-wrap, .bili-pager', timeout=10000)
            
            # 尝试多种分页按钮选择器
            pagination_selectors = [
                f'.vui_button.vui_pagenation--btn-num:has-text("{target_page_num}")',
                f'.page-item:has-text("{target_page_num}")',
                f'button:has-text("{target_page_num}")',
                f'a:has-text("{target_page_num}")'
            ]
            
            button_found = False
            for selector in pagination_selectors:
                try:
                    # 检查按钮是否存在
                    button = self.page.locator(selector).first
                    if await button.count() > 0:
                        logger.info(f"找到分页按钮，使用选择器: {selector}")
                        
                        # 滚动到按钮位置确保可见
                        await button.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(1000)
                        
                        # 点击按钮
                        await button.click()
                        
                        # 等待页面加载和网络请求完成
                        await self.page.wait_for_load_state('networkidle', timeout=15000)
                        await self.page.wait_for_timeout(2000)  # 额外等待确保内容加载
                        
                        button_found = True
                        logger.info(f"成功点击第{target_page_num}页分页按钮")
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
                
                for selector in next_button_selectors:
                    try:
                        button = self.page.locator(selector).first
                        if await button.count() > 0 and await button.is_enabled():
                            logger.info(f"点击下一页按钮，选择器: {selector}")
                            
                            await button.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(1000)
                            await button.click()
                            
                            await self.page.wait_for_load_state('networkidle', timeout=15000)
                            await self.page.wait_for_timeout(2000)
                            
                            button_found = True
                            logger.info(f"成功点击下一页按钮")
                            break
                            
                    except Exception as e:
                        logger.debug(f"下一页选择器 {selector} 不可用: {e}")
                        continue
            
            return button_found
            
        except Exception as e:
            logger.error(f"导航到第{target_page_num}页失败: {e}")
            return False
            
    def parse_videos_from_html(self, html_content):
        """解析HTML内容获取视频数据"""
        if not BS4_AVAILABLE:
            logger.error("BeautifulSoup4 not available, cannot parse HTML content")
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        videos = []
        
        # 首先尝试从JavaScript状态数据解析
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_content = script.string
            if script_content and 'window.__INITIAL_STATE__' in script_content:
                try:
                    # 提取JSON数据
                    start = script_content.find('window.__INITIAL_STATE__=') + len('window.__INITIAL_STATE__=')
                    end = script_content.find(';(function()', start)
                    if end == -1:
                        end = script_content.find('</script>', start)
                    
                    json_str = script_content[start:end].strip()
                    if json_str.endswith(';'):
                        json_str = json_str[:-1]
                    
                    initial_state = json.loads(json_str)
                    
                    # 从初始状态中提取视频数据
                    if 'space' in initial_state and 'videoList' in initial_state['space']:
                        video_list = initial_state['space']['videoList']
                        if 'list' in video_list and 'vlist' in video_list['list']:
                            for video in video_list['list']['vlist']:
                                videos.append({
                                    'aid': video.get('aid', 0),
                                    'view': video.get('play', 0),
                                    'comment': video.get('comment', 0),
                                    'title': video.get('title', ''),
                                    'created': video.get('created', 0)
                                })
                    
                    if videos:
                        logger.info(f"从JavaScript状态解析到 {len(videos)} 个视频")
                        return videos
                    else:
                        logger.debug("JavaScript状态中没有找到视频数据")
                        
                except json.JSONDecodeError as e:
                    logger.debug(f"解析JSON失败: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"解析初始状态失败: {e}")
                    continue
        
        # 如果JS解析失败，回退到HTML解析
        logger.info("JavaScript状态解析失败，回退到HTML解析")
        return self._parse_videos_from_html_elements(soup)
    
    def _parse_videos_from_html_elements(self, soup):
        """从HTML元素解析视频数据"""
        videos = []
        
        # 查找视频卡片元素
        video_cards = soup.find_all('div', class_=['small-item', 'bili-video-card']) or \
                     soup.find_all('li', class_=['small-item', 'bili-video-card'])
        
        for card in video_cards:
            try:
                # 提取视频链接和aid
                link = card.find('a', href=True)
                if not link:
                    continue
                    
                href = link['href']
                aid = 0
                
                # 提取aid
                if '/video/av' in href:
                    aid_match = re.search(r'/video/av(\d+)', href)
                    if aid_match:
                        aid = int(aid_match.group(1))
                elif '/video/BV' in href:
                    # BV号转换为aid（简化处理，实际可能需要更复杂的转换）
                    bv_match = re.search(r'/video/(BV\w+)', href)
                    if bv_match:
                        # 这里使用BV号的hash作为临时aid
                        aid = abs(hash(bv_match.group(1))) % (10**9)
                
                # 提取标题
                title_elem = card.find('a', {'title': True}) or card.find('h3') or card.find('h4')
                title = title_elem.get('title', '') or title_elem.get_text(strip=True) if title_elem else ''
                
                # 提取播放量和评论数
                view_count = 0
                comment_count = 0
                
                # 查找统计数据
                stats_container = card.find('div', class_=re.compile(r'(stats|count|data)'))
                if stats_container:
                    spans = stats_container.find_all('span')
                    for i, span in enumerate(spans):
                        text = span.get_text(strip=True)
                        number = self._parse_stats_number(text)
                        if i == 0:  # 通常第一个是播放量
                            view_count = number
                        elif i == 1:  # 第二个是评论数
                            comment_count = number
                
                # 提取发布时间戳
                created_timestamp = self._extract_publish_timestamp(card)
                
                if aid > 0:
                    videos.append({
                        'aid': aid,
                        'view': view_count,
                        'comment': comment_count,
                        'title': title,
                        'created': created_timestamp
                    })
                    
            except Exception as e:
                logger.debug(f"解析视频卡片失败: {e}")
                continue
        
        logger.info(f"从HTML元素解析到 {len(videos)} 个视频")
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


async def fetch_videos(uid, start_date, end_date, mode="auto", use_fallback=True, extended_pages=False, headless=None):
    """
    获取指定日期范围内的视频数据 (支持API和Playwright两种模式)
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param mode: 获取模式 ("api", "playwright", "auto")
        - "api": 使用bilibili-api-python库 (快速但可能触发412错误)
        - "playwright": 使用Playwright真实浏览器自动化 (最强反检测能力)
        - "auto": 自动选择 (优先API，失败时切换到Playwright)
    :param use_fallback: 保留参数以保持兼容性 (已停用模拟数据功能)
    :param extended_pages: 是否启用扩展页数爬取 (用于历史数据计算，获取更多视频)
    :param headless: 是否使用无头模式 (仅对Playwright模式有效, None: 使用配置文件设置)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    
    if mode == "api" or (mode == "auto" and API_MODE_AVAILABLE):
        try:
            logger.info(f"开始使用API模式获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
            return await fetch_videos_api(uid, start_date, end_date, extended_pages)
        except Exception as e:
            error_msg = str(e)
            if mode == "api":
                # API模式失败时直接抛出错误
                logger.error(f"API模式获取失败: {error_msg}")
                raise
            else:
                # auto模式下，API失败时切换到Playwright
                logger.warning(f"API模式失败: {error_msg}，切换到Playwright模式")
                return await fetch_videos_playwright(uid, start_date, end_date, use_fallback, extended_pages, headless)
    
    elif mode == "playwright" or mode == "auto":
        logger.info(f"开始使用Playwright模式获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
        return await fetch_videos_playwright(uid, start_date, end_date, use_fallback, extended_pages, headless)
    
    else:
        raise ValueError(f"不支持的模式: {mode}. 支持的模式: 'api', 'playwright', 'auto'。browser模式已移除，请使用playwright模式替代。")


async def fetch_videos_api(uid, start_date, end_date, extended_pages=False):
    """
    使用bilibili-api-python库获取视频数据 (传统API模式)
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param extended_pages: 是否启用扩展页数爬取 (API模式中此参数将被忽略，API会尝试获取所有可用视频)
    :return: 视频列表
    """
    if not API_MODE_AVAILABLE:
        raise ImportError("bilibili-api-python库不可用，请安装或使用浏览器模拟模式")
    
    u = user.User(uid)
    all_videos = []
    pn = 1
    
    logger.info("使用API模式获取视频数据...")
    
    while True:
        try:
            # 调用B站API获取分页视频列表
            res = await u.get_videos(pn=pn, order=user.VideoOrder.PUBDATE)
            if not res["list"]["vlist"]:
                break
                
            for video_info in res["list"]["vlist"]:
                pubdate = datetime.datetime.fromtimestamp(video_info["created"]).strftime("%Y-%m-%d")
                # 仅保留指定日期范围内的视频
                if start_date <= pubdate <= end_date:
                    all_videos.append({
                        "aid": video_info["aid"],
                        "view": int(video_info["play"]),
                        "comment": int(video_info["comment"]),
                        "pubdate": pubdate,
                        "title": video_info["title"],
                        "created": video_info["created"]
                    })
            pn += 1
            
            # 添加请求间隔，避免触发风控
            await asyncio.sleep(API_REQUEST_CONFIG.get("rate_limit_delay", 1))
            
        except Exception as e:
            if "412" in str(e) or "安全风控" in str(e):
                raise SecurityControlException(f"API模式触发安全风控: {e}")
            raise
    
    logger.info(f"API模式成功获取 {len(all_videos)} 个视频")
    return all_videos





async def fetch_videos_playwright(uid, start_date, end_date, use_fallback=True, extended_pages=False, headless=None):
    """
    使用Playwright真实浏览器获取视频数据
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param use_fallback: 保留参数以保持兼容性
    :param extended_pages: 是否启用扩展页数爬取 (获取更多视频数据，用于历史计算)
    :param headless: 是否使用无头模式 (None: 使用配置文件设置, True/False: 覆盖配置)
    :return: 视频列表
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright库不可用，请安装: pip install playwright && playwright install chromium")
    
    # 如果未指定headless参数，使用配置文件中的设置
    if headless is None:
        headless = BROWSER_CONFIG["headless"]
    
    all_videos = []
    
    for attempt in range(API_REQUEST_CONFIG["retry_attempts"]):
        try:
            logger.info(f"Playwright模式 - 第 {attempt + 1} 次尝试获取视频数据...")
            
            async with PlaywrightBrowserSimulator(headless=headless) as browser:
                page = 1
                consecutive_failures = 0  # 连续失败页数
                max_consecutive_failures = 3  # 允许的最大连续失败页数
                
                # 根据是否启用扩展模式动态设置页数限制
                if extended_pages:
                    max_pages = 25  # 扩展模式：最多获取15页数据
                    logger.info("启用扩展爬取模式，将获取更多页面的视频数据")
                else:
                    max_pages = 10  # 标准模式：最多获取5页数据
                
                while page <= max_pages:
                    try:
                        logger.info(f"正在获取第 {page} 页数据...")
                        # 首页直接导航，后续页面通过点击分页按钮导航
                        is_first_page = (page == 1)
                        html_content = await browser.fetch_user_videos(uid, page, is_first_page=is_first_page)
                        
                        # 如果获取内容失败（比如点击按钮失败），停止翻页
                        if html_content is None:
                            logger.info(f"第 {page} 页无法获取内容（可能没有更多页面），停止翻页")
                            break
                        
                        # 解析视频数据
                        page_videos = browser.parse_videos_from_html(html_content)
                        
                        if not page_videos:
                            logger.info(f"第 {page} 页没有更多视频数据，停止翻页")
                            break
                        
                        logger.info(f"第 {page} 页成功解析到 {len(page_videos)} 个视频")
                        
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
                        
                        # 重置连续失败计数
                        consecutive_failures = 0
                        page += 1
                        
                        # 添加页面间隔，避免被检测为爬虫
                        if page <= max_pages:
                            await asyncio.sleep(random.uniform(3, 6))  # Playwright模式使用稍长的延迟
                        
                    except SecurityControlException:
                        logger.error("触发安全风控，停止尝试")
                        raise
                    except Exception as e:
                        consecutive_failures += 1
                        logger.error(f"获取第 {page} 页数据失败 (连续失败 {consecutive_failures} 次): {e}")
                        
                        # 如果连续失败次数超过阈值，停止翻页
                        if consecutive_failures >= max_consecutive_failures:
                            logger.error(f"连续 {consecutive_failures} 页解析失败，停止翻页")
                            break
                        
                        # 否则继续下一页
                        page += 1
                        await asyncio.sleep(random.uniform(2, 4))  # 失败后稍微等待
                
                
                if all_videos:
                    logger.info(f"Playwright模式成功获取到 {len(all_videos)} 个符合条件的视频 (日期范围: {start_date} 至 {end_date})")
                    # 添加时间戳验证日志
                    valid_timestamps = sum(1 for video in all_videos if video.get('created', 0) > 0)
                    logger.info(f"其中 {valid_timestamps} 个视频有有效的时间戳信息")
                    return all_videos
                else:
                    raise Exception(f"未获取到符合日期范围 {start_date} 至 {end_date} 的任何视频数据")
                    
        except SecurityControlException:
            logger.error("触发安全风控，停止重试")
            break
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"第 {attempt + 1} 次尝试失败: {error_msg}")
            
            if attempt < API_REQUEST_CONFIG["retry_attempts"] - 1:
                delay = API_REQUEST_CONFIG["retry_delay"] * (2 ** attempt)
                logger.info(f"将在 {delay} 秒后重试...")
                await asyncio.sleep(delay)
            else:
                logger.error("所有重试尝试均失败")
    
    # 如果所有重试尝试均失败，抛出最终错误
    logger.error("所有重试尝试均失败")
    raise Exception("无法获取视频数据")


class SecurityControlException(Exception):
    """Bilibili安全风控异常"""
    pass





def configure_api_settings(**kwargs):
    """
    配置API和Playwright设置
    
    可用参数:
    - timeout: 超时时间
    - retry_attempts: 重试次数
    - retry_delay: 重试延迟
    - rate_limit_delay: 请求间隔
    """
    for key, value in kwargs.items():
        if key in API_REQUEST_CONFIG:
            API_REQUEST_CONFIG[key] = value
            logger.info(f"已更新 {key} = {value}")
        else:
            logger.warning(f"未知配置项: {key}")


def get_api_troubleshooting_info():
    """
    返回API故障排除信息 (支持API和Playwright两种模式)
    """
    info = [
        "=== 李大霄指数计算程序故障排除信息 ===",
        f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Playwright可用: {'是' if PLAYWRIGHT_AVAILABLE else '否'}",
        "",
        "支持的获取模式:",
        "1. API模式 (api): 使用bilibili-api-python库，速度快但可能触发412错误",
        "2. Playwright模式 (playwright): 使用真实浏览器自动化，最强反检测能力",
        "3. 自动模式 (auto): 优先使用API，失败时自动切换到Playwright",
        "",
        "当前配置:",
        f"- 超时时间: {API_REQUEST_CONFIG.get('timeout', 'N/A')} 秒",
        f"- 重试次数: {API_REQUEST_CONFIG.get('retry_attempts', 'N/A')} 次",
        f"- 重试延迟: {API_REQUEST_CONFIG.get('retry_delay', 'N/A')} 秒",
        f"- 请求间隔: {API_REQUEST_CONFIG.get('rate_limit_delay', 'N/A')} 秒",
        "",
        "推荐解决方案:",
        "1. 使用配置工具: python3 api_config_tool.py safe",
        "2. 尝试Playwright模式: python3 lidaxiao.py --mode playwright",
        "3. 使用演示数据: python3 demo.py",
        "",
        "注意: browser模式已移除，请使用playwright模式替代"
    ]
    return "\n".join(info)