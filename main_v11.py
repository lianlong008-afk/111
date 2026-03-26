# -*- coding: utf-8 -*-
"""
微信高情商回复助手 V11.0 (大模型专用版)
- 严格控制的 System Prompt
- Few-Shot 示例引导
- 回复解析器过滤
- 输出验证 + 兜底机制
- 7 轮连续对话不混乱
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import json
from typing import Optional, Dict, List

# 导入 V11 大模型引擎
from reply_engine_v11 import generate_reply as ai_generate_reply

# ============== 配置 ==============
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
FRIENDS_FILE = os.path.join(os.path.dirname(__file__), 'friends.json')

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


def load_config() -> dict:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": "", "dark_mode": False}


def save_config(config: dict) -> None:
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# 加载配置
CONFIG = load_config()
API_KEY = CONFIG.get("api_key", "")


class FriendManager:
    """好友管理器"""
    
    def __init__(self):
        self.friends = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(FRIENDS_FILE):
            try:
                with open(FRIENDS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save(self) -> None:
        with open(FRIENDS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.friends, f, ensure_ascii=False, indent=2)
    
    def add_friend(self, name: str, relation: str) -> None:
        self.friends[name] = {"relation": relation, "history": ""}
        self.save()
    
    def get_friend(self, name: str) -> Optional[dict]:
        return self.friends.get(name)
    
    def update_history(self, name: str, history: str) -> None:
        if name in self.friends:
            self.friends[name]["history"] = history[-5000:]  # 保留最近 5000 字
            self.save()


class App:
    """微信高情商回复助手 V11.0"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信高情商回复 V11.0")
        self.root.geometry("450x750")
        
        self.friend_manager = FriendManager()
        self.current_friend: Optional[str] = None
        self.conversation_history: str = ""
        self.processing: bool = False
        
        # UI 组件
        self.api_key_var = tk.StringVar(value=API_KEY)
        self.relation_var = tk.StringVar()
        self.style_var = tk.StringVar(value="升温版")
        
        self._setup_ui()
        
        # 检查 API Key
        if not API_KEY:
            self.root.after(500, self.show_config)
        
        self.root.mainloop()
    
    def _setup_ui(self) -> None:
        """设置 UI"""
        # 顶部标题栏
        self._create_header()
        
        # 好友选择区
        self._create_friend_panel()
        
        # 关系和风格选择
        self._create_option_panel()
        
        # 对话显示区
        self._create_chat_display()
        
        # 输入区
        self._create_input_area()
        
        # 回复显示区
        self._create_reply_area()
    
    def _create_header(self) -> None:
        """创建顶部"""
        header = tk.Frame(self.root, bg="#667eea", pady=12)
        header.pack(fill="x")
        
        tk.Label(header, text="💬 微信高情商回复 V11", font=("微软雅黑", 14, "bold"),
                bg="#667eea", fg="white").pack(side="left", padx=15)
        
        tk.Button(header, text="⚙️ 设置", font=("微软雅黑", 10),
                 bg="#4CAF50", fg="white", relief="flat", padx=10,
                 command=self.show_config).pack(side="right", padx=10)
    
    def _create_friend_panel(self) -> None:
        """创建好友面板"""
        frame = tk.Frame(self.root, bg="white", pady=5)
        frame.pack(fill="x")
        
        tk.Label(frame, text="👥 好友:", font=("微软雅黑", 10),
                bg="white").pack(side="left", padx=10)
        
        self.friend_combo = ttk.Combobox(frame, font=("微软雅黑", 10), width=15)
        self.friend_combo.pack(side="left", padx=5)
        self.friend_combo.bind("<<ComboboxSelected>>", self.on_friend_selected)
        
        tk.Button(frame, text="➕ 添加", font=("微软雅黑", 9),
                 bg="#4CAF50", fg="white", relief="flat", padx=8,
                 command=self.add_friend).pack(side="left", padx=5)
        
        self._update_friend_list()
    
    def _create_option_panel(self) -> None:
        """创建选项面板"""
        frame = tk.Frame(self.root, bg="#f5f5f5", pady=8)
        frame.pack(fill="x")
        
        # 关系选择
        tk.Label(frame, text="💝 关系:", font=("微软雅黑", 10),
                bg="#f5f5f5").pack(side="left", padx=10)
        
        self.relation_combo = ttk.Combobox(frame, textvariable=self.relation_var,
                                          values=[n for n, e, d in RELATIONS],
                                          font=("微软雅黑", 10), width=8, state="readonly")
        self.relation_combo.pack(side="left", padx=5)
        self.relation_combo.set("恋人")
        
        # 风格选择
        tk.Label(frame, text="🎨 风格:", font=("微软雅黑", 10),
                bg="#f5f5f5").pack(side="left", padx=10)
        
        self.style_combo = ttk.Combobox(frame, textvariable=self.style_var,
                                       values=["稳妥版", "轻松版", "升温版"],
                                       font=("微软雅黑", 10), width=6, state="readonly")
        self.style_combo.pack(side="left", padx=5)
    
    def _create_chat_display(self) -> None:
        """创建对话显示区"""
        frame = tk.Frame(self.root, bg="white", padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        
        self.chat_text = tk.Text(frame, font=("微软雅黑", 11), bg="#f9f9f9",
                                relief="flat", wrap="word", padx=10, pady=8)
        self.chat_text.pack(fill="both", expand=True)
    
    def _create_input_area(self) -> None:
        """创建输入区"""
        frame = tk.Frame(self.root, bg="white", padx=10, pady=10)
        frame.pack(fill="x")
        
        self.input_text = tk.Text(frame, font=("微软雅黑", 11), height=3,
                                 relief="flat", bg="#f5f5f5", padx=10, pady=8)
        self.input_text.pack(fill="x")
        
        # 按钮
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        tk.Button(btn_frame, text="📋 粘贴", font=("微软雅黑", 9),
                 bg="#e0e0e0", relief="flat", padx=15,
                 command=self.paste).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="🚀 生成回复", font=("微软雅黑", 10, "bold"),
                 bg="#667eea", fg="white", relief="flat", padx=20, pady=5,
                 command=self.generate).pack(side="right")
    
    def _create_reply_area(self) -> None:
        """创建回复显示区"""
        frame = tk.Frame(self.root, bg="white", padx=10, pady=5)
        frame.pack(fill="x")
        
        tk.Label(frame, text="👇 点击复制回复:", font=("微软雅黑", 9, "bold"),
                bg="white").pack(anchor="w")
        
        self.reply_list = tk.Listbox(frame, font=("微软雅黑", 10), height=3,
                                    bg="#f8f9fa", relief="flat")
        self.reply_list.pack(fill="x", pady=3)
        self.reply_list.bind("<ButtonRelease-1>", self.copy_reply)
    
    def _update_friend_list(self) -> None:
        """更新好友列表"""
        friends = list(self.friend_manager.friends.keys())
        self.friend_combo["values"] = friends
        if friends:
            self.friend_combo.set(friends[0])
            self.on_friend_selected(None)
    
    def on_friend_selected(self, event) -> None:
        """选择好友"""
        name = self.friend_combo.get()
        if not name:
            return
        
        self.current_friend = name
        friend = self.friend_manager.get_friend(name)
        
        if friend:
            self.relation_var.set(friend.get("relation", "恋人"))
            self.conversation_history = friend.get("history", "")
        
        # 显示历史对话
        self.chat_text.delete("1.0", "end")
        if self.conversation_history:
            self.chat_text.insert("1.0", self.conversation_history)
    
    def add_friend(self) -> None:
        """添加好友"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加好友")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="好友昵称:", font=("微软雅黑", 10)).pack(pady=5)
        name_entry = tk.Entry(dialog, font=("微软雅黑", 10))
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="关系类型:", font=("微软雅黑", 10)).pack(pady=5)
        rel_combo = ttk.Combobox(dialog, values=[n for n, e, d in RELATIONS],
                                font=("微软雅黑", 10), state="readonly")
        rel_combo.pack(pady=5)
        rel_combo.set("恋人")
        
        def confirm():
            name = name_entry.get().strip()
            rel = rel_combo.get()
            if name:
                self.friend_manager.add_friend(name, rel)
                self._update_friend_list()
                self.friend_combo.set(name)
                self.on_friend_selected(None)
                dialog.destroy()
        
        tk.Button(dialog, text="确定", bg="#4CAF50", fg="white",
                 command=confirm).pack(pady=10)
    
    def paste(self) -> None:
        """粘贴"""
        try:
            text = self.root.clipboard_get()
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", text)
        except:
            pass
    
    def generate(self) -> None:
        """生成回复"""
        if self.processing:
            return
        
        message = self.input_text.get("1.0", "end").strip()
        if not message:
            messagebox.showwarning("提示", "请输入对方的消息")
            return
        
        if not self.current_friend:
            messagebox.showwarning("提示", "请先选择或添加好友")
            return
        
        if not API_KEY:
            messagebox.showwarning("提示", "请先配置 API Key")
            return
        
        # 显示对方消息
        self.chat_text.insert("end", f"\nTA: {message}\n")
        self.chat_text.see("end")
        
        self.processing = True
        self.input_text.delete("1.0", "end")
        
        # 后台调用 API
        threading.Thread(
            target=self._generate_reply,
            args=(message,),
            daemon=True
        ).start()
    
    def _generate_reply(self, message: str) -> None:
        """生成回复（后台线程）"""
        try:
            relation = self.relation_var.get() or "恋人"
            style = self.style_var.get() or "升温版"
            
            # 调用 V11 引擎
            replies, info = ai_generate_reply(
                message=message,
                relation=relation,
                style=style,
                conversation_history=self.conversation_history,
                api_key=API_KEY
            )
            
            # 更新 UI
            self.root.after(0, lambda: self._show_replies(replies, info))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
        finally:
            self.root.after(0, lambda: setattr(self, 'processing', False))
    
    def _show_replies(self, replies: List[str], info: str) -> None:
        """显示回复"""
        if not replies:
            messagebox.showwarning("提示", "未生成回复，请重试")
            return
        
        # 显示回复选项
        self.reply_list.delete(0, "end")
        for reply in replies:
            self.reply_list.insert("end", reply)
        
        # 自动选择第一条
        if replies:
            self.chat_text.insert("end", f"我：{replies[0]}\n")
            self.chat_text.see("end")
            
            # 保存历史
            self._save_conversation(replies[0])
    
    def _save_conversation(self, reply: str) -> None:
        """保存对话历史"""
        if self.current_friend:
            input_msg = self.input_text.get("1.0", "end").strip()
            self.conversation_history += f"TA: {input_msg}\n我：{reply}\n"
            self.friend_manager.update_history(self.current_friend, self.conversation_history)
    
    def copy_reply(self, event) -> None:
        """复制回复"""
        selection = self.reply_list.curselection()
        if selection:
            reply = self.reply_list.get(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(reply)
            self.root.update()
            messagebox.showinfo("✅ 完成", "已复制到剪贴板")
            
            # 更新历史
            self._save_conversation(reply)
    
    def show_config(self) -> None:
        """显示设置"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ 设置")
        dialog.geometry("400x200")
        
        tk.Label(dialog, text="🔑 API Key", font=("微软雅黑", 11, "bold")).pack(pady=10)
        
        api_entry = tk.Entry(dialog, font=("Consolas", 11), show="*")
        api_entry.pack(fill="x", padx=20, pady=5)
        if API_KEY:
            api_entry.insert(0, API_KEY)
        
        tk.Label(dialog, text="* MiniMax API Key，用于 AI 回复生成",
                font=("微软雅黑", 9), fg="#888").pack(pady=5)
        
        def save():
            new_key = api_entry.get().strip()
            if new_key:
                CONFIG["api_key"] = new_key
                save_config(CONFIG)
                global API_KEY
                API_KEY = new_key
                messagebox.showinfo("完成", "API Key 已保存")
                dialog.destroy()
        
        tk.Button(dialog, text="💾 保存", bg="#667eea", fg="white",
                 font=("微软雅黑", 10, "bold"), command=save).pack(pady=10)


if __name__ == "__main__":
    print("=" * 60)
    print("微信高情商回复助手 V11.0")
    print("大模型专用版 - 严格控制的回复生成")
    print("=" * 60)
    App()
