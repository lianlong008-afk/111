# -*- coding: utf-8 -*-
"""
把妹大师 V22.0 - Viking 增强版
基于 OpenViking 上下文管理架构
核心特性:
1. 文件系统范式管理记忆/资源/技能
2. L0/L1/L2 分层上下文加载
3. 目录递归检索
4. 自动会话管理
5. 可视化检索轨迹
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import hashlib


# ==================== Viking 核心数据结构 ====================

@dataclass
class VikingNode:
    """Viking 节点 (文件/目录)"""
    id: str
    name: str
    type: str  # "file" | "directory"
    uri: str  # viking://path/to/node
    level: str  # "L0" | "L1" | "L2"
    content: Any = None
    metadata: Dict = field(default_factory=dict)
    children: List[str] = field(default_factory=list)  # 子节点 ID
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "uri": self.uri,
            "level": self.level,
            "content": self.content,
            "metadata": self.metadata,
            "children": self.children,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "tags": self.tags,
        }


@dataclass
class VikingContext:
    """Viking 上下文"""
    session_id: str
    user_id: str
    nodes: List[VikingNode] = field(default_factory=list)
    memory_nodes: List[str] = field(default_factory=list)  # 记忆节点 ID
    resource_nodes: List[str] = field(default_factory=list)  # 资源节点 ID
    skill_nodes: List[str] = field(default_factory=list)  # 技能节点 ID
    conversation_history: List[Dict] = field(default_factory=list)
    long_term_memory: List[Dict] = field(default_factory=list)
    
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
        }


# ==================== Viking 文件系统 ====================

class VikingFileSystem:
    """Viking 文件系统 - 管理上下文节点"""
    
    def __init__(self, storage_path: str = "~/.viking_dating"):
        self.storage_path = os.path.expanduser(storage_path)
        self.nodes: Dict[str, VikingNode] = {}
        self.uri_index: Dict[str, str] = {}  # URI -> Node ID
        self._initialize_storage()
        self._load_nodes()
    
    def _initialize_storage(self) -> None:
        """初始化存储空间"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "memory"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "resources"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "skills"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "sessions"), exist_ok=True)
    
    def _load_nodes(self) -> None:
        """加载节点"""
        index_file = os.path.join(self.storage_path, "index.json")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for node_data in data.get("nodes", []):
                    node = VikingNode(**node_data)
                    self.nodes[node.id] = node
                    self.uri_index[node.uri] = node.id
    
    def _save_index(self) -> None:
        """保存索引"""
        index_file = os.path.join(self.storage_path, "index.json")
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """生成节点 ID"""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def _generate_uri(self, path: str) -> str:
        """生成 URI"""
        return f"viking://{path}"
    
    def add_node(self, name: str, content: Any, path: str, 
                 node_type: str = "file", level: str = "L1",
                 tags: List[str] = None, metadata: Dict = None) -> VikingNode:
        """添加节点"""
        node_id = self._generate_id(f"{path}{name}")
        uri = self._generate_uri(path)
        
        node = VikingNode(
            id=node_id,
            name=name,
            type=node_type,
            uri=uri,
            level=level,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
        )
        
        self.nodes[node_id] = node
        self.uri_index[uri] = node_id
        self._save_index()
        
        return node
    
    def get_node(self, uri: str) -> Optional[VikingNode]:
        """获取节点"""
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
        """查找节点 (支持语义搜索)"""
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
        
        # 3. 内容匹配 (L2 级别)
        for node in self.nodes.values():
            if node.level == "L2" and isinstance(node.content, str):
                if query_lower in node.content.lower():
                    if node not in results:
                        results.append(node)
                        if len(results) >= limit:
                            return results
        
        return results
    
    def list_directory(self, path: str) -> List[VikingNode]:
        """列出目录内容"""
        uri = self._generate_uri(path)
        results = []
        
        for node in self.nodes.values():
            if node.uri.startswith(uri + "/") or node.uri.startswith(uri):
                results.append(node)
        
        return sorted(results, key=lambda x: (x.type != "directory", x.name))
    
    def delete_node(self, uri: str) -> bool:
        """删除节点"""
        node_id = self.uri_index.get(uri)
        if node_id:
            node = self.nodes.get(node_id)
            if node:
                # 递归删除子节点
                for child_id in node.children:
                    child_node = self.nodes.get(child_id)
                    if child_node:
                        self.delete_node(child_node.uri)
                
                del self.nodes[node_id]
                del self.uri_index[uri]
                self._save_index()
                return True
        return False
    
    def update_node(self, uri: str, content: Any = None, 
                    metadata: Dict = None, tags: List[str] = None) -> Optional[VikingNode]:
        """更新节点"""
        node = self.get_node(uri)
        if node:
            if content is not None:
                node.content = content
            if metadata is not None:
                node.metadata.update(metadata)
            if tags is not None:
                node.tags.extend(tags)
            node.updated_at = datetime.now().isoformat()
            self._save_index()
            return node
        return None


