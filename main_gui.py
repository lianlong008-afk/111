#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V23.0 - Viking 终极版 - GUI 启动程序
基于 tkinter 的现代化界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys

# 导入核心引擎
from pickup_master_v23_ultimate import PickupMasterV23


class PickupMasterGUI:
    """把妹大师 GUI 界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💘 把妹大师 V23.0 - Viking 终极版")
        self.root.geometry("900x700")
        
        # 初始化引擎
        self.master_engine = None
        self.session_id = None
        self.current_girl = tk.StringVar()
        self.girl_history = []
        
        # 设置样式
        self._setup_styles()
        
        # 创建界面
        self._create_menu()
        self._create_header()
        self._create_main_area()
        self._create_status_bar()
        
        # 初始化引擎 (后台)
        self._init_engine_async()
        
        self.root.mainloop()
    
    def _setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'bg': '#f5f5f5',
            'card': '#ffffff',
        }
        
        self.root.configure(bg=self.colors['bg'])
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建会话", command=self._new_session)
        file_menu.add_command(label="导出聊天记录", command=self._export_chat)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="开场白生成器", command=self._open_opener_tool)
        tools_menu.add_command(label="兴趣度分析", command=self._open_interest_tool)
        tools_menu.add_command(label="星座查询", command=self._open_zodiac_tool)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用指南", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_header(self):
        """创建顶部"""
        header = tk.Frame(self.root, bg=self.colors['primary'], pady=15)
        header.pack(fill="x")
        
        # 标题
        title_label = tk.Label(
            header, 
            text="💘 把妹大师 V23.0", 
            font=("微软雅黑", 18, "bold"),
            bg=self.colors['primary'], 
            fg="white"
        )
        title_label.pack(side="left", padx=20)
        
        # 副标题
        subtitle_label = tk.Label(
            header,
            text="Viking 终极整合版 | 12000+ 技巧库",
            font=("微软雅黑", 10),
            bg=self.colors['primary'],
            fg="rgba(255,255,255,0.8)"
        )
        subtitle_label.pack(side="left", padx=10, pady=18)
        
        # 状态指示
        self.status_indicator = tk.Label(
            header,
            text="⚪ 初始化中...",
            font=("微软雅黑", 10),
            bg=self.colors['primary'],
            fg="white"
        )
        self.status_indicator.pack(side="right", padx=20, pady=18)
    
    def _create_main_area(self):
        """创建主区域"""
        # 左右分栏
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['bg'], sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = tk.Frame(main_paned, bg=self.colors['card'], width=250)
        main_paned.add(left_frame)
        
        self._create_left_panel(left_frame)
        
        # 右侧面板
        right_frame = tk.Frame(main_paned, bg=self.colors['card'])
        main_paned.add(right_frame)
        
        self._create_right_panel(right_frame)
    
    def _create_left_panel(self, parent):
        """创建左侧面板"""
        # 女生选择
        girl_frame = tk.Frame(parent, bg=self.colors['card'])
        girl_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            girl_frame, 
            text="👧 当前女生", 
            font=("微软雅黑", 12, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 10))
        
        # 女生输入
        self.girl_entry = ttk.Combobox(girl_frame, textvariable=self.current_girl, font=("微软雅黑", 10))
        self.girl_entry.pack(fill="x", pady=5)
        self.girl_entry.bind("<<ComboboxSelected>>", self._on_girl_selected)
        
        # 添加女生按钮
        tk.Button(
            girl_frame,
            text="➕ 添加女生",
            font=("微软雅黑", 9),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            command=self._add_girl
        ).pack(fill="x", pady=5)
        
        # 女生列表
        self.girl_listbox = tk.Listbox(
            girl_frame, 
            font=("微软雅黑", 10), 
            bg="#f8f9fa", 
            relief="flat",
            height=10
        )
        self.girl_listbox.pack(fill="both", expand=True, pady=10)
        self.girl_listbox.bind("<<ListboxSelect>>", self._on_girl_list_selected)
        
        # 快捷工具
        tools_frame = tk.Frame(parent, bg=self.colors['card'])
        tools_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            tools_frame,
            text="🛠️ 快捷工具",
            font=("微软雅黑", 12, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Button(
            tools_frame,
            text="💬 开场白生成",
            font=("微软雅黑", 9),
            bg=self.colors['success'],
            fg="white",
            relief="flat",
            command=self._generate_opener
        ).pack(fill="x", pady=3)
        
        tk.Button(
            tools_frame,
            text="💕 调情短信",
            font=("微软雅黑", 9),
            bg=self.colors['warning'],
            fg="white",
            relief="flat",
            command=self._generate_flirty_text
        ).pack(fill="x", pady=3)
        
        tk.Button(
            tools_frame,
            text="⭐ 兴趣度分析",
            font=("微软雅黑", 9),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            command=self._analyze_interest
        ).pack(fill="x", pady=3)
    
    def _create_right_panel(self, parent):
        """创建右侧面板"""
        # 聊天历史
        chat_frame = tk.Frame(parent, bg=self.colors['card'])
        chat_frame.pack(fill="both", expand=True, padx=15, pady=(15, 10))
        
        tk.Label(
            chat_frame,
            text="💬 聊天记录",
            font=("微软雅黑", 12, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 10))
        
        # 聊天显示区
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=("微软雅黑", 11),
            bg="#f8f9fa",
            relief="flat",
            wrap="word",
            spacing1=5,
            spacing3=5,
        )
        self.chat_display.pack(fill="both", expand=True)
        
        # 输入区
        input_frame = tk.Frame(parent, bg=self.colors['card'])
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="✏️ 输入消息",
            font=("微软雅黑", 12, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 10))
        
        # 输入框
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            font=("微软雅黑", 11),
            bg="#f8f9fa",
            relief="flat",
            height=4,
        )
        self.input_text.pack(fill="x", pady=5)
        
        # 按钮
        btn_frame = tk.Frame(input_frame, bg=self.colors['card'])
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame,
            text="🚀 生成回复",
            font=("微软雅黑", 11, "bold"),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            padx=20,
            pady=8,
            command=self._generate_reply
        ).pack(side="right")
        
        tk.Button(
            btn_frame,
            text="📋 粘贴",
            font=("微软雅黑", 9),
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=8,
            command=self._paste_text
        ).pack(side="right", padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ 清空",
            font=("微软雅黑", 9),
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=8,
            command=self._clear_chat
        ).pack(side="right", padx=5)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = tk.Frame(self.root, bg=self.colors['secondary'], pady=8)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="就绪",
            font=("微软雅黑", 9),
            bg=self.colors['secondary'],
            fg="white"
        )
        self.status_label.pack(side="left", padx=20)
        
        self.stats_label = tk.Label(
            status_bar,
            text="",
            font=("微软雅黑", 9),
            bg=self.colors['secondary'],
            fg="rgba(255,255,255,0.8)"
        )
        self.stats_label.pack(side="right", padx=20)
    
    def _init_engine_async(self):
        """异步初始化引擎"""
        def init():
            try:
                self.master_engine = PickupMasterV23()
                self.session_id = self.master_engine.start_session("gui_user")
                
                self.root.after(0, self._on_engine_ready)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"初始化失败：{e}"))
        
        threading.Thread(target=init, daemon=True).start()
    
    def _on_engine_ready(self):
        """引擎就绪"""
        self.status_indicator.config(text="🟢 已就绪", fg="#4caf50")
        self._update_status()
        self._append_to_chat("系统", "🎉 把妹大师 V23.0 已启动！准备好撩妹了吗？", is_system=True)
    
    def _update_status(self):
        """更新状态"""
        if self.master_engine:
            status = self.master_engine.status()
            self.stats_label.config(
                text=f"技巧库：{status['techniques_v20'] + status['techniques_v21']}个 | 会话：{status['sessions']}个"
            )
    
    def _add_girl(self):
        """添加女生"""
        girl_name = self.girl_entry.get().strip()
        if not girl_name:
            messagebox.showwarning("提示", "请输入女生名字")
            return
        
        if girl_name not in self.girl_history:
            self.girl_history.append(girl_name)
            self.girl_listbox.insert(tk.END, girl_name)
            self.girl_entry['values'] = self.girl_history
        
        self.current_girl.set(girl_name)
        self._append_to_chat("系统", f"👧 已添加女生：{girl_name}", is_system=True)
    
    def _on_girl_selected(self, event):
        """女生选择变更"""
        girl_name = self.current_girl.get()
        self._append_to_chat("系统", f"切换到女生：{girl_name}", is_system=True)
    
    def _on_girl_list_selected(self, event):
        """女生列表选择"""
        selection = self.girl_listbox.curselection()
        if selection:
            girl_name = self.girl_listbox.get(selection[0])
            self.current_girl.set(girl_name)
            self._append_to_chat("系统", f"切换到女生：{girl_name}", is_system=True)
    
    def _generate_opener(self):
        """生成开场白"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        categories = ["好奇类", "赞美类", "关心类", "分享类", "直球类"]
        category = random.choice(categories)
        
        opener = self.master_engine.get_opening_line(category)
        
        self._append_to_chat("系统", f"💬 {category}开场白：{opener}", is_system=True)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", opener)
    
    def _generate_flirty_text(self):
        """生成调情短信"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        categories = ["早安短信", "晚安短信", "甜蜜短信", "调情短信", "关心短信"]
        category = random.choice(categories)
        
        text = self.master_engine.get_flirty_text(category)
        
        self._append_to_chat("系统", f"💕 {category}：{text}", is_system=True)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", text)
    
    def _analyze_interest(self):
        """分析兴趣度"""
        # 获取最近聊天
        chat_history = self._get_recent_chat()
        
        if not chat_history:
            messagebox.showwarning("提示", "暂无聊天记录")
            return
        
        if not self.master_engine:
            return
        
        analysis = self.master_engine.analyze_girl_interest(chat_history)
        
        result = f"""
