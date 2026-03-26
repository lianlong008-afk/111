# -*- coding: utf-8 -*-
"""
微信高情商回复助手 V10.0 - 上下文感知优化版
核心改进:
1. 真正的上下文感知 - 根据历史对话调整回复
2. 动态模板选择 - 避免重复回复
3. 情绪状态追踪 - 记住对话情绪走向
4. 回复多样性 - 同一意图不同场景不同回复
"""

import re
import random
import hashlib
from typing import List, Tuple, Optional, Dict
from datetime import datetime


class ConversationContext:
    """对话上下文管理器"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[Dict] = []  # 完整对话历史
        self.last_intent: Optional[str] = None
        self.last_reply_index: int = 0  # 上次使用的回复索引
        self.emotion_state: str = "neutral"  # 当前情绪状态
        self.topic_chain: List[str] = []  # 话题链
    
    def add_message(self, role: str, content: str, intent: str = "") -> None:
        """添加消息到历史"""
        self.messages.append({
            "role": role,
            "content": content,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史长度
        if len(self.messages) > self.max_history * 2:  # 保留 N 轮对话
            self.messages = self.messages[-self.max_history * 2:]
        
        # 更新状态
        if intent:
            self.last_intent = intent
        
        # 更新情绪状态
        self.emotion_state = self._detect_emotion(content)
        
        # 追踪话题链
        if intent in ["share", "complaint", "work"]:
            self.topic_chain.append(intent)
            if len(self.topic_chain) > 5:
                self.topic_chain = self.topic_chain[-5:]
    
    def _detect_emotion(self, text: str) -> str:
        """检测情绪"""
        positive = ["开心", "高兴", "哈哈", "嘻嘻", "棒", "爽", "爱", "喜欢"]
        negative = ["烦", "气", "怒", "哭", "难过", "郁闷", "累", "困"]
        
        if any(kw in text for kw in positive):
            return "positive"
        elif any(kw in text for kw in negative):
            return "negative"
        return "neutral"
    
    def get_recent_history(self, n: int = 5) -> str:
        """获取最近 N 轮对话"""
        recent = self.messages[-n*2:] if len(self.messages) > n*2 else self.messages
        lines = []
        for msg in recent:
            role = "TA" if msg["role"] == "user" else "我"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    
    def get_topic_context(self) -> str:
        """获取当前话题上下文"""
        if not self.topic_chain:
            return "日常聊天"
        
        # 统计主要话题
        topic_counts = {}
        for topic in self.topic_chain:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        main_topic = max(topic_counts.items(), key=lambda x: x[1])[0]
        return f"正在讨论{main_topic}相关话题"
    
    def should_avoid_reply(self, reply: str) -> bool:
        """检查是否应该避免某个回复（避免重复）"""
        # 检查最近是否用过这个回复
        for msg in reversed(self.messages[-10:]):
            if msg["role"] == "assistant" and msg["content"] == reply:
                return True
        return False
    
    def clear(self) -> None:
        """清空上下文"""
        self.messages = []
        self.last_intent = None
        self.last_reply_index = 0
        self.emotion_state = "neutral"
        self.topic_chain = []


class ReplyEngineV10:
    """V10 回复引擎 - 上下文感知版"""
    
    # 简化的意图关键词（只保留核心）
    INTENT_KEYWORDS = {
        "checkin": ["在吗", "在不在", "在么", "在", "hello", "hi"],
        "question": ["干嘛呢", "干什么", "干啥", "咋啦", "怎么了"],
        "meal": ["吃", "饭", "饿", "外卖", "餐厅"],
        "invite": ["出来", "约", "见面", "有空", "聚聚"],
        "affection": ["想", "爱", "喜欢", "宝贝", "亲爱的"],
        "night": ["晚安", "睡觉", "困了", "睡了"],
        "thanks": ["谢谢", "感谢", "谢啦"],
        "care": ["注意", "小心", "感冒", "照顾", "身体"],
        "complaint": ["烦", "累", "不想", "讨厌", "郁闷"],
        "share": ["了！", "了~", "哈哈", "太棒了", "成功"],
        "work": ["工作", "忙", "加班", "上班", "项目"],
        "help": ["帮", "借", "怎么办", "求助"],
    }
    
    # 丰富的模板库 - 每个意图有多个变体
    TEMPLATES = {
        "恋人": {
            "checkin": [
                ["亲爱的我在呢", "宝贝我在，怎么啦", "在的，想你"],
                ["来啦~", "在呢在呢", "随时待命！"],
                ["终于找我啦！", "一直在线等你~", "我也正好在想你！"],
            ],
            "question": [
                ["在想你呢", "没事，在想我们的周末", "在发呆"],
                ["在刷手机~", "在听音乐", "在休息"],
                ["在等你找我呀！", "在看我们的聊天记录！", "在想你有没有想我"],
            ],
            "meal": [
                ["我刚好也饿了", "想吃你做的饭~", "一起吃吧"],
                ["还没吃呢", "在想要吃什么", "你推荐一下"],
                ["想和你一起吃~", "喂我一口嘛", "一起做饭呀~"],
            ],
            "affection": [
                ["我也想你", "我也爱你~", "心里一直有你"],
                ["嘿嘿", "知道啦~", "我也是！"],
                ["超级无敌想你！", "我的心给你~", "爱你三千遍！"],
            ],
            "invite": [
                ["好呀，什么时候见", "周六日都可以~", "想去哪里呀"],
                ["有空呀", "想见你", "什么时候"],
                ["超想见你！", "终于约我啦~", "我化妆很快的！"],
            ],
            "night": [
                ["晚安亲爱的，好梦", "爱你，晚安~", "么么哒，晚安"],
                ["早点休息", "别熬夜", "盖好被子"],
                ["要抱着我睡哦~", "梦里见宝贝", "爱你哟，晚安~"],
            ],
            "care": [
                ["会的，你也是哦", "谢谢你关心~", "你也是呀"],
                ["知道啦~", "会的会的", "你也是哦"],
                ["照顾好自己不然我会心疼的", "么么么么", "爱你哟~"],
            ],
            "complaint": [
                ["理解", "确实烦", "抱抱"],
                ["心疼你", "别难过", "有我在"],
                ["累坏了吧~给你揉揉", "我养你呀~", "心疼你么么"],
            ],
            "share": [
                ["挺好的", "恭喜", "不错"],
                ["真棒！", "厉害！", "为你开心！"],
                ["太棒了！", "恭喜恭喜！", "必须庆祝！"],
            ],
            "work": [
                ["辛苦了~", "工作顺利呀", "别太累"],
                ["加油加油", "忙完就好啦", "挺住！"],
                ["累坏了吧~给你揉揉", "我养你呀~", "心疼你么么"],
            ],
            "help": [
                ["帮", "怎么说", "我尽力"],
                ["我来帮你", "一起想办法", "别急"],
                ["必须帮！", "我挺你！", "有事说话！"],
            ],
            "thanks": [
                ["不客气呀~", "应该的~", "么么哒"],
                ["客气啥", "小事小事~", "哈哈不客气"],
                ["为你做什么都愿意~", "么么么么", "不客气啦爱你~"],
            ],
        },
        "朋友": {
            "checkin": [
                ["在的，有事吗", "在呢，怎么啦", "在的，请说"],
                ["嗨~", "在在在", "咋啦"],
                ["想我啦？", "终于想起我了！", "啥事呀~"],
            ],
            "question": [
                ["没事，随便聊聊", "在想你呢", "发呆"],
                ["在发呆~", "在想你！", "没事干~"],
                ["在等你找我呀！", "在想你呢~", "在看我们的聊天记录！"],
            ],
            "invite": [
                ["可以啊，什么时候", "没问题，去哪", "有空，去"],
                ["走走走！", "约约约！", "搞起！"],
                ["必须约！", "想死你了！", "走起走起~"],
            ],
            "complaint": [
                ["理解", "确实烦", "抱抱"],
                ["哈哈", "理解", "摸鱼"],
                ["太惨了", "心疼你", "出来喝一杯？"],
            ],
            "share": [
                ["挺好的", "恭喜", "不错"],
                ["可以可以", "厉害", "666"],
                ["太棒了！", "恭喜恭喜！", "必须庆祝！"],
            ],
            "help": [
                ["多少？", "什么时候用？", "我看看"],
                ["多少啊？", "急用吗？", "我看看情况"],
                ["需要多少？", "我转你！", "别说借！"],
            ],
        },
        "同事": {
            "checkin": [
                ["在的，请说", "您好，请讲", "在，有什么事"],
                ["在~", "请说", "啥事"],
                ["您好~", "请讲请讲", "在的呢~"],
            ],
            "work": [
                ["好的收到", "明白了", "处理中"],
                ["OK", "好嘞", "知道啦"],
                ["辛苦啦~", "加油！", "么么~"],
            ],
            "thanks": [
                ["不客气", "应该的", "不用谢"],
                ["客气~", "不客气~", "没事~"],
                ["么么么！", "不客气呀~", "客气啥~"],
            ],
        },
    }
    
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}  # 每个好友独立上下文
    
    def get_context(self, friend_id: str) -> ConversationContext:
        """获取好友的对话上下文"""
        if friend_id not in self.contexts:
            self.contexts[friend_id] = ConversationContext()
        return self.contexts[friend_id]
    
    def detect_intent(self, message: str) -> str:
        """检测意图"""
        message = message.lower()
        
        # 精确匹配
        exact_matches = {
            "干嘛呢": "question", "干什么": "question", "干啥": "question",
            "吃了吗": "meal", "吃饭没": "meal",
            "睡了吗": "night", "睡觉没": "night",
            "不想上班": "complaint", "不想工作": "complaint",
            "早点睡觉": "care", "注意身体": "care",
        }
        if message in exact_matches:
            return exact_matches[message]
        
        # 关键词匹配
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in message:
                    return intent
        
        return "default"
    
    def generate(self, message: str, relation: str = "朋友", style: str = "稳妥版",
                 friend_id: str = "default") -> Tuple[List[str], str]:
        """
        生成回复（上下文感知版）
        
        Args:
            message: 对方消息
            relation: 关系类型
            style: 回复风格 (稳妥版/轻松版/升温版)
            friend_id: 好友 ID（用于追踪上下文）
        
        Returns:
            (回复列表，信息)
        """
        # 获取上下文
        context = self.get_context(friend_id)
        
        # 检测意图
        intent = self.detect_intent(message)
        
        # 获取模板
        relation_templates = self.TEMPLATES.get(relation, self.TEMPLATES.get("朋友", {}))
        
        # 风格映射
        style_map = {"稳妥版": 0, "轻松版": 1, "升温版": 2}
        style_index = style_map.get(style, 0)
        
        # 获取该意图的所有模板变体
        intent_variants = relation_templates.get(intent, {})
        if not intent_variants:
            # 降级到 checkin
            intent_variants = relation_templates.get("checkin", {})
        
        # 获取指定风格的变体列表
        variants_list = list(intent_variants.values())
        if style_index < len(variants_list):
            candidate_replies = variants_list[style_index]
        else:
            candidate_replies = variants_list[0]
        
        # 上下文感知：避免重复回复
        final_replies = []
        for reply in candidate_replies:
            if context.should_avoid_reply(reply):
                # 如果有其他变体，从其他变体中选择
                for i, variant in enumerate(variants_list):
                    if i != style_index and reply in variant:
                        # 找不同的回复
                        for alt_reply in variant:
                            if not context.should_avoid_reply(alt_reply):
                                final_replies.append(alt_reply)
                                break
            else:
                final_replies.append(reply)
        
        # 确保有 3 条回复
        while len(final_replies) < 3:
            # 从其他变体中补充
            for variant in variants_list:
                for reply in variant:
                    if reply not in final_replies:
                        final_replies.append(reply)
                        if len(final_replies) >= 3:
                            break
                if len(final_replies) >= 3:
                    break
            
            # 如果还不够，添加通用回复
            if len(final_replies) < 3:
                final_replies.append("收到~")
        
        # 更新上下文
        context.add_message("user", message, intent)
        context.add_message("assistant", final_replies[0], intent)
        
        info = f"[意图:{intent}] [情绪:{context.emotion_state}] [话题:{context.get_topic_context()}]"
        
        return final_replies[:3], info
    
    def get_context_summary(self, friend_id: str) -> str:
        """获取上下文摘要"""
        context = self.contexts.get(friend_id)
        if not context:
            return "暂无对话历史"
        
        return f"""
