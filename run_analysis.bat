@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════╗
echo ║           📈 股票分析系统 - 快速启动                  ║
echo ╚══════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM 检查依赖
echo [检查] 验证 Python 环境...
py -c "import pandas; import requests" 2>nul
if errorlevel 1 (
    echo ⚠️  缺少依赖库，正在安装...
    py -m pip install pandas requests numpy -q
    if errorlevel 1 (
        echo ❌ 安装失败，请手动运行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 环境检查通过
)

echo.
echo [运行] 启动股票分析...
echo.

REM 运行分析
py scripts/main.py %*

echo.
pause
