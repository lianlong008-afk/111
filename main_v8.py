# -*- coding: utf-8 -*-
"""
微信高情商回复助手 V8.2 (优化重构版)
- 本地+AI 混合引擎（无需 API 也能回复）
- 12 种意图智能识别
- 3 种回复风格（稳妥版/轻松版/升温版）
- 画像分析功能
- 对话历史自动保存
- AI 思考日志系统
- 快捷短语库
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import re
import json
import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field

# 导入优化后的回复引擎
from reply_engine_v81 import ReplyEngineV82

# ============== 常量定义 ==============
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
FRIENDS_FILE = os.path.join(os.path.dirname(__file__), 'friends.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'v6_log.txt')
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

# 关系类型配置
RELATIONS: List[Tuple[str, str, str]] = [
    ("恋人", "💕", "情侣/配偶关系"),
    ("朋友", "👯", "普通朋友关系"),
    ("同事", "💼", "工作同事关系"),
    ("客户", "🤝", "商务客户关系"),
    ("家人", "👨‍👩‍👧", "家庭成员关系"),
    ("追求者", "🌹", "追求/暗恋关系"),
    ("海王", "🌊", "暧昧/养鱼关系"),
    ("高冷", "🧊", "高冷女神/男神"),
]

# 主题配置
THEMES = {
    "dark": {
        "bg": "#1e1e1e", "fg": "#e0e0e0", "input_bg": "#2d2d2d",
        "button_bg": "#3d3d3d", "accent": "#667eea",
        "bubble_self": "#667eea", "bubble_other": "#3d3d3d",
        "text_self": "#ffffff", "text_other": "#e0e0e0",
    },
    "light": {
        "bg": "#f5f5f5", "fg": "#333333", "input_bg": "#f5f5f5",
        "button_bg": "#e0e0e0", "accent": "#667eea",
        "bubble_self": "#667eea", "bubble_other": "#ffffff",
        "text_self": "#ffffff", "text_other": "#333333",
    }
}

# 关系语气指导
TONE_GUIDES: Dict[str, str] = {
    "恋人": "甜蜜亲密，体现关心和爱意",
    "朋友": "自然轻松，幽默风趣",
    "同事": "专业礼貌，保持适当距离",
    "客户": "商务专业，稳妥可靠",
    "家人": "亲情温暖，体贴关怀",
    "追求者": "委婉得体，不伤害对方",
    "海王": "保持暧昧，欲拒还迎",
    "高冷": "简洁冷淡，爱搭不理"
}

# 风格描述
STYLE_DESCRIPTIONS: Dict[str, str] = {
    "稳妥版": "稳重得体，不过不失",
    "轻松版": "轻松俏皮",
    "升温版": "热情主动"
}


@dataclass
class AppConfig:
    """应用配置数据类"""
    api_key: str = ""
    dark_mode: bool = False
    quick_replies: List[str] = field(default_factory=list)
    reply_mode: str = "hybrid"

    @classmethod
    def load(cls) -> 'AppConfig':
        """从文件加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(
                        api_key=data.get("api_key", ""),
                        dark_mode=data.get("dark_mode", False),
                        quick_replies=data.get("quick_replies", []),
                        reply_mode=data.get("reply_mode", "hybrid")
                    )
            except (json.JSONDecodeError, IOError):
                pass
        return cls()

    def save(self) -> None:
        """保存配置到文件"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "api_key": self.api_key,
                "dark_mode": self.dark_mode,
                "quick_replies": self.quick_replies,
                "reply_mode": self.reply_mode
            }, f, ensure_ascii=False, indent=2)


@dataclass
class FriendData:
    """好友数据数据类"""
    relation: str
    chat_history: str = ""
    profile: str = ""
    update_time: str = ""


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.config = AppConfig.load()

    @property
    def api_key(self) -> str:
        return self.config.api_key

    @api_key.setter
    def api_key(self, value: str):
        self.config.api_key = value
        self.config.save()

    @property
    def dark_mode(self) -> bool:
        return self.config.dark_mode

    @dark_mode.setter
    def dark_mode(self, value: bool):
        self.config.dark_mode = value
        self.config.save()

    @property
    def quick_replies(self) -> List[str]:
        return self.config.quick_replies

    def add_quick_reply(self, reply: str) -> bool:
        """添加快捷短语"""
        if reply not in self.config.quick_replies:
            self.config.quick_replies.append(reply)
            self.config.save()
            return True
        return False

    def remove_quick_reply(self, index: int) -> bool:
        """删除快捷短语"""
        if 0 <= index < len(self.config.quick_replies):
            self.config.quick_replies.pop(index)
            self.config.save()
            return True
        return False


class FriendManager:
    """好友管理器"""

    def __init__(self):
        self.friends: Dict[str, Dict[str, str]] = self._load()

    def _load(self) -> Dict[str, Dict[str, str]]:
        """加载好友数据"""
        if os.path.exists(FRIENDS_FILE):
            try:
                with open(FRIENDS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save(self) -> None:
        """保存好友数据"""
        with open(FRIENDS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.friends, f, ensure_ascii=False, indent=2)

    def add_friend(self, name: str, relation: str,
                   chat_history: str = "", profile: str = "") -> None:
        """添加/更新好友"""
        self.friends[name] = {
            "relation": relation,
            "chat_history": chat_history,
            "profile": profile,
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._save()

    def get_friend(self, name: str) -> Optional[Dict[str, str]]:
        """获取好友信息"""
        return self.friends.get(name)

    def delete_friend(self, name: str) -> bool:
        """删除好友"""
        if name in self.friends:
            del self.friends[name]
            self._save()
            return True
        return False

    def get_all_names(self) -> List[str]:
        """获取所有好友名称"""
        return list(self.friends.keys())


class LogWindow:
    """日志窗口"""

    def __init__(self, parent: tk.Tk):
        self.window = tk.Toplevel(parent)
        self.window.title("AI 思考过程")
        self.window.geometry("600x400")
        self.window.configure(bg="#1e1e1e")
        self.window.withdraw()  # 初始隐藏

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置 UI"""
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

    def log(self, text: str, color: str = "#00ff00") -> None:
        """添加日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text.insert("end", f"[{timestamp}] {text}\n")
        self.text.see("end")
        self._save_to_file(timestamp, text)

    def _save_to_file(self, timestamp: str, text: str) -> None:
        """保存日志到文件"""
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {text}\n")
        except IOError:
            pass

    def clear(self) -> None:
        """清空日志"""
        self.text.delete("1.0", "end")


class BubbleMessage:
    """气泡消息组件"""

    def __init__(self, parent: tk.Widget, is_self: bool = False):
        self.frame = tk.Frame(parent, bg="#f0f0f0")
        self.avatar = tk.Label(self.frame, text="😀" if is_self else "👤",
                              font=("微软雅黑", 16), bg="#f0f0f0")
        self.avatar.pack(side="right" if is_self else "left", padx=5)

        self.bubble = tk.Frame(self.frame, bg="#667eea" if is_self else "#ffffff")
        self.bubble.pack(side="right" if is_self else "left", fill="x", expand=True)

        self.text = tk.Label(self.bubble, text="", font=("微软雅黑", 10),
                           bg="#667eea" if is_self else "#ffffff",
                           fg="#ffffff" if is_self else "#333333",
                           wraplength=250, justify="right" if is_self else "left",
                           padx=10, pady=8)
        self.text.pack(padx=5, pady=3)

    def set_text(self, text: str) -> None:
        """设置消息文本"""
        self.text.config(text=text)

    def pack(self, **kwargs) -> None:
        """打包布局"""
        self.frame.pack(**kwargs)


class App:
    """微信高情商回复助手主应用"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信高情商回复 V8.2")
        self.root.geometry("400x700")

        # 初始化配置和管理器
        self.config_manager = ConfigManager()
        self.friend_manager = FriendManager()
        self.reply_engine = ReplyEngineV82(
            api_key=self.config_manager.api_key,
            log_callback=self.log
        )

        # 状态变量
        self.current_friend: Optional[str] = None
        self.conversation: List[Tuple[str, Optional[str]]] = []
        self.friend_profile: str = ""
        self.processing: bool = False
        self.current_replies: List[str] = []
        self.current_style: str = "稳妥版"
        self.quick_buttons_frame: Optional[tk.Frame] = None

        # UI 组件引用
        self.log_window = LogWindow(self.root)
        self.friend_listbox: Optional[tk.Listbox] = None
        self.relation_var: Optional[tk.StringVar] = None
        self.input_txt: Optional[tk.Text] = None
        self.reply_list: Optional[tk.Listbox] = None
        self.gen_btn: Optional[tk.Button] = None
        self.messages_frame: Optional[tk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None

        # 检查 API Key
        self.root.after(500, self._check_api_key)

        self._setup_ui()
        self.root.mainloop()

    def _check_api_key(self) -> None:
        """检查 API Key"""
        if not self.config_manager.api_key:
            self.show_config()

    def log(self, text: str) -> None:
        """记录日志"""
        self.log_window.log(text)
        print(f"[LOG] {text}")

    def _setup_ui(self) -> None:
        """设置 UI"""
        # ===== 顶部标题栏 =====
        self._create_header()

        # ===== 中间主区域 =====
        self._create_main_area()

        # ===== 底部输入区域 =====
        self._create_input_area()

        # ===== 回复显示区域 =====
        self._create_reply_area()

        # 加载好友列表
        self.update_friend_list()

    def _create_header(self) -> None:
        """创建顶部标题栏"""
        header = tk.Frame(self.root, bg="#667eea", pady=12)
        header.pack(fill="x")

        # 标题
        tk.Label(header, text="💬 微信高情商回复", font=("微软雅黑", 14, "bold"),
                bg="#667eea", fg="white").pack(side="left", padx=15)

        # 按钮区
        btn_frame = tk.Frame(header, bg="#667eea")
        btn_frame.pack(side="right", padx=15)

        # 深色模式按钮
        self.dark_mode_btn = tk.Button(
            btn_frame, text="☀️" if self.config_manager.dark_mode else "🌙",
            font=("微软雅黑", 12), bg="#5568d6", fg="white", relief="flat",
            padx=10, pady=2, command=self.toggle_dark_mode
        )
        self.dark_mode_btn.pack(side="right", padx=5)

        # 设置按钮
        tk.Button(btn_frame, text="⚙️ 设置", font=("微软雅黑", 11, "bold"),
                 bg="#4CAF50", fg="white", relief="flat", padx=12, pady=2,
                 command=self.show_config).pack(side="right", padx=5)

    def _create_main_area(self) -> None:
        """创建中间主区域"""
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                   bg="#f0f0f0", sashrelief=tk.RAISED, sashwidth=4)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧好友面板
        left_frame = tk.Frame(main_paned, bg="white", width=100)
        main_paned.add(left_frame, minsize=100)

        self._create_friend_panel(left_frame)

        # 右侧对话区域
        right_frame = tk.Frame(main_paned, bg="#f0f0f0")
        main_paned.add(right_frame, minsize=250)

        self._create_chat_area(right_frame)

    def _create_friend_panel(self, parent: tk.Frame) -> None:
        """创建好友面板"""
        tk.Label(parent, text="👥 好友", font=("微软雅黑", 11, "bold"),
                bg="white", fg="#333").pack(pady=(10, 5))

        self.friend_listbox = tk.Listbox(
            parent, font=("微软雅黑", 10), bg="#f8f9fa",
            relief=tk.FLAT, borderwidth=0
        )
        self.friend_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.friend_listbox.bind('<<ListboxSelect>>', self.on_friend_selected)

        tk.Button(parent, text="➕ 添加好友", font=("微软雅黑", 9),
                 bg="#4CAF50", fg="white", relief=tk.FLAT,
                 command=self.add_friend).pack(pady=5, padx=5, fill=tk.X)

    def _create_chat_area(self, parent: tk.Frame) -> None:
        """创建聊天区域"""
        # 关系选择栏
        self._create_relation_bar(parent)

        # 对话气泡区域
        self.canvas = tk.Canvas(parent, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5)

        scrollbar = tk.Scrollbar(parent, command=self.canvas.yview)
        scrollbar.pack(fill=tk.Y)
        self.canvas.config(yscrollcommand=scrollbar.set)

        self.messages_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor=tk.NW)
        self.messages_frame.bind("<Configure>",
                                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _create_relation_bar(self, parent: tk.Frame) -> None:
        """创建关系选择栏"""
        relation_bar = tk.Frame(parent, bg="white", pady=8)
        relation_bar.pack(fill=tk.X)

        tk.Label(relation_bar, text="💝 关系:", font=("微软雅黑", 10),
                bg="white").pack(side=tk.LEFT, padx=10)

        self.relation_var = tk.StringVar()
        relation_combo = ttk.Combobox(
            relation_bar, textvariable=self.relation_var,
            values=[f"{e} {n}" for n, e, d in RELATIONS],
            font=("微软雅黑", 10), state="readonly", width=15
        )
        relation_combo.pack(side=tk.LEFT, padx=5)
        relation_combo.bind("<<ComboboxSelected>>", self.on_relation_selected)

        # 画像按钮
        tk.Button(relation_bar, text="🔍 分析画像", font=("微软雅黑", 9),
                 bg="#2196F3", fg="white", relief=tk.FLAT,
                 command=self.analyze_profile).pack(side=tk.RIGHT, padx=5)

        tk.Button(relation_bar, text="👁 查看画像", font=("微软雅黑", 9),
                 bg="#9C27B0", fg="white", relief=tk.FLAT,
                 command=self.show_friend_profile).pack(side=tk.RIGHT, padx=5)

    def _create_input_area(self) -> None:
        """创建输入区域"""
        input_area = tk.Frame(self.root, bg="white", padx=10, pady=10)
        input_area.pack(fill=tk.X, side=tk.BOTTOM)

        # 输入框
        self.input_txt = tk.Text(input_area, height=3, font=("微软雅黑", 11),
                                bg="#f5f5f5", relief=tk.FLAT, padx=10, pady=8)
        self.input_txt.pack(fill=tk.X, pady=(0, 8))

        # 操作按钮行
        btn_row = tk.Frame(input_area, bg="white")
        btn_row.pack(fill=tk.X)

        # 工具按钮
        tools = [
            ("📋 粘贴", self.paste),
            ("📷 截图", self.screenshot_ocr),
            ("📁 导入", self.import_chat),
            ("⚡ 快捷", self.show_quick_buttons),
        ]
        for text, cmd in tools:
            tk.Button(btn_row, text=text, font=("微软雅黑", 9),
                    bg="#e0e0e0", relief=tk.FLAT, command=cmd).pack(side=tk.LEFT, padx=3)

        # 生成按钮
        self.gen_btn = tk.Button(btn_row, text="🚀 生成回复",
                                font=("微软雅黑", 10, "bold"), bg="#667eea", fg="white",
                                relief=tk.FLAT, padx=20, pady=5, command=self.generate)
        self.gen_btn.pack(side=tk.RIGHT, padx=3)

    def _create_reply_area(self) -> None:
        """创建回复显示区域"""
        reply_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        reply_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(reply_frame, text="👇 点击选择回复:", font=("微软雅黑", 9, "bold"),
                bg="white").pack(anchor="w")

        self.reply_list = tk.Listbox(reply_frame, font=("微软雅黑", 10),
                                    height=3, bg="#f8f9fa", relief=tk.FLAT)
        self.reply_list.pack(fill=tk.X, pady=3)
        self.reply_list.bind("<ButtonRelease-1>", self.copy_reply)

    # ==================== 好友管理 ====================

    def update_friend_list(self) -> None:
        """更新好友列表"""
        if not self.friend_listbox:
            return

        self.friend_listbox.delete(0, tk.END)

        for name in self.friend_manager.get_all_names():
            friend = self.friend_manager.get_friend(name)
            rel = friend.get("relation", "") if friend else ""
            rel_emoji = next((e for n, e, d in RELATIONS if n == rel), "")
            self.friend_listbox.insert(tk.END, f"{rel_emoji} {name}")

        # 选择第一个好友
        if self.friend_listbox.size() > 0:
            self.root.after(200, self._select_first_friend)

    def _select_first_friend(self) -> None:
        """选择第一个好友"""
        if self.friend_listbox and self.friend_listbox.size() > 0:
            self.on_friend_selected(None)

    def on_friend_selected(self, event: Optional[tk.Event]) -> None:
        """选择好友"""
        if not self.friend_listbox:
            return

        selection = self.friend_listbox.curselection()
        if not selection:
            return

        display_text = self.friend_listbox.get(selection[0])
        name = display_text.split(" ", 1)[-1] if " " in display_text else display_text

        friend = self.friend_manager.get_friend(name)
        if friend:
            self.current_friend = name
            self.friend_profile = friend.get("profile", "")

            # 设置关系
            rel = friend.get("relation", "")
            for n, e, d in RELATIONS:
                if n == rel:
                    self.relation_var.set(f"{e} {n}")
                    break

            self.log(f"切换到好友：{name}")

            # 清空对话
            self._clear_messages()
            self.conversation = []
            self.load_conversation_history()

    def _clear_messages(self) -> None:
        """清空消息显示"""
        if self.messages_frame:
            for widget in self.messages_frame.winfo_children():
                widget.destroy()

    def on_relation_selected(self, event: tk.Event) -> None:
        """选择关系类型"""
        if self.current_friend:
            rel_text = self.relation_var.get()
            rel_name = rel_text.split()[1] if len(rel_text.split()) > 1 else ""
            self.friend_manager.add_friend(self.current_friend, rel_name)
            self.log(f"更新关系类型：{rel_name}")

    def add_friend(self) -> None:
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

        def confirm() -> None:
            name = name_entry.get().strip()
            rel = rel_var.get()
            if name:
                self.friend_manager.add_friend(name, rel)
                self.update_friend_list()
                dialog.destroy()
                self.log(f"添加好友：{name}")

        tk.Button(dialog, text="确定", bg="#4CAF50", fg="white",
                 command=confirm).pack(pady=10)

    # ==================== 消息显示 ====================

    def add_message(self, text: str, is_self: bool = False) -> None:
        """添加消息气泡"""
        if not self.messages_frame:
            return

        bubble = BubbleMessage(self.messages_frame, is_self)
        bubble.set_text(text)
        bubble.pack(fill="x", pady=3)
        self.root.update()
        if self.canvas:
            self.canvas.yview_moveto(1.0)

    # ==================== 生成回复 ====================

    def generate(self) -> None:
        """生成回复"""
        if self.processing or not self.input_txt:
            return

        msg = self.input_txt.get("1.0", "end").strip()
        if not msg:
            messagebox.showwarning("提示", "请输入对方的消息")
            return

        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择或添加好友")
            return

        # 添加对方消息
        self.add_message(msg, False)
        self.conversation.append((msg, None))

        self.processing = True
        if self.gen_btn:
            self.gen_btn.config(state="disabled")
        self.log(f"对方：{msg[:30]}...")

        threading.Thread(target=self._generate_reply, args=(msg,), daemon=True).start()

    def _generate_reply(self, message: str) -> None:
        """生成回复（后台线程）"""
        try:
            if not self.config_manager.api_key:
                self.root.after(0, lambda: messagebox.showwarning("警告", "请先配置 API Key"))
                return

            rel_text = self.relation_var.get() or "朋友"
            rel_name = rel_text.split()[1] if len(rel_text.split()) > 1 else "朋友"
            style = self.current_style

            # 构建上下文
            context_parts = [
                f"【我和 TA 的关系】{rel_name}",
            ]

            if self.friend_profile:
                context_parts.append(f"【TA 的性格画像】{self.friend_profile[:200]}")

            if self.conversation:
                history_lines = ["【最近聊天记录】"]
                for their, ours in self.conversation[-5:]:
                    history_lines.append(f"TA 说：{their}")
                    if ours:
                        history_lines.append(f"我说：{ours}")
                context_parts.append("\n".join(history_lines))

            context_parts.extend([
                f"【TA 刚发来】{message}",
                f"【我的角色】{rel_name}，风格{STYLE_DESCRIPTIONS.get(style, '稳重得体')}"
            ])

            user_prompt = "\n\n".join(context_parts) + "\n\n输出 3 条回复，每行一条："

            self.log(f"AI 思考中... (关系:{rel_name})")

            # 调用 AI 生成
            replies, info = self.reply_engine.generate(
                message=message,
                relation=rel_name,
                style=style,
                mode=self.config_manager.config.reply_mode
            )

            # 确保有 3 条回复
            while len(replies) < 3:
                replies.append("(稍后重试)")

            self.log(f"生成回复：{replies}")
            self.root.after(0, lambda: self.show_replies(replies))

        except Exception as e:
            error_msg = str(e)
            self.log(f"生成失败：{error_msg}")
            self._show_error(error_msg)
        finally:
            self.root.after(0, lambda: self._reset_generate_state())

    def _reset_generate_state(self) -> None:
        """重置生成状态"""
        self.processing = False
        if self.gen_btn:
            self.gen_btn.config(state="normal")

    def _show_error(self, error_msg: str) -> None:
        """显示错误"""
        if "API" in error_msg or "Key" in error_msg:
            self.root.after(0, lambda: messagebox.showerror("API 错误", "请检查 API Key 是否正确"))
        elif "timeout" in error_msg.lower():
            self.root.after(0, lambda: messagebox.showerror("网络错误", "请求超时，请检查网络"))
        else:
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))

    def show_replies(self, replies: List[str]) -> None:
        """显示回复选项"""
        if not self.reply_list:
            return

        self.reply_list.delete(0, tk.END)
        for r in replies:
            self.reply_list.insert(tk.END, r)

        self.current_replies = replies
        self.show_collect_button()

    def show_collect_button(self) -> None:
        """显示收藏按钮"""
        # 清除旧的收藏框架
        if hasattr(self, 'collect_frame') and self.collect_frame:
            self.collect_frame.destroy()

        self.collect_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        self.collect_frame.pack(fill="x")

        tk.Label(self.collect_frame, text="💾 收藏到快捷短语:",
                font=("微软雅黑", 9), bg="white").pack(side="left")

        for reply in self.current_replies[:3]:
            display_text = reply[:12] + "..." if len(reply) > 12 else reply
            btn = tk.Button(self.collect_frame, text=f"💾 {display_text}",
                          font=("微软雅黑", 8), bg="#4CAF50", fg="white",
                          relief="flat", padx=8,
                          command=lambda r=reply: self.collect_to_quick(r))
            btn.pack(side="left", padx=3)

    def collect_to_quick(self, reply: str) -> None:
        """收藏回复到快捷短语"""
        if self.config_manager.add_quick_reply(reply):
            messagebox.showinfo("收藏成功", f"已添加到快捷短语！\n\n{reply}")
            self.log(f"收藏快捷短语：{reply[:20]}")
        else:
            messagebox.showinfo("提示", "这条回复已经在快捷短语中了")

    def copy_reply(self, event: tk.Event) -> None:
        """复制选中的回复"""
        if not self.reply_list:
            return

        selection = self.reply_list.curselection()
        if selection:
            reply = self.reply_list.get(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(reply)

            # 更新对话历史
            if self.conversation and self.conversation[-1][1] is None:
                msg, _ = self.conversation[-1]
                self.conversation[-1] = (msg, reply)
                self.add_message(reply, True)

            self.log(f"复制回复：{reply}")
            self.save_conversation_history()

            if self.input_txt:
                self.input_txt.delete("1.0", "end")

    # ==================== 历史记录 ====================

    def save_conversation_history(self) -> None:
        """保存对话历史"""
        if not self.current_friend or not self.conversation:
            return

        try:
            history_text = ""
            for their_msg, our_reply in self.conversation:
                history_text += f"对方：{their_msg}\n"
                if our_reply:
                    history_text += f"我：{our_reply}\n"

            friend = self.friend_manager.get_friend(self.current_friend)
            if friend:
                old_history = friend.get("chat_history", "")
                new_history = (old_history + "\n" + history_text)[-5000:]
                self.friend_manager.add_friend(
                    self.current_friend,
                    friend.get("relation", "朋友"),
                    new_history,
                    friend.get("profile", "")
                )
                self.log("对话历史已保存")
        except Exception as e:
            self.log(f"保存对话历史失败：{e}")

    def load_conversation_history(self) -> None:
        """加载历史对话"""
        if not self.current_friend:
            return

        friend = self.friend_manager.get_friend(self.current_friend)
        if not friend:
            return

        history = friend.get("chat_history", "")
        if not history:
            return

        lines = history.split("\n")
        temp_conv: List[Tuple[str, str]] = []
        their_msg: Optional[str] = None

        for line in lines:
            if line.startswith("对方："):
                their_msg = line[4:]
            elif line.startswith("我：") and their_msg:
                temp_conv.append((their_msg, line[3:]))
                their_msg = None

        # 加载最近 8 轮对话
        for their_msg, our_reply in temp_conv[-8:]:
            self.add_message(their_msg, False)
            if our_reply:
                self.add_message(our_reply, True)
                self.conversation.append((their_msg, our_reply))

        if temp_conv:
            self.log(f"已加载 {len(temp_conv)} 轮历史对话")

    # ==================== 快捷短语 ====================

    def show_quick_buttons(self) -> None:
        """显示快捷短语按钮"""
        if self.quick_buttons_frame:
            self.quick_buttons_frame.destroy()

        self.quick_buttons_frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        self.quick_buttons_frame.pack(fill="x")

        quick_replies = self.config_manager.quick_replies
        if not quick_replies:
            tk.Label(self.quick_buttons_frame, text="暂无快捷短语，请在设置中添加",
                    bg="white", fg="#888").pack()
            self.root.after(2000, lambda: self.quick_buttons_frame.destroy() if self.quick_buttons_frame else None)
            return

        tk.Label(self.quick_buttons_frame, text="⚡ 快捷回复:", font=("微软雅黑", 9),
                bg="white").pack(anchor="w")

        # 滚动框架
        quick_canvas = tk.Canvas(self.quick_buttons_frame, bg="white", height=60, highlightthickness=0)
        quick_canvas.pack(fill="x")

        quick_scroll = tk.Scrollbar(self.quick_buttons_frame, orient="horizontal",
                                   command=quick_canvas.xview)
        quick_scroll.pack(fill="x")
        quick_canvas.config(xscrollcommand=quick_scroll.set)

        btn_frame = tk.Frame(quick_canvas, bg="white")
        quick_canvas.create_window((0, 0), window=btn_frame, anchor="nw")

        for q in quick_replies[:10]:
            btn = tk.Button(btn_frame, text=q[:15] + "..." if len(q) > 15 else q,
                          font=("微软雅黑", 8), bg="#FF9800", fg="white",
                          relief="flat", padx=10, pady=5,
                          command=lambda text=q: self.use_quick_reply(text))
            btn.pack(side="left", padx=3, pady=5)

        btn_frame.update_idletasks()
        quick_canvas.configure(scrollregion=quick_canvas.bbox("all"))

        tk.Button(self.quick_buttons_frame, text="✕ 收起", font=("微软雅黑", 8),
                 bg="#e0e0e0", relief="flat",
                 command=lambda: self.quick_buttons_frame.destroy() if self.quick_buttons_frame else None).pack(pady=3)

    def use_quick_reply(self, text: str) -> None:
        """使用快捷短语"""
        if self.input_txt:
            self.input_txt.delete("1.0", "end")
            self.input_txt.insert("1.0", text)
        self.log(f"使用快捷回复：{text[:20]}")

    # ==================== 工具功能 ====================

    def paste(self) -> None:
        """粘贴"""
        try:
            text = self.root.clipboard_get()
            if self.input_txt:
                self.input_txt.delete("1.0", "end")
                self.input_txt.insert("1.0", text)
        except tk.TclError:
            pass

    def screenshot_ocr(self) -> None:
        """截图 OCR"""
        def do_ocr() -> None:
            try:
                from PIL import ImageGrab
                import requests

                self.log("开始 OCR...")

                img = ImageGrab.grabclipboard()
                if not img or not isinstance(img, Image.Image):
                    self.root.after(0, lambda: messagebox.showwarning(
                        "失败", "请先截图！\n\n步骤：\n1. 按 Win+Shift+S 截图\n2. 再点此按钮"))
                    return

                temp_path = os.path.join(os.path.dirname(__file__), 'temp_ocr.png')
                img.save(temp_path)
                self.log("图片已保存，调用在线 OCR...")

                try:
                    with open(temp_path, 'rb') as f:
                        files = {'file': f}
                        data = {'language': 'chs', 'isOverlayRequired': 'false'}
                        resp = requests.post('https://api.ocr.space/parse/image',
                                           files=files, data=data, timeout=60)

                    result_json = resp.json()
                    self.log(f"API 返回：{str(result_json)[:100]}")

                    if result_json.get('ParsedResults'):
                        text = result_json['ParsedResults'][0]['ParsedText'].strip()
                        self.log(f"识别结果：{text[:50] if text else '空'}")

                        if text:
                            self.root.after(0, lambda: self._fill_ocr_result(text))
                        else:
                            self.root.after(0, lambda: messagebox.showwarning("OCR", "未识别到文字"))
                    else:
                        error_msg = result_json.get('ErrorMessage', '未知错误')
                        self.log(f"OCR 失败：{error_msg}")
                        self.root.after(0, lambda: messagebox.showwarning("OCR 失败", error_msg))

                except Exception as api_err:
                    self.log(f"在线 OCR 异常：{str(api_err)[:50]}")
                    self.root.after(0, lambda: messagebox.showwarning("OCR 失败", f"网络错误：{api_err}"))

                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            except Exception as e:
                self.log(f"OCR 错误：{str(e)[:80]}")
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))

        threading.Thread(target=do_ocr, daemon=True).start()

    def _fill_ocr_result(self, text: str) -> None:
        """填充 OCR 结果"""
        if self.input_txt:
            self.input_txt.delete("1.0", "end")
            self.input_txt.insert("1.0", text)
        self._copy_to_clipboard(text)
        self.log(f"OCR 成功：{text[:30]}...")

    def _copy_to_clipboard(self, text: str) -> None:
        """复制到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("✅ 完成", "文字已复制到剪贴板，可直接粘贴")
        except Exception as e:
            self.log(f"剪贴板失败：{e}")

    def import_chat(self) -> str:
        """导入聊天记录"""
        file_path = filedialog.askopenfilename(title="选择聊天记录",
                                             filetypes=[("文本", "*.txt"), ("所有", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                friend_name = self._parse_friend_name(content, file_path)

                if friend_name and not self.friend_manager.get_friend(friend_name):
                    self.friend_manager.add_friend(friend_name, "朋友", "", "")
                    self.update_friend_list()
                    self.log(f"自动创建好友：{friend_name}")

                if friend_name and not self.current_friend:
                    self._select_friend_by_name(friend_name)

                self.add_message(f"📁 已导入 [{friend_name}] 的聊天记录 ({len(content)}字符)", False)
                self.log(f"导入聊天记录：{len(content)}字符，好友：{friend_name}")
                return content[:3000]
            except Exception as e:
                self.log(f"导入失败：{e}")
        return ""

    def _parse_friend_name(self, content: str, file_path: str) -> str:
        """解析好友名称"""
        lines = content.split('\n')
        if lines:
            first_line = lines[0].strip()
            match = re.match(r'^([^\-]+)-[a-zA-Z0-9_]+$', first_line)
            if match:
                return match.group(1).strip()
            if first_line and len(first_line) <= 20 and not re.match(r'\d+[/年]', first_line):
                if not any(kw in first_line for kw in ['对方', '我:', '20']):
                    return first_line

        filename = os.path.basename(file_path)
        name = os.path.splitext(filename)[0]
        name = re.sub(r'^(聊天记录 | 微信|wechat)_?', '', name)
        return name.strip() if name else "新好友"

    def _select_friend_by_name(self, name: str) -> None:
        """根据名称选择好友"""
        for i in range(self.friend_listbox.size()):
            if name in self.friend_listbox.get(i):
                self.friend_listbox.selection_clear(0, tk.END)
                self.friend_listbox.selection_set(i)
                self.on_friend_selected(None)
                return

    # ==================== 画像分析 ====================

    def analyze_profile(self) -> None:
        """分析好友画像"""
        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择或添加好友")
            return

        if not self.config_manager.api_key:
            messagebox.showwarning("提示", "请先配置 API Key")
            return

        self.log("开始分析好友画像...")
        if self.gen_btn:
            self.gen_btn.config(state="disabled")

        threading.Thread(target=self._analyze_profile, daemon=True).start()

    def _analyze_profile(self) -> None:
        """分析好友画像（后台线程）"""
        try:
            import requests

            chat_content = self.import_chat()
            if not chat_content:
                chat_content = "无聊天记录，请根据好友昵称和关系类型分析"

            prompt = self._build_profile_prompt(chat_content)

            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.config_manager.api_key}"}
            data = {
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }

            resp = requests.post(url, headers=headers, json=data, timeout=30)

            if resp.status_code != 200:
                raise Exception(f"API 错误：{resp.status_code}")

            result = resp.json()
            api_msg = result.get("choices", [{}])[0].get("message", {})
            profile = api_msg.get("content", "") or api_msg.get("reasoning_content", "")

            if not profile:
                raise Exception("API 返回为空")

            self.log(f"画像生成成功：{profile[:50]}...")

            # 保存画像
            self._save_profile(profile, chat_content)

            self.root.after(0, lambda: messagebox.showinfo("完成", f"画像分析完成\n\n{profile[:300]}"))

        except Exception as e:
            error_msg = str(e)
            self.log(f"分析失败：{error_msg}")
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            self.root.after(0, lambda: self.gen_btn.config(state="normal") if self.gen_btn else None)

    def _build_profile_prompt(self, chat_content: str) -> str:
        """构建画像分析提示词"""
        return f"""【角色】你是用户的老朋友，正在帮用户分析一个朋友/恋人的性格。