📊 兴趣度分析报告

得分：{analysis['score']}分 ({analysis['level']})
积极信号：{', '.join(analysis['positive_signals']) if analysis['positive_signals'] else '无'}
消极信号：{', '.join(analysis['negative_signals']) if analysis['negative_signals'] else '无'}
建议：{analysis['suggestions'][0] if analysis['suggestions'] else '继续聊天'}
"""
        self._append_to_chat("系统", result.strip(), is_system=True)
    
    def _generate_reply(self):
        """生成回复"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("提示", "请输入消息")
            return
        
        girl_name = self.current_girl.get() or "未知女生"
        
        # 显示用户消息
        self._append_to_chat(girl_name, message, is_user=True)
        
        # 禁用按钮
        self._set_buttons_state(tk.DISABLED)
        
        # 后台生成回复
        def generate():
            try:
                result = self.master_engine.chat(message, girl_name=girl_name)
                
                self.root.after(0, lambda: self._on_reply_generated(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"生成失败：{e}"))
                self.root.after(0, lambda: self._set_buttons_state(tk.NORMAL))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _on_reply_generated(self, result):
        """回复生成完成"""
        self._append_to_chat("AI", result['reply'])
        self.input_text.delete("1.0", tk.END)
        self._set_buttons_state(tk.NORMAL)
        self._update_status()
    
    def _set_buttons_state(self, state):
        """设置按钮状态"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=state)
    
    def _paste_text(self):
        """粘贴文本"""
        try:
            text = self.root.clipboard_get()
            self.input_text.insert(tk.END, text)
        except:
            pass
    
    def _clear_chat(self):
        """清空聊天"""
        self.chat_display.delete("1.0", tk.END)
    
    def _get_recent_chat(self):
        """获取最近聊天"""
        content = self.chat_display.get("1.0", tk.END)
        return content[-1000:] if len(content) > 1000 else content
    
    def _append_to_chat(self, sender, message, is_user=False, is_system=False):
        """添加消息到聊天"""
        self.chat_display.config(state=tk.NORMAL)
        
        if is_system:
            self.chat_display.insert(tk.END, f"[{sender}] {message}\n\n")
            self.chat_display.tag_add("system", "end-2l", "end-1l")
            self.chat_display.tag_config("system", foreground="#667eea")
        elif is_user:
            self.chat_display.insert(tk.END, f"👤 {sender}: {message}\n\n")
        else:
            self.chat_display.insert(tk.END, f"🤖 {sender}: {message}\n\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _new_session(self):
        """新建会话"""
        if self.master_engine:
            self.session_id = self.master_engine.start_session("gui_user")
            self._clear_chat()
            self._append_to_chat("系统", "🎉 新会话已创建", is_system=True)
            self._update_status()
    
    def _export_chat(self):
        """导出聊天记录"""
        messagebox.showinfo("提示", "功能开发中...")
    
    def _open_opener_tool(self):
        """打开开场白工具"""
        messagebox.showinfo("提示", "功能开发中...")
    
    def _open_interest_tool(self):
        """打开兴趣度工具"""
        self._analyze_interest()
    
    def _open_zodiac_tool(self):
        """打开星座工具"""
        messagebox.showinfo("提示", "功能开发中...")
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
📖 使用指南

1. 添加女生
   - 在左侧输入女生名字
   - 点击"添加女生"按钮

2. 开始聊天
   - 选择女生
   - 输入对方消息
   - 点击"生成回复"

3. 快捷工具
   - 开场白生成：获取高质量开场白
   - 调情短信：生成甜蜜短信
   - 兴趣度分析：分析她对你的兴趣

4. 技巧库
   - V20: 10000+ 专业把妹技巧
   - V21: 全球技巧 + 星座指南
   - V22: Viking 上下文管理

💡 提示
- 每次聊天前选择正确的女生
- 多使用快捷工具获取灵感
- 定期查看兴趣度分析
"""
        messagebox.showinfo("使用指南", help_text)
    
    def _show_about(self):
        """显示关于"""
        about_text = """
💘 把妹大师 V23.0

Viking 终极整合版

技术栈:
- Python 3.8+
- tkinter GUI
- Viking 上下文管理

技巧库:
- V20: 8 大模块 10000+ 技巧
- V21: 全球技巧 + 12 星座
- V22: Viking 架构

GitHub:
https://github.com/lianlong008-afk/111

© 2024 All Rights Reserved
"""
        messagebox.showinfo("关于", about_text)


# 导入 random (用于随机选择)
import random


# ==================== 启动程序 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("💘 把妹大师 V23.0 - Viking 终极版")
    print("正在启动 GUI...")
    print("=" * 60)
    
    try:
        app = PickupMasterGUI()
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
