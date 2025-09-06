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
import streamlit as st
from src.core.PaperHelper import main_page

# 初始化session state - 移到模块级别确保在部署时也能执行
if 'current_page' not in st.session_state:
    st.session_state.current_page = "选题指导"
if 'user_topic' not in st.session_state:
    st.session_state.user_topic = ""
if 'topic_analysis' not in st.session_state:
    st.session_state.topic_analysis = None
if 'paper_content' not in st.session_state:
    st.session_state.paper_content = ""
if 'annotation_result' not in st.session_state:
    st.session_state.annotation_result = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'file_info' not in st.session_state:
    st.session_state.file_info = None
if 'format_content' not in st.session_state:
    st.session_state.format_content = ""
if 'format_result' not in st.session_state:
    st.session_state.format_result = None
if 'format_analysis_result' not in st.session_state:
    st.session_state.format_analysis_result = None

# 运行主页面
main_page()
