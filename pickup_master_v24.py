# -*- coding: utf-8 -*-
"""
把妹大师 V24.0 - Viking 大模型版
核心：Viking 上下文管理 + MiniMax API 大模型回复
"""

import os
import json
import hashlib
import random
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple


# ==================== 配置管理 ====================

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config() -> dict:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": "", "model": "MiniMax-M2.7"}

def save_config(config: dict) -> None:
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

CONFIG = load_config()
API_KEY = CONFIG.get("api_key", "")
MODEL = CONFIG.get("model", "MiniMax-M2.7")


# ==================== Viking 上下文管理 ====================

class VikingContext:
    """Viking 上下文"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.memories: List[Dict] = []
        self.girl_profiles: Dict[str, Dict] = {}
        self.conversation_history: List[Dict] = []
        self.long_term_memory: List[Dict] = []
        self.current_girl: Optional[str] = None
    
    def add_memory(self, girl_name: str, content: str, tags: List[str] = None) -> None:
        """添加记忆"""
        self.memories.append({
            "girl_name": girl_name,
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_conversation(self, role: str, content: str, girl_name: str = None) -> None:
        """添加对话"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "girl_name": girl_name,
            "timestamp": datetime.now().isoformat(),
        })
        
        # 压缩历史 (保留最近 10 条)
        if len(self.conversation_history) > 10:
            old = self.conversation_history[:-10]
            self.long_term_memory.append({
                "type": "conversation_summary",
                "count": len(old),
                "summary": f"之前进行了{len(old)}轮对话",
            })
            self.conversation_history = self.conversation_history[-10:]
    
    def get_memories(self, girl_name: str = None) -> List[Dict]:
        """获取记忆"""
        if girl_name:
            return [m for m in self.memories if m.get("girl_name") == girl_name]
        return self.memories
    
    def get_recent_history(self, limit: int = 5) -> str:
        """获取最近对话历史"""
        recent = self.conversation_history[-limit:]
        lines = []
        for conv in recent:
            role = "TA" if conv["role"] == "user" else "我"
            lines.append(f"{role}: {conv['content']}")
        return "\n".join(lines)


class VikingContextManager:
    """Viking 上下文管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, VikingContext] = {}
        self.current_session: Optional[VikingContext] = None
    
    def create_session(self, user_id: str) -> VikingContext:
        """创建会话"""
        session_id = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        context = VikingContext(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = context
        self.current_session = context
        return context
    
    def get_current_session(self) -> Optional[VikingContext]:
        """获取当前会话"""
        return self.current_session
    
    def set_current_girl(self, girl_name: str) -> None:
        """设置当前女生"""
        if self.current_session:
            self.current_session.current_girl = girl_name
    
    def add_memory(self, girl_name: str, content: str, tags: List[str] = None) -> None:
        """添加记忆"""
        if self.current_session:
            self.current_session.add_memory(girl_name, content, tags)
    
    def add_conversation(self, role: str, content: str, girl_name: str = None) -> None:
        """添加对话"""
        if self.current_session:
            self.current_session.add_conversation(role, content, girl_name)
    
    def get_context_for_reply(self) -> Dict:
        """获取回复所需的上下文"""
        if not self.current_session:
            return {}
        
        return {
            "current_girl": self.current_session.current_girl,
            "memories": self.current_session.get_memories(self.current_session.current_girl),
            "recent_history": self.current_session.get_recent_history(5),
            "long_term_memory": self.current_session.long_term_memory[-3:],
        }


# ==================== MiniMax API 调用 ====================

class MiniMaxAPI:
    """MiniMax API 调用"""
    
    def __init__(self, api_key: str, model: str = "MiniMax-M2.7"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    
    def generate_reply(self, prompt: str, system_prompt: str = None) -> Tuple[List[str], str]:
        """生成回复"""
        import requests
        
        if not self.api_key:
            return ["API Key 未配置，请在设置中配置", "请先配置 API Key", "缺少 API Key"], "无 API Key"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 300,
                "temperature": 0.8,
                "top_p": 0.9,
            }
            
            resp = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析回复 (按行分割)
            replies = [line.strip() for line in content.strip().split("\n") if line.strip()]
            
            # 确保至少 3 条
            while len(replies) < 3:
                replies.append("(请重试)")
            
            return replies[:3], f"API 返回{len(replies)}条"
            
        except requests.exceptions.Timeout:
            return ["请求超时，请重试", "网络超时", "请稍后再试"], "请求超时"
        except requests.exceptions.RequestException as e:
            return [f"API 错误：{str(e)}", "网络错误", "请检查网络"], f"请求失败：{e}"
        except Exception as e:
            return [f"错误：{str(e)}", "未知错误", "请重试"], f"异常：{e}"


# ==================== Prompt 构建 ====================

class PromptBuilder:
    """Prompt 构建器"""
    
    SYSTEM_PROMPT = """你是微信高情商聊天专家，擅长根据情境生成得体、温暖、有趣的回复。

