@echo off
chcp 65001 >nul
echo ============================================================
echo 💘 把妹大师 V23.0 - Viking 终极版
echo ============================================================
echo.

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 版本:
python --version
echo.

REM 启动 GUI
echo 🚀 启动 GUI 界面...
echo.
python main_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    pause
)