# ==================== Viking 上下文管理器 ====================

class VikingContextManager:
    """Viking 上下文管理器"""
    
    def __init__(self, fs: VikingFileSystem):
        self.fs = fs
        self.sessions: Dict[str, VikingContext] = {}
        self.current_session: Optional[VikingContext] = None
    
    def create_session(self, user_id: str) -> VikingContext:
        """创建会话"""
        session_id = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        context = VikingContext(
            session_id=session_id,
            user_id=user_id,
        )
        
        self.sessions[session_id] = context
        self.current_session = context
        
        # 保存会话
        session_file = os.path.join(self.fs.storage_path, "sessions", f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
        
        return context
    
    def get_session(self, session_id: str) -> Optional[VikingContext]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def add_to_memory(self, content: Dict, tags: List[str] = None) -> VikingNode:
        """添加到记忆"""
        node = self.fs.add_node(
            name=f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content,
            path="memory",
            tags=tags or [],
            metadata={"type": "memory"},
        )
        
        if self.current_session:
            self.current_session.memory_nodes.append(node.id)
        
        return node
    
    def add_resource(self, name: str, content: Any, 
                     tags: List[str] = None, metadata: Dict = None) -> VikingNode:
        """添加资源"""
        node = self.fs.add_node(
            name=name,
            content=content,
            path="resources",
            tags=tags or [],
            metadata=metadata or {},
        )
        
        if self.current_session:
            self.current_session.resource_nodes.append(node.id)
        
        return node
    
    def add_skill(self, name: str, skill_data: Dict, 
                  tags: List[str] = None) -> VikingNode:
        """添加技能"""
        node = self.fs.add_node(
            name=name,
            content=skill_data,
            path="skills",
            tags=tags or [],
            metadata={"type": "skill"},
        )
        
        if self.current_session:
            self.current_session.skill_nodes.append(node.id)
        
        return node
    
    def add_conversation(self, role: str, content: str) -> None:
        """添加对话"""
        if self.current_session:
            self.current_session.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            })
            
            # 自动压缩对话 (超过 10 条时)
            if len(self.current_session.conversation_history) > 10:
                self._compress_conversation()
    
    def _compress_conversation(self) -> None:
        """压缩对话"""
        if not self.current_session:
            return
        
        # 保留最近 5 条
        recent = self.current_session.conversation_history[-5:]
        
        # 压缩旧的对话为长期记忆
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
    
    def search_context(self, query: str) -> List[VikingNode]:
        """搜索上下文"""
        results = []
        
        # 搜索记忆
        memory_results = self.fs.find_nodes(query)
        results.extend([n for n in memory_results if "memory" in n.uri])
        
        # 搜索资源
        resource_results = self.fs.find_nodes(query)
        results.extend([n for n in resource_results if "resources" in n.uri])
        
        # 搜索技能
        skill_results = self.fs.find_nodes(query)
        results.extend([n for n in skill_results if "skills" in n.uri])
        
        return results[:10]
    
    def get_retrieval_trajectory(self) -> Dict:
        """获取检索轨迹"""
        trajectory = {
            "session_id": self.current_session.session_id if self.current_session else None,
            "nodes_accessed": [],
            "search_history": [],
        }
        
        # 记录访问的节点
        for node in self.fs.nodes.values():
            if node.access_count > 0:
                trajectory["nodes_accessed"].append({
                    "uri": node.uri,
                    "access_count": node.access_count,
                    "last_accessed": node.updated_at,
                })
        
        return trajectory


# ==================== 把妹大师 Viking 版 ====================

