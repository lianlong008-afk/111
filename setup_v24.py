#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把妹大师 V24.0 - API Key 配置工具
"""

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": "", "model": "MiniMax-M2.7"}


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    print("=" * 60)
    print("⚙️  把妹大师 V24.0 - API Key 配置")
    print("=" * 60)
    
    config = load_config()
    
    print(f"\n当前配置:")
    print(f"  API Key: {config['api_key'][:10]}..." if config['api_key'] else "  API Key: 未配置")
    print(f"  模型：{config.get('model', 'MiniMax-M2.7')}")
    
    print("\n" + "-" * 60)
    print("获取 API Key:")
    print("1. 访问 MiniMax 开放平台：https://platform.minimaxi.com/")
    print("2. 注册/登录账号")
    print("3. 进入 API Key 管理页面")
    print("4. 创建新的 API Key")
    print("5. 复制 Key 并粘贴到下方")
    print("-" * 60)
    
    new_key = input("\n输入新的 API Key (留空保持不变): ").strip()
    
    if new_key:
        config["api_key"] = new_key
        
        # 模型选择
        print("\n选择模型:")
        print("1. MiniMax-M2.7 (推荐)")
        print("2. MiniMax-M2.5")
        model_choice = input("请选择 (1/2) [1]: ").strip()
        
        if model_choice == "2":
            config["model"] = "MiniMax-M2.5"
        else:
            config["model"] = "MiniMax-M2.7"
        
        save_config(config)
        print("\n✅ 配置已保存!")
        print(f"   API Key: {new_key[:10]}...")
        print(f"   模型：{config['model']}")
    else:
        print("\nℹ️  配置未更改")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
