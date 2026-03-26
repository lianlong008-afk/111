#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V23.0 - Viking 终极版 - GUI 界面
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
    print(f"⚠️  tkinter 不可用：{e}")
    print("请使用命令行版本：python3 main_cli.py")
    sys.exit(1)

# 导入核心引擎
from pickup_master_v23_ultimate import PickupMasterV23
import threading


class PickupMasterGUI:
    """把妹大师 GUI 界面 - 兼容 macOS 26.2+"""
    
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("💘 把妹大师 V23.0 - Viking 终极版")
            self.root.geometry("900x700")
            self.root.minsize(800, 600)
            
            # 设置窗口背景色
            self.root.configure(bg='#f0f0f0')
            
            # 初始化变量
            self.master_engine = None
            self.session_id = None
            self.current_girl = tk.StringVar()
            self.girl_history = []
            self.processing = False
            
            # 设置样式
            self._setup_styles()
            
            # 创建界面
            self._create_header()
            self._create_main_area()
            self._create_status_bar()
            
            # 绑定关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # 异步初始化引擎
            self.root.after(100, self._init_engine_async)
            
        except Exception as e:
            print(f"❌ GUI 初始化失败：{e}")
            print("请使用命令行版本：python3 main_cli.py")
            sys.exit(1)
    
    def _setup_styles(self):
        """设置样式"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            self.colors = {
                'primary': '#667eea',
                'secondary': '#764ba2',
                'success': '#4caf50',
                'warning': '#ff9800',
                'danger': '#f44336',
                'bg': '#f0f0f0',
                'card': '#ffffff',
            }
        except Exception as e:
            print(f"⚠️ 样式设置警告：{e}")
    
    def _create_header(self):
        """创建顶部"""
        header = tk.Frame(self.root, bg=self.colors['primary'], pady=10)
        header.pack(fill="x")
        
        # 标题
        title_label = tk.Label(
            header, 
            text="💘 把妹大师 V23.0", 
            font=("Arial", 16, "bold"),
            bg=self.colors['primary'], 
            fg="white"
        )
        title_label.pack(side="left", padx=15)
        
        # 副标题
        subtitle_label = tk.Label(
            header,
            text="Viking 终极整合版",
            font=("Arial", 10),
            bg=self.colors['primary'],
            fg="white"
        )
        subtitle_label.pack(side="left", padx=10, pady=8)
        
        # 状态指示
        self.status_indicator = tk.Label(
            header,
            text="⚪ 初始化中...",
            font=("Arial", 10),
            bg=self.colors['primary'],
            fg="white"
        )
        self.status_indicator.pack(side="right", padx=15, pady=8)
    
    def _create_main_area(self):
        """创建主区域"""
        # 左右分栏
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['bg'], sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = tk.Frame(main_paned, bg=self.colors['card'], width=220)
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
        girl_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            girl_frame, 
            text="👧 当前女生", 
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 8))
        
        # 女生输入
        self.girl_entry = ttk.Combobox(girl_frame, textvariable=self.current_girl, font=("Arial", 10))
        self.girl_entry.pack(fill="x", pady=3)
        self.girl_entry.bind("<<ComboboxSelected>>", self._on_girl_selected)
        
        # 添加女生按钮
        tk.Button(
            girl_frame,
            text="➕ 添加女生",
            font=("Arial", 9),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            command=self._add_girl
        ).pack(fill="x", pady=3)
        
        # 女生列表
        self.girl_listbox = tk.Listbox(
            girl_frame, 
            font=("Arial", 10), 
            bg="#f8f9fa", 
            relief="flat",
            height=8
        )
        self.girl_listbox.pack(fill="both", expand=True, pady=8)
        self.girl_listbox.bind("<<ListboxSelect>>", self._on_girl_list_selected)
        
        # 快捷工具
        tools_frame = tk.Frame(parent, bg=self.colors['card'])
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            tools_frame,
            text="🛠️ 快捷工具",
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 8))
        
        tk.Button(
            tools_frame,
            text="💬 开场白",
            font=("Arial", 9),
            bg=self.colors['success'],
            fg="white",
            relief="flat",
            command=self._generate_opener
        ).pack(fill="x", pady=2)
        
        tk.Button(
            tools_frame,
            text="💕 调情短信",
            font=("Arial", 9),
            bg=self.colors['warning'],
            fg="white",
            relief="flat",
            command=self._generate_flirty_text
        ).pack(fill="x", pady=2)
        
        tk.Button(
            tools_frame,
            text="⭐ 兴趣度",
            font=("Arial", 9),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            command=self._analyze_interest
        ).pack(fill="x", pady=2)
    
    def _create_right_panel(self, parent):
        """创建右侧面板"""
        # 聊天历史
        chat_frame = tk.Frame(parent, bg=self.colors['card'])
        chat_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        tk.Label(
            chat_frame,
            text="💬 聊天记录",
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 8))
        
        # 聊天显示区
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=("Arial", 11),
            bg="#f8f9fa",
            relief="flat",
            wrap="word",
            spacing1=3,
            spacing3=3,
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.config(state="disabled")
        
        # 输入区
        input_frame = tk.Frame(parent, bg=self.colors['card'])
        input_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        tk.Label(
            input_frame,
            text="✏️ 输入消息",
            font=("Arial", 11, "bold"),
            bg=self.colors['card']
        ).pack(anchor="w", pady=(0, 8))
        
        # 输入框
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            font=("Arial", 11),
            bg="#f8f9fa",
            relief="flat",
            height=4,
        )
        self.input_text.pack(fill="x", pady=3)
        
        # 按钮
        btn_frame = tk.Frame(input_frame, bg=self.colors['card'])
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame,
            text="🗑️ 清空",
            font=("Arial", 9),
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=5,
            command=self._clear_chat
        ).pack(side="left", padx=3)
        
        tk.Button(
            btn_frame,
            text="📋 粘贴",
            font=("Arial", 9),
            bg="#e0e0e0",
            relief="flat",
            padx=15,
            pady=5,
            command=self._paste_text
        ).pack(side="left", padx=3)
        
        tk.Button(
            btn_frame,
            text="🚀 生成回复",
            font=("Arial", 10, "bold"),
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            command=self._generate_reply
        ).pack(side="right", padx=3)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = tk.Frame(self.root, bg=self.colors['secondary'], pady=5)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="就绪",
            font=("Arial", 9),
            bg=self.colors['secondary'],
            fg="white"
        )
        self.status_label.pack(side="left", padx=15)
        
        self.stats_label = tk.Label(
            status_bar,
            text="",
            font=("Arial", 9),
            bg=self.colors['secondary'],
            fg="white"
        )
        self.stats_label.pack(side="right", padx=15)
    
    def _init_engine_async(self):
        """异步初始化引擎"""
        def init():
            try:
                self.master_engine = PickupMasterV23()
                self.session_id = self.master_engine.start_session("gui_user")
                self.root.after(0, self._on_engine_ready)
            except Exception as e:
                self.root.after(0, lambda: self._show_error(f"初始化失败：{e}"))
        
        threading.Thread(target=init, daemon=True).start()
    
    def _on_engine_ready(self):
        """引擎就绪"""
        self.status_indicator.config(text="🟢 已就绪", fg="#4caf50")
        self._update_status()
        self._append_to_chat("系统", "🎉 把妹大师 V23.0 已启动！准备好撩妹了吗？", is_system=True)
    
    def _update_status(self):
        """更新状态"""
        if self.master_engine:
            try:
                status = self.master_engine.status()
                self.stats_label.config(
                    text=f"技巧库：{status['techniques_v20'] + status['techniques_v21']}个 | 会话：{status['sessions']}个"
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
        
        categories = ["好奇类", "赞美类", "关心类"]
        category = random.choice(categories)
        
        try:
            opener = self.master_engine.get_opening_line(category)
            self._append_to_chat("系统", f"💬 {category}开场白：{opener}", is_system=True)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", opener)
        except Exception as e:
            self._show_error(f"生成失败：{e}")
    
    def _generate_flirty_text(self):
        """生成调情短信"""
        if not self.master_engine:
            messagebox.showwarning("提示", "引擎未初始化")
            return
        
        categories = ["早安短信", "晚安短信", "甜蜜短信"]
        category = random.choice(categories)
        
        try:
            text = self.master_engine.get_flirty_text(category)
            self._append_to_chat("系统", f"💕 {category}：{text}", is_system=True)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", text)
        except Exception as e:
            self._show_error(f"生成失败：{e}")
    
    def _analyze_interest(self):
        """分析兴趣度"""
        chat_history = self._get_recent_chat()
        
        if not chat_history or len(chat_history) < 10:
            messagebox.showwarning("提示", "暂无足够聊天记录")
            return
        
        if not self.master_engine:
            return
        
        try:
            analysis = self.master_engine.analyze_girl_interest(chat_history)
            
            result = f"""