对话轮数：{len(context.messages)//2}轮
最近话题：{context.get_topic_context()}
当前情绪：{context.emotion_state}
最近对话:
{context.get_recent_history(3)}
"""
    
    def clear_context(self, friend_id: str) -> None:
        """清空指定好友的上下文"""
        if friend_id in self.contexts:
            self.contexts[friend_id].clear()


# 测试
if __name__ == "__main__":
    engine = ReplyEngineV10()
    
    print("=" * 60)
    print("微信高情商回复助手 V10.0 - 上下文感知测试")
    print("=" * 60)
    print()
    
    # 模拟连续对话
    friend_id = "test_lover"
    messages = [
        "在吗",
        "干嘛呢",
        "想你了",
        "我也想你",
        "周末有空吗",
        "出来吃饭",
        "晚安",
    ]
    
    for msg in messages:
        replies, info = engine.generate(
            message=msg,
            relation="恋人",
            style="升温版",
            friend_id=friend_id
        )
        
        print(f"Q: {msg}")
        print(f"   {info}")
        print(f"   A: {replies[0]}")
        print(f"   备选：{replies[1]} | {replies[2]}")
        print()
    
    # 查看上下文摘要
    print("=" * 60)
    print("上下文摘要:")
    print(engine.get_context_summary(friend_id))
