#!/bin/bash

# 新传论文智能辅导系统 - 启动脚本

echo "========================================"
echo "    新传论文智能辅导系统"
echo "========================================"
echo

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    echo "请先安装Python 3.8或更高版本"
    exit 1
fi

echo "✅ Python环境正常"

# 检查虚拟环境
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "🔍 检测到虚拟环境，正在激活..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    echo "✅ 虚拟环境已激活"
fi

echo
echo "🚀 启动系统..."
echo

# 启动系统
streamlit run main.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ 系统启动失败"
    exit 1
fi

echo
echo "✅ 系统已停止"
