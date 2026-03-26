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

# 启动智能启动器
echo "🚀 启动程序..."
echo ""
python3 start_smart.py