📊 兴趣度分析报告

得分：{analysis['score']}分 ({analysis['level']})
积极信号：{', '.join(analysis['positive_signals']) if analysis['positive_signals'] else '无'}
消极信号：{', '.join(analysis['negative_signals']) if analysis['negative_signals'] else '无'}
建议：{analysis['suggestions'][0] if analysis['suggestions'] else '继续聊天'}
"""
            self._append_to_chat("系统", result.strip(), is_system=True)
        except Exception as e:
            self._show_error(f"分析失败：{e}")
    
    def _generate_reply(self):
        """生成回复"""
        if self.processing:
            return
        
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
        self.processing = True
        
        # 后台生成回复
        def generate():
            try:
                result = self.master_engine.chat(message, girl_name=girl_name)
                self.root.after(0, lambda: self._on_reply_generated(result))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(f"生成失败：{e}"))
                self.root.after(0, lambda: setattr(self, 'processing', False))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _on_reply_generated(self, result):
        """回复生成完成"""
        self._append_to_chat("AI", result['reply'])
        self.input_text.delete("1.0", tk.END)
        self.processing = False
        self._update_status()
    
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
    
    def _get_recent_chat(self):
        """获取最近聊天"""
        self.chat_display.config(state="normal")
        content = self.chat_display.get("1.0", tk.END)
        self.chat_display.config(state="disabled")
        return content[-1000:] if len(content) > 1000 else content
    
    def _append_to_chat(self, sender, message, is_user=False, is_system=False):
        """添加消息到聊天"""
        self.chat_display.config(state="normal")
        
        if is_system:
            self.chat_display.insert(tk.END, f"[{sender}] {message}\n\n")
        elif is_user:
            self.chat_display.insert(tk.END, f"👤 {sender}: {message}\n\n")
        else:
            self.chat_display.insert(tk.END, f"🤖 {sender}: {message}\n\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
    
    def _show_error(self, message):
        """显示错误"""
        messagebox.showerror("错误", message)
    
    def _on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()


# 导入 random
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
        app.root.mainloop()
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        print("\n请使用命令行版本：python3 main_cli.py")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
