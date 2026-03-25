# -*- coding: utf-8 -*-
"""
高情商回复助手 - 智能回复引擎 V9.0
优化：
1. 好友画像分析（关系 + 重要事件）
2. 高情商回复工作流（画像 + 记忆 + 上下文 + 关系）
3. 性能优化（缓存、异步、批量）
"""

import re
import json
import hashlib
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from functools import lru_cache
import threading

# 导入 Prompt 工作流
from prompt_workflows_v9 import (
    build_profile_prompt,
    build_reply_prompt,
    get_tone_guide,
    get_style_description,
    get_time_context,
    PromptContext,
    RELATION_TONE_GUIDES,
    STYLE_DESCRIPTIONS
)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hit_count: int = 0


class ReplyCache:
    """回复缓存管理器"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = threading.Lock()
    
    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{args}:{kwargs}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            entry = self.cache.get(key)
            if entry:
                if time.time() < entry.expires_at:
                    entry.hit_count += 1
                    return entry.value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        with self._lock:
            now = time.time()
            if len(self.cache) >= self.max_size:
                self._evict()
            
            self.cache[key] = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=now + (ttl or self.default_ttl)
            )
    
    def _evict(self) -> None:
        """清理过期或最少使用的缓存"""
        now = time.time()
        expired = [k for k, v in self.cache.items() if now >= v.expires_at]
        for k in expired:
            del self.cache[k]
        
        if len(self.cache) >= self.max_size:
            least_used = min(self.cache.items(), key=lambda x: x[1].hit_count)
            del self.cache[least_used[0]]
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self.cache.clear()


@dataclass
class FriendProfile:
    """好友画像数据类"""
    name: str
    relation: str = "朋友"
    chat_style: Dict[str, str] = field(default_factory=dict)
    personality: Dict[str, str] = field(default_factory=dict)
    important_events: List[Dict[str, str]] = field(default_factory=list)
    relationship_intimacy: Dict[str, str] = field(default_factory=dict)
    summary: str = ""
    updated_at: str = ""
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'FriendProfile':
        """从 JSON 创建"""
        return cls(
            name=data.get("name", "未知"),
            relation=data.get("relation_type", "朋友"),
            chat_style=data.get("chat_style", {}),
            personality=data.get("personality", {}),
            important_events=data.get("important_events", []),
            relationship_intimacy=data.get("relationship_intimacy", {}),
            summary=data.get("summary", ""),
            updated_at=data.get("updated_at", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "relation_type": self.relation,
            "chat_style": self.chat_style,
            "personality": self.personality,
            "important_events": self.important_events,
            "relationship_intimacy": self.relationship_intimacy,
            "summary": self.summary,
            "updated_at": self.updated_at
        }
    
    def format_for_prompt(self) -> str:
        """格式化为 Prompt 文本"""
        lines = [f"好友：{self.name}"]
        lines.append(f"关系：{self.relation}")
        
        if self.chat_style:
            lines.append(f"聊天风格：{', '.join(f'{k}:{v}' for k, v in self.chat_style.items())}")
        
        if self.personality:
            lines.append(f"性格特点：{', '.join(f'{k}:{v}' for k, v in self.personality.items())}")
        
        if self.important_events:
            events = [e.get("event", "") for e in self.important_events[:3]]
            lines.append(f"重要事件：{', '.join(events)}")
        
        if self.summary:
            lines.append(f"综合印象：{self.summary}")
        
        return "\n".join(lines)


class ReplyEngineV9:
    """高情商回复引擎 V9.0"""
    
    # 意图关键词映射 - 增强版
    INTENT_KEYWORDS: Dict[str, List[str]] = {
        "checkin": ["在吗", "干嘛呢", "忙吗", "现在", "下班", "休息", "吃了吗", "睡了吗", "干嘛", "干啥",
                   "你好", "嗨", "哈喽", "在不在", "hello", "hi", "在么", "在"],
        "night": ["晚安", "睡觉", "困了", "累了", "休息", "下线", "困", "打哈欠", "睡了", "熬不动了"],
        "invite": ["出来", "玩", "约", "见面", "吃饭", "看电影", "逛街", "一起", "有空", "约吗",
                  "聚聚", "出来玩", "去哪里", "什么时候", "吃饭不", "出来吃饭"],
        "meal": ["吃", "饭", "外卖", "做菜", "做饭", "饿了", "美食", "餐厅", "饥饿", "想吃", "饿"],
        "affection": ["想", "喜欢", "爱", "心", "宝贝", "亲爱的", "么么", "爱你", "想你了", "想念",
                     "爱你", "心疼", "牵挂"],
        "light": ["嗯", "哦", "好的", "收到", "知道了", "行", "可以", "okay", "ok", "好", "行吧"],
        "thanks": ["谢谢", "感谢", "帮忙", "感恩", "感激", "谢啦", "多谢", "谢谢你", "辛苦了"],
        "apology": ["抱歉", "对不起", "不好意思", "sorry", "歉意", "抱歉抱歉", "我的错"],
        "care": ["注意", "小心", "感冒", "保暖", "多穿", "照顾", "身体", "健康", "别累着", "保重", "感冒了"],
        "decision": ["决定", "好了", "选好了", "就这样", "定了", "行吧", "那就这样", "算了"],
        "work": ["工作", "忙", "项目", "开会", "加班", "老板", "同事", "上班", "下班", "累", "辛苦",
                "不想上班"],
        "question": ["怎么", "为什么", "什么", "哪里", "谁", "多少", "?", "？", "干嘛呢", "怎么了",
                    "啥", "如何", "能借", "借我"],
        "emotional": ["开心", "高兴", "爽", "棒", "哈哈", "嘻嘻"],
        "share": ["今天", "刚刚", "发生", "遇到", "看到", "吃到", "买到", "完成", "成功", "脱单", "升职"],
        "complaint": ["烦死了", "讨厌", "气死", "无语", "服了", "什么鬼", "太过分", "凭什么",
                     "不想上班", "烦", "郁闷", "不爽"],
        "help": ["帮", "教", "指导", "建议", "怎么办", "怎么弄", "求助", "麻烦", "借我"],
        "congratulate": ["恭喜", "祝贺", "厉害", "牛", "棒棒", "优秀", "佩服", "脱单", "升职"],
        "comfort": ["安慰", "抱抱", "别哭", "没事", "我在", "别怕", "别难过"],
    }
    
    def __init__(self, api_key: str = "", log_callback: Optional[callable] = None):
        self.api_key = api_key
        self.log_callback = log_callback
        
        # 缓存系统
        self.reply_cache = ReplyCache(max_size=500, default_ttl=1800)  # 30 分钟 TTL
        self.profile_cache = ReplyCache(max_size=100, default_ttl=86400)  # 24 小时 TTL
        
        # 请求限流
        self._request_times: List[float] = []
        self._rate_limit = 10  # 每秒最多 10 次请求
        self._rate_limit_lock = threading.Lock()
        
        # 批量处理支持
        self._batch_mode = False
        self._batch_results: List[Any] = []
    
    def _log(self, msg: str) -> None:
        """记录日志"""
        if self.log_callback:
            self.log_callback(msg)
    
    def _check_rate_limit(self) -> bool:
        """检查请求限流"""
        with self._rate_limit_lock:
            now = time.time()
            self._request_times = [t for t in self._request_times if now - t < 1.0]
            
            if len(self._request_times) >= self._rate_limit:
                return False
            
            self._request_times.append(now)
            return True
    
    def detect_intent(self, message: str) -> str:
        """检测消息意图（增强版）"""
        message = message.lower()
        
        # 精确匹配优先规则
        # 「干嘛呢」「干什么」「咋啦」→ question 而不是 checkin
        if message in ["干嘛呢", "干什么", "干啥呢", "咋啦", "怎么了", "干嘛", "干啥"]:
            return "question"
        if message in ["吃了吗", "吃饭没", "吃饭了吗"]:
            return "meal"
        if message in ["睡了吗", "睡觉没"]:
            return "night"
        
        # 计算每个意图的匹配度
        intent_scores: Dict[str, int] = {}
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in message:
                    # 完整匹配得分更高
                    score += 2 if kw == message else 1
            if score > 0:
                intent_scores[intent] = score
        
        # 特殊规则：包含情绪词优先识别为 emotional/share/complaint
        if any(kw in message for kw in ["开心", "高兴", "爽", "棒", "哈哈", "嘻嘻"]):
            intent_scores["share"] = intent_scores.get("share", 0) + 3
        if any(kw in message for kw in ["烦死了", "讨厌", "气死", "无语", "服了", "什么鬼"]):
            intent_scores["complaint"] = intent_scores.get("complaint", 0) + 3
        if any(kw in message for kw in ["了！", "了。", "啦！", "啦~"]):
            intent_scores["share"] = intent_scores.get("share", 0) + 2
        
        if not intent_scores:
            return "default"
        
        # 返回得分最高的意图
        return max(intent_scores.items(), key=lambda x: x[1])[0]
    
    def detect_emotion(self, message: str) -> Dict[str, Any]:
        """检测消息情绪"""
        positive_words = ["开心", "高兴", "爽", "棒", "好", "棒", "哈哈", "嘻嘻", "爱", "喜欢"]
        negative_words = ["烦", "气", "怒", "哭", "难过", "郁闷", "不爽", "讨厌", "恨", "痛苦"]
        anxious_words = ["焦虑", "担心", "害怕", "紧张", "慌", "急"]
        
        emotion = {
            "type": "neutral",
            "intensity": 0,
            "keywords": []
        }
        
        for word in positive_words:
            if word in message:
                emotion["type"] = "positive"
                emotion["intensity"] += 1
                emotion["keywords"].append(word)
        
        for word in negative_words:
            if word in message:
                emotion["type"] = "negative"
                emotion["intensity"] += 1
                emotion["keywords"].append(word)
        
        for word in anxious_words:
            if word in message:
                emotion["type"] = "anxious"
                emotion["intensity"] += 1
                emotion["keywords"].append(word)
        
        # 感叹号增强情绪强度
        emotion["intensity"] += message.count("!") + message.count("！")
        
        return emotion
    
    def analyze_profile(self, chat_history: str, use_cache: bool = True) -> Optional[FriendProfile]:
        """分析好友画像"""
        cache_key = f"profile:{hashlib.md5(chat_history[:500].encode()).hexdigest()}"
        
        if use_cache:
            cached = self.profile_cache.get(cache_key)
            if cached:
                self._log("[缓存] 使用好友画像缓存")
                return FriendProfile.from_json(cached)
        
        if not self.api_key:
            self._log("[画像] 无 API Key，使用简化分析")
            return self._simple_profile_analysis(chat_history)
        
        try:
            import requests
            
            prompt = build_profile_prompt(chat_history[:3000])  # 限制长度
            
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": "MiniMax-M2.7",
                "messages": [
                    {"role": "system", "content": "你是人际关系分析师，请严格按照 JSON 格式输出分析结果"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            if not self._check_rate_limit():
                self._log("[限流] 请求过于频繁，稍后重试")
                time.sleep(0.5)
            
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            
            if resp.status_code != 200:
                self._log(f"[画像] API 错误：{resp.status_code}")
                return self._simple_profile_analysis(chat_history)
            
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析 JSON 结果
            profile_data = self._parse_profile_json(content)
            
            if profile_data:
                profile = FriendProfile.from_json(profile_data)
                profile.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # 缓存结果
                self.profile_cache.set(cache_key, profile.to_dict())
                
                self._log(f"[画像] 分析成功：{profile.name} - {profile.relation}")
                return profile
            else:
                return self._simple_profile_analysis(chat_history)
                
        except Exception as e:
            self._log(f"[画像] 分析失败：{str(e)}")
            return self._simple_profile_analysis(chat_history)
    
    def _simple_profile_analysis(self, chat_history: str) -> FriendProfile:
        """简化版好友画像分析（无 API）"""
        # 从聊天内容推断关系
        relation = "朋友"
        
        if any(kw in chat_history for kw in ["宝贝", "亲爱的", "老公", "老婆", "爱你"]):
            relation = "恋人"
        elif any(kw in chat_history for kw in ["爸妈", "爸", "妈", "家里"]):
            relation = "家人"
        elif any(kw in chat_history for kw in ["工作", "项目", "会议", "老板", "同事"]):
            relation = "同事"
        elif any(kw in chat_history for kw in ["合作", "合同", "价格", "客户"]):
            relation = "客户"
        
        # 分析聊天风格
        avg_length = sum(len(line) for line in chat_history.split("\n") if line) / max(1, len(chat_history.split("\n")))
        
        return FriendProfile(
            name="好友",
            relation=relation,
            chat_style={
                "expression_length": "长篇" if avg_length > 20 else "简洁",
                "tone": "正常"
            },
            personality={},
            important_events=[],
            summary=f"根据聊天内容推断为{relation}关系，聊天风格{'较为详细' if avg_length > 20 else '简洁'}。"
        )
    
    def _parse_profile_json(self, content: str) -> Optional[Dict[str, Any]]:
        """解析画像 JSON 结果"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 块
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试查找第一个{到最后一个}
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        self._log(f"[画像] JSON 解析失败：{content[:100]}...")
        return None
    
    def generate(self, message: str, relation: str = "朋友", style: str = "稳妥版",
                 mode: str = "hybrid", conversation_history: str = "",
                 friend_profile: Optional[FriendProfile] = None,
                 context: str = "", use_cache: bool = True) -> Tuple[List[str], str]:
        """
        生成回复（完整工作流）
        
        Args:
            message: 对方消息
            relation: 关系类型
            style: 回复风格
            mode: 模式 (local/ai/hybrid)
            conversation_history: 对话历史
            friend_profile: 好友画像
            context: 对话背景
            use_cache: 是否使用缓存
        
        Returns:
            (回复列表，信息)
        """
        # 检查缓存
        cache_key = f"reply:{hashlib.md5(f'{message}{relation}{style}{conversation_history[:200]}'.encode()).hexdigest()}"
        
        if use_cache:
            cached = self.reply_cache.get(cache_key)
            if cached:
                self._log("[缓存] 使用回复缓存")
                return cached, "[缓存] 命中"
        
        # 检测意图和情绪
        intent = self.detect_intent(message)
        emotion = self.detect_emotion(message)
        
        self._log(f"[意图] {intent}, [情绪] {emotion['type']} (强度:{emotion['intensity']})")
        
        # 获取语气指导
        tone_guide = get_tone_guide(relation, intent)
        style_desc = get_style_description(style)
        
        # 获取时间情境
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        time_context = get_time_context(now.hour, is_weekend)
        
        # 构建最近聊天记忆
        recent_memory = self._build_recent_memory(conversation_history)
        
        # 构建 Prompt 上下文
        prompt_context = PromptContext(
            friend_profile=friend_profile.format_for_prompt() if friend_profile else "暂无详细画像",
            relation=relation,
            tone_guide=tone_guide,
            recent_memory=recent_memory,
            current_message=message,
            context=context or "日常聊天",
            time_context=time_context,
            style=style,
            style_description=style_desc
        )
        
        # 生成回复
        if mode == "local" or not self.api_key:
            replies = self._generate_local_reply(message, relation, style, intent)
            info = f"[本地模式] 意图:{intent}"
        else:
            replies, info = self._generate_ai_reply(prompt_context, intent, emotion)
        
        # 确保有 3 条回复
        while len(replies) < 3:
            replies.append(self._generate_fallback_reply(relation, style))
        
        # 缓存结果
        if use_cache:
            self.reply_cache.set(cache_key, replies)
        
        return replies[:3], info
    
    def _build_recent_memory(self, conversation_history: str) -> str:
        """构建最近聊天记忆"""
        if not conversation_history:
            return "暂无历史对话"
        
        lines = conversation_history.strip().split("\n")
        recent_lines = []
        
        for line in lines[-10:]:  # 最近 10 行
            if line.startswith("对方:"):
                recent_lines.append(f"TA 说：{line[3:]}")
            elif line.startswith("我:"):
                recent_lines.append(f"我说：{line[2:]}")
        
        return "\n".join(recent_lines) if recent_lines else "暂无历史对话"
    
    def _generate_local_reply(self, message: str, relation: str, 
                             style: str, intent: str) -> List[str]:
        """生成本地回复（基于模板）"""
        
        # 丰富的关系 × 意图 × 风格模板
        TEMPLATES = {
            "恋人": {
                "checkin": {
                    "稳妥版": ["亲爱的我在呢", "宝贝我在，怎么啦", "在的，想你"],
                    "轻松版": ["干嘛呀~我在", "在在在！", "想你啦~"],
                    "升温版": ["终于找我啦！", "一直在线等你~", "我也正好在想你！"]
                },
                "question": {
                    "稳妥版": ["在想你呢", "没事，在想我们的周末", "在发呆"],
                    "轻松版": ["在发呆~", "在想你！", "在刷手机~"],
                    "升温版": ["在等你找我呀！", "在想你呢~", "在看我们的聊天记录！"]
                },
                "night": {
                    "稳妥版": ["晚安亲爱的，好梦", "爱你，晚安~", "么么哒，晚安"],
                    "轻松版": ["晚安啦~好梦", "睡个好觉哦", "晚安么么"],
                    "升温版": ["要抱着我睡哦~", "梦里见宝贝", "爱你哟，晚安~"]
                },
                "affection": {
                    "稳妥版": ["我也想你", "我也爱你~", "心里一直有你"],
                    "轻松版": ["嘿嘿", "知道啦~", "我也是！"],
                    "升温版": ["超级无敌想你！", "我的心给你~", "爱你三千遍！"]
                },
                "meal": {
                    "稳妥版": ["我刚好也饿了", "想吃你做的饭~", "一起吃吧"],
                    "轻松版": ["干饭人干饭魂！", "吃啥吃啥", "走起！"],
                    "升温版": ["想和你一起吃~", "喂我一口嘛", "一起做饭呀~"]
                },
                "care": {
                    "稳妥版": ["会的，你也是哦", "谢谢你关心~", "你也是呀"],
                    "轻松版": ["知道啦~", "会的会的", "你也是哦"],
                    "升温版": ["照顾好自己不然我会心疼的", "么么么么", "爱你哟~"]
                },
                "work": {
                    "稳妥版": ["辛苦了~", "工作顺利呀", "别太累"],
                    "轻松版": ["加油加油", "忙完就好啦", "挺住！"],
                    "升温版": ["累坏了吧~给你揉揉", "我养你呀~", "心疼你么么"]
                },
                "invite": {
                    "稳妥版": ["好呀，什么时候见", "周六日都可以~", "想去哪里呀"],
                    "轻松版": ["好哇！去哪玩", "约约约！", "走走走！"],
                    "升温版": ["超想见你！", "终于约我啦~", "我化妆很快的！"]
                },
            },
            "朋友": {
                "checkin": {
                    "稳妥版": ["在的，有事吗", "在呢，怎么啦", "在的，请说"],
                    "轻松版": ["嗨~", "在在在", "咋啦"],
                    "升温版": ["想我啦？", "终于想起我了！", "啥事呀~"]
                },
                "question": {
                    "稳妥版": ["没事，随便聊聊", "在想你呢", "发呆"],
                    "轻松版": ["在发呆~", "在想你！", "没事干~"],
                    "升温版": ["在等你找我呀！", "在想你呢~", "在看我们的聊天记录！"]
                },
                "night": {
                    "稳妥版": ["晚安~", "好梦", "早点睡"],
                    "轻松版": ["晚安晚安", "睡啦睡啦", "886~"],
                    "升温版": ["梦里见兄弟！", "爱你么么哒", "想你想你想你~"]
                },
                "invite": {
                    "稳妥版": ["可以啊，什么时候", "没问题，去哪", "有空，去"],
                    "轻松版": ["走走走！", "约约约！", "搞起！"],
                    "升温版": ["必须约！", "想死你了！", "走起走起~"]
                },
                "meal": {
                    "稳妥版": ["走，请客", "吃啥，我请", "我知道一家好的"],
                    "轻松版": ["吃吃吃！", "干饭去！", "走起！"],
                    "升温版": ["我请！我请！", "想和你一起吃~", "必须搓一顿~"]
                },
                "thanks": {
                    "稳妥版": ["不客气", "小事", "应该的"],
                    "轻松版": ["客气啥", "不用谢~", "哈哈"],
                    "升温版": ["必须的！", "为你两肋插刀！", "么么么~"]
                },
                "work": {
                    "稳妥版": ["加油", "辛苦了", "挺住"],
                    "轻松版": ["冲！", "加油加油", "你可以的！"],
                    "升温版": ["我养你吧！", "累坏了吧~", "么么哒~"]
                },
                "complaint": {
                    "稳妥版": ["理解", "确实烦", "抱抱"],
                    "轻松版": ["哈哈", "理解", "摸鱼"],
                    "升温版": ["想你想你想你！", "我的好兄弟！", "爱你么么！"]
                },
                "share": {
                    "稳妥版": ["挺好的", "恭喜", "不错"],
                    "轻松版": ["可以可以", "厉害", "666"],
                    "升温版": ["太棒了！", "恭喜恭喜！", "必须庆祝！"]
                },
                "congratulate": {
                    "稳妥版": ["恭喜恭喜", "厉害", "佩服"],
                    "轻松版": ["可以可以", "牛啊", "666"],
                    "升温版": ["太棒了！", "请客请客！", "我为你骄傲！"]
                },
                "question": {
                    "稳妥版": ["多少？", "什么时候用？", "我看看"],
                    "轻松版": ["多少啊？", "急用吗？", "我看看情况"],
                    "升温版": ["需要多少？", "我转你！", "别说借！"]
                },
                "help": {
                    "稳妥版": ["帮", "怎么说", "我尽力"],
                    "轻松版": ["帮帮帮！", "说", "咋帮"],
                    "升温版": ["必须帮！", "我挺你！", "有事说话！"]
                },
            },
            "同事": {
                "checkin": {
                    "稳妥版": ["在的，请说", "您好，请讲", "在，有什么事"],
                    "轻松版": ["在~", "请说", "啥事"],
                    "升温版": ["您好~", "请讲请讲", "在的呢~"]
                },
                "work": {
                    "稳妥版": ["好的收到", "明白了", "处理中"],
                    "轻松版": ["OK", "好嘞", "知道啦"],
                    "升温版": ["辛苦啦~", "加油！", "么么~"]
                },
                "thanks": {
                    "稳妥版": ["不客气", "应该的", "不用谢"],
                    "轻松版": ["客气~", "不客气~", "没事~"],
                    "升温版": ["么么么！", "不客气呀~", "客气啥~"]
                },
            },
            "客户": {
                "checkin": {
                    "稳妥版": ["您好，请讲", "在的，请说", "您好，请问有什么"],
                    "轻松版": ["您好~", "在的~", "请说~"],
                    "升温版": ["您好您好~", "在的呢~", "请讲请讲~"]
                },
                "thanks": {
                    "稳妥版": ["不客气", "应该的", "不用谢"],
                    "轻松版": ["不客气~", "应该的~", "哈哈~"],
                    "升温版": ["么么么！", "不客气呀~", "客气啥~"]
                },
            },
            "家人": {
                "checkin": {
                    "稳妥版": ["在的，爸妈", "干嘛呀爸妈", "有啥事呀"],
                    "轻松版": ["在嘞~", "咋啦~", "爸妈~"],
                    "升温版": ["爸妈我想你们！", "爸~妈~", "干啥呀~"]
                },
                "meal": {
                    "稳妥版": ["好的，一起吃", "可以", "做给我吃~"],
                    "轻松版": ["吃吃吃！", "干饭！", "走起~"],
                    "升温版": ["想吃爸妈做的饭！", "一起一起~", "我请你们！"]
                },
                "care": {
                    "稳妥版": ["会的，爸妈也是", "注意身体", "会的"],
                    "轻松版": ["知道啦~", "会的~", "爸妈也是~"],
                    "升温版": ["要照顾好自己！", "爱你们~", "么么么~"]
                },
                "night": {
                    "稳妥版": ["晚安爸妈", "好梦~", "早点睡"],
                    "轻松版": ["晚安~", "睡啦~", "886~"],
                    "升温版": ["爱你们~", "爸妈晚安~", "么么么~"]
                },
            },
            "追求者": {
                "checkin": {
                    "稳妥版": ["在的，有事吗", "请说", "有什么事"],
                    "轻松版": ["在~", "啥事~", "干嘛~"],
                    "升温版": ["想我啦？", "终于找我啦~", "啥事呀~"]
                },
                "invite": {
                    "稳妥版": ["看情况吧", "再说吧", "可能有空"],
                    "轻松版": ["再说吧~", "看看~", "嗯~"],
                    "升温版": ["好呀！", "可以呀~", "想去~"]
                },
            },
            "海王": {
                "checkin": {
                    "稳妥版": ["在忙", "稍等", "干什么"],
                    "轻松版": ["忙~", "啥事", "在~"],
                    "升温版": ["想你啦？", "终于找我啦~", "想我了？"]
                },
                "invite": {
                    "稳妥版": ["再看", "不一定", "最近没空"],
                    "轻松版": ["再看~", "不知道~", "嗯~"],
                    "升温版": ["好呀！", "可以~", "想去~"]
                },
            },
            "高冷": {
                "checkin": {
                    "稳妥版": ["嗯", "啥", "说"],
                    "轻松版": ["嗯？", "干嘛", "说"],
                    "升温版": ["干啥", "啥事", "说~"]
                },
                "night": {
                    "稳妥版": ["嗯", "晚", "睡"],
                    "轻松版": ["嗯", "晚安", "886"],
                    "升温版": ["晚安~", "好~", "睡~"]
                },
            },
        }
        
        # 获取模板
        relation_templates = TEMPLATES.get(relation, TEMPLATES.get("朋友", {}))
        intent_templates = relation_templates.get(intent, relation_templates.get("checkin", {}))
        replies = intent_templates.get(style, intent_templates.get("稳妥版", ["收到~", "好的呢", "知道啦"]))
        
        return replies
    
    def _generate_ai_reply(self, context: PromptContext, 
                          intent: str, emotion: Dict) -> Tuple[List[str], str]:
        """生成 AI 回复"""
        try:
            import requests
            
            prompt = build_reply_prompt(context)
            
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 根据情绪调整 temperature
            temperature = 0.7
            if emotion["type"] == "negative":
                temperature = 0.5  # 负面情绪时更保守
            elif emotion["type"] == "positive":
                temperature = 0.8  # 正面情绪时更活泼
            
            data = {
                "model": "MiniMax-M2.7",
                "messages": [
                    {"role": "system", "content": "你是高情商聊天专家，回复要真诚、温暖、得体"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": temperature
            }
            
            if not self._check_rate_limit():
                self._log("[限流] 请求过于频繁")
                time.sleep(0.5)
            
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            
            if resp.status_code != 200:
                return self._generate_local_reply(context.current_message, 
                                                  context.relation, context.style, intent), \
                       f"API 错误：{resp.status_code}"
            
            result = resp.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析回复
            replies = self._parse_replies(content)
            
            if len(replies) >= 2:
                return replies[:3], f"[AI 模式] 解析到{len(replies)}条"
            else:
                return self._generate_local_reply(context.current_message,
                                                  context.relation, context.style, intent), \
                       f"AI 解析失败 (仅{len(replies)}条)"
                       
        except Exception as e:
            self._log(f"[AI] 生成失败：{str(e)}")
            return ["稍等一下~", "我想想怎么说", "让我组织下语言"], f"AI 错误：{str(e)}"
    
    def _parse_replies(self, content: str) -> List[str]:
        """解析 AI 回复"""
        if not content:
            return []
        
        replies = []
        
        # 按行分割
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and len(line) >= 4 and len(line) <= 30:
                # 清理编号和标记
                line = re.sub(r'^[\d一二三四五 67890]+[.、:：)]', '', line)
                line = re.sub(r'^回复\s*\d*[:：]?', '', line)
                line = line.strip()
                
                if line and not any(kw in line for kw in ["让我", "我来", "建议", "可以"]):
                    replies.append(line)
        
        # 去重
        seen = set()
        unique = []
        for r in replies:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        
        return unique[:3]
    
    def _generate_fallback_reply(self, relation: str, style: str) -> str:
        """生成兜底回复"""
        fallbacks = {
            "恋人": ["想你啦~", "在呢宝贝", "爱你哟"],
            "朋友": ["哈哈可以", "没问题", "走走走"],
            "同事": ["好的收到", "明白", "我处理一下"],
            "客户": ["感谢您的信任", "我尽快安排", "有问题随时联系"],
            "家人": ["好的知道了", "你们也要注意身体", "爱你们"],
            "追求者": ["谢谢", "我先看看", "再说吧"],
            "海王": ["在忙", "晚点说", "最近比较累"],
            "高冷": ["嗯", "哦", "好"]
        }
        
        return fallbacks.get(relation, ["收到~", "好的", "知道啦"])[0]
    
    def batch_generate(self, messages: List[Dict[str, Any]]) -> List[Tuple[List[str], str]]:
        """批量生成回复（用于测试）"""
        self._batch_mode = True
        self._batch_results = []
        
        results = []
        for msg_data in messages:
            result = self.generate(
                message=msg_data.get("message", ""),
                relation=msg_data.get("relation", "朋友"),
                style=msg_data.get("style", "稳妥版"),
                use_cache=True
            )
            results.append(result)
        
        self._batch_mode = False
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "reply_cache_size": len(self.reply_cache.cache),
            "profile_cache_size": len(self.profile_cache.cache),
            "reply_cache_hits": sum(e.hit_count for e in self.reply_cache.cache.values()),
            "profile_cache_hits": sum(e.hit_count for e in self.profile_cache.cache.values())
        }
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.reply_cache.clear()
        self.profile_cache.clear()
        self._log("[缓存] 已清空")
