@echo off
chcp 65001 >nul
title 新传论文智能辅导系统

echo.
echo ========================================
echo    新传论文智能辅导系统
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🚀 启动系统...
echo.

streamlit run main.py

if errorlevel 1 (
    echo.
    echo ❌ 系统启动失败
    pause
    exit /b 1
)

echo.
echo ✅ 系统已停止
pause
