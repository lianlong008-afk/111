#!/bin/bash
# 把妹大师 V23.0 - Viking 终极版 - 启动脚本 (Mac/Linux)

echo "============================================================"
echo "💘 把妹大师 V23.0 - Viking 终极版"
echo "============================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    echo "请先安装 Python3: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告：tkinter 未安装"
    echo "Mac: brew install python-tk"
    echo "Ubuntu: sudo apt-get install python3-tk"
    echo ""
fi

# 启动 GUI
echo "🚀 启动 GUI 界面..."
echo ""
python3 main_gui.py