【任务】根据聊天记录，用轻松、口语化的方式描述这个人的性格特点。

【输出内容】
- 聊天风格（话多/话少/打字快慢/爱发表情包吗）
- 性格印象（暖男/高冷/幽默/慢性子/急性子）
- 相处感受（让人舒服/需要哄/有点粘人/很独立）
- 一个有趣的小细节（从聊天中发现的独特习惯）

【要求】
- 80-120 字，像朋友间八卦聊天一样自然
- 用"他"或"她"而不是"该用户"
- 语气温暖有爱，像在说一个真实的人
- 不要 JSON，不要列表格式，用一段话自然描述

【聊天记录摘要】
{chat_content[:800] if chat_content else '暂无详细聊天记录，仅根据昵称和关系分析'}

请开始分析："""

    def _save_profile(self, profile: str, chat_content: str) -> None:
        """保存画像"""
        rel_text = self.relation_var.get() or ""
        rel_name = next((n for n, e, d in RELATIONS if n in rel_text or e in rel_text), "朋友")

        current_friend_data = self.friend_manager.get_friend(self.current_friend)
        existing_history = current_friend_data.get("chat_history", "") if current_friend_data else ""

        merged_history = existing_history
        if chat_content and chat_content != "无聊天记录，请根据好友昵称和关系类型分析":
            merged_history = (existing_history + "\n" + chat_content)[-5000:] if existing_history else chat_content

        self.friend_manager.add_friend(
            self.current_friend,
            rel_name,
            merged_history,
            profile
        )
        self.friend_profile = profile

        saved = self.friend_manager.get_friend(self.current_friend)
        if saved and saved.get("profile"):
            self.log("画像已保存到好友数据")
        else:
            self.log("警告：画像保存验证失败")

    def show_friend_profile(self) -> None:
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

        dialog = tk.Toplevel(self.root)
        dialog.title(f"👤 {self.current_friend} 的画像")
        dialog.geometry("400x300")
        dialog.configure(bg="white")

        tk.Label(dialog, text=f"【{self.current_friend}】的画像",
                font=("微软雅黑", 12, "bold"), bg="white", fg="#667eea").pack(pady=10)

        text_widget = tk.Text(dialog, font=("微软雅黑", 10), bg="#f8f9fa",
                            relief=tk.FLAT, padx=15, pady=15, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        text_widget.insert("1.0", profile)
        text_widget.config(state="disabled")

        tk.Button(dialog, text="关闭", bg="#e0e0e0", command=dialog.destroy).pack(pady=10)

    # ==================== 设置和统计 ====================

    def toggle_dark_mode(self) -> None:
        """切换深色模式"""
        self.config_manager.dark_mode = not self.config_manager.dark_mode
        self.dark_mode_btn.config(text="☀️" if self.config_manager.dark_mode else "🌙")
        messagebox.showinfo("提示", "深色模式将在重启后生效" if not self.config_manager.dark_mode else "深色模式已开启")

    def show_stats(self) -> None:
        """显示统计面板"""
        self.log("打开统计面板...")
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 使用统计")
        dialog.geometry("350x200")
        dialog.configure(bg="white")

        tk.Label(dialog, text="📊 我的使用统计", font=("微软雅黑", 14, "bold"),
                bg="white", fg="#667eea").pack(pady=15)

        stats_frame = tk.Frame(dialog, bg="white")
        stats_frame.pack(pady=10)

        friend_count = len(self.friend_manager.friends)
        tk.Label(stats_frame, text="👥 好友数量", font=("微软雅黑", 10),
                bg="white", fg="#888").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        tk.Label(stats_frame, text=str(friend_count), font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2196F3").grid(row=0, column=1, padx=20, pady=10, sticky="e")

        quick_count = len(self.config_manager.quick_replies)
        tk.Label(stats_frame, text="⚡ 快捷短语", font=("微软雅黑", 10),
                bg="white", fg="#888").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        tk.Label(stats_frame, text=str(quick_count), font=("微软雅黑", 16, "bold"),
                bg="white", fg="#9C27B0").grid(row=1, column=1, padx=20, pady=10, sticky="e")

        tk.Button(dialog, text="关闭", bg="#e0e0e0", command=dialog.destroy).pack(pady=15)

    def show_config(self) -> None:
        """显示设置窗口"""
        self.log("打开设置窗口...")
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ 设置")
        dialog.geometry("450x450")
        dialog.configure(bg="white")

        # 功能按钮
        func_btn_frame = tk.Frame(dialog, bg="#667eea", pady=10)
        func_btn_frame.pack(fill="x")

        btn_style = {"font": ("微软雅黑", 11, "bold"), "bg": "#4CAF50", "fg": "white",
                    "relief": "flat", "padx": 15, "pady": 8}

        tk.Button(func_btn_frame, text="📊 统计", command=self.show_stats,
                 **btn_style).pack(side="left", padx=10, expand=True, fill="x")

        tk.Button(func_btn_frame, text="📋 日志", command=lambda: self.log_window.window.deiconify(),
                 **btn_style).pack(side="left", padx=10, expand=True, fill="x")

        # API Key 配置
        tk.Label(dialog, text="🔑 API Key", font=("微软雅黑", 11, "bold"),
                bg="white").pack(anchor="w", padx=20, pady=(15, 5))

        api_entry = tk.Entry(dialog, font=("Consolas", 10), show="*")
        api_entry.pack(fill="x", padx=20, pady=5)
        if self.config_manager.api_key:
            api_entry.insert(0, self.config_manager.api_key)

        tk.Label(dialog, text="* 请输入 MiniMax API Key",
                font=("微软雅黑", 8), bg="white", fg="#888").pack(anchor="w", padx=20)

        def save_api() -> None:
            new_key = api_entry.get().strip()
            if new_key:
                self.config_manager.api_key = new_key
                self.reply_engine.api_key = new_key
                messagebox.showinfo("完成", "API Key 已保存！")
            else:
                messagebox.showwarning("警告", "请输入 API Key")

        tk.Button(dialog, text="💾 保存 API Key", bg="#667eea", fg="white",
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

        for q in self.config_manager.quick_replies:
            self.quick_list.insert(tk.END, q)

        quick_btn_frame = tk.Frame(dialog, bg="white")
        quick_btn_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(quick_btn_frame, text="+", bg="#4CAF50", fg="white",
                 command=lambda: self.add_quick_reply(dialog, self.quick_list)).pack(side="left", padx=2)
        tk.Button(quick_btn_frame, text="-", bg="#f44336", fg="white",
                 command=lambda: self.del_quick_reply(self.quick_list)).pack(side="left", padx=2)

    def add_quick_reply(self, dialog: tk.Toplevel, listbox: tk.Listbox) -> None:
        """添加快捷短语"""
        dialog2 = tk.Toplevel(dialog)
        dialog2.title("添加快捷短语")
        dialog2.geometry("300x100")

        tk.Label(dialog2, text="输入快捷短语:").pack(pady=5)
        entry = tk.Entry(dialog2, font=("微软雅黑", 10))
        entry.pack(pady=5)

        def confirm() -> None:
            text = entry.get().strip()
            if text:
                listbox.insert(tk.END, text)
                self.config_manager.add_quick_reply(text)
                dialog2.destroy()

        tk.Button(dialog2, text="确定", command=confirm).pack(pady=5)

    def del_quick_reply(self, listbox: tk.Listbox) -> None:
        """删除快捷短语"""
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])
            self.config_manager.remove_quick_reply(selection[0])


# ==================== 程序入口 ====================

if __name__ == "__main__":
    print("微信高情商回复助手 V8.2 (优化重构版)")
    tesseract_installed = any(os.path.exists(p) for p in TESSERACT_PATHS)
    print(f"Tesseract: {'已安装' if tesseract_installed else '未安装'}")
    print("-" * 40)
    App()
