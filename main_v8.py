# -*- coding: utf-8 -*-
"""
微信高情商回复助手 V8.1 (P0稳定性重构版)
- 本地+AI混合引擎（无需API也能回复）
- 12种意图智能识别
- 3种回复风格（稳妥版/轻松版/升温版）
- 画像分析功能
- 对话历史自动保存
- AI思考日志系统
- 快捷短语库
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import re
import time
import json
import datetime
from PIL import Image, ImageGrab

# ============== 配置 ==============
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": "", "dark_mode": False, "quick_replies": [], "reply_mode": "hybrid"}

def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 加载配置
CONFIG = load_config()
API_KEY = CONFIG.get("api_key", "")
REPLY_MODE = CONFIG.get("reply_mode", "hybrid")

# Tesseract路径
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if not os.path.exists(TESSERACT_PATH):
    for path in [
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ]:
        if os.path.exists(path):
            TESSERACT_PATH = path
            break

# 好友数据存储文件
FRIENDS_FILE = os.path.join(os.path.dirname(__file__), 'friends.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'v6_log.txt')

# 主题配置
DARK_THEME = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "input_bg": "#2d2d2d",
    "button_bg": "#3d3d3d",
    "accent": "#667eea",
    "bubble_self": "#667eea",
    "bubble_other": "#3d3d3d",
    "text_self": "#ffffff",
    "text_other": "#e0e0e0",
}

LIGHT_THEME = {
    "bg": "#f5f5f5",
    "fg": "#333333",
    "input_bg": "#f5f5f5",
    "button_bg": "#e0e0e0",
    "accent": "#667eea",
    "bubble_self": "#667eea",
    "bubble_other": "#ffffff",
    "text_self": "#ffffff",
    "text_other": "#333333",
}

# 关系类型
RELATIONS = [
    ("恋人", "💕", "情侣/配偶关系"),
    ("朋友", "👯", "普通朋友关系"),
    ("同事", "💼", "工作同事关系"),
    ("客户", "🤝", "商务客户关系"),
    ("家人", "👨‍👩‍👧", "家庭成员关系"),
    ("追求者", "🌹", "追求/暗恋关系"),
    ("海王", "🌊", "暧昧/养鱼关系"),
    ("高冷", "🧊", "高冷女神/男神"),
]

print("微信高情商回复助手 V8.1 (P0稳定性重构版)")
print(f"Tesseract: {'已安装' if os.path.exists(TESSERACT_PATH) else '未安装'}")
print("-" * 40)

class LogWindow:
    """日志窗口"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("AI 思考过程")
        self.window.geometry("600x400")
        self.window.configure(bg="#1e1e1e")

        # 标题
        tk.Label(self.window, text="🤔 AI 思考日志", font=("微软雅黑", 12, "bold"),
                bg="#1e1e1e", fg="#00ff00").pack(pady=5)

        # 日志文本框
        self.text = tk.Text(self.window, font=("Consolas", 9),
                           bg="#1e1e1e", fg="#00ff00", relief="flat")
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

        # 滚动条
        scroll = tk.Scrollbar(self.text)
        scroll.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scroll.set)
        scroll.config(command=self.text.yview)

        # 按钮
        btn_frame = tk.Frame(self.window, bg="#1e1e1e")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="清空", bg="#333", fg="white", relief="flat",
                 command=self.clear).pack(side="left", padx=5)
        tk.Button(btn_frame, text="关闭", bg="#333", fg="white", relief="flat",
                 command=self.window.withdraw).pack(side="left", padx=5)

    def log(self, text, color="#00ff00"):
        """添加日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text.insert("end", f"[{timestamp}] {text}\n")
        self.text.see("end")
        # 保存到文件
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {text}\n")
        except:
            pass

    def clear(self):
        self.text.delete("1.0", "end")

class FriendManager:
    """好友管理器"""
    def __init__(self):
        self.friends = self.load_friends()

    def load_friends(self):
        """加载好友列表"""
        if os.path.exists(FRIENDS_FILE):
            try:
                with open(FRIENDS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_friends(self):
        """保存好友列表"""
        with open(FRIENDS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.friends, f, ensure_ascii=False, indent=2)

    def add_friend(self, name, relation_type, chat_history="", profile=""):
        """添加/更新好友"""
        self.friends[name] = {
            "relation": relation_type,
            "chat_history": chat_history,
            "profile": profile,
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.save_friends()

    def get_friend(self, name):
        """获取好友信息"""
        return self.friends.get(name)

    def delete_friend(self, name):
        """删除好友"""
        if name in self.friends:
            del self.friends[name]
            self.save_friends()

class BubbleMessage:
    """气泡消息组件"""
    def __init__(self, parent, is_self=False):
        self.frame = tk.Frame(parent, bg="#f0f0f0")

        # 头像
        avatar_label = tk.Label(self.frame, text="👤" if not is_self else "😀",
                               font=("微软雅黑", 16), bg="#f0f0f0")
        avatar_label.pack(side="left" if not is_self else "right", padx=5)

        # 消息气泡
        self.bubble = tk.Frame(self.frame, bg="#ffffff" if not is_self else "#667eea")
        self.bubble.pack(side="left" if not is_self else "right", fill="x", expand=True)

        self.text = tk.Label(self.bubble, text="", font=("微软雅黑", 10),
                           bg="#ffffff" if not is_self else "#667eea",
                           fg="#333333" if not is_self else "#ffffff",
                           wraplength=250, justify="left" if not is_self else "right",
                           padx=10, pady=8)
        self.text.pack(padx=5, pady=3)

    def set_text(self, text):
        self.text.config(text=text)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信高情商回复 V7.1")
        self.root.geometry("400x700")
        self.root.configure(bg='#f5f5f5')

        # 数据初始化
        self.friend_manager = FriendManager()
        self.current_friend = None
        self.conversation = []  # 当前对话历史 [(对方消息, 回复选项), ...]
        self.processing = False

        # 好友画像
        self.friend_profile = ""

        # 新增变量初始化（修复未定义bug）
        self.friend_var = tk.StringVar()
        self.current_style = tk.StringVar(value="稳妥版")
        self.quick_buttons_frame = None
        self.current_replies = []

        # 创建日志窗口
        self.log_window = LogWindow(self.root)

        # 检查API Key
        if not API_KEY:
            self.root.after(500, self.show_config)

        self.setup_ui()
        self.root.mainloop()

    def log(self, text):
        """记录日志"""
        self.log_window.log(text)
        print(f"[LOG] {text}")

    def setup_ui(self):
        # ===== 简洁现代化UI布局 =====

        # 1. 顶部标题栏（只有一个设置按钮）
        header = tk.Frame(self.root, bg="#667eea", pady=12)
        header.pack(fill="x")
        header.pack_propagate(False)

        # 左侧标题
        tk.Label(header, text="💬 微信高情商回复", font=("微软雅黑", 14, "bold"),
                bg="#667eea", fg="white").pack(side="left", padx=15)

        # 右侧 - 合并为一个设置按钮
        header_btn_frame = tk.Frame(header, bg="#667eea")
        header_btn_frame.pack(side="right", padx=15)

        # 深色模式按钮
        self.dark_mode = CONFIG.get("dark_mode", False)
        dark_text = "☀️" if self.dark_mode else "🌙"

        self.dark_mode_btn = tk.Button(header_btn_frame, text=dark_text,
                                       font=("微软雅黑", 12), bg="#5568d6", fg="white",
                                       relief="flat", padx=10, pady=2,
                                       command=self.toggle_dark_mode)
        self.dark_mode_btn.pack(side="right", padx=5)

        # 设置按钮（合并所有功能）
        tk.Button(header_btn_frame, text="⚙️ 设置",
                 font=("微软雅黑", 11, "bold"), bg="#4CAF50", fg="white",
                 relief="flat", padx=12, pady=2,
                 command=self.show_config).pack(side="right", padx=5)

        # 2. 中间主区域 - 使用PanedWindow左右分栏
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#f0f0f0", sashrelief=tk.RAISED, sashwidth=4)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧好友面板 (100px宽度)
        left_frame = tk.Frame(main_paned, bg="white", width=100)
        main_paned.add(left_frame, minsize=100)

        # 左侧好友列表标题
        tk.Label(left_frame, text="👥 好友", font=("微软雅黑", 11, "bold"),
                bg="white", fg="#333").pack(pady=(10, 5))

        # 好友列表
        self.friend_listbox = tk.Listbox(left_frame, font=("微软雅黑", 10),
                                        bg="#f8f9fa", relief=tk.FLAT, borderwidth=0)
        self.friend_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.friend_listbox.bind('<<ListboxSelect>>', self.on_friend_list_selected)

        # 添加好友按钮
        tk.Button(left_frame, text="➕ 添加好友", font=("微软雅黑", 9),
                 bg="#4CAF50", fg="white", relief=tk.FLAT,
                 command=self.add_friend).pack(pady=5, padx=5, fill=tk.X)

        # 右侧对话区域
        right_frame = tk.Frame(main_paned, bg="#f0f0f0")
        main_paned.add(right_frame, minsize=250)

        # 右侧顶部 - 关系选择
        relation_bar = tk.Frame(right_frame, bg="white", pady=8)
        relation_bar.pack(fill=tk.X)

        tk.Label(relation_bar, text="💝 关系:", font=("微软雅黑", 10),
                bg="white").pack(side=tk.LEFT, padx=10)

        self.relation_var = tk.StringVar()
        relation_combo = ttk.Combobox(relation_bar, textvariable=self.relation_var,
                                      values=[f"{e} {n}" for n, e, d in RELATIONS],
                                      font=("微软雅黑", 10), state="readonly", width=15)
        relation_combo.pack(side=tk.LEFT, padx=5)
        relation_combo.bind("<<ComboboxSelected>>", self.on_relation_selected)

        # 画像分析按钮
        tk.Button(relation_bar, text="🔍 分析画像", font=("微软雅黑", 9),
                 bg="#2196F3", fg="white", relief=tk.FLAT,
                 command=self.analyze_profile).pack(side=tk.RIGHT, padx=5)

        # 查看画像按钮
        tk.Button(relation_bar, text="👁 查看画像", font=("微软雅黑", 9),
                 bg="#9C27B0", fg="white", relief=tk.FLAT,
                 command=self.show_friend_profile).pack(side=tk.RIGHT, padx=5)

        # 对话气泡区域
        self.chat_frame = tk.Frame(right_frame, bg="#f0f0f0")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        self.canvas = tk.Canvas(self.chat_frame, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.chat_frame, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=scrollbar.set)

        self.messages_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor=tk.NW)
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 3. 底部输入区域
        input_area = tk.Frame(self.root, bg="white", padx=10, pady=10)
        input_area.pack(fill=tk.X, side=tk.BOTTOM)

        # 输入框
        self.input_txt = tk.Text(input_area, height=3, font=("微软雅黑", 11),
                                bg="#f5f5f5", relief=tk.FLAT, padx=10, pady=8)
        self.input_txt.pack(fill=tk.X, pady=(0, 8))

        # 操作按钮行
        btn_row = tk.Frame(input_area, bg="white")
        btn_row.pack(fill=tk.X)

        # 左侧工具按钮
        tool_btns = [
            ("📋 粘贴", self.paste),
            ("📷 截图", self.screenshot_ocr),
            ("📁 导入", self.import_chat),
            ("⚡ 快捷", self.show_quick_buttons),
        ]

        for text, cmd in tool_btns:
            tk.Button(btn_row, text=text, font=("微软雅黑", 9),
                    bg="#e0e0e0", relief=tk.FLAT,
                    command=cmd).pack(side=tk.LEFT, padx=3)

        # 右侧生成按钮
        self.gen_btn = tk.Button(btn_row, text="🚀 生成回复",
                                font=("微软雅黑", 10, "bold"), bg="#667eea", fg="white",
                                relief=tk.FLAT, padx=20, pady=5, command=self.generate)
        self.gen_btn.pack(side=tk.RIGHT, padx=3)

        # 回复显示区域
        reply_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        reply_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(reply_frame, text="👇 点击选择回复:", font=("微软雅黑", 9, "bold"),
                bg="white").pack(anchor="w")

        self.reply_list = tk.Listbox(reply_frame, font=("微软雅黑", 10),
                                    height=3, bg="#f8f9fa", relief=tk.FLAT)
        self.reply_list.pack(fill=tk.X, pady=3)
        self.reply_list.bind("<ButtonRelease-1>", self.copy_reply)

        # 加载好友列表
        self.update_friend_list()

    def update_friend_list(self):
        """更新好友列表"""
        # 清空列表
        self.friend_listbox.delete(0, tk.END)

        # 添加好友到列表
        friends = list(self.friend_manager.friends.keys())
        for friend in friends:
            # 获取关系类型
            friend_data = self.friend_manager.get_friend(friend)
            rel = friend_data.get("relation", "") if friend_data else ""
            # 关系emoji
            rel_emoji = ""
            for n, e, d in RELATIONS:
                if n == rel:
                    rel_emoji = e
                    break

            display_text = f"{rel_emoji} {friend}"
            self.friend_listbox.insert(tk.END, display_text)

        # 选择第一个好友
        if friends:
            self.friend_listbox.selection_set(0)
            self.friend_listbox.bind('<<ListboxSelect>>', self.on_friend_list_selected)
            # 触发选择第一个好友（延迟执行确保UI已初始化）
            self.root.after(200, self._select_first_friend)

    def _select_first_friend(self):
        """选择第一个好友（延迟执行）"""
        if hasattr(self, 'friend_listbox') and self.friend_listbox.size() > 0:
            self.on_friend_list_selected(None)

    def on_friend_list_selected(self, event):
        """从列表选择好友"""
        # 安全检查
        if not hasattr(self, 'friend_listbox') or not self.friend_listbox:
            return

        selection = self.friend_listbox.curselection()
        if not selection:
            return

        # 获取选中的好友名称（去掉emoji）
        display_text = self.friend_listbox.get(selection[0])
        name = display_text.split(" ", 1)[-1] if " " in display_text else display_text

        if not name:
            return

        friend = self.friend_manager.get_friend(name)
        if friend:
            self.current_friend = name
            self.friend_profile = friend.get("profile", "")

            # 设置关系类型
            rel = friend.get("relation", "")
            for n, e, d in RELATIONS:
                if n == rel:
                    self.relation_var.set(f"{e} {n}")
                    break

            self.log(f"切换到好友: {name}")

            # 清空对话显示
            for widget in self.messages_frame.winfo_children():
                widget.destroy()

            # 清空当前对话历史（关键修复！）
            self.conversation = []

            # 加载历史对话
            self.load_conversation_history()

    def on_friend_selected(self, event):
        """选择好友（兼容旧代码）"""
        # 检查必要变量是否已初始化
        if not hasattr(self, 'relation_var') or not self.relation_var:
            return

        name = self.friend_var.get()
        if not name:
            return

        friend = self.friend_manager.get_friend(name)
        if friend:
            self.current_friend = name
            self.friend_profile = friend.get("profile", "")
            # 设置关系类型
            rel = friend.get("relation", "")
            for i, (n, e, d) in enumerate(RELATIONS):
                if n == rel:
                    self.relation_var.set(f"{e} {n} - {d}")
                    break
            self.log(f"切换到好友: {name}")
            # 清空显示
            for widget in self.messages_frame.winfo_children():
                widget.destroy()

            # 清空当前对话历史（关键修复！）
            self.conversation = []

            # 加载历史对话
            self.load_conversation_history()

    def on_relation_selected(self, event):
        """选择关系类型"""
        if self.current_friend:
            rel_text = self.relation_var.get()
            rel_name = rel_text.split()[1] if len(rel_text.split()) > 1 else ""
            self.friend_manager.add_friend(self.current_friend, rel_name)
            self.log(f"更新关系类型: {rel_name}")

    def add_friend(self):
        """添加好友"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加好友")
        dialog.geometry("300x150")
        dialog.configure(bg="white")

        tk.Label(dialog, text="好友昵称:", font=("微软雅黑", 10), bg="white").pack(pady=5)
        name_entry = tk.Entry(dialog, font=("微软雅黑", 10))
        name_entry.pack(pady=5)

        tk.Label(dialog, text="关系类型:", font=("微软雅黑", 10), bg="white").pack(pady=5)
        rel_var = tk.StringVar()
        rel_combo = ttk.Combobox(dialog, textvariable=rel_var,
                                 values=[n for n, e, d in RELATIONS])
        rel_combo.pack(pady=5)

        def confirm():
            name = name_entry.get().strip()
            rel = rel_var.get()
            if name:
                self.friend_manager.add_friend(name, rel)
                self.update_friend_list()
                self.friend_var.set(name)
                self.on_friend_selected(None)
                dialog.destroy()
                self.log(f"添加好友: {name}")

        tk.Button(dialog, text="确定", bg="#4CAF50", fg="white",
                 command=confirm).pack(pady=10)

    def delete_friend(self):
        """删除好友"""
        name = self.friend_var.get()
        if name:
            if messagebox.askyesno("确认", f"确定删除好友 {name} 吗?"):
                self.friend_manager.delete_friend(name)
                self.update_friend_list()
                self.log(f"删除好友: {name}")

    def show_log(self):
        """显示日志窗口"""
        print("[DEBUG] show_log 被点击!")
        self.log_window.window.deiconify()

    def show_friend_profile(self):
        """查看好友画像"""
        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择好友")
            return

        friend = self.friend_manager.get_friend(self.current_friend)
        if not friend:
            messagebox.showwarning("提示", "好友信息不存在")
            return

        profile = friend.get("profile", "")
        if not profile:
            messagebox.showinfo("画像", f"【{self.current_friend}】\n\n暂无画像分析\n\n点击「🔍 分析画像」生成")
            return

        # 显示画像弹窗
        dialog = tk.Toplevel(self.root)
        dialog.title(f"👤 {self.current_friend} 的画像")
        dialog.geometry("400x300")
        dialog.configure(bg="white")

        tk.Label(dialog, text=f"【{self.current_friend}】的画像", 
                font=("微软雅黑", 12, "bold"), bg="white", fg="#667eea").pack(pady=10)

        # 画像内容
        text_widget = tk.Text(dialog, font=("微软雅黑", 10), bg="#f8f9fa",
                            relief=tk.FLAT, padx=15, pady=15, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        text_widget.insert("1.0", profile)
        text_widget.config(state="disabled")  # 只读

        tk.Button(dialog, text="关闭", bg="#e0e0e0",
                 command=dialog.destroy).pack(pady=10)

    def toggle_dark_mode(self):
        """切换深色模式"""
        self.dark_mode = not self.dark_mode

        # 保存配置
        CONFIG["dark_mode"] = self.dark_mode
        save_config(CONFIG)

        # 更新按钮
        self.dark_mode_btn.config(text="☀️" if self.dark_mode else "🌙")

        # 刷新UI
        messagebox.showinfo("提示", "深色模式将在重启后生效" if not self.dark_mode else "深色模式已开启")

    def show_stats(self):
        """显示使用统计面板"""
        self.log("打开统计面板...")
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 使用统计")
        dialog.geometry("350x200")
        dialog.configure(bg="white")

        # 标题
        tk.Label(dialog, text="📊 我的使用统计", font=("微软雅黑", 14, "bold"),
                bg="white", fg="#667eea").pack(pady=15)

        # 统计卡片
        stats_frame = tk.Frame(dialog, bg="white")
        stats_frame.pack(pady=10)

        # 好友数量
        friend_count = len(self.friend_manager.friends)
        tk.Label(stats_frame, text="👥 好友数量", font=("微软雅黑", 10),
                bg="white", fg="#888").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        tk.Label(stats_frame, text=str(friend_count), font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2196F3").grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # 快捷短语数量
        quick_count = len(CONFIG.get("quick_replies", []))
        tk.Label(stats_frame, text="⚡ 快捷短语", font=("微软雅黑", 10),
                bg="white", fg="#888").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        tk.Label(stats_frame, text=str(quick_count), font=("微软雅黑", 16, "bold"),
                bg="white", fg="#9C27B0").grid(row=1, column=1, padx=20, pady=10, sticky="e")

        # 关闭按钮
        tk.Button(dialog, text="关闭", bg="#e0e0e0",
                 command=dialog.destroy).pack(pady=15)

    def show_config(self):
        """显示设置窗口（整合配置、统计、日志）"""
        print("[DEBUG] show_config 被点击!")
        self.log("打开设置窗口...")
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ 设置")
        dialog.geometry("450x450")
        dialog.configure(bg="white")

        # ===== 顶部功能按钮 =====
        func_btn_frame = tk.Frame(dialog, bg="#667eea", pady=10)
        func_btn_frame.pack(fill="x")

        btn_style = {"font": ("微软雅黑", 11, "bold"), "bg": "#4CAF50", "fg": "white",
                    "relief": "flat", "padx": 15, "pady": 8}

        tk.Button(func_btn_frame, text="📊 统计", command=self.show_stats,
                 **btn_style).pack(side="left", padx=10, expand=True, fill="x")

        tk.Button(func_btn_frame, text="📋 日志", command=self.show_log,
                 **btn_style).pack(side="left", padx=10, expand=True, fill="x")

        # ===== API Key配置 =====
        tk.Label(dialog, text="🔑 API Key", font=("微软雅黑", 11, "bold"),
                bg="white").pack(anchor="w", padx=20, pady=(15, 5))

        api_entry = tk.Entry(dialog, font=("Consolas", 10), show="*")
        api_entry.pack(fill="x", padx=20, pady=5)
        if API_KEY:
            api_entry.insert(0, API_KEY)

        tk.Label(dialog, text="* 请输入MiniMax API Key",
                font=("微软雅黑", 8), bg="white", fg="#888").pack(anchor="w", padx=20)

        # 保存按钮
        def save_api():
            new_key = api_entry.get().strip()
            if new_key:
                global API_KEY
                API_KEY = new_key
                CONFIG["api_key"] = new_key
                save_config(CONFIG)
                messagebox.showinfo("完成", "API Key已保存！")
            else:
                messagebox.showwarning("警告", "请输入API Key")

        tk.Button(dialog, text="💾 保存API Key", bg="#667eea", fg="white",
                 font=("微软雅黑", 10, "bold"), command=save_api).pack(pady=5)

        # 快捷短语库
        tk.Label(dialog, text="⚡ 快捷短语:", font=("微软雅黑", 10, "bold"),
                bg="white").pack(anchor="w", padx=20, pady=(20, 5))

        quick_frame = tk.Frame(dialog, bg="white")
        quick_frame.pack(fill="both", expand=True, padx=20)

        self.quick_list = tk.Listbox(quick_frame, font=("微软雅黑", 9), height=5)
        self.quick_list.pack(side="left", fill="both", expand=True)

        quick_scroll = tk.Scrollbar(quick_frame)
        quick_scroll.pack(side="right", fill="y")
        self.quick_list.config(yscrollcommand=quick_scroll.set)
        quick_scroll.config(command=self.quick_list.yview)

        # 加载快捷短语
        quick_replies = CONFIG.get("quick_replies", [])
        for q in quick_replies:
            self.quick_list.insert(tk.END, q)

        # 添加/删除快捷短语
        quick_btn_frame = tk.Frame(dialog, bg="white")
        quick_btn_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(quick_btn_frame, text="+", bg="#4CAF50", fg="white",
                 command=lambda: self.add_quick_reply(dialog, self.quick_list)).pack(side="left", padx=2)
        tk.Button(quick_btn_frame, text="-", bg="#f44336", fg="white",
                 command=lambda: self.del_quick_reply(self.quick_list)).pack(side="left", padx=2)

        # 保存按钮
        def save_api():
            new_key = api_entry.get().strip()
            if new_key:
                global API_KEY
                API_KEY = new_key
                CONFIG["api_key"] = new_key
                save_config(CONFIG)
                messagebox.showinfo("完成", "API Key已保存！")
            else:
                messagebox.showwarning("警告", "请输入API Key")

    def add_quick_reply(self, dialog, listbox):
        """添加快捷短语"""
        dialog2 = tk.Toplevel(dialog)
        dialog2.title("添加快捷短语")
        dialog2.geometry("300x100")

        tk.Label(dialog2, text="输入快捷短语:").pack(pady=5)
        entry = tk.Entry(dialog2, font=("微软雅黑", 10))
        entry.pack(pady=5)

        def confirm():
            text = entry.get().strip()
            if text:
                listbox.insert(tk.END, text)
                quick_list = list(listbox.get(0, tk.END))
                CONFIG["quick_replies"] = quick_list
                save_config(CONFIG)
                dialog2.destroy()

        tk.Button(dialog2, text="确定", command=confirm).pack(pady=5)

    def del_quick_reply(self, listbox):
        """删除快捷短语"""
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])
            quick_list = list(listbox.get(0, tk.END))
            CONFIG["quick_replies"] = quick_list
            save_config(CONFIG)

    def add_message(self, text, is_self=False):
        """添加消息气泡"""
        bubble = BubbleMessage(self.messages_frame, is_self)
        bubble.set_text(text)
        bubble.pack(fill="x", pady=3)
        # 滚动到底部
        self.root.update()
        self.canvas.yview_moveto(1.0)

    def paste(self):
        """粘贴"""
        try:
            text = self.root.clipboard_get()
            self.input_txt.delete("1.0", "end")
            self.input_txt.insert("1.0", text)
        except:
            pass

    def _copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("✅ 完成", "文字已复制到剪贴板，可直接粘贴")
        except Exception as e:
            self.log(f"剪贴板失败: {e}")

    def screenshot_ocr(self):
        """截图OCR - 只用在线API"""
        def do_ocr():
            try:
                from PIL import ImageGrab
                import requests

                self.log("开始OCR...")
                
                # 获取剪贴板图片
                img = ImageGrab.grabclipboard()
                
                if not img or not isinstance(img, Image.Image):
                    self.log("错误：剪贴板没有图片")
                    self.root.after(0, lambda: messagebox.showwarning("失败", "请先截图！\n\n步骤：\n1. 按 Win+Shift+S 截图\n2. 再点此按钮"))
                    return

                # 保存临时文件
                temp_path = os.path.join(os.path.dirname(__file__), 'temp_ocr.png')
                img.save(temp_path)
                self.log("图片已保存，调用在线OCR...")

                # 调用在线OCR API
                try:
                    with open(temp_path, 'rb') as f:
                        files = {'file': f}
                        data = {'language': 'chs', 'isOverlayRequired': 'false'}
                        resp = requests.post('https://api.ocr.space/parse/image', 
                                           files=files, data=data, timeout=60)
                    
                    result_json = resp.json()
                    self.log(f"API返回: {str(result_json)[:100]}")
                    
                    if result_json.get('ParsedResults'):
                        text = result_json['ParsedResults'][0]['ParsedText'].strip()
                        self.log(f"识别结果: {text[:50] if text else '空'}")
                        
                        if text and len(text) > 0:
                            # 成功！填入输入框并复制
                            self.root.after(0, lambda: self.input_txt.delete("1.0", "end"))
                            self.root.after(0, lambda: self.input_txt.insert("1.0", text))
                            self.root.after(0, lambda: self._copy_to_clipboard(text))
                            self.root.after(0, lambda: self.log(f"OCR成功: {text[:30]}..."))
                        else:
                            self.root.after(0, lambda: messagebox.showwarning("OCR", "未识别到文字"))
                    else:
                        error_msg = result_json.get('ErrorMessage', '未知错误')
                        self.log(f"OCR失败: {error_msg}")
                        self.root.after(0, lambda: messagebox.showwarning("OCR失败", error_msg))
                        
                except Exception as api_err:
                    self.log(f"在线OCR异常: {str(api_err)[:50]}")
                    self.root.after(0, lambda: messagebox.showwarning("OCR失败", f"网络错误: {api_err}"))

                # 清理
                try:
                    os.remove(temp_path)
                except:
                    pass

            except Exception as e:
                self.log(f"OCR错误: {str(e)[:80]}")
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))

        threading.Thread(target=do_ocr, daemon=True).start()

    def import_chat(self):
        """导入聊天记录"""
        file_path = filedialog.askopenfilename(title="选择聊天记录",
                                             filetypes=[("文本", "*.txt"), ("所有", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 解析好友名称（从文件名或内容第一行）
                friend_name = self._parse_friend_name(content, file_path)

                # 如果好友不存在，自动创建
                if friend_name and not self.friend_manager.get_friend(friend_name):
                    self.friend_manager.add_friend(friend_name, "朋友", "", "")
                    self.update_friend_list()
                    self.log(f"自动创建好友: {friend_name}")

                # 如果当前没有选中好友，选中新导入的好友
                if friend_name and not self.current_friend:
                    self._select_friend_by_name(friend_name)

                # 显示导入的内容
                self.add_message(f"📁 已导入 [{friend_name}] 的聊天记录 ({len(content)}字符)", False)
                self.log(f"导入聊天记录: {len(content)}字符，好友: {friend_name}")
                return content[:3000]
            except Exception as e:
                self.log(f"导入失败: {e}")
        return ""

    def _parse_friend_name(self, content, file_path):
        """从聊天内容或文件名解析好友名称"""
        import re
        # 尝试从内容第一行解析（微信导出格式：昵称-微信号）
        lines = content.split('\n')
        if lines:
            first_line = lines[0].strip()
            # 匹配 昵称-微信号 格式
            match = re.match(r'^([^\-]+)-[a-zA-Z0-9_]+$', first_line)
            if match:
                return match.group(1).strip()
            # 如果第一行很短且不是日期，可能是昵称
            if first_line and len(first_line) <= 20 and not re.match(r'\d+[/年]', first_line):
                if not any(kw in first_line for kw in ['对方', '我:', '20']):
                    return first_line
        # 从文件名解析
        filename = os.path.basename(file_path)
        name = os.path.splitext(filename)[0]
        # 去掉常见的导出前缀
        name = re.sub(r'^(聊天记录|微信|wechat)_?', '', name)
        return name.strip() if name else "新好友"

    def _select_friend_by_name(self, name):
        """根据名称选中新好友"""
        # 查找好友列表中的索引
        for i in range(self.friend_listbox.size()):
            if name in self.friend_listbox.get(i):
                self.friend_listbox.selection_clear(0, tk.END)
                self.friend_listbox.selection_set(i)
                self.on_friend_list_selected(None)
                return

    def analyze_profile(self):
        """分析好友画像"""
        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择或添加好友")
            return

        if not API_KEY:
            messagebox.showwarning("提示", "请先配置API Key")
            return

        self.log("开始分析好友画像...")
        self.gen_btn.config(state="disabled")

        def run():
            try:
                import requests

                # 获取聊天记录内容
                chat_content = self.import_chat()
                if not chat_content:
                    chat_content = "无聊天记录，请根据好友昵称和关系类型分析"

                prompt = f"""【角色】你是用户的老朋友，正在帮用户分析一个朋友/恋人的性格。

【任务】根据聊天记录，用轻松、口语化的方式描述这个人的性格特点。

【输出内容】
- 聊天风格（话多/话少/打字快慢/爱发表情包吗）
- 性格印象（暖男/高冷/幽默/慢性子/急性子）
- 相处感受（让人舒服/需要哄/有点粘人/很独立）
- 一个有趣的小细节（从聊天中发现的独特习惯）

【要求】
- 80-120字，像朋友间八卦聊天一样自然
- 用"他"或"她"而不是"该用户"
- 语气温暖有爱，像在说一个真实的人
- 不要JSON，不要列表格式，用一段话自然描述

【聊天记录摘要】
{chat_content[:800] if chat_content else '暂无详细聊天记录，仅根据昵称和关系分析'}

请开始分析："""

                url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
                data = {
                    "model": "MiniMax-M2.7",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                }

                resp = requests.post(url, headers=headers, json=data, timeout=30)

                if resp.status_code != 200:
                    raise Exception(f"API错误: {resp.status_code}")

                result = resp.json()
                api_msg = result.get("choices", [{}])[0].get("message", {})
                profile = api_msg.get("content", "") or api_msg.get("reasoning_content", "")

                if not profile:
                    raise Exception("API返回为空")

                self.log(f"画像生成成功: {profile[:50]}...")

                # 保存画像
                rel_text = self.relation_var.get() or ""
                rel_name = "朋友"
                for n, e, d in RELATIONS:
                    if n in rel_text or e in rel_text:
                        rel_name = n
                        break

                # 获取已有聊天记录
                current_friend_data = self.friend_manager.get_friend(self.current_friend)
                existing_history = ""
                if current_friend_data:
                    existing_history = current_friend_data.get("chat_history", "")

                # 合并聊天记录
                merged_history = existing_history
                if chat_content and chat_content != "无聊天记录，请根据好友昵称和关系类型分析":
                    if existing_history:
                        merged_history = existing_history + "\n" + chat_content
                    else:
                        merged_history = chat_content

                # 保存到好友
                self.friend_manager.add_friend(
                    self.current_friend,
                    rel_name,
                    merged_history[:5000],
                    profile
                )
                self.friend_profile = profile

                # 验证保存
                saved = self.friend_manager.get_friend(self.current_friend)
                if saved and saved.get("profile"):
                    self.log("画像已保存到好友数据")
                else:
                    self.log("警告：画像保存验证失败")

                self.root.after(0, lambda: messagebox.showinfo("完成", f"画像分析完成\n\n{profile[:300]}"))

            except Exception as e:
                error_msg = str(e)
                self.log(f"分析失败: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, lambda: self.gen_btn.config(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def generate(self):
        """生成回复"""
        if self.processing:
            return

        msg = self.input_txt.get("1.0", "end").strip()
        if not msg:
            messagebox.showwarning("提示", "请输入对方的消息")
            return

        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择或添加好友")
            return

        # 添加对方消息到对话
        self.add_message(msg, False)
        self.conversation.append((msg, None))

        self.processing = True
        self.gen_btn.config(state="disabled")
        self.log(f"对方: {msg[:30]}...")

        def run():
            try:
                import requests

                # 检查API Key
                if not API_KEY:
                    self.root.after(0, lambda: messagebox.showwarning("警告", "请先配置API Key"))
                    return

                name = self.current_friend
                rel_text = self.relation_var.get() or "朋友"
                rel_name = rel_text.split()[1] if len(rel_text.split()) > 1 else "朋友"
                rel_emoji = ""
                for n, e, d in RELATIONS:
                    if n == rel_name:
                        rel_emoji = e
                        break

                # 构建上下文
                context = ""
                if self.conversation:
                    context_lines = []
                    for i, (their_msg, our_reply) in enumerate(self.conversation[-8:]):
                        context_lines.append(f"第{i+1}轮 - 对方说: {their_msg}")
                        if our_reply:
                            context_lines.append(f"   我的回复: {our_reply}")
                    context = "\n".join(context_lines)

                # 根据关系类型选择不同的语气指导
                tone_guide = {
                    "恋人": "甜蜜亲密，体现关心和爱意",
                    "朋友": "自然轻松，幽默风趣",
                    "同事": "专业礼貌，保持适当距离",
                    "客户": "商务专业，稳妥可靠",
                    "家人": "亲情温暖，体贴关怀",
                    "追求者": "委婉得体，不伤害对方",
                    "海王": "保持暧昧，欲拒还迎",
                    "高冷": "简洁冷淡，爱搭不理"
                }
                guide = tone_guide.get(rel_name, "自然得体")

                # 根据关系类型提供示例
                examples = {
                    "恋人": "想你我刚忙完你呢\n好呀周六见\n爱你么么哒",
                    "朋友": "可以啊去哪吃\n哈哈没问题\n周末约一个",
                    "客户": "感谢您的认可\n期待合作愉快\n我尽快安排",
                    "同事": "好的收到\n明白\n我处理一下",
                    "家人": "不用担心有我呢\n好的爸妈\n我爱你们",
                    "追求者": "谢谢你的心意\n我们先了解吧\n我现在比较忙",
                    "海王": "在忙晚点说\n最近比较累\n你有事吗",
                    "高冷": "哦\n干嘛\n有事说事"
                }
                style = self.current_style.get() or "稳妥版"

                style_map = {
                    "稳妥版": "稳重得体",
                    "轻松版": "轻松俏皮",
                    "升温版": "热情主动"
                }
                style_tag = style_map.get(style, "稳重得体")

                # 简化的system prompt
                system_prompt = f"""你是微信回复助手。请根据对话输出3条回复，每条6-16字，只输出中文回复，不要解释。"""

                # 构建完整上下文
                context_parts = []
                
                # 1. 用户关系
                context_parts.append(f"【我和TA的关系】{rel_name}")
                
                # 2. TA的性格画像（如果有）
                if self.friend_profile:
                    context_parts.append(f"【TA的性格画像】{self.friend_profile[:200]}")
                
                # 3. 最近聊天历史（最近的5轮对话）
                if self.conversation and len(self.conversation) > 0:
                    history_lines = ["【最近聊天记录】"]
                    for i, (their, ours) in enumerate(self.conversation[-5:]):
                        history_lines.append(f"TA说：{their}")
                        if ours:
                            history_lines.append(f"我说：{ours}")
                    context_parts.append("\n".join(history_lines))
                
                # 4. 当前情境
                context_parts.append(f"【TA刚发来】{msg}")
                context_parts.append(f"【我的角色】{rel_name}，风格{style_tag}")
                
                full_context = "\n\n".join(context_parts)
                
                user_prompt = f"""{full_context}

输出3条回复，每行一条，只输出中文："""

                self.log(f"AI思考中... (关系:{rel_name})")

                url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
                data = {
                    "model": "MiniMax-M2.7",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 300
                }

                resp = requests.post(url, headers=headers, json=data, timeout=30)

                # 检查HTTP状态
                if resp.status_code != 200:
                    error_msg = resp.json().get("base_resp", {}).get("error_msg", "未知错误")
                    raise Exception(f"API错误: {error_msg}")

                result = resp.json()
                # 兼容M2.5模型：同时获取content和reasoning_content
                api_msg = result.get("choices", [{}])[0].get("message", {})
                content = api_msg.get("content", "")
                reasoning = api_msg.get("reasoning_content", "")
                # 优先使用content，如果为空则使用reasoning_content
                combined = content if content else reasoning
                # 记录AI思考过程日志
                if reasoning:
                    self.log(f"[AI思考] {reasoning[:50]}...")

                if not combined:
                    raise Exception("API返回为空，请检查API Key是否有效")

                # 解析回复（V8.1 P0重构：严格过滤+智能提取）
                replies = self._parse_ai_replies(combined)

                replies = replies[:3]

                # 确保有3条回复
                while len(replies) < 3:
                    replies.append("(稍后重试)")

                self.log(f"生成回复: {replies}")

                self.root.after(0, self.show_replies, replies)

            except Exception as e:
                error_msg = str(e)
                self.log(f"生成失败: {error_msg}")

                # 友好错误提示
                if "API" in error_msg or "Key" in error_msg:
                    self.root.after(0, lambda: messagebox.showerror("API错误", "请检查API Key是否正确"))
                elif "timeout" in error_msg.lower():
                    self.root.after(0, lambda: messagebox.showerror("网络错误", "请求超时，请检查网络"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, lambda: self.gen_btn.config(state="normal"))
                self.root.after(0, lambda: setattr(self, 'processing', False))

        threading.Thread(target=run, daemon=True).start()

    def show_replies(self, replies):
        """显示回复选项"""
        self.reply_list.delete(0, tk.END)
        for r in replies:
            self.reply_list.insert(tk.END, r)

        # 保存当前回复选项供收藏使用
        self.current_replies = replies

        # 显示收藏按钮（如果有回复）
        if replies and len(replies) > 0:
            self.show_collect_button()
            btn.pack(side="left", padx=3)

    def show_collect_button(self):
        """显示收藏按钮"""
        # 创建收藏框架
        self.collect_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        self.collect_frame.pack(fill="x")

        tk.Label(self.collect_frame, text="💾 收藏到快捷短语:",
                font=("微软雅黑", 9), bg="white").pack(side="left")

        # 为每个回复选项创建收藏按钮
        if hasattr(self, 'current_replies'):
            for i, reply in enumerate(self.current_replies[:3]):
                # 截断过长的回复
                display_text = reply[:12] + "..." if len(reply) > 12 else reply
                btn = tk.Button(self.collect_frame, text=f"💾 {display_text}",
                              font=("微软雅黑", 8), bg="#4CAF50", fg="white",
                              relief="flat", padx=8,
                              command=lambda r=reply: self.collect_to_quick(r))
                btn.pack(side="left", padx=3)

    def collect_to_quick(self, reply):
        """收藏回复到快捷短语"""
        quick_replies = CONFIG.get("quick_replies", [])

        # 检查是否已存在
        if reply in quick_replies:
            messagebox.showinfo("提示", "这条回复已经在快捷短语中了")
            return

        # 添加到快捷短语
        quick_replies.append(reply)
        CONFIG["quick_replies"] = quick_replies
        save_config(CONFIG)

        messagebox.showinfo("收藏成功", f"已添加到快捷短语！\n\n{reply}")
        self.log(f"收藏快捷短语: {reply[:20]}")

    def copy_reply(self, event):
        """复制选中的回复"""
        selection = self.reply_list.curselection()
        if selection:
            reply = self.reply_list.get(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(reply)

            # 更新对话历史
            if self.conversation and self.conversation[-1][1] is None:
                msg, _ = self.conversation[-1]
                self.conversation[-1] = (msg, reply)
                # 显示我的回复
                self.add_message(reply, True)

            self.log(f"复制回复: {reply}")

            # 保存对话历史到文件
            self.save_conversation_history()

            # 清空输入
            self.input_txt.delete("1.0", "end")

    def save_conversation_history(self):
        """保存对话历史到文件"""
        if not self.current_friend or not self.conversation:
            return

        try:
            # 构建聊天历史文本
            history_text = ""
            for their_msg, our_reply in self.conversation:
                history_text += f"对方: {their_msg}\n"
                if our_reply:
                    history_text += f"我: {our_reply}\n"

            # 获取当前好友信息
            friend = self.friend_manager.get_friend(self.current_friend)
            if friend:
                old_history = friend.get("chat_history", "")
                # 追加新对话（保留最近5000字符）
                new_history = (old_history + "\n" + history_text)[-5000:]
                self.friend_manager.add_friend(
                    self.current_friend,
                    friend.get("relation", "朋友"),
                    new_history,
                    friend.get("profile", "")
                )
                self.log("对话历史已保存")
        except Exception as e:
            self.log(f"保存对话历史失败: {e}")

    def show_quick_buttons(self):
        """显示快捷短语按钮"""
        # 清除旧的快捷按钮
        if self.quick_buttons_frame:
            self.quick_buttons_frame.destroy()

        # 创建新的快捷按钮框架
        self.quick_buttons_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        self.quick_buttons_frame.pack(fill="x")

        quick_replies = CONFIG.get("quick_replies", [])
        if not quick_replies:
            tk.Label(self.quick_buttons_frame, text="暂无快捷短语，请在设置中添加",
                    bg="white", fg="#888").pack()
            # 2秒后自动关闭
            self.root.after(2000, lambda: self.quick_buttons_frame.destroy() if self.quick_buttons_frame else None)
            return

        tk.Label(self.quick_buttons_frame, text="⚡ 快捷回复:", font=("微软雅黑", 9),
                bg="white").pack(anchor="w")

        # 创建滚动框架
        quick_canvas = tk.Canvas(self.quick_buttons_frame, bg="white", height=60, highlightthickness=0)
        quick_canvas.pack(fill="x")

        quick_scroll = tk.Scrollbar(self.quick_buttons_frame, orient="horizontal",
                                   command=quick_canvas.xview)
        quick_scroll.pack(fill="x")
        quick_canvas.config(xscrollcommand=quick_scroll.set)

        btn_frame = tk.Frame(quick_canvas, bg="white")
        quick_canvas.create_window((0, 0), window=btn_frame, anchor="nw")

        # 添加快捷按钮
        for q in quick_replies[:10]:  # 最多显示10个
            btn = tk.Button(btn_frame, text=q[:15] + "..." if len(q) > 15 else q,
                          font=("微软雅黑", 8), bg="#FF9800", fg="white",
                          relief="flat", padx=10, pady=5,
                          command=lambda text=q: self.use_quick_reply(text))
            btn.pack(side="left", padx=3, pady=5)

        btn_frame.update_idletasks()
        quick_canvas.configure(scrollregion=quick_canvas.bbox("all"))

        # 关闭按钮
        tk.Button(self.quick_buttons_frame, text="✕ 收起", font=("微软雅黑", 8),
                 bg="#e0e0e0", relief="flat",
                 command=lambda: self.quick_buttons_frame.destroy() if self.quick_buttons_frame else None).pack(pady=3)

    def use_quick_reply(self, text):
        """使用快捷短语"""
        self.input_txt.delete("1.0", "end")
        self.input_txt.insert("1.0", text)
        self.log(f"使用快捷回复: {text[:20]}")

    def load_conversation_history(self):
        """加载历史对话"""
        if not self.current_friend:
            return

        friend = self.friend_manager.get_friend(self.current_friend)
        if not friend:
            return

        history = friend.get("chat_history", "")
        if not history:
            return

        # 解析历史对话
        lines = history.split("\n")
        temp_conv = []
        their_msg = None

        for line in lines:
            if line.startswith("对方: "):
                their_msg = line[4:]
            elif line.startswith("我: ") and their_msg:
                temp_conv.append((their_msg, line[3:]))
                their_msg = None

        # 加载最近8轮对话
        for their_msg, our_reply in temp_conv[-8:]:
            self.add_message(their_msg, False)
            if our_reply:
                self.add_message(our_reply, True)
                self.conversation.append((their_msg, our_reply))

        if temp_conv:
            self.log(f"已加载 {len(temp_conv)} 轮历史对话")

    def _parse_ai_replies(self, content):
        """
        V8.1 P0重构: 解析AI返回内容
        策略1: 处理Python列表格式
        策略2: 提取引号内句子
        策略3: 智能分割
        """
        if not content:
            return []

        import re
        replies = []

        # 严格过滤关键词
        skip_words = [
            '让我来写', '我来写', '检查一下', '字数', '这样吧', '要不', '或者',
            '不如', '例如', '比如', '假设', '如果', '可能', '应该', '大概',
            '以下', '上面', '下面', '回复', '建议', '分析', '类型', '抱歉',
            '已经', '最低', '提供', '选择', '适合', '满意', '希望', '试试',
            '给你', '这样', '这么', '多么', '怎么', '什么', '为什么',
            '是否', '能不能', '是否', 'shall', 'would', 'could', 'might',
            'here are', 'here is', 'three', '3条', '三条', '3个', '三个',
            '第一条', '第二条', '第三条', '答案', '如下', '是的', '不是',
            '当然', '确实', '其实', '自然', '简单', 'reply', 'response',
            '根据', '看来', '看起来', '总之', '总的来说', '亲爱的用户',
            '14字', '15字', '16字', '17字', '18字', '19字', '20字', '- 14字', '- 16字'
        ]

        # 前置处理：如果content看起来像Python列表，先尝试提取
        content_str = str(content).strip()
        if content_str.startswith('[') and content_str.endswith(']'):
            # 尝试从列表格式中提取内容
            try:
                # 移除外层 brackets
                inner = content_str[1:-1]
                # 分割列表元素（处理嵌套引号）
                parts = re.split(r"',\s*'", inner)
                for part in parts:
                    # 清理引号
                    part = part.strip().strip("'\"").strip()
                    if part and 6 <= len(part) <= 20:
                        if not any(sw in part for sw in skip_words):
                            replies.append(part)
            except:
                pass

        # 策略1: 提取被引号包裹的完整句子
        for quote in ['"', '"', "'", '「', '」', '『', '』']:
            pattern = f'{quote}([^{quote}]{{6,20}}){quote}'
            matches = re.findall(pattern, content_str)
            for match in matches:
                if match and not any(sw in match for sw in skip_words):
                    replies.append(match.strip())

        # 策略2: 分割线/编号分割 - 严格模式
        if len(replies) < 2:
            for line in content_str.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 严格检查：跳过任何包含中英文标点混合的复杂行
                # 如果行包含某些关键词或者格式奇怪，直接跳过
                if len(line) < 4 or len(line) > 25:
                    continue
                if any(sw in line for sw in skip_words):
                    continue
                # 跳过包含换行符编码的行
                if '\\n' in line or '\\t' in line:
                    continue
                # 跳过包含奇怪字符的行
                if line.startswith("'") or line.startswith('"') or line.startswith('-'):
                    line = re.sub(r'^[-"\']+\s*', '', line)

                # 清理编号前缀
                line = re.sub(r'^[\d一二二三四五六七八九十百千万]+[.、:：)\]】}]+\s*', '', line)
                line = re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]+\s*', '', line)
                line = re.sub(r'^[\-\*\.\·]+\s*', '', line)
                line = re.sub(r'^\*\*', '', line)
                line = re.sub(r'\*\*$', '', line)
                line = re.sub(r'\s*[-－]\s*\d+字.*$', '', line)
                line = re.sub(r'[（(]\d+字[)）]$', '', line)
                line = re.sub(r"['\"\",，、。；：]\s*$", '', line)
                line = line.strip()

                # 最终验证
                if 6 <= len(line) <= 20 and not line.isdigit() and len(line) > 2:
                    replies.append(line)

        # 策略3: 句号分割
        if len(replies) < 2:
            for part in re.split(r'[。;；]', content_str):
                part = part.strip()
                if len(part) >= 6 and len(part) <= 20:
                    if not any(sw in part for sw in skip_words) and not part.isdigit():
                        replies.append(part)

        # 去重并限制3条
        seen = set()
        unique_replies = []
        for r in replies:
            if r not in seen and 6 <= len(r) <= 20:
                seen.add(r)
                unique_replies.append(r)

        return unique_replies[:3]

if __name__ == "__main__":
    App()
