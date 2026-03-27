#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V24.0 - Viking 大模型版 - 现代化 GUI 界面
兼容 macOS 26.2+
"""

import sys
import os

# 检查 tkinter 可用性
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    TKINTER_AVAILABLE = True
except ImportError as e:
    TKINTER_AVAILABLE = False
    print(f"⚠️ tkinter 不可用：{e}")
    sys.exit(1)

from pickup_master_v24 import PickupMasterV24, CONFIG, save_config, API_KEY
import threading


class PickupMasterV24GUI:
    """把妹大师 V24.0 GUI 界面 - 现代化设计"""
    
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("💘 把妹大师 V24.0 - Viking 大模型版")
            self.root.geometry("1000x750")
            self.root.minsize(900, 650)
            
            # 设置窗口背景色
            self.root.configure(bg='#f0f0f0')
            
            # 初始化变量
            self.master_engine = None
            self.session_id = None
            self.current_girl = tk.StringVar()
            self.current_relation = tk.StringVar(value="恋人")
            self.girl_history = []
            self.processing = False
            self.api_key = API_KEY
            
            # 设置样式
            self._setup_styles()
            
            # 创建界面
            self._create_menu()
            self._create_header()
            self._create_main_area()
            self._create_status_bar()
            
            # 绑定关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # 异步初始化引擎
            self.root.after(100, self._init_engine_async)
            
        except Exception as e:
            print(f"❌ GUI 初始化失败：{e}")
            print("请使用命令行版本：python3 main_cli_v24.py")
            sys.exit(1)
    
    def _setup_styles(self):
        """设置样式"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # 配置颜色方案
            self.colors = {
                'primary': '#667eea',      # 主色调 - 紫色
                'secondary': '#764ba2',    # 辅助色 - 深紫
                'success': '#4caf50',      # 成功 - 绿色
                'warning': '#ff9800',      # 警告 - 橙色
                'danger': '#f44336',       # 危险 - 红色
                'info': '#2196f3',         # 信息 - 蓝色
                'bg': '#f0f0f0',           # 背景 - 浅灰
                'card': '#ffffff',         # 卡片 - 白色
                'text': '#333333',         # 文字 - 深灰
                'text_light': '#666666',   # 浅文字
            }
            
            # 配置字体
            self.fonts = {
                'title': ('Arial', 18, 'bold'),
                'heading': ('Arial', 14, 'bold'),
                'normal': ('Arial', 11),
                'small': ('Arial', 9),
                'chat': ('Arial', 12),
            }
            
        except Exception as e:
            print(f"⚠️ 样式设置警告：{e}")
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建会话", command=self._new_session)
        file_menu.add_command(label="配置 API Key", command=self._show_config_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="兴趣度分析", command=self._show_interest_analysis)
        tools_menu.add_command(label="查看记忆", command=self._show_memories)
        tools_menu.add_command(label="清空记忆", command=self._clear_memories)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用指南", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_header(self):
        """创建顶部"""
        header = tk.Frame(self.root, bg=self.colors['primary'], pady=12)
        header.pack(fill="x")
        
        # 标题
        title_label = tk.Label(
            header, 
            text="💘 把妹大师 V24.0", 
            font=self.fonts['title'],
            bg=self.colors['primary'], 
            fg="white"
        )
        title_label.pack(side="left", padx=20)
        
        # 副标题
        subtitle_label = tk.Label(
            header,
            text="Viking 大模型版 | AI 高情商回复",
            font=self.fonts['small'],
            bg=self.colors['primary'],
            fg="white"
        )
        subtitle_label.pack(side="left", padx=10, pady=10)
        
        # 右侧状态
        right_frame = tk.Frame(header, bg=self.colors['primary'])
        right_frame.pack(side="right", padx=20)
        
        # API Key 状态
        self.api_status = tk.Label(
            right_frame,
            text="🔑 API: " + ("已配置" if self.api_key else "未配置"),
            font=self.fonts['small'],
            bg=self.colors['primary'],
            fg="white"
        )
        self.api_status.pack(side="right", padx=10)
        
        # 连接状态
        self.status_indicator = tk.Label(
            right_frame,
            text="⚪ 初始化中...",
            font=self.fonts['small'],
            bg=self.colors['primary'],
            fg="white"
        )
        self.status_indicator.pack(side="right", padx=10)
    
    def _create_main_area(self):
        """创建主区域"""
        # 左右分栏
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['bg'], sashrelief=tk.RAISED, sashwidth=4)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 (280px)
        left_frame = tk.Frame(main_paned, bg=self.colors['card'], width=280)
        main_paned.add(left_frame)
        
        self._create_left_panel(left_frame)
        
        # 右侧面板
        right_frame = tk.Frame(main_paned, bg=self.colors['card'])
        main_paned.add(right_frame)
        
        self._create_right_panel(right_frame)
    
    def _create_left_panel(self, parent):
        """创建左侧面板"""
        # 滚动区域
        canvas = tk.Canvas(parent, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === 女生管理 ===
        girl_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
        girl_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            girl_frame, 
            text="👧 女生管理", 
            font=self.fonts['heading'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(0, 10))
        
        # 女生输入
        input_frame = tk.Frame(girl_frame, bg=self.colors['card'])
        input_frame.pack(fill="x", pady=5)
        
        self.girl_entry = ttk.Combobox(input_frame, textvariable=self.current_girl, font=self.fonts['normal'])
        self.girl_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.girl_entry.bind("<<ComboboxSelected>>", self._on_girl_selected)
        
        tk.Button(
            input_frame,
            text="➕",
            font=self.fonts['small'],
            bg=self.colors['success'],
            fg="white",
            relief="flat",
            width=3,
            command=self._add_girl
        ).pack(side="left")
        
        # 女生列表
        self.girl_listbox = tk.Listbox(
            girl_frame, 
            font=self.fonts['normal'], 
            bg="#f8f9fa", 
            relief="flat",
            height=6,
            selectbackground=self.colors['primary']
        )
        self.girl_listbox.pack(fill="both", expand=True, pady=10)
        self.girl_listbox.bind("<<ListboxSelect>>", self._on_girl_list_selected)
        
        # === 关系选择 ===
        relation_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
        relation_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            relation_frame, 
            text="💝 关系类型", 
            font=self.fonts['heading'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(0, 10))
        
        relations = ["恋人", "朋友", "同事", "客户", "家人", "追求者", "海王", "高冷"]
        for rel in relations:
            rb = tk.Radiobutton(
                relation_frame,
                text=rel,
                variable=self.current_relation,
                value=rel,
                font=self.fonts['normal'],
                bg=self.colors['card'],
                activebackground=self.colors['card']
            )
            rb.pack(anchor="w", pady=2)
        
        # === 快捷工具 ===
        tools_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
        tools_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(
            tools_frame,
            text="🛠️ 快捷工具",
            font=self.fonts['heading'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Button(
            tools_frame,
            text="⭐ 兴趣度分析",
            font=self.fonts['normal'],
            bg=self.colors['info'],
            fg="white",
            relief="flat",
            pady=8,
            command=self._show_interest_analysis
        ).pack(fill="x", pady=3)
        
        tk.Button(
            tools_frame,
            text="📝 查看记忆",
            font=self.fonts['normal'],
            bg=self.colors['warning'],
            fg="white",
            relief="flat",
            pady=8,
            command=self._show_memories
        ).pack(fill="x", pady=3)
        
        tk.Button(
            tools_frame,
            text="🗑️ 清空记忆",
            font=self.fonts['normal'],
            bg=self.colors['danger'],
            fg="white",
            relief="flat",
            pady=8,
            command=self._clear_memories
        ).pack(fill="x", pady=3)
    
    def _create_right_panel(self, parent):
        """创建右侧面板"""
        # === 聊天区域 ===
        chat_frame = tk.Frame(parent, bg=self.colors['card'])
        chat_frame.pack(fill="both", expand=True, padx=15, pady=(15, 10))
        
        # 聊天标题
        title_frame = tk.Frame(chat_frame, bg=self.colors['card'])
        title_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            title_frame,
            text="💬 聊天记录",
            font=self.fonts['heading'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side="left")
        
        self.chat_title = tk.Label(
            title_frame,
            text="",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['text_light']
        )
        self.chat_title.pack(side="right")
        
        # 聊天显示区
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=self.fonts['chat'],
            bg="#f8f9fa",
            relief="flat",
            wrap="word",
            spacing1=5,
            spacing3=5,
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.config(state="disabled")
        
        # 配置标签颜色
        self.chat_display.tag_config("system", foreground=self.colors['info'])
        self.chat_display.tag_config("user", foreground=self.colors['text'])
        self.chat_display.tag_config("ai", foreground=self.colors['success'])
        
        # === 输入区域 ===
        input_frame = tk.Frame(parent, bg=self.colors['card'])
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="✏️ 输入对方消息",
            font=self.fonts['heading'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(0, 10))
        
        # 输入框
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            font=self.fonts['chat'],
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
            text="🗑️ 清空",
            font=self.fonts['normal'],
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=8,
            command=self._clear_chat
        ).pack(side="left", padx=3)
        
        tk.Button(
            btn_frame,
            text="📋 粘贴",
            font=self.fonts['normal'],
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=8,
            command=self._paste_text
        ).pack(side="left", padx=3)
        
        self.generate_btn = tk.Button(
            btn_frame,
            text="🚀 生成 AI 回复",
            font=self.fonts['heading'],
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            padx=25,
            pady=10,
            command=self._generate_reply
        )
        self.generate_btn.pack(side="right", padx=3)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = tk.Frame(self.root, bg=self.colors['secondary'], pady=8)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="就绪",
            font=self.fonts['small'],
            bg=self.colors['secondary'],
            fg="white"
        )
        self.status_label.pack(side="left", padx=20)
        
        self.stats_label = tk.Label(
            status_bar,
            text="",
            font=self.fonts['small'],
            bg=self.colors['secondary'],
            fg="white"
        )
        self.stats_label.pack(side="right", padx=20)
    
    def _init_engine_async(self):
        """异步初始化引擎"""
        def init():
            try:
                self.master_engine = PickupMasterV24(self.api_key if self.api_key else None)
                self.session_id = self.master_engine.start_session("gui_user")
                self.root.after(0, self._on_engine_ready)
            except Exception as e:
                self.root.after(0, lambda: self._show_error(f"初始化失败：{e}"))
        
        threading.Thread(target=init, daemon=True).start()
    
    def _on_engine_ready(self):
        """引擎就绪"""
        self.status_indicator.config(text="🟢 已就绪", fg="#4caf50")
        
        if self.api_key:
            self.api_status.config(text="🔑 API: 已配置", fg="#4caf50")
        else:
            self.api_status.config(text="🔑 API: 未配置", fg="#ff9800")
        
        self._update_status()
        self._append_to_chat("系统", "🎉 把妹大师 V24.0 已启动！AI 高情商回复助手", is_system=True)
        
        if not self.api_key:
            self._append_to_chat("系统", "⚠️ API Key 未配置，请在「文件」菜单中配置", is_system=True)
    
    def _update_status(self):
        """更新状态"""
        if self.master_engine:
            try:
                status = self.master_engine.get_status()
                self.stats_label.config(
                    text=f"模型：{status['model']} | 会话：{status['current_session'][:8]}..."
                )
            except:
                pass
    
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
        self.chat_title.config(text=f"当前：{girl_name}")
        self._append_to_chat("系统", f"👧 已添加女生：{girl_name}", is_system=True)
        
        if self.master_engine:
            self.master_engine.set_current_girl(girl_name)
    
    def _on_girl_selected(self, event):
        """女生选择变更"""
        girl_name = self.current_girl.get()
        self.chat_title.config(text=f"当前：{girl_name}")
        self._append_to_chat("系统", f"切换到女生：{girl_name}", is_system=True)
        
        if self.master_engine:
            self.master_engine.set_current_girl(girl_name)
    
    def _on_girl_list_selected(self, event):
        """女生列表选择"""
        selection = self.girl_listbox.curselection()
        if selection:
            girl_name = self.girl_listbox.get(selection[0])
            self.current_girl.set(girl_name)
            self.chat_title.config(text=f"当前：{girl_name}")
            self._append_to_chat("系统", f"切换到女生：{girl_name}", is_system=True)
            
            if self.master_engine:
                self.master_engine.set_current_girl(girl_name)
    
    def _generate_reply(self):
        """生成回复"""
        if self.processing:
            return
        
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        if not self.api_key:
            messagebox.showwarning("提示", "请先配置 API Key\n\n文件 → 配置 API Key")
            return
        
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("提示", "请输入消息")
            return
        
        girl_name = self.current_girl.get()
        if not girl_name:
            messagebox.showwarning("提示", "请先选择或添加女生")
            return
        
        relation = self.current_relation.get()
        
        # 显示用户消息
        self._append_to_chat(girl_name, message, is_user=True)
        
        # 禁用按钮
        self.processing = True
        self.generate_btn.config(state="disabled", text="⏳ 生成中...")
        
        # 后台生成回复
        def generate():
            try:
                result = self.master_engine.chat(message, girl_name=girl_name, relation=relation)
                self.root.after(0, lambda: self._on_reply_generated(result))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(f"生成失败：{e}"))
                self.root.after(0, lambda: self._reset_generate_btn())
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _on_reply_generated(self, result):
        """回复生成完成"""
        self._append_to_chat("AI", result['reply'])
        self.input_text.delete("1.0", tk.END)
        self._reset_generate_btn()
        self._update_status()
        
        # 显示其他选项
        if len(result['options']) > 1:
            options_text = "💡 其他选项:\n"
            for i, opt in enumerate(result['options'][1:], 2):
                options_text += f"  {i}. {opt}\n"
            self._append_to_chat("系统", options_text.strip(), is_system=True)
    
    def _reset_generate_btn(self):
        """重置生成按钮"""
        self.processing = False
        self.generate_btn.config(state="normal", text="🚀 生成 AI 回复")
    
    def _paste_text(self):
        """粘贴文本"""
        try:
            text = self.root.clipboard_get()
            self.input_text.insert(tk.END, text)
        except:
            pass
    
    def _clear_chat(self):
        """清空聊天"""
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state="disabled")
    
    def _append_to_chat(self, sender, message, is_user=False, is_system=False):
        """添加消息到聊天"""
        self.chat_display.config(state="normal")
        
        if is_system:
            self.chat_display.insert(tk.END, f"[{sender}] {message}\n\n", "system")
        elif is_user:
            self.chat_display.insert(tk.END, f"👤 {sender}: {message}\n\n", "user")
        else:
            self.chat_display.insert(tk.END, f"🤖 AI: {message}\n\n", "ai")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
    
    def _show_error(self, message):
        """显示错误"""
        messagebox.showerror("错误", message)
    
    def _show_config_dialog(self):
        """显示配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ 配置 API Key")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 标题
        tk.Label(
            dialog,
            text="🔑 配置 MiniMax API Key",
            font=self.fonts['heading']
        ).pack(pady=15)
        
        # 当前状态
        current_text = f"当前：{self.api_key[:10]}..." if self.api_key else "当前：未配置"
        tk.Label(
            dialog,
            text=current_text,
            font=self.fonts['normal'],
            fg=self.colors['text_light']
        ).pack(pady=5)
        
        # 输入框
        input_frame = tk.Frame(dialog)
        input_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(
            input_frame,
            text="新的 API Key:",
            font=self.fonts['normal']
        ).pack(side="left")
        
        api_entry = tk.Entry(input_frame, font=self.fonts['normal'], show="*")
        api_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # 说明
        help_frame = tk.Frame(dialog)
        help_frame.pack(fill="x", padx=30, pady=10)
        
        help_text = """获取 API Key:
