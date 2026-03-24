@echo off
chcp 65001 >nul
cd /d "%~dp0"
python main_v8.py
pause
