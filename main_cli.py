#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V23.0 - Viking 终极版 - 命令行交互版
无需 GUI，终端即可使用
"""

from pickup_master_v23_ultimate import PickupMasterV23
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

  1. 💬 开始聊天
  2. 👧 切换女生
  3. 🛠️ 快捷工具
  4. 📊 查看状态
  5. ❓ 帮助
  0. 🚪 退出

""")


def print_tools_menu():
    """工具菜单"""
    print("""
🛠️ 快捷工具:

  1. 💬 生成开场白
  2. 💕 生成调情短信
  3. ⭐ 兴趣度分析
  4. ♈ 星座建议
  0. 返回主菜单

""")


def main():
    """主函数"""
    print_header("💘 把妹大师 V23.0 - Viking 终极版")
    print("  命令行交互模式")
    print("=" * 60)
    
    # 初始化引擎
    print("\n🔄 正在初始化引擎...")
    try:
        master = PickupMasterV23()
        session_id = master.start_session("cli_user")
        print("✅ 引擎初始化完成")
        print(f"   会话 ID: {session_id}")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        input("按回车退出...")
        return
    
    # 状态
    current_girl = None
    
    # 主循环
    while True:
        print_menu()
        choice = input("请选择 (0-5): ").strip()
        
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
            message = input("💬 对方消息：").strip()
            
            if message:
                print("\n🤖 正在生成回复...")
                result = master.chat(message, girl_name=girl_name)
                print(f"\n💡 建议回复：{result['reply']}")
                print(f"   使用上下文：{result.get('context_used', 0)}条")
                print(f"   使用技巧：{result.get('techniques_used', 0)}个")
        
        elif choice == "2":
            # 切换女生
            girl_name = input("\n👧 女生名字：").strip()
            if girl_name:
                current_girl = girl_name
                print(f"✅ 已切换到：{girl_name}")
        
        elif choice == "3":
            # 工具菜单
            while True:
                print_tools_menu()
                tool_choice = input("请选择 (0-4): ").strip()
                
                if tool_choice == "0":
                    break
                
                elif tool_choice == "1":
                    # 开场白
                    category = input("   类别 (好奇/赞美/关心/分享/直球，留空随机): ").strip()
                    if category:
                        opener = master.get_opening_line(category + "类")
                    else:
                        opener = master.get_opening_line()
                    print(f"\n💬 开场白：{opener}")
                
                elif tool_choice == "2":
                    # 调情短信
                    category = input("   类别 (早安/晚安/甜蜜/调情/关心，留空随机): ").strip()
                    if category:
                        text = master.get_flirty_text(category + "短信")
                    else:
                        text = master.get_flirty_text()
                    print(f"\n💕 调情短信：{text}")
                
                elif tool_choice == "3":
                    # 兴趣度分析
                    chat = input("   聊天记录：").strip()
                    if chat:
                        analysis = master.analyze_girl_interest(chat)
                        print(f"\n📊 兴趣度：{analysis['score']}分 ({analysis['level']})")
                        print(f"   积极信号：{', '.join(analysis['positive_signals'])}")
                        print(f"   消极信号：{', '.join(analysis['negative_signals'])}")
                        print(f"   建议：{analysis['suggestions'][0]}")
                
                elif tool_choice == "4":
                    # 星座
                    sign = input("   星座 (金牛/双子/巨蟹...): ").strip()
                    if sign:
                        advice = master.get_zodiac_advice(sign + "座")
                        if "error" not in advice:
                            print(f"\n♈ {sign}座特点：{advice['特点']}")
                            print(f"   追求技巧：{', '.join(advice['追求技巧'][:3])}")
                            print(f"   禁忌：{', '.join(advice['禁忌'][:3])}")
        
        elif choice == "4":
            # 状态
            status = master.status()
            print("\n📊 系统状态:")
            print(f"   存储路径：{status['storage_path']}")
            print(f"   总节点数：{status['total_nodes']}")
            print(f"   V20 技巧：{status['techniques_v20']}个")
            print(f"   V21 技巧：{status['techniques_v21']}个")
            print(f"   当前会话：{status['current_session']}")
            if current_girl:
                print(f"   当前女生：{current_girl}")
        
        elif choice == "5":
            # 帮助
            print("""
❓ 使用帮助:

1. 开始聊天
   - 输入女生名字
   - 输入对方的消息
   - 获取智能回复建议

2. 切换女生
   - 支持多女生管理
   - 每个女生独立记忆

3. 快捷工具
   - 开场白：生成高质量开场
   - 调情短信：甜蜜撩妹
   - 兴趣度：分析她对你的感觉
   - 星座：查看星座特点

4. 技巧库
   - V20: 10000+ 专业把妹技巧
   - V21: 全球技巧 + 星座指南
   - V22: Viking 上下文管理

💡 提示
   - 多使用工具获取灵感
   - 定期查看兴趣度
   - 根据星座调整策略

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