1. 访问 https://platform.minimaxi.com/
2. 注册/登录账号
3. 进入 API Key 管理页面
4. 创建新的 API Key"""
        
        tk.Label(
            help_frame,
            text=help_text,
            font=self.fonts['small'],
            fg=self.colors['text_light'],
            justify="left"
        ).pack(anchor="w")
        
        # 按钮
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        def save_api_key():
            new_key = api_entry.get().strip()
            if new_key:
                CONFIG["api_key"] = new_key
                CONFIG["model"] = "MiniMax-M2.7"
                save_config(CONFIG)
                self.api_key = new_key
                self.api_status.config(text="🔑 API: 已配置", fg="#4caf50")
                messagebox.showinfo("成功", "API Key 已保存!\n请重启程序以应用新配置")
                dialog.destroy()
            else:
                messagebox.showwarning("提示", "请输入 API Key")
        
        tk.Button(
            btn_frame,
            text="保存",
            font=self.fonts['normal'],
            bg=self.colors['success'],
            fg="white",
            relief="flat",
            padx=30,
            pady=8,
            command=save_api_key
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="取消",
            font=self.fonts['normal'],
            bg="#e0e0e0",
            relief="flat",
            padx=30,
            pady=8,
            command=dialog.destroy
        ).pack(side="left", padx=10)
    
    def _show_interest_analysis(self):
        """显示兴趣度分析"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        # 获取最近聊天
        self.chat_display.config(state="normal")
        chat_history = self.chat_display.get("1.0", tk.END)[-1000:]
        self.chat_display.config(state="disabled")
        
        if len(chat_history) < 20:
            messagebox.showwarning("提示", "暂无足够聊天记录")
            return
        
        analysis = self.master_engine.analyze_interest(chat_history)
        
        # 创建结果窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("⭐ 兴趣度分析")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        # 标题
        tk.Label(
            dialog,
            text=f"📊 兴趣度：{analysis['score']}分 ({analysis['level']})",
            font=self.fonts['heading'],
            fg=self.colors['primary']
        ).pack(pady=15)
        
        # 积极信号
        if analysis['positive_signals']:
            tk.Label(
                dialog,
                text="✅ 积极信号:",
                font=self.fonts['normal'],
                fg=self.colors['success']
            ).pack(anchor="w", padx=30)
            for signal in analysis['positive_signals']:
                tk.Label(
                    dialog,
                    text=f"  • {signal}",
                    font=self.fonts['small']
                ).pack(anchor="w", padx=50)
        
        # 消极信号
        if analysis['negative_signals']:
            tk.Label(
                dialog,
                text="⚠️ 消极信号:",
                font=self.fonts['normal'],
                fg=self.colors['warning']
            ).pack(anchor="w", padx=30, pady=(10, 0))
            for signal in analysis['negative_signals']:
                tk.Label(
                    dialog,
                    text=f"  • {signal}",
                    font=self.fonts['small']
                ).pack(anchor="w", padx=50)
        
        # 建议
        if analysis['suggestions']:
            tk.Label(
                dialog,
                text="💡 建议:",
                font=self.fonts['normal'],
                fg=self.colors['info']
            ).pack(anchor="w", padx=30, pady=(10, 0))
            for suggestion in analysis['suggestions']:
                tk.Label(
                    dialog,
                    text=f"  • {suggestion}",
                    font=self.fonts['small']
                ).pack(anchor="w", padx=50)
        
        # 关闭按钮
        tk.Button(
            dialog,
            text="关闭",
            font=self.fonts['normal'],
            bg="#e0e0e0",
            relief="flat",
            padx=30,
            pady=8,
            command=dialog.destroy
        ).pack(pady=15)
    
    def _show_memories(self):
        """显示记忆"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        context = self.master_engine.get_context()
        memories = context.get("memories", [])
        
        # 创建结果窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("📝 查看记忆")
        dialog.geometry("500x400")
        
        # 标题
        tk.Label(
            dialog,
            text=f"📝 记忆列表 ({len(memories)}条)",
            font=self.fonts['heading']
        ).pack(pady=10)
        
        # 记忆列表
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        if memories:
            text_widget = scrolledtext.ScrolledText(
                list_frame,
                font=self.fonts['normal'],
                bg="#f8f9fa",
                relief="flat"
            )
            text_widget.pack(fill="both", expand=True)
            
            for mem in memories[-20:]:  # 最近 20 条
                text_widget.insert(tk.END, f"• {mem['content']}\n\n")
            
            text_widget.config(state="disabled")
        else:
            tk.Label(
                list_frame,
                text="暂无记忆",
                font=self.fonts['normal'],
                fg=self.colors['text_light']
            ).pack(pady=50)
        
        # 关闭按钮
        tk.Button(
            dialog,
            text="关闭",
            font=self.fonts['normal'],
            bg="#e0e0e0",
            relief="flat",
            padx=30,
            pady=8,
            command=dialog.destroy
        ).pack(pady=10)
    
    def _clear_memories(self):
        """清空记忆"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        if messagebox.askyesno("确认", "确定清空所有记忆？\n\n此操作不可恢复！"):
            if self.master_engine.current_session:
                self.master_engine.current_session.memories = []
            messagebox.showinfo("成功", "记忆已清空")
    
    def _new_session(self):
        """新建会话"""
        if self.master_engine:
            self.session_id = self.master_engine.start_session("gui_user")
            self._clear_chat()
            self._append_to_chat("系统", "🎉 新会话已创建", is_system=True)
            self._update_status()
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
💘 把妹大师 V24.0 - 使用指南

