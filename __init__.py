#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李大霄指数计算程序包
Li Daxiao Index Calculation Package

This package contains modular components for calculating Li Daxiao index from Bilibili video data.

Modules:
- config: Configuration constants and settings
- crawler: Video data fetching and mock data generation
- calculator: Index calculation logic
- storage: JSON data persistence operations
- visualizer: Chart generation for data visualization

Main programs:
- lidaxiao.py: Production version with real API integration
- demo.py: Demo version with mock data for testing
"""

__version__ = "1.0.0"
__author__ = "GitHub Copilot"

# Convenience imports for easier access to main functions
from .calculator import calculate_index, calculate_video_contribution
from .storage import save_all_data, load_history_data
from .visualizer import generate_all_charts
from .crawler import configure_api_settings, get_api_troubleshooting_info, SecurityControlException