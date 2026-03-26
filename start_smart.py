#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V23.0 - 智能启动器
自动检测系统并选择合适的启动方式
"""

import sys
import os
import platform


def check_tkinter():
    """检查 tkinter 可用性"""
    try:
        import tkinter as tk
        # 尝试创建窗口测试
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception as e:
        print(f"⚠️  tkinter 检测失败：{e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("💘 把妹大师 V23.0 - Viking 终极版")
    print("=" * 60)
    print()
    
    # 系统信息
    print(f"系统：{platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    # 检查 tkinter
    tkinter_available = check_tkinter()
    
    if tkinter_available:
        print("✅ tkinter 可用，启动 GUI 版本...")
        print()
        from main_gui_fixed import main as gui_main
        gui_main()
    else:
        print("⚠️  tkinter 不可用，启动命令行版本...")
        print()
        from main_cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
