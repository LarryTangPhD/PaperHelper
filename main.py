#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新传论文智能辅导系统 - 主启动文件
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行主应用
from src.core.PaperHelper import main_page

if __name__ == "__main__":
    main_page()