1. 配置 API Key
   - 文件 → 配置 API Key
   - 访问 https://platform.minimaxi.com/
   - 获取 MiniMax API Key

2. 添加女生
   - 左侧输入女生名字
   - 点击"➕"添加
   - 或从列表选择

3. 选择关系类型
   - 恋人/朋友/同事/客户等
   - 不同关系不同语气

4. 开始聊天
   - 输入对方消息
   - 点击"生成 AI 回复"
   - AI 生成 3 条选项

5. 快捷工具
   - 兴趣度分析：分析她对你的感觉
   - 查看记忆：查看当前女生的所有记忆
   - 清空记忆：重置记忆

💡 提示
   - 记忆越多，回复越精准
   - 可以切换不同女生聊天
   - 每个女生独立记忆
   - API 按使用量计费
"""
        messagebox.showinfo("使用指南", help_text)
    
    def _show_about(self):
        """显示关于"""
        about_text = """
💘 把妹大师 V24.0
Viking 大模型版

核心特性:
- MiniMax 大模型 API
- Viking 上下文管理
- 智能 Prompt 工程
- 多女生独立记忆
- 兴趣度分析

技术栈:
- Python 3.8+
- tkinter GUI
- MiniMax-M2.7

GitHub:
https://github.com/lianlong008-afk/111

© 2024 All Rights Reserved
"""
        messagebox.showinfo("关于", about_text)
    
    def _on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()


# ==================== 启动程序 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("💘 把妹大师 V24.0 - Viking 大模型版")
    print("正在启动 GUI...")
    print("=" * 60)
    
    try:
        app = PickupMasterV24GUI()
        app.root.mainloop()
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        print("\n请使用命令行版本：python3 main_cli_v24.py")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
