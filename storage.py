#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据存储模块
Data Storage Module

This module handles JSON file operations for saving and loading index data.
"""

import json
import os


def save_daily_data(date, index_value):
    """
    保存单日JSON文件
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    """
    from config import DAILY_FILE_TEMPLATE
    
    filename = DAILY_FILE_TEMPLATE.format(date=date)
    with open(filename, "w", encoding='utf-8') as f:
        json.dump({"date": date, "index": index_value}, f, indent=2, ensure_ascii=False)


def update_history_data(date, index_value, data_type="current", source="calculation", metadata=None):
    """
    更新累积历史JSON文件 - 统一的历史数据存储
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    :param data_type: 数据类型 ("current", "historical", "estimated")
    :param source: 数据来源 ("calculation", "batch_historical", "weekly_historical", etc.)
    :param metadata: 额外元数据 (dict)
    """
    from config import HISTORY_FILE
    import datetime
    
    history_structure = load_master_history_data()
    
    # 准备新的数据条目
    entry = {
        "date": date,
        "index": round(float(index_value), 2),
        "data_type": data_type,
        "source": source,
        "updated_at": datetime.datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # 检查是否已存在当日数据，如果存在则更新，否则添加
    updated = False
    for item in history_structure["data"]:
        if item["date"] == date:
            # 更新现有条目，保留创建时间
            entry["created_at"] = item.get("created_at", entry["updated_at"])
            history_structure["data"][history_structure["data"].index(item)] = entry
            updated = True
            break
    
    if not updated:
        entry["created_at"] = entry["updated_at"]
        history_structure["data"].append(entry)
    
    # 按日期排序
    history_structure["data"].sort(key=lambda x: x["date"])
    
    # 更新统计信息
    history_structure["statistics"]["total_entries"] = len(history_structure["data"])
    history_structure["statistics"]["last_updated"] = entry["updated_at"]
    if history_structure["data"]:
        history_structure["statistics"]["date_range"]["start"] = history_structure["data"][0]["date"]
        history_structure["statistics"]["date_range"]["end"] = history_structure["data"][-1]["date"]
    
    # 保存到主历史文件
    save_master_history_data(history_structure)


def load_history_data():
    """
    加载历史数据 - 保持向后兼容
    :return: 历史数据列表，如果文件不存在则返回空列表
    """
    from config import HISTORY_FILE
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            # 如果是新的结构化格式，返回数据部分；如果是旧格式，直接返回
            if isinstance(data, dict) and "data" in data:
                return [{"date": item["date"], "index": item["index"]} for item in data["data"]]
            else:
                return data  # 旧格式
    return []


def load_master_history_data():
    """
    加载完整的主历史数据结构
    :return: 完整的历史数据结构
    """
    from config import HISTORY_FILE
    import datetime
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                # 如果是新的结构化格式，直接返回
                if isinstance(data, dict) and "version" in data:
                    return data
                # 如果是旧格式，转换为新格式
                elif isinstance(data, list):
                    return _migrate_legacy_history_data(data)
        except (json.JSONDecodeError, KeyError):
            pass
    
    # 返回默认的空结构
    return {
        "version": "2.0",
        "description": "李大霄指数历史数据统一存储文件 - 长期计算备份",
        "created_at": datetime.datetime.now().isoformat(),
        "statistics": {
            "total_entries": 0,
            "last_updated": None,
            "date_range": {
                "start": None,
                "end": None
            },
            "data_types": {
                "current": 0,
                "historical": 0,
                "estimated": 0
            }
        },
        "data": []
    }


def save_master_history_data(history_structure):
    """
    保存完整的主历史数据结构
    :param history_structure: 完整的历史数据结构
    """
    from config import HISTORY_FILE
    
    # 更新统计信息
    data_types = {"current": 0, "historical": 0, "estimated": 0}
    for item in history_structure["data"]:
        data_type = item.get("data_type", "current")
        if data_type in data_types:
            data_types[data_type] += 1
    history_structure["statistics"]["data_types"] = data_types
    
    with open(HISTORY_FILE, "w", encoding='utf-8') as f:
        json.dump(history_structure, f, indent=2, ensure_ascii=False)


def _migrate_legacy_history_data(legacy_data):
    """
    将旧格式的历史数据迁移到新格式
    :param legacy_data: 旧格式数据列表
    :return: 新格式数据结构
    """
    import datetime
    
    new_structure = {
        "version": "2.0",
        "description": "李大霄指数历史数据统一存储文件 - 长期计算备份",
        "created_at": datetime.datetime.now().isoformat(),
        "migration_note": "从旧格式自动迁移",
        "statistics": {
            "total_entries": len(legacy_data),
            "last_updated": datetime.datetime.now().isoformat(),
            "date_range": {
                "start": None,
                "end": None
            },
            "data_types": {
                "current": len(legacy_data),
                "historical": 0,
                "estimated": 0
            }
        },
        "data": []
    }
    
    # 迁移数据
    for item in legacy_data:
        entry = {
            "date": item["date"],
            "index": item["index"],
            "data_type": "current",  # 假设旧数据都是当前数据
            "source": "legacy_migration",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "metadata": {"migrated_from_legacy": True}
        }
        new_structure["data"].append(entry)
    
    # 排序并更新日期范围
    if new_structure["data"]:
        new_structure["data"].sort(key=lambda x: x["date"])
        new_structure["statistics"]["date_range"]["start"] = new_structure["data"][0]["date"]
        new_structure["statistics"]["date_range"]["end"] = new_structure["data"][-1]["date"]
    
    return new_structure


def save_all_data(date, index_value):
    """
    保存所有数据（单日 + 历史更新）
    :param date: 日期 (YYYY-MM-DD)
    :param index_value: 指数值
    """
    save_daily_data(date, index_value)
    update_history_data(date, index_value, data_type="current", source="daily_calculation")


def consolidate_scattered_files(cleanup_after_consolidation=False):
    """
    整合散落的历史数据文件到主历史文件中
    :param cleanup_after_consolidation: 是否在整合后删除散落的文件
    :return: 整合的文件数量和统计信息
    """
    import glob
    import datetime
    
    consolidated_count = 0
    file_patterns = [
        "historical_batch_*.json",
        "historical_week_*.json",
        "20*.json"  # 单日文件格式
    ]
    
    history_structure = load_master_history_data()
    consolidated_files = []
    
    print("正在扫描和整合散落的历史数据文件...")
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if file_path == "history.json":  # 跳过主历史文件
                continue
                
            try:
                print(f"正在处理: {file_path}")
                with open(file_path, "r", encoding='utf-8') as f:
                    file_data = json.load(f)
                
                if isinstance(file_data, dict):
                    if "results" in file_data:  # 批量历史文件格式
                        for result in file_data["results"]:
                            if "error" not in result:
                                update_history_data(
                                    result["date"], 
                                    result["index"],
                                    data_type="historical", 
                                    source=f"consolidated_from_{os.path.basename(file_path)}",
                                    metadata={"original_file": file_path}
                                )
                                consolidated_count += 1
                    elif "date" in file_data and "index" in file_data:  # 单日文件格式
                        update_history_data(
                            file_data["date"], 
                            file_data["index"],
                            data_type="current", 
                            source=f"consolidated_from_{os.path.basename(file_path)}",
                            metadata={"original_file": file_path}
                        )
                        consolidated_count += 1
                
                consolidated_files.append(file_path)
                
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
    
    # 清理文件（如果请求的话）
    if cleanup_after_consolidation and consolidated_files:
        print(f"正在清理 {len(consolidated_files)} 个已整合的文件...")
        for file_path in consolidated_files:
            try:
                os.remove(file_path)
                print(f"已删除: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")
    
    print(f"整合完成: 处理了 {consolidated_count} 条历史数据记录")
    return {
        "consolidated_count": consolidated_count,
        "processed_files": len(consolidated_files),
        "file_list": consolidated_files
    }


def export_long_term_analysis_data(start_date=None, end_date=None, output_file=None):
    """
    导出长期分析数据
    :param start_date: 开始日期 (YYYY-MM-DD)，None表示从最早开始
    :param end_date: 结束日期 (YYYY-MM-DD)，None表示到最新
    :param output_file: 输出文件名，None表示使用默认名称
    :return: 导出的数据统计信息
    """
    import datetime
    
    history_structure = load_master_history_data()
    data = history_structure["data"]
    
    # 过滤数据
    filtered_data = []
    for item in data:
        item_date = item["date"]
        if start_date and item_date < start_date:
            continue
        if end_date and item_date > end_date:
            continue
        filtered_data.append(item)
    
    # 生成分析数据
    analysis_data = {
        "export_info": {
            "exported_at": datetime.datetime.now().isoformat(),
            "date_range": {
                "start": start_date or (filtered_data[0]["date"] if filtered_data else None),
                "end": end_date or (filtered_data[-1]["date"] if filtered_data else None)
            },
            "total_entries": len(filtered_data)
        },
        "statistics": _calculate_long_term_statistics(filtered_data),
        "data": filtered_data
    }
    
    # 保存到文件
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"lidaxiao_long_term_analysis_{timestamp}.json"
    
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"长期分析数据已导出到: {output_file}")
    print(f"包含 {len(filtered_data)} 条记录")
    
    return analysis_data["export_info"]


def _calculate_long_term_statistics(data):
    """
    计算长期统计信息
    :param data: 历史数据列表
    :return: 统计信息字典
    """
    if not data:
        return {}
    
    indices = [item["index"] for item in data]
    
    stats = {
        "index_statistics": {
            "min": min(indices),
            "max": max(indices),
            "average": sum(indices) / len(indices),
            "median": sorted(indices)[len(indices) // 2],
        },
        "data_type_distribution": {},
        "source_distribution": {},
        "time_span_days": None
    }
    
    # 数据类型分布
    for item in data:
        data_type = item.get("data_type", "unknown")
        stats["data_type_distribution"][data_type] = stats["data_type_distribution"].get(data_type, 0) + 1
    
    # 数据来源分布
    for item in data:
        source = item.get("source", "unknown")
        stats["source_distribution"][source] = stats["source_distribution"].get(source, 0) + 1
    
    # 时间跨度
    if len(data) >= 2:
        from datetime import datetime
        start_date = datetime.strptime(data[0]["date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data[-1]["date"], "%Y-%m-%d").date()
        stats["time_span_days"] = (end_date - start_date).days
    
    return stats