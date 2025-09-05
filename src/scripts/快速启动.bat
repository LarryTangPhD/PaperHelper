@echo off
chcp 65001
echo.
echo 🚀 新传论文智能辅导系统 - 快速启动
echo ================================================
echo.

echo 📋 检查系统环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 📦 检查依赖包...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安装依赖包...
    pip install -r requirements.txt
) else (
    echo ✅ 依赖包已安装
)

echo.
echo 🔑 检查API密钥...
if "%DASHSCOPE_API_KEY%"=="" (
    echo ⚠️  未设置DASHSCOPE_API_KEY环境变量
    echo 💡 提示：系统默认使用通义千问-Plus模型，需要设置API密钥
    echo.
    echo 可选的API密钥：
    echo   - DASHSCOPE_API_KEY (通义千问-Plus) - 推荐
    echo   - OPENAI_API_KEY (GPT-3.5-Turbo)
    echo   - ANTHROPIC_API_KEY (Claude-3-Haiku)
    echo   - DEEPSEEK_API_KEY (DeepSeek)
    echo.
    echo 📖 详细设置请参考：通义千问配置指南.md
    echo.
) else (
    echo ✅ 通义千问-Plus API密钥已设置
)

echo.
echo 🚀 启动系统...
echo 📱 系统将在浏览器中打开
echo 🔗 本地地址: http://localhost:8501
echo.
echo 💡 提示：
echo   - 系统默认使用通义千问-Plus模型，响应速度快
echo   - 如需切换模型，请在侧边栏选择其他模型
echo   - 详细说明请参考：通义千问配置指南.md
echo.

streamlit run main.py

pause
