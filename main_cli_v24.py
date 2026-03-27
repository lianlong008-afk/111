#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V24.0 - Viking 大模型版 - 命令行交互版
"""

from pickup_master_v24 import PickupMasterV24, CONFIG, save_config, API_KEY
import sys


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_menu():
    """打印菜单"""
    print("""
📋 主菜单:

  1. 💬 开始聊天 (AI 生成)
  2. 👧 切换女生
  3. 🛠️ 快捷工具
  4. 📊 查看状态
  5. ⚙️  配置 API Key
  6. ❓ 帮助
  0. 🚪 退出

""")


def print_tools_menu():
    """工具菜单"""
    print("""
🛠️ 快捷工具:

  1. ⭐ 兴趣度分析
  2. 📝 查看记忆
  3. 🗑️ 清空记忆
  0. 返回主菜单

""")


def main():
    """主函数"""
    print_header("💘 把妹大师 V24.0 - Viking 大模型版")
    print("  命令行交互版")
    print("=" * 60)
    
    # 检查 API Key
    if not API_KEY:
        print("\n⚠️  警告：API Key 未配置")
        print("请先配置 API Key (选项 5)")
    else:
        print(f"\n✅ API Key 已配置 ({API_KEY[:10]}...)")
    
    # 初始化引擎
    print("\n🔄 正在初始化引擎...")
    try:
        master = PickupMasterV24()
        session_id = master.start_session("cli_user")
        print("✅ 引擎初始化完成")
        print(f"   会话 ID: {session_id}")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        input("按回车退出...")
        return
    
    # 状态
    current_girl = None
    current_relation = "恋人"
    
    # 主循环
    while True:
        print_menu()
        choice = input("请选择 (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 再见！祝你撩妹成功！")
            break
        
        elif choice == "1":
            # 聊天
            girl_name = input("\n👧 女生名字：").strip()
            if not girl_name:
                if current_girl:
                    girl_name = current_girl
                else:
                    print("❌ 请先设置女生名字")
                    continue
            
            current_girl = girl_name
            
            # 关系选择
            relation = input("关系 (恋人/朋友/同事/客户/家人/追求者/海王/高冷) [恋人]: ").strip()
            if relation:
                current_relation = relation
            
            message = input("💬 对方消息：").strip()
            
            if message:
                print("\n🤖 AI 正在生成回复...")
                result = master.chat(message, girl_name=girl_name, relation=current_relation)
                print(f"\n💡 建议回复：{result['reply']}")
                print(f"\n其他选项:")
                for i, opt in enumerate(result['options'][1:], 2):
                    print(f"   {i}. {opt}")
                print(f"\n📊 使用记忆：{result['context_used']}条 | {result['info']}")
        
        elif choice == "2":
            # 切换女生
            girl_name = input("\n👧 女生名字：").strip()
            if girl_name:
                current_girl = girl_name
                master.set_current_girl(girl_name)
                print(f"✅ 已切换到：{girl_name}")
        
        elif choice == "3":
            # 工具菜单
            while True:
                print_tools_menu()
                tool_choice = input("请选择 (0-3): ").strip()
                
                if tool_choice == "0":
                    break
                
                elif tool_choice == "1":
                    # 兴趣度分析
                    chat = input("   聊天记录：").strip()
                    if chat:
                        analysis = master.analyze_interest(chat)
                        print(f"\n📊 兴趣度：{analysis['score']}分 ({analysis['level']})")
                        print(f"   积极信号：{', '.join(analysis['positive_signals'])}")
                        print(f"   消极信号：{', '.join(analysis['negative_signals'])}")
                        print(f"   建议：{analysis['suggestions'][0]}")
                
                elif tool_choice == "2":
                    # 查看记忆
                    context = master.get_context()
                    memories = context.get("memories", [])
                    if memories:
                        print(f"\n📝 记忆列表 ({len(memories)}条):")
                        for mem in memories[-10:]:
                            print(f"   - {mem['content']}")
                    else:
                        print("\n暂无记忆")
                
                elif tool_choice == "3":
                    # 清空记忆
                    confirm = input("   确定清空记忆？(y/n): ").strip().lower()
                    if confirm == "y":
                        master.ctx_manager.current_session.memories = []
                        print("   ✅ 记忆已清空")
        
        elif choice == "4":
            # 状态
            status = master.get_status()
            print("\n📊 系统状态:")
            print(f"   API Key: {'已配置' if status['api_key_configured'] else '未配置'}")
            print(f"   模型：{status['model']}")
            print(f"   会话数：{status['sessions']}")
            print(f"   当前会话：{status['current_session']}")
            if current_girl:
                print(f"   当前女生：{current_girl}")
                print(f"   关系：{current_relation}")
        
        elif choice == "5":
            # 配置 API Key
            print("\n⚙️  配置 API Key")
            print(f"当前：{API_KEY[:10]}..." if API_KEY else "当前：未配置")
            
            new_key = input("新的 API Key (留空不变): ").strip()
            if new_key:
                CONFIG["api_key"] = new_key
                save_config(CONFIG)
                print("✅ API Key 已保存")
                print("请重启程序以应用新配置")
                return
        
        elif choice == "6":
            # 帮助
            print("""
❓ 使用帮助:

1. 配置 API Key
   - 首次使用请先配置 (选项 5)
   - MiniMax API Key

2. 开始聊天
   - 输入女生名字
   - 选择关系类型
   - 输入对方消息
   - AI 自动生成 3 条回复

3. 快捷工具
   - 兴趣度：分析聊天记录
   - 查看记忆：当前女生的所有记忆
   - 清空记忆：重置记忆

4. Viking 特性
   - 自动记忆每次对话
   - 基于上下文生成回复
   - 长期记忆积累

💡 提示
   - 记忆越多，回复越精准
   - 可以切换不同女生聊天
   - 每个女生独立记忆

""")
            input("按回车继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序中断，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