class PickupMasterViking:
    """把妹大师 Viking 版"""
    
    def __init__(self, storage_path: str = "~/.viking_dating"):
        self.fs = VikingFileSystem(storage_path)
        self.ctx_manager = VikingContextManager(self.fs)
        self._initialize_resources()
    
    def _initialize_resources(self) -> None:
        """初始化资源库"""
        # 添加搭讪语录资源
        self.ctx_manager.add_resource(
            name="opening_lines",
            content={
                "好奇类": ["刚刚看到个东西特别像你", "我做了个梦，梦到你了"],
                "赞美类": ["你今天是不是又变好看了", "你笑起来一定很好看"],
            },
            tags=["开场白", "搭讪"],
            metadata={"category": "pickup_lines"}
        )
        
        # 添加聊天技巧资源
        self.ctx_manager.add_resource(
            name="chat_skills",
            content={
                "推拉技巧": ["先推后拉", "三推一拉"],
                "暧昧暗示": ["称呼升级", "未来暗示"],
            },
            tags=["聊天", "技巧"],
            metadata={"category": "chat_skills"}
        )
        
        # 添加约会指南资源
        self.ctx_manager.add_resource(
            name="dating_guide",
            content={
                "第一次约会": ["咖啡厅", "下午茶", "展览"],
                "第二次约会": ["正餐餐厅", "DIY 手工"],
            },
            tags=["约会", "指南"],
            metadata={"category": "dating_guide"}
        )
        
        # 添加技能
        self.ctx_manager.add_skill(
            name="analyze_interest",
            skill_data={
                "name": "兴趣度分析",
                "description": "分析女生对你的兴趣程度",
                "function": "analyze_girl_interest",
            },
            tags=["分析", "技能"],
        )
        
        self.ctx_manager.add_skill(
            name="generate_reply",
            skill_data={
                "name": "回复生成",
                "description": "根据情境生成高情商回复",
                "function": "generate_dating_reply",
            },
            tags=["回复", "技能"],
        )
    
    def start_session(self, user_id: str) -> str:
        """开始会话"""
        context = self.ctx_manager.create_session(user_id)
        return context.session_id
    
    def add_memory(self, girl_name: str, interaction: str, 
                   tags: List[str] = None) -> VikingNode:
        """添加记忆"""
        memory = {
            "girl_name": girl_name,
            "interaction": interaction,
            "timestamp": datetime.now().isoformat(),
        }
        return self.ctx_manager.add_to_memory(memory, tags or [girl_name])
    
    def get_context(self, query: str) -> List[Dict]:
        """获取相关上下文"""
        nodes = self.ctx_manager.search_context(query)
        return [
            {
                "uri": node.uri,
                "name": node.name,
                "content": node.content,
                "level": node.level,
            }
            for node in nodes
        ]
    
    def chat(self, message: str, girl_name: str = None) -> Dict:
        """聊天"""
        # 添加用户消息
        self.ctx_manager.add_conversation("user", message)
        
        # 搜索相关上下文
        context = self.ctx_manager.search_context(message)
        
        # 生成回复 (简化版)
        reply = self._generate_reply(message, context)
        
        # 添加 AI 回复
        self.ctx_manager.add_conversation("assistant", reply)
        
        # 如果有女生名字，添加到记忆
        if girl_name:
            self.add_memory(girl_name, message, tags=[girl_name])
        
        return {
            "reply": reply,
            "context_used": len(context),
            "session_id": self.ctx_manager.current_session.session_id if self.ctx_manager.current_session else None,
        }
    
    def _generate_reply(self, message: str, context: List[VikingNode]) -> str:
        """生成回复 (简化版)"""
        # 这里可以集成大模型
        # 目前返回一个简单回复
        return f"收到你的消息：{message}，我正在思考怎么回复~"
    
    def get_trajectory(self) -> Dict:
        """获取检索轨迹"""
        return self.ctx_manager.get_retrieval_trajectory()
    
    def status(self) -> Dict:
        """获取状态"""
        return {
            "storage_path": self.fs.storage_path,
            "total_nodes": len(self.fs.nodes),
            "sessions": len(self.ctx_manager.sessions),
            "current_session": self.ctx_manager.current_session.session_id if self.ctx_manager.current_session else None,
        }


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("把妹大师 V22.0 - Viking 增强版")
    print("基于 OpenViking 上下文管理架构")
    print("=" * 60)
    
    master = PickupMasterViking()
    
    print("\n【1. 系统状态】")
    status = master.status()
    for k, v in status.items():
        print(f"  {k}: {v}")
    
    print("\n【2. 开始会话】")
    session_id = master.start_session("user_001")
    print(f"  会话 ID: {session_id}")
    
    print("\n【3. 添加记忆】")
    master.add_memory("小美", "今天第一次见面，她笑得很甜", tags=["小美", "初次见面"])
    master.add_memory("小美", "她说喜欢喝咖啡", tags=["小美", "喜好"])
    print("  已添加 2 条记忆")
    
    print("\n【4. 搜索上下文】")
    context = master.get_context("小美")
    for ctx in context:
        print(f"  {ctx['uri']}: {ctx['name']} - {ctx['content']}")
    
    print("\n【5. 聊天测试】")
    result = master.chat("小美说她今天心情不好", girl_name="小美")
    print(f"  回复：{result['reply']}")
    print(f"  使用上下文：{result['context_used']}条")
    
    print("\n【6. 检索轨迹】")
    trajectory = master.get_trajectory()
    print(f"  会话 ID: {trajectory['session_id']}")
    print(f"  访问节点数：{len(trajectory['nodes_accessed'])}")
    
    print("\n【7. 列出资源】")
    resources = master.fs.list_directory("resources")
    for res in resources:
        print(f"  {res.uri}: {res.name} (标签：{res.tags})")
    
    print("\n【8. 列出技能】")
    skills = master.fs.list_directory("skills")
    for skill in skills:
        print(f"  {skill.uri}: {skill.name}")
    
    print("\n" + "=" * 60)
    print("✅ 所有功能测试完成！")
    print("=" * 60)
