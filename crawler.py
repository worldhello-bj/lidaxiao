#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据爬取模块
Video Crawling Module

This module handles fetching video data from Bilibili API and generating mock data for testing.
"""

from bilibili_api import user, request_settings, ResponseCodeException, NetworkException
import datetime
import random
import asyncio
import logging
from config import API_REQUEST_CONFIG, ERROR_MESSAGES

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_videos(uid, start_date, end_date, use_fallback=True):
    """
    获取指定日期范围内的视频数据 (增强版，处理412安全风控错误)
    :param uid: UP主UID (2137589551)
    :param start_date: 起始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param use_fallback: 是否在API失败时使用模拟数据回退
    :return: 视频列表 [{"aid": 视频ID, "view": 播放量, "comment": 评论数, "pubdate": 发布日期, "title": 标题, "created": 时间戳}]
    """
    # 配置请求设置以降低触发安全风控的概率
    request_settings.set_timeout(API_REQUEST_CONFIG["timeout"])
    request_settings.set_verify_ssl(API_REQUEST_CONFIG["verify_ssl"])
    request_settings.set_trust_env(API_REQUEST_CONFIG["trust_env"])
    
    logger.info(f"开始获取用户 {uid} 在 {start_date} 至 {end_date} 期间的视频数据")
    
    for attempt in range(API_REQUEST_CONFIG["retry_attempts"]):
        try:
            logger.info(f"第 {attempt + 1} 次尝试获取视频数据...")
            
            u = user.User(uid)
            all_videos = []
            pn = 1
            
            while True:
                try:
                    # 添加请求间隔以降低触发风控的概率
                    if pn > 1:
                        await asyncio.sleep(API_REQUEST_CONFIG["rate_limit_delay"])
                    
                    # 调用B站API获取分页视频列表
                    logger.debug(f"获取第 {pn} 页数据...")
                    res = await u.get_videos(pn=pn, order=user.VideoOrder.PUBDATE)
                    
                    if not res["list"]["vlist"]:
                        logger.info(f"已获取所有分页数据，共 {len(all_videos)} 个视频")
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
                    
                except ResponseCodeException as e:
                    error_code = str(e.code) if hasattr(e, 'code') else 'unknown'
                    logger.error(f"API响应错误 (代码: {error_code}): {str(e)}")
                    
                    if '412' in str(e) or error_code == '412':
                        logger.error(ERROR_MESSAGES["412"])
                        raise SecurityControlException(f"触发Bilibili 412安全风控: {str(e)}")
                    
                    # 对于其他响应错误，抛出异常让上层处理
                    raise
                
            logger.info(f"成功获取到 {len(all_videos)} 个符合条件的视频")
            return all_videos
            
        except SecurityControlException:
            # 412安全风控错误，不进行重试，直接进入回退模式
            logger.error("触发安全风控，停止重试")
            break
            
        except (NetworkException, OSError, Exception) as e:
            error_msg = str(e)
            logger.warning(f"第 {attempt + 1} 次尝试失败: {error_msg}")
            
            if attempt < API_REQUEST_CONFIG["retry_attempts"] - 1:
                delay = API_REQUEST_CONFIG["retry_delay"] * (2 ** attempt)  # 指数退避
                logger.info(f"将在 {delay} 秒后重试...")
                await asyncio.sleep(delay)
            else:
                logger.error("所有重试尝试均失败")
    
    # 如果启用回退且API请求失败，使用模拟数据
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
    配置API请求设置
    
    可用参数:
    - proxy: 代理设置 (如: "http://127.0.0.1:8080")
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
        elif key == "proxy":
            # 设置代理
            request_settings.set_proxy(value)
            logger.info(f"已设置代理: {value}")
        else:
            logger.warning(f"未知配置项: {key}")


def get_api_troubleshooting_info():
    """
    返回API故障排除信息
    """
    return f"""
Bilibili API 故障排除指南:

1. 412 安全风控错误解决方案:
   - 降低请求频率: configure_api_settings(rate_limit_delay=3)  
   - 增加重试延迟: configure_api_settings(retry_delay=5)
   - 设置代理: configure_api_settings(proxy="http://proxy:port")
   - 启用回退模式: configure_api_settings(enable_fallback=True)

2. 网络连接问题:
   - 检查防火墙设置
   - 尝试使用代理
   - 增加超时时间: configure_api_settings(timeout=30)

3. 当前配置:
   {API_REQUEST_CONFIG}

4. 推荐设置 (降低风控概率):
   configure_api_settings(
       timeout=15,
       retry_attempts=2, 
       retry_delay=5,
       rate_limit_delay=3,
       enable_fallback=True
   )
"""