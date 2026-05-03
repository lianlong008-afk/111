# -*- coding: utf-8 -*-
"""
把妹大师 V23.0 - Viking 终极整合版
整合 V20/V21 所有把妹技巧 + Viking 上下文管理
核心特性:
1. Viking 文件系统管理 10000+ 技巧
2. L0/L1/L2 分层上下文加载
3. 基于上下文的智能回复生成
4. 记忆 + 技巧 + 场景三维检索
5. 自动会话管理和长期记忆
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import hashlib
import random


# ==================== V20/V21 技巧库导入 ====================

# 从 V20 导入基础技巧库
from pickup_master_v20 import (
    ATTRACTION_BUILDING,
    OPENING_LINES,
    CHAT_ESCALATION,
    DATING_SKILLS,
    PHYSICAL_ESCALATION,
    RELATIONSHIP_CONFIRMATION,
    LONG_TERM_MAINTENANCE,
    CASE_STUDIES,
)

# 从 V21 导入全球技巧库
from pickup_master_v21_global import (
    GLOBAL_PICKUP_LINES,
    BODY_LANGUAGE_SIGNALS,
    FLIRTY_TEXTS,
    SOCIAL_MEDIA_FLIRTING,
    LONG_DISTANCE_TIPS,
    ZODIAC_TIPS,
)


# ==================== Viking 核心数据结构 ====================

@dataclass
class VikingNode:
    """Viking 节点"""
    id: str
    name: str
    type: str
    uri: str
    level: str
    content: Any = None
    metadata: Dict = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {k: getattr(self, k) for k in ['id', 'name', 'type', 'uri', 'level', 
                                               'content', 'metadata', 'children', 
                                               'parent_id', 'created_at', 'updated_at', 
                                               'access_count', 'tags']}


@dataclass
class VikingContext:
    """Viking 上下文"""
    session_id: str
    user_id: str
    nodes: List[VikingNode] = field(default_factory=list)
    memory_nodes: List[str] = field(default_factory=list)
    resource_nodes: List[str] = field(default_factory=list)
    skill_nodes: List[str] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    long_term_memory: List[Dict] = field(default_factory=list)
    current_girl: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "memory_nodes": self.memory_nodes,
            "resource_nodes": self.resource_nodes,
            "skill_nodes": self.skill_nodes,
            "conversation_history": self.conversation_history,
            "long_term_memory": self.long_term_memory,
            "current_girl": self.current_girl,
        }


# ==================== Viking 文件系统 ====================

class VikingFileSystem:
    """Viking 文件系统"""
    
    def __init__(self, storage_path: str = "~/.viking_dating"):
        self.storage_path = os.path.expanduser(storage_path)
        self.nodes: Dict[str, VikingNode] = {}
        self.uri_index: Dict[str, str] = {}
        self._initialize_storage()
        self._load_nodes()
    
    def _initialize_storage(self) -> None:
        os.makedirs(self.storage_path, exist_ok=True)
        for subdir in ["memory", "resources", "skills", "sessions", "techniques"]:
            os.makedirs(os.path.join(self.storage_path, subdir), exist_ok=True)
    
    def _load_nodes(self) -> None:
        index_file = os.path.join(self.storage_path, "index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                return

            for node_data in data.get("nodes", []):
                try:
                    node = VikingNode(**node_data)
                except TypeError:
                    continue
                if node.uri in self.uri_index:
                    old_node_id = self.uri_index[node.uri]
                    self.nodes.pop(old_node_id, None)
                self.nodes[node.id] = node
                self.uri_index[node.uri] = node.id
    
    def _save_index(self) -> None:
        index_file = os.path.join(self.storage_path, "index.json")
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str, deterministic: bool = False) -> str:
        seed = content if deterministic else f"{content}{datetime.now().isoformat()}"
        return hashlib.md5(seed.encode()).hexdigest()[:12]
    
    def _generate_uri(self, path: str, name: str = "") -> str:
        clean_path = path.strip("/")
        clean_name = (name or "").strip("/")
        if clean_name:
            return f"viking://{clean_path}/{clean_name}"
        return f"viking://{clean_path}"
    
    def add_node(self, name: str, content: Any, path: str, 
                 node_type: str = "file", level: str = "L1",
                 tags: List[str] = None, metadata: Dict = None,
                 dedupe: bool = True) -> VikingNode:
        uri = self._generate_uri(path, name)
        existing_id = self.uri_index.get(uri) if dedupe else None
        existing = self.nodes.get(existing_id) if existing_id else None
        now = datetime.now().isoformat()
        node_id = existing.id if existing else self._generate_id(uri, deterministic=dedupe)
        
        node = VikingNode(
            id=node_id, name=name, type=node_type, uri=uri, level=level,
            content=content, metadata=metadata or {}, tags=tags or [],
            created_at=existing.created_at if existing else now,
            updated_at=now,
            access_count=existing.access_count if existing else 0,
        )
        
        self.nodes[node_id] = node
        self.uri_index[uri] = node_id
        self._save_index()
        return node
    
    def get_node(self, uri: str) -> Optional[VikingNode]:
        node_id = self.uri_index.get(uri)
        if node_id:
            node = self.nodes.get(node_id)
            if node:
                node.access_count += 1
                node.updated_at = datetime.now().isoformat()
                self._save_index()
                return node
        return None
    
    def find_nodes(self, query: str, limit: int = 10) -> List[VikingNode]:
        results = []
        query_lower = query.lower()
        
        # 1. 标签匹配
        for node in self.nodes.values():
            if any(query_lower in tag.lower() for tag in node.tags):
                results.append(node)
                if len(results) >= limit:
                    return results
        
        # 2. 名称匹配
        for node in self.nodes.values():
            if query_lower in node.name.lower():
                if node not in results:
                    results.append(node)
                    if len(results) >= limit:
                        return results
        
        # 3. 内容匹配
        for node in self.nodes.values():
            if isinstance(node.content, str) and query_lower in node.content.lower():
                if node not in results:
                    results.append(node)
                    if len(results) >= limit:
                        return results
        
        return results
    
    def list_directory(self, path: str) -> List[VikingNode]:
        uri = self._generate_uri(path)
        results = []
        for node in self.nodes.values():
            if node.uri.startswith(uri + "/"):
                results.append(node)
        return sorted(results, key=lambda x: (x.type != "directory", x.name))


# ==================== Viking 上下文管理器 ====================

class VikingContextManager:
    """Viking 上下文管理器"""
    
    def __init__(self, fs: VikingFileSystem):
        self.fs = fs
        self.sessions: Dict[str, VikingContext] = {}
        self.current_session: Optional[VikingContext] = None
    
    def create_session(self, user_id: str) -> VikingContext:
        session_id = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        context = VikingContext(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = context
        self.current_session = context
        self._save_session()
        return context
    
    def get_session(self, session_id: str) -> Optional[VikingContext]:
        return self.sessions.get(session_id)
    
    def _save_session(self) -> None:
        if self.current_session:
            session_file = os.path.join(self.fs.storage_path, "sessions", f"{self.current_session.session_id}.json")
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(self.current_session.to_dict(), f, ensure_ascii=False, indent=2)
    
    def add_to_memory(self, content: Dict, tags: List[str] = None) -> VikingNode:
        node = self.fs.add_node(
            name=f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            content=content, path="memory", tags=tags or [], metadata={"type": "memory"},
            dedupe=False,
        )
        if self.current_session:
            self.current_session.memory_nodes.append(node.id)
            self._save_session()
        return node
    
    def add_conversation(self, role: str, content: str, girl_name: str = None) -> None:
        if self.current_session:
            self.current_session.conversation_history.append({
                "role": role, "content": content,
                "timestamp": datetime.now().isoformat(),
                "girl_name": girl_name,
            })
            if len(self.current_session.conversation_history) > 10:
                self._compress_conversation()
    
    def _compress_conversation(self) -> None:
        if not self.current_session:
            return
        recent = self.current_session.conversation_history[-5:]
        old_conv = self.current_session.conversation_history[:-5]
        if old_conv:
            summary = {
                "type": "conversation_summary",
                "count": len(old_conv),
                "summary": f"之前进行了{len(old_conv)}轮对话",
                "timestamp": datetime.now().isoformat(),
            }
            self.current_session.long_term_memory.append(summary)
        self.current_session.conversation_history = recent
        self._save_session()
    
    def search_context(self, query: str) -> List[VikingNode]:
        return self.fs.find_nodes(query, limit=10)
    
    def get_retrieval_trajectory(self) -> Dict:
        return {
            "session_id": self.current_session.session_id if self.current_session else None,
            "nodes_accessed": [{"uri": n.uri, "access_count": n.access_count} 
                              for n in self.fs.nodes.values() if n.access_count > 0],
        }


# ==================== 把妹大师 V23.0 - 终极整合版 ====================

class PickupMasterV23:
    """把妹大师 V23.0 - Viking 终极整合版"""
    
    def __init__(self, storage_path: str = "~/.viking_dating"):
        self.fs = VikingFileSystem(storage_path)
        self.ctx_manager = VikingContextManager(self.fs)
        self._initialize_techniques()
        self._initialize_resources()
    
    def _initialize_techniques(self) -> None:
        """初始化 V20/V21 技巧库到 Viking 文件系统"""
        # V20 技巧
        techniques_v20 = {
            "attraction_building": ATTRACTION_BUILDING,
            "opening_lines": OPENING_LINES,
            "chat_escalation": CHAT_ESCALATION,
            "dating_skills": DATING_SKILLS,
            "physical_escalation": PHYSICAL_ESCALATION,
            "relationship_confirmation": RELATIONSHIP_CONFIRMATION,
            "long_term_maintenance": LONG_TERM_MAINTENANCE,
            "case_studies": CASE_STUDIES,
        }
        
        for name, content in techniques_v20.items():
            self.fs.add_node(
                name=name, content=content, path="techniques",
                level="L1", tags=[name, "v20"], metadata={"version": "20.0", "type": "technique"}
            )
        
        # V21 技巧
        techniques_v21 = {
            "global_pickup_lines": GLOBAL_PICKUP_LINES,
            "body_language_signals": BODY_LANGUAGE_SIGNALS,
            "flirty_texts": FLIRTY_TEXTS,
            "social_media_flirting": SOCIAL_MEDIA_FLIRTING,
            "long_distance_tips": LONG_DISTANCE_TIPS,
            "zodiac_tips": ZODIAC_TIPS,
        }
        
        for name, content in techniques_v21.items():
            self.fs.add_node(
                name=name, content=content, path="techniques",
                level="L1", tags=[name, "v21", "global"], metadata={"version": "21.0", "type": "technique"}
            )
    
    def _initialize_resources(self) -> None:
        """初始化资源"""
        # 从技巧库提取常用资源
        opening_lines = {}
        for cat, lines in OPENING_LINES.get("微信开场白库", {}).items():
            opening_lines[cat] = [line["话术"] for line in lines[:3]]
        
        self.fs.add_node(
            name="opening_lines_quick", content=opening_lines, path="resources",
            level="L0", tags=["开场白", "快速"], metadata={"type": "quick_reference"}
        )
        
        # 约会地点
        date_locations = DATING_SKILLS.get("约会地点选择", {})
        self.fs.add_node(
            name="date_locations", content=date_locations, path="resources",
            level="L0", tags=["约会", "地点"], metadata={"type": "quick_reference"}
        )
    
    def start_session(self, user_id: str) -> str:
        context = self.ctx_manager.create_session(user_id)
        return context.session_id
    
    def set_current_girl(self, girl_name: str) -> None:
        """设置当前聊天女生"""
        if self.ctx_manager.current_session:
            self.ctx_manager.current_session.current_girl = girl_name
            self.ctx_manager._save_session()
    
    def add_memory(self, girl_name: str, interaction: str, tags: List[str] = None) -> VikingNode:
        memory = {
            "girl_name": girl_name,
            "interaction": interaction,
            "timestamp": datetime.now().isoformat(),
        }
        return self.ctx_manager.add_to_memory(memory, tags or [girl_name])
    
    def get_opening_line(self, category: str = None, scenario: str = None) -> str:
        """获取开场白 (从 V20 技巧库)"""
        if not category:
            category = random.choice(list(OPENING_LINES.get("微信开场白库", {}).keys()))
        
        templates = OPENING_LINES.get("微信开场白库", {}).get(category, [])
        if templates:
            return random.choice(templates)["话术"]
        return "在干嘛呢~"
    
    def get_chat_technique(self, category: str) -> Dict:
        """获取聊天技巧 (从 V20)"""
        techniques = CHAT_ESCALATION.get(category, {})
        if techniques:
            key = random.choice(list(techniques.keys()))
            return {key: techniques[key]}
        return {}
    
    def get_flirty_text(self, category: str = None) -> str:
        """获取调情短信 (从 V21)"""
        if not category:
            category = random.choice(list(FLIRTY_TEXTS.keys()))
        
        texts = FLIRTY_TEXTS.get(category, [])
        if texts:
            return random.choice(texts)
        return "想你啦~"
    
    def get_zodiac_advice(self, sign: str) -> Dict:
        """获取星座建议 (从 V21)"""
        return ZODIAC_TIPS.get(sign, {"error": "未知星座"})
    
    def analyze_girl_interest(self, chat_history: str) -> Dict:
        """分析女生兴趣度"""
        signals_positive = []
        signals_negative = []
        
        if "哈哈" in chat_history or "嘻嘻" in chat_history:
            signals_positive.append("经常笑")
        if "想你" in chat_history:
            signals_positive.append("表达思念")
        if "嗯" in chat_history and chat_history.count("嗯") > 5:
            signals_negative.append("回复敷衍")
        
        score = 50 + len(signals_positive) * 10 - len(signals_negative) * 10
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "level": "高" if score >= 80 else ("中" if score >= 60 else "低"),
            "positive_signals": signals_positive,
            "negative_signals": signals_negative,
            "suggestions": ["继续升温"] if score >= 80 else ["建立吸引力"],
        }
    
    def generate_reply(self, message: str, girl_name: str = None, 
                      context: str = None) -> Dict:
        """生成回复 (整合技巧库 + Viking 上下文)"""
        # 1. 搜索相关上下文
        search_results = self.ctx_manager.search_context(message)
        
        # 2. 搜索相关技巧
        technique_results = self.fs.find_nodes(message, limit=5)
        
        # 3. 基于上下文和技巧生成回复
        reply = self._generate_smart_reply(message, search_results, technique_results)
        
        return {
            "reply": reply,
            "context_used": len(search_results),
            "techniques_used": len(technique_results),
            "session_id": self.ctx_manager.current_session.session_id if self.ctx_manager.current_session else None,
        }
    
    def _generate_smart_reply(self, message: str, context: List[VikingNode], 
                              techniques: List[VikingNode]) -> str:
        """智能生成回复"""
        # 简化版：基于规则生成
        # 实际应该调用大模型
        
        # 检查是否有女生记忆
        girl_memories = [n for n in context if n.metadata.get("type") == "memory"]
        
        if girl_memories:
            # 有记忆，生成个性化回复
            return f"我记得你之前说过类似的话~ 让我想想怎么回复你比较好"
        
        # 默认回复
        return random.choice([
            "在呢在呢，想你啦~",
            "刚忙完，就看到你消息了",
            "你说，我在听~",
            "哈哈，这个有意思",
        ])
    
    def chat(self, message: str, girl_name: str = None) -> Dict:
        """聊天"""
        # 设置当前女生
        if girl_name:
            self.set_current_girl(girl_name)
        
        # 添加用户消息
        self.ctx_manager.add_conversation("user", message, girl_name)
        
        # 生成回复
        result = self.generate_reply(message, girl_name)
        
        # 添加 AI 回复
        self.ctx_manager.add_conversation("assistant", result["reply"], girl_name)
        
        # 添加到记忆
        if girl_name:
            self.add_memory(girl_name, message, tags=[girl_name, "chat"])
        
        return result
    
    def get_trajectory(self) -> Dict:
        """获取检索轨迹"""
        return self.ctx_manager.get_retrieval_trajectory()
    
    def status(self) -> Dict:
        """获取状态"""
        return {
            "storage_path": self.fs.storage_path,
            "total_nodes": len(self.fs.nodes),
            "techniques_v20": len([n for n in self.fs.nodes.values() if n.metadata.get("version") == "20.0"]),
            "techniques_v21": len([n for n in self.fs.nodes.values() if n.metadata.get("version") == "21.0"]),
            "sessions": len(self.ctx_manager.sessions),
            "current_session": self.ctx_manager.current_session.session_id if self.ctx_manager.current_session else None,
        }


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("把妹大师 V23.0 - Viking 终极整合版")
    print("整合 V20/V21 所有技巧 + Viking 上下文管理")
    print("=" * 60)
    
    master = PickupMasterV23()
    
    print("\n【1. 系统状态】")
    status = master.status()
    print(f"  存储路径：{status['storage_path']}")
    print(f"  总节点数：{status['total_nodes']}")
    print(f"  V20 技巧：{status['techniques_v20']} 个")
    print(f"  V21 技巧：{status['techniques_v21']} 个")
    
    print("\n【2. 开始会话】")
    session_id = master.start_session("user_001")
    print(f"  会话 ID: {session_id}")
    
    print("\n【3. 获取开场白 (V20)】")
    for cat in ["好奇类", "赞美类", "关心类"]:
        line = master.get_opening_line(cat)
        print(f"  {cat}: {line}")
    
    print("\n【4. 获取调情短信 (V21)】")
    for cat in ["早安短信", "晚安短信", "甜蜜短信"]:
        text = master.get_flirty_text(cat)
        print(f"  {cat}: {text}")
    
    print("\n【5. 星座建议 (V21)】")
    for sign in ["金牛座", "双子座", "巨蟹座"]:
        advice = master.get_zodiac_advice(sign)
        if "error" not in advice:
            print(f"  {sign}: {advice['特点']}")
    
    print("\n【6. 兴趣度分析】")
    test_chat = "哈哈，想你啦~ 你今天过得怎么样？"
    analysis = master.analyze_girl_interest(test_chat)
    print(f"  聊天内容：{test_chat}")
    print(f"  兴趣度：{analysis['score']}分 ({analysis['level']})")
    print(f"  积极信号：{analysis['positive_signals']}")
    
    print("\n【7. 聊天测试】")
    messages = [
        ("小美", "在干嘛呢"),
        ("小美", "今天好累啊"),
        ("小美", "想你啦"),
    ]
    
    for girl, msg in messages:
        result = master.chat(msg, girl_name=girl)
        print(f"  💬 {girl}: {msg}")
        print(f"  🤖 AI: {result['reply']}")
        print(f"  📊 上下文：{result['context_used']}条 | 技巧：{result['techniques_used']}个")
    
    print("\n【8. 检索轨迹】")
    trajectory = master.get_trajectory()
    print(f"  会话 ID: {trajectory['session_id']}")
    print(f"  访问节点：{len(trajectory['nodes_accessed'])}个")
    
    print("\n" + "=" * 60)
    print("✅ V23.0 所有功能测试完成！")
    print("=" * 60)
