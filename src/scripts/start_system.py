#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新传论文智能辅导系统 - 启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要的包
    try:
        import streamlit
        print("✅ Streamlit已安装")
    except ImportError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
        return False
    
    try:
        import plotly
        print("✅ Plotly已安装")
    except ImportError:
        print("❌ Plotly未安装，请运行: pip install plotly")
        return False
    
    return True

def check_api_key():
    """检查API密钥"""
    # 优先检查通义千问API密钥
    qwen_key = os.getenv("DASHSCOPE_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if qwen_key:
        print("✅ 通义千问API密钥已设置")
        return True
    elif deepseek_key:
        print("✅ DeepSeek API密钥已设置")
        return True
    else:
        print("⚠️  警告: 未设置API密钥")
        print("推荐设置通义千问API密钥:")
        print("export DASHSCOPE_API_KEY='your_dashscope_api_key'")
        print("或者设置DeepSeek API密钥:")
        print("export DEEPSEEK_API_KEY='your_deepseek_api_key'")
        print("或者创建.env文件并添加相应的API密钥")
        return False

def start_streamlit():
    """启动Streamlit应用"""
    print("\n🚀 启动新传论文智能辅导系统...")
    
    try:
        # 启动Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", "8501"]
        process = subprocess.Popen(cmd)
        
        print("✅ 系统启动成功！")
        print("🌐 正在打开浏览器...")
        
        # 等待几秒钟让Streamlit启动
        time.sleep(3)
        
        # 打开浏览器
        webbrowser.open("http://localhost:8501")
        
        print("\n📋 系统信息:")
        print("• 本地地址: http://localhost:8501")
        print("• 网络地址: http://127.0.0.1:8501")
        print("• 按Ctrl+C停止系统")
        
        # 等待用户停止
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止系统...")
            process.terminate()
            process.wait()
            print("✅ 系统已停止")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("📚 新传论文智能辅导系统")
    print("=" * 40)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return False
    
    # 检查API密钥
    check_api_key()
    
    # 启动系统
    return start_streamlit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
