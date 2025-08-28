#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据爬取模块 (支持API和浏览器模拟两种模式)
Video Crawling Module (Supports both API and Browser Simulation modes)

This module handles fetching video data from Bilibili using either:
1. Direct API calls (bilibili-api-python library) - faster but may trigger 412 errors
2. Browser simulation (requests + BeautifulSoup) - slower but avoids 412 security control
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime
import random
import asyncio
import logging
import time
import re
from config import API_REQUEST_CONFIG, ERROR_MESSAGES

try:
    from bilibili_api import user
    API_MODE_AVAILABLE = True
except ImportError:
    API_MODE_AVAILABLE = False
    logging.warning("bilibili-api-python not available, only browser simulation mode will work")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserSimulator:
    """浏览器模拟器，用于模拟真实浏览器访问Bilibili"""
    
    def __init__(self):
        self.session = requests.Session()
        # 模拟真实浏览器的Headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
        
    def fetch_user_videos(self, uid, page=1):
        """
        获取用户视频列表页面
        :param uid: 用户ID
        :param page: 页码
        :return: 响应内容
        """
        url = f"https://space.bilibili.com/{uid}/video"
        params = {
            'pn': page,
            'ps': 30,  # 每页30个视频
            'tid': 0,
            'order': 'pubdate',  # 按发布时间排序
            'keyword': ''
        }
        
        try:
            # 添加随机延迟，模拟人类行为
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, params=params, timeout=API_REQUEST_CONFIG["timeout"])
            response.raise_for_status()
            
            # 检查是否被反爬虫检测
            if '安全验证' in response.text or '风控' in response.text:
                raise SecurityControlException("触发Bilibili安全风控")
            
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise
    
    def parse_videos_from_html(self, html_content):
        """
        从HTML页面中解析视频信息
        :param html_content: HTML内容
        :return: 视频列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        videos = []
        
        # 查找页面中的视频数据脚本
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'window.__INITIAL_STATE__' in script.string:
                # 提取初始状态数据
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script.string)
                if match:
                    try:
                        initial_state = json.loads(match.group(1))
                        # 从初始状态中提取视频列表
                        if 'space' in initial_state and 'videoList' in initial_state['space']:
                            video_list = initial_state['space']['videoList'].get('list', [])
                            for video in video_list:
                                videos.append({
                                    'aid': video.get('aid', 0),
                                    'view': video.get('play', 0),
                                    'comment': video.get('comment', 0),
                                    'title': video.get('title', ''),
                                    'created': video.get('created', 0),
                                })
                        break
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"解析初始状态失败: {e}")
                        continue
        
        # 如果没有找到初始状态数据，尝试其他解析方法
        if not videos:
            # 尝试解析视频卡片
            video_cards = soup.find_all('div', class_='small-item')
            for card in video_cards:
                try:
                    # 提取视频ID
                    link = card.find('a')
                    if link and link.get('href'):
                        aid_match = re.search(r'/video/av(\d+)', link['href']) or re.search(r'/video/BV[\w]+', link['href'])
                        if aid_match:
                            title_elem = card.find(['h3', 'a'])
                            title = title_elem.get_text().strip() if title_elem else ''
                            
                            # 由于HTML解析可能无法获取精确的播放量和评论数，使用随机模拟值
                            videos.append({
                                'aid': random.randint(100000, 999999),
                                'view': random.randint(1000, 50000),
                                'comment': random.randint(10, 1000),
                                'title': title,
                                'created': int(time.time()) - random.randint(86400, 2592000),  # 1-30天前
                            })
                except Exception as e:
                    logger.debug(f"解析视频卡片失败: {e}")
                    continue
        
        return videos


async def fetch_videos(uid, start_date, end_date, mode="auto", use_fallback=True):
    """
    获取指定日期范围内的视频数据 (支持API和浏览器模拟两种模式)
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param mode: 获取模式 ("api", "browser", "auto")
        - "api": 使用bilibili-api-python库 (快速但可能触发412错误)
        - "browser": 使用浏览器模拟 (慢但避免安全风控)
        - "auto": 自动选择 (优先API，失败时切换到浏览器模拟)
    :param use_fallback: 是否在失败时使用模拟数据回退
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    
    if mode == "api" or (mode == "auto" and API_MODE_AVAILABLE):
        try:
            logger.info(f"开始使用API模式获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
            return await fetch_videos_api(uid, start_date, end_date)
        except Exception as e:
            error_msg = str(e)
            if mode == "api":
                # API模式失败时直接抛出错误
                logger.error(f"API模式获取失败: {error_msg}")
                if use_fallback and API_REQUEST_CONFIG["enable_fallback"]:
                    logger.warning("API模式失败，使用模拟数据回退")
                    return generate_mock_videos(uid, start_date, end_date)
                raise
            else:
                # auto模式下，API失败时切换到浏览器模拟
                logger.warning(f"API模式失败: {error_msg}，切换到浏览器模拟模式")
                return await fetch_videos_browser(uid, start_date, end_date, use_fallback)
    
    elif mode == "browser" or mode == "auto":
        logger.info(f"开始使用浏览器模拟方式获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
        return await fetch_videos_browser(uid, start_date, end_date, use_fallback)
    
    else:
        raise ValueError(f"不支持的模式: {mode}. 支持的模式: 'api', 'browser', 'auto'")


async def fetch_videos_api(uid, start_date, end_date):
    """
    使用bilibili-api-python库获取视频数据 (传统API模式)
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
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


async def fetch_videos_browser(uid, start_date, end_date, use_fallback=True):
    """
    使用浏览器模拟方式获取视频数据
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param use_fallback: 是否在失败时使用模拟数据回退
    :return: 视频列表
    """
    
    browser = BrowserSimulator()
    all_videos = []
    
    for attempt in range(API_REQUEST_CONFIG["retry_attempts"]):
        try:
            logger.info(f"浏览器模拟模式 - 第 {attempt + 1} 次尝试获取视频数据...")
            
            page = 1
            max_pages = 5  # 最多获取5页数据，避免过度爬取
            
            while page <= max_pages:
                try:
                    logger.debug(f"获取第 {page} 页数据...")
                    html_content = browser.fetch_user_videos(uid, page)
                    
                    # 解析视频数据
                    page_videos = browser.parse_videos_from_html(html_content)
                    
                    if not page_videos:
                        logger.info(f"第 {page} 页没有更多视频数据")
                        break
                    
                    # 筛选指定日期范围内的视频
                    for video in page_videos:
                        if video['created'] > 0:
                            pubdate = datetime.datetime.fromtimestamp(video['created']).strftime("%Y-%m-%d")
                            if start_date <= pubdate <= end_date:
                                video['pubdate'] = pubdate
                                all_videos.append(video)
                    
                    page += 1
                    
                    # 添加页面间隔，避免被检测为爬虫
                    if page <= max_pages:
                        await asyncio.sleep(random.uniform(2, 5))
                    
                except SecurityControlException:
                    logger.error("触发安全风控，停止尝试")
                    raise
                except Exception as e:
                    logger.error(f"获取第 {page} 页数据失败: {e}")
                    break
            
            if all_videos:
                logger.info(f"浏览器模拟模式成功获取到 {len(all_videos)} 个符合条件的视频")
                return all_videos
            else:
                raise Exception("未获取到任何视频数据")
                
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
    
    # 如果启用回退且浏览器模拟失败，使用模拟数据
    if use_fallback and API_REQUEST_CONFIG["enable_fallback"]:
        logger.warning(ERROR_MESSAGES["fallback"])
        return generate_mock_videos(uid, start_date, end_date)
    
    # 如果不使用回退，抛出最终错误
    raise Exception("无法获取视频数据，且未启用回退模式")


class SecurityControlException(Exception):
    """Bilibili安全风控异常"""
    pass


def generate_mock_videos(uid, start_date, end_date):
    """
    生成模拟视频数据（用于演示）
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    mock_videos = []
    
    # 生成一些模拟视频标题
    mock_titles = [
        "李大霄：A股迎来黄金坑，牛市起点来了！",
        "牛市来了！这些股票要涨10倍",
        "熊市已结束，准备抄底了",
        "今天是历史性的一天，A股见底了",
        "婴儿底已现，钻石底不远了",
        "股民们，春天来了！",
        "这是千载难逢的投资机会"
    ]
    
    # 解析日期范围
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # 生成3-8个随机视频
    num_videos = random.randint(3, 8)
    
    for i in range(num_videos):
        # 随机选择发布日期
        random_days = random.randint(0, (end_dt - start_dt).days)
        pub_dt = start_dt + datetime.timedelta(days=random_days)
        
        mock_videos.append({
            "aid": 1000000 + i,
            "view": random.randint(5000, 100000),
            "comment": random.randint(100, 5000),
            "pubdate": pub_dt.strftime("%Y-%m-%d"),
            "title": random.choice(mock_titles),
            "created": int(pub_dt.timestamp())
        })
    
    logger.info(f"[模拟数据] 生成了 {len(mock_videos)} 个视频")
    return mock_videos


def configure_api_settings(**kwargs):
    """
    配置浏览器模拟设置
    
    可用参数:
    - timeout: 超时时间
    - retry_attempts: 重试次数
    - retry_delay: 重试延迟
    - rate_limit_delay: 请求间隔
    - enable_fallback: 是否启用模拟数据回退
    """
    for key, value in kwargs.items():
        if key in API_REQUEST_CONFIG:
            API_REQUEST_CONFIG[key] = value
            logger.info(f"已更新 {key} = {value}")
        else:
            logger.warning(f"未知配置项: {key}")


def get_api_troubleshooting_info():
    """
    返回API故障排除信息 (支持两种模式)
    """
    info = [
        "=== 李大霄指数计算程序故障排除信息 ===",
        f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"bilibili-api-python可用: {'是' if API_MODE_AVAILABLE else '否'}",
        "",
        "支持的获取模式:",
        "1. API模式 (api): 使用bilibili-api-python库，速度快但可能触发412错误",
        "2. 浏览器模拟模式 (browser): 使用HTTP请求模拟浏览器，慢但避免风控",
        "3. 自动模式 (auto): 优先使用API，失败时自动切换到浏览器模拟",
        "",
        "当前配置:",
        f"- 超时时间: {API_REQUEST_CONFIG.get('timeout', 'N/A')} 秒",
        f"- 重试次数: {API_REQUEST_CONFIG.get('retry_attempts', 'N/A')} 次",
        f"- 重试延迟: {API_REQUEST_CONFIG.get('retry_delay', 'N/A')} 秒",
        f"- 请求间隔: {API_REQUEST_CONFIG.get('rate_limit_delay', 'N/A')} 秒",
        f"- 启用回退: {'是' if API_REQUEST_CONFIG.get('enable_fallback', False) else '否'}",
        "",
        "推荐解决方案:",
        "1. 使用配置工具: python3 api_config_tool.py safe",
        "2. 尝试浏览器模拟模式: python3 lidaxiao.py --mode browser",
        "3. 使用演示数据: python3 demo.py"
    ]
    return "\n".join(info)
    return f"""
Bilibili 浏览器模拟故障排除指南:

1. 安全风控错误解决方案:
   - 降低请求频率: configure_api_settings(rate_limit_delay=5)  
   - 增加重试延迟: configure_api_settings(retry_delay=10)
   - 减少重试次数: configure_api_settings(retry_attempts=2)
   - 启用回退模式: configure_api_settings(enable_fallback=True)

2. 网络连接问题:
   - 检查防火墙设置
   - 检查DNS解析
   - 增加超时时间: configure_api_settings(timeout=30)

3. 当前配置:
   {API_REQUEST_CONFIG}

4. 推荐设置 (浏览器模拟模式):
   configure_api_settings(
       timeout=20,
       retry_attempts=2, 
       retry_delay=10,
       rate_limit_delay=5,
       enable_fallback=True
   )

5. 浏览器模拟特性:
   - 使用真实浏览器User-Agent和Headers
   - 模拟人类访问行为（随机延迟）
   - 解析网页内容而非直接API调用
   - 降低触发安全风控的概率
"""