【输出规则】
1. 生成 3 条回复，每行一条
2. 每条回复 8-20 字
3. 符合微信聊天习惯，自然口语化
4. 不要编号、不要引号、不要解释

【回复原则】
1. 先共情再回应 - 识别对方情绪
2. 符合关系身份 - 什么关系说什么话
3. 留有话题空间 - 让对方能继续聊
4. 真诚第一 - 不要套路感
5. 适度幽默 - 轻松但不轻浮"""

    def build_reply_prompt(self, message: str, context: Dict, relation: str = "恋人") -> str:
        """构建回复生成 Prompt"""
        
        parts = []
        
        # 关系设定
        relation_guide = {
            "恋人": "甜蜜亲密，体现关心和爱意，可以用宝贝/亲爱的等昵称",
            "朋友": "轻松随意，可以调侃开玩笑，像兄弟一样",
            "同事": "专业礼貌，保持适当距离",
            "客户": "商务专业，热情但不卑微",
            "家人": "亲情温暖，体贴关怀",
            "追求者": "委婉得体，不伤害对方",
            "海王": "若即若离，不要太主动",
            "高冷": "简洁冷淡，不延伸话题",
        }
        
        parts.append(f"【当前关系】{relation}")
        parts.append(f"语气指导：{relation_guide.get(relation, '自然得体')}")
        parts.append("")
        
        # 对方信息
        if context.get("current_girl"):
            parts.append(f"【对方名字】{context['current_girl']}")
            parts.append("")
        
        # 记忆信息
        memories = context.get("memories", [])
        if memories:
            parts.append("【历史记忆】")
            for mem in memories[:5]:
                parts.append(f"- {mem['content']}")
            parts.append("")
        
        # 最近对话
        recent_history = context.get("recent_history", "")
        if recent_history:
            parts.append("【最近对话】")
            parts.append(recent_history)
            parts.append("")
        
        # 当前消息
        parts.append("【TA 刚说】")
        parts.append(message)
        parts.append("")
        
        # 生成指令
        parts.append("请生成 3 条高情商回复，每行一条：")
        
        return "\n".join(parts)


# ==================== 把妹大师 V24.0 主引擎 ====================

class PickupMasterV24:
    """把妹大师 V24.0 - Viking 大模型版"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.ctx_manager = VikingContextManager()
        self.minimax = MiniMaxAPI(self.api_key, MODEL)
        self.prompt_builder = PromptBuilder()
        self.session_id = None
    
    def start_session(self, user_id: str) -> str:
        """开始会话"""
        context = self.ctx_manager.create_session(user_id)
        self.session_id = context.session_id
        return self.session_id
    
    def set_current_girl(self, girl_name: str) -> None:
        """设置当前女生"""
        self.ctx_manager.set_current_girl(girl_name)
    
    def add_memory(self, girl_name: str, content: str, tags: List[str] = None) -> None:
        """添加记忆"""
        self.ctx_manager.add_memory(girl_name, content, tags)
    
    def get_context(self) -> Dict:
        """获取当前上下文"""
        return self.ctx_manager.get_context_for_reply()
    
    def generate_reply(self, message: str, girl_name: str = None, 
                      relation: str = "恋人") -> Dict:
        """生成回复 (核心方法)"""
        
        # 设置当前女生
        if girl_name:
            self.set_current_girl(girl_name)
        
        # 添加用户消息到对话历史
        self.ctx_manager.add_conversation("user", message, girl_name)
        
        # 获取上下文
        context = self.get_context()
        
        # 构建 Prompt
        prompt = self.prompt_builder.build_reply_prompt(message, context, relation)
        
        # 调用 API 生成回复
        replies, info = self.minimax.generate_reply(
            prompt=prompt,
            system_prompt=PromptBuilder.SYSTEM_PROMPT
        )
        
        # 添加 AI 回复到对话历史
        if replies:
            self.ctx_manager.add_conversation("assistant", replies[0], girl_name)
        
        # 添加到记忆
        if girl_name:
            self.add_memory(girl_name, message, tags=[girl_name, "chat"])
        
        return {
            "reply": replies[0] if replies else "",
            "options": replies,
            "context_used": len(context.get("memories", [])),
            "info": info,
            "session_id": self.session_id,
        }
    
    def chat(self, message: str, girl_name: str = None, 
             relation: str = "恋人") -> Dict:
        """聊天 (便捷方法)"""
        return self.generate_reply(message, girl_name, relation)
    
    def analyze_interest(self, chat_history: str) -> Dict:
        """分析兴趣度 (本地分析)"""
        signals_positive = []
        signals_negative = []
        
        # 积极信号
        if "哈哈" in chat_history or "嘻嘻" in chat_history:
            signals_positive.append("经常笑/使用语气词")
        if "想你" in chat_history:
            signals_positive.append("表达思念")
        if "宝贝" in chat_history or "亲爱的" in chat_history:
            signals_positive.append("使用亲密称呼")
        if "！" in chat_history or "~" in chat_history:
            signals_positive.append("使用感叹号/波浪号（情绪高）")
        
        # 消极信号
        if chat_history.count("嗯") > 5:
            signals_negative.append("经常回复'嗯'（敷衍）")
        if chat_history.count("哦") > 3:
            signals_negative.append("经常回复'哦'（冷淡）")
        if chat_history.count("?") < 2:
            signals_negative.append("很少提问（不好奇）")
        
        # 计算分数
        score = 50 + len(signals_positive) * 10 - len(signals_negative) * 10
        score = max(0, min(100, score))
        
        level = "高" if score >= 80 else ("中" if score >= 60 else "低")
        
        suggestions = []
        if level == "高":
            suggestions = ["可以正式邀约了", "考虑表白时机"]
        elif level == "中":
            suggestions = ["继续升温关系", "尝试模糊邀约"]
        else:
            suggestions = ["先建立吸引力", "不要急于邀约"]
        
        return {
            "score": score,
            "level": level,
            "positive_signals": signals_positive,
            "negative_signals": signals_negative,
            "suggestions": suggestions,
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "api_key_configured": bool(self.api_key),
            "model": MODEL,
            "sessions": len(self.ctx_manager.sessions),
            "current_session": self.session_id,
        }


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("把妹大师 V24.0 - Viking 大模型版 测试")
    print("=" * 60)
    
    # 检查 API Key
    if not API_KEY:
        print("\n⚠️  警告：API Key 未配置")
        print("请在 config.json 中配置 API Key，或传入 api_key 参数")
        print("\n配置方法:")
        print("1. 创建 config.json 文件")
        print('2. 添加内容：{"api_key": "sk-xxx", "model": "MiniMax-M2.7"}')
        print("\n使用命令行版本配置：python3 main_cli.py")
    else:
        print(f"\n✅ API Key 已配置")
        print(f"模型：{MODEL}")
    
    # 测试引擎初始化
    print("\n【1. 引擎初始化】")
    master = PickupMasterV24()
    session_id = master.start_session("test_user")
    print(f"   会话 ID: {session_id}")
    
    # 测试状态
    print("\n【2. 系统状态】")
    status = master.get_status()
    for k, v in status.items():
        print(f"   {k}: {v}")
    
    # 测试聊天 (如果有 API Key)
    if API_KEY:
        print("\n【3. 聊天测试】")
        result = master.chat("在干嘛呢", girl_name="小美")
        print(f"   回复：{result['reply']}")
        print(f"   选项：{result['options']}")
        print(f"   信息：{result['info']}")
    else:
        print("\n【3. 聊天测试】")
        print("   ⚠️  需要 API Key 才能测试聊天功能")
    
    print("\n" + "=" * 60)
    print("✅ V24.0 引擎测试完成！")
    print("=" * 60)
