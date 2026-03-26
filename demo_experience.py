#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V22.0 - Viking 增强版 - 交互体验程序
"""

from pickup_master_v22_viking import PickupMasterViking
import time


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_step(step: int, text: str):
    """打印步骤"""
    print(f"\n【步骤 {step}】{text}")
    print("-" * 40)


def main():
    """主体验程序"""
    print_header("🎯 把妹大师 V22.0 - Viking 增强版 交互体验")
    print("基于 OpenViking 上下文管理架构")
    print("让你体验智能化管理撩妹记忆和上下文！")
    
    # 初始化
    print_step(1, "初始化系统")
    master = PickupMasterViking()
    print("✅ 系统初始化完成")
    print(f"   存储路径：{master.fs.storage_path}")
    print(f"   预置资源：{len(master.fs.nodes)} 个")
    
    # 开始会话
    print_step(2, "开始会话")
    user_id = "demo_user"
    session_id = master.start_session(user_id)
    print(f"✅ 会话已创建")
    print(f"   会话 ID: {session_id}")
    
    # 添加记忆
    print_step(3, "添加记忆 - 认识小美")
    memories = [
        ("小美", "今天第一次见面，她笑得很甜，眼睛弯弯的", ["小美", "初次见面", "外貌"]),
        ("小美", "她说喜欢喝咖啡，特别是拿铁", ["小美", "喜好", "咖啡"]),
        ("小美", "她在互联网公司做产品经理", ["小美", "工作", "产品经理"]),
        ("小美", "她养了一只猫，叫奶茶", ["小美", "宠物", "猫"]),
        ("小美", "她周末喜欢去看展览和电影", ["小美", "爱好", "展览", "电影"]),
    ]
    
    for girl_name, interaction, tags in memories:
        master.add_memory(girl_name, interaction, tags)
        print(f"   ✅ 添加记忆：{interaction[:20]}...")
        time.sleep(0.3)
    
    # 查看系统状态
    print_step(4, "查看系统状态")
    status = master.status()
    print(f"   存储路径：{status['storage_path']}")
    print(f"   总节点数：{status['total_nodes']}")
    print(f"   会话数：{status['sessions']}")
    print(f"   当前会话：{status['current_session']}")
    
    # 搜索上下文
    print_step(5, "搜索上下文 - 小美的喜好")
    context = master.get_context("小美 喜好")
    print(f"   找到 {len(context)} 条相关信息:")
    for i, ctx in enumerate(context, 1):
        content = ctx['content']
        if isinstance(content, dict):
            print(f"   {i}. {ctx['name']}: {content.get('interaction', '')[:40]}...")
        else:
            print(f"   {i}. {ctx['name']}: {str(content)[:40]}...")
    
    # 列出所有资源
    print_step(6, "查看资源库")
    resources = master.fs.list_directory("resources")
    print(f"   资源库内容:")
    for res in resources:
        print(f"   - {res.name}")
        print(f"     URI: {res.uri}")
        print(f"     标签：{', '.join(res.tags)}")
        if isinstance(res.content, dict):
            print(f"     内容预览：{list(res.content.keys())}")
        print()
    
    # 列出技能
    print_step(7, "查看技能库")
    skills = master.fs.list_directory("skills")
    print(f"   可用技能:")
    for skill in skills:
        print(f"   - {skill.name}")
        print(f"     URI: {skill.uri}")
        if isinstance(skill.content, dict):
            print(f"     描述：{skill.content.get('description', '')}")
        print()
    
    # 聊天测试
    print_step(8, "聊天测试 - 模拟真实对话")
    
    chat_scenarios = [
        ("小美说她今天心情不好", "小美"),
        ("我想约小美周末出来", "小美"),
        ("小美说她喜欢喝拿铁", "小美"),
        ("小美的猫叫什么名字", "小美"),
    ]
    
    for message, girl_name in chat_scenarios:
        print(f"\n   💬 你：{message}")
        result = master.chat(message, girl_name=girl_name)
        print(f"   🤖 AI: {result['reply']}")
        print(f"   📊 使用上下文：{result['context_used']}条")
        time.sleep(0.5)
    
    # 查看检索轨迹
    print_step(9, "查看检索轨迹")
    trajectory = master.get_trajectory()
    print(f"   会话 ID: {trajectory['session_id']}")
    print(f"   访问节点数：{len(trajectory['nodes_accessed'])}")
    if trajectory['nodes_accessed']:
        print(f"   访问的节点:")
        for node in trajectory['nodes_accessed'][:5]:
            print(f"     - {node['uri']} (访问{node['access_count']}次)")
    
    # 查看长期记忆
    print_step(10, "查看长期记忆")
    if master.ctx_manager.current_session:
        long_term_mem = master.ctx_manager.current_session.long_term_memory
        print(f"   长期记忆数：{len(long_term_mem)}")
        for mem in long_term_mem:
            if isinstance(mem, dict):
                print(f"   - {mem.get('summary', '')}")
    
    # 查看对话历史
    print_step(11, "查看对话历史")
    if master.ctx_manager.current_session:
        history = master.ctx_manager.current_session.conversation_history
        print(f"   对话轮数：{len(history)}")
        for conv in history[-5:]:  # 显示最近 5 条
            role = "💬 你" if conv['role'] == 'user' else "🤖 AI"
            content = conv['content'][:50]
            print(f"   {role}: {content}...")
    
    # 添加更多记忆 (模拟多女生场景)
    print_step(12, "多女生场景测试 - 添加小丽的记忆")
    girl2_memories = [
        ("小丽", "在健身房认识的，她身材很好", ["小丽", "初次见面", "健身"]),
        ("小丽", "她是健身教练，很专业", ["小丽", "工作", "健身教练"]),
        ("小丽", "她喜欢吃健康餐", ["小丽", "喜好", "健康餐"]),
    ]
    
    for girl_name, interaction, tags in girl2_memories:
        master.add_memory(girl_name, interaction, tags)
        print(f"   ✅ 添加记忆：{girl_name} - {interaction[:20]}...")
    
    # 搜索小丽的信息
    print_step(13, "搜索小丽的上下文")
    context = master.get_context("小丽")
    print(f"   找到 {len(context)} 条关于小丽的信息:")
    for ctx in context:
        content = ctx['content']
        if isinstance(content, dict):
            print(f"   - {content.get('interaction', '')[:40]}...")
    
    # 最终状态
    print_step(14, "最终系统状态")
    status = master.status()
    print(f"   总节点数：{status['total_nodes']}")
    print(f"   会话数：{status['sessions']}")
    print(f"   当前会话：{status['current_session']}")
    
    # 体验总结
    print_header("✅ 体验完成！")
    print("""
📊 体验总结:

1. ✅ 文件系统管理
   - 使用 viking:// 协议统一管理记忆/资源/技能
   - memory/ resources/ skills/ sessions/ 分类清晰

2. ✅ 分层上下文加载
   - L0/L1/L2 三层结构，按需加载
   - 快速检索 + 深度阅读结合

3. ✅ 目录递归检索
   - 支持标签/名称/内容多维度搜索
   - 精确获取相关上下文

4. ✅ 自动会话管理
   - 自动压缩对话内容
   - 提取长期记忆
   - 上下文自迭代

5. ✅ 可视化检索轨迹
   - 记录节点访问历史
   - 清晰观察检索过程

6. ✅ 多女生场景支持
   - 同时管理多个女生的记忆
   - 会话不混乱，信息不串场

🎯 核心优势:
- 记住每个女生的所有细节
- 根据上下文生成个性化回复
- 长期记忆积累，越聊越了解她
- 多女生同时聊天不混乱

📁 数据存储位置:
   {storage_path}

🔗 GitHub:
   https://github.com/lianlong008-afk/111/tree/optimize-v8.2
    """.format(storage_path=master.fs.storage_path))
    
    print_header("感谢体验！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 体验中断，再见！")
    except Exception as e:
        print(f"\n\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
