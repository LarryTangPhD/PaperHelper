#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新传论文智能辅导系统 - 功能测试脚本
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_imports():
    """测试所有必要的模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
    except ImportError as e:
        print(f"❌ Streamlit 导入失败: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly 导入成功")
    except ImportError as e:
        print(f"❌ Plotly 导入失败: {e}")
        return False
    
    try:
        from src.utils.PaperHelper_utils import generate_paper, topic_diagnosis
        print("✅ PaperHelper_utils 导入成功")
    except ImportError as e:
        print(f"❌ PaperHelper_utils 导入失败: {e}")
        return False
    
    return True

def test_api_key():
    """测试API密钥设置"""
    print("\n🔑 测试API密钥设置...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print("✅ DEEPSEEK_API_KEY 已设置")
        return True
    else:
        print("❌ DEEPSEEK_API_KEY 未设置")
        print("请设置环境变量: export DEEPSEEK_API_KEY='your_api_key'")
        return False

def test_basic_functions():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        from src.utils.PaperHelper_utils import generate_default_feasibility_data
        
        # 测试默认可行性数据生成
        feasibility_data = generate_default_feasibility_data()
        if isinstance(feasibility_data, dict) and 'score' in feasibility_data:
            print("✅ 默认可行性数据生成成功")
        else:
            print("❌ 默认可行性数据生成失败")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n📁 测试文件结构...")
    
    required_files = [
        "main.py",
        "src/core/PaperHelper.py",
        "src/utils/PaperHelper_utils.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 缺失")
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少文件: {missing_files}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 新传论文智能辅导系统 - 功能测试")
    print("=" * 50)
    
    # 测试文件结构
    if not test_file_structure():
        print("\n❌ 文件结构测试失败")
        return False
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    # 测试API密钥
    if not test_api_key():
        print("\n⚠️  API密钥未设置，部分功能可能无法使用")
    
    # 测试基本功能
    if not test_basic_functions():
        print("\n❌ 基本功能测试失败")
        return False
    
    print("\n🎉 所有测试通过！")
    print("\n📋 系统状态:")
    print("✅ 文件结构完整")
    print("✅ 模块导入正常")
    print("✅ 基本功能可用")
    
    if os.getenv("DEEPSEEK_API_KEY"):
        print("✅ API密钥已设置")
    else:
        print("⚠️  API密钥未设置")
    
    print("\n🚀 可以运行以下命令启动系统:")
    print("streamlit run main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
