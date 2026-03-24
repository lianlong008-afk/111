# 微信高情商回复助手 V8.2

一款基于 AI 的微信高情商回复辅助工具，支持智能生成回复、好友画像分析、聊天记录分析等功能。

## 功能特性

- **AI 智能回复**：基于 MiniMax API 生成高情商回复
- **本地+AI 混合模式**：无需 API Key 也能生成回复
- **好友画像分析**：AI 分析好友性格特点
- **多种关系模式**：恋人、朋友、同事、客户、家人、追求者、海王、高冷
- **三种回复风格**：稳妥版、轻松版、升温版
- **对话历史保存**：自动保存聊天记录
- **快捷短语库**：收藏常用回复
- **截图 OCR**：识别图片中的文字

## 环境要求

- Python 3.8+
- Windows 操作系统
- MiniMax API Key（可选，用于 AI 回复功能）

## 快速开始

1. 双击 `启动 V8.bat` 启动程序
2. 首次使用需要设置 MiniMax API Key（在设置中配置）
3. 添加好友，选择关系类型
4. 输入对方消息，点击生成回复

## 目录结构

```
wechat-reply-assistant/
├── main_v8.py          # 主程序
├── reply_engine_v81.py # 回复引擎
├── config.json         # 配置文件（不提交）
├── friends.json        # 好友数据（不提交）
├── 启动 V8.bat         # 启动脚本
└── README.md           # 说明文档
```

## 配置 API Key

1. 点击界面上的「⚙️ 设置」
2. 输入 MiniMax API Key
3. 保存即可

## V8.2 优化说明

### Bug 修复
- ✅ 修复 `reply_engine_v81.py` 中 `generate()` 方法返回语句截断问题
- ✅ 修复 `main_v8.py` 中 `show_replies()` 中 `btn` 变量未定义问题
- ✅ 修复全局配置加载时机问题，使用配置管理器统一管理

### 代码优化
- ✅ 添加完整的类型注解（typing）
- ✅ 使用 dataclass 替代字典存储配置（AppConfig、FriendData）
- ✅ 重构配置管理为 ConfigManager 类
- ✅ 重构好友管理为 FriendManager 类
- ✅ 提取常量为模块级常量（RELATIONS、THEMES、TONE_GUIDES 等）
- ✅ 删除重复代码（_parse_ai_replies 和 _parse_ai_response 合并）
- ✅ 优化长函数，拆分为多个小函数（_setup_ui 拆分为多个子方法）
- ✅ 改进错误处理，统一异常处理策略
- ✅ 优化导入结构，使用 ReplyEngineV82

### 代码质量提升
- ✅ 所有公共方法添加类型注解
- ✅ 使用 docstring 说明类和方法功能
- ✅ 常量使用大写命名
- ✅ 私有方法使用下划线前缀
- ✅ 消除魔法数字，使用具名常量

## 免责声明

本工具仅供学习和娱乐使用，请勿用于任何商业或不当用途。
