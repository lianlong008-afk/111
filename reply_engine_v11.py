# -*- coding: utf-8 -*-
"""
高情商回复助手 V11.0 - 大模型专用 Prompt 工程
核心：严格控制大模型输出，只返回 3 条纯回复
"""

import json
import re
from typing import List, Tuple, Optional


# ==================== System Prompt - 核心控制 ====================

SYSTEM_PROMPT = """你是微信高情商聊天专家。

【输出规则】
1. 只输出 3 条回复，每行一条
2. 每条回复 8-20 字
3. 不要编号、不要引号、不要任何其他内容
4. 不要解释、不要分析、不要思考过程
5. 只用中文，符合微信聊天习惯

【错误示例 - 不要这样输出】
```
让我想想...
1. 你好啊
2. 在干嘛
3. 吃了吗
```

【正确示例 - 要这样输出】
```
在呢在呢，想你啦~
在发呆，你呢？
刚忙完，正想找你！
```

【关系语气指导】
- 恋人：甜蜜亲密，可以用宝贝/亲爱的/么么哒
- 朋友：轻松随意，可以调侃开玩笑
- 同事：专业礼貌，保持适当距离
- 客户：商务专业，热情但不卑微
- 家人：温暖关心，听话懂事
- 追求者：友好但保持距离
- 海王：若即若离，不要太主动
- 高冷：简洁冷淡，不延伸话题

【回复原则】
1. 先共情再回应 - 识别对方情绪
2. 符合关系身份 - 什么关系说什么话
3. 留有话题空间 - 让对方能继续聊
4. 避免查户口 - 不要连续提问
5. 真诚第一 - 不要套路感

【当前任务】
根据对话历史和对方消息，生成 3 条高情商回复。
"""


# ==================== Few-Shot 示例库 ====================

FEW_SHOT_EXAMPLES = {
    "恋人": [
        {
            "history": "TA: 在吗\n我：终于找我啦~\nTA: 干嘛呢",
            "replies": "在等你找我呀！\n在想你呢~\n在看我们的聊天记录！"
        },
        {
            "history": "TA: 想你了\n我：我也想你\nTA: 有多想",
            "replies": "超级无敌螺旋想！\n想你想得睡不着\n想立刻见到你！"
        },
        {
            "history": "TA: 我感冒了\n我：心疼死我了\nTA: 好难受",
            "replies": "抱抱我的宝贝\n吃药了吗乖乖\n我来照顾你好不好"
        },
    ],
    "朋友": [
        {
            "history": "TA: 在吗\n我：在在在\nTA: 出来玩吗",
            "replies": "走走走！\n去哪玩？\n约约约！"
        },
        {
            "history": "TA: 我脱单了\n我：？？？\nTA: 哈哈",
            "replies": "可以啊你！\n恭喜恭喜！\n什么时候请客？"
        },
        {
            "history": "TA: 不想上班\n我：哈哈我也\nTA: 好累",
            "replies": "理解理解\n摸鱼吧兄弟\n周末出来喝一杯？"
        },
    ],
    "同事": [
        {
            "history": "TA: 在吗\n我：在的请说\nTA: 这个文件能帮我看看吗",
            "replies": "好的发我\n稍等我看下\n没问题发我吧"
        },
        {
            "history": "TA: 谢谢帮忙\n我：不客气\nTA: 改天请你吃饭",
            "replies": "哈哈好的\n应该的应该的\n客气啦~"
        },
    ],
}


# ==================== 回复生成 Prompt ====================

def build_generation_prompt(
    relation: str,
    style: str,
    recent_history: str,
    current_message: str,
    emotion: str = "",
    context_note: str = ""
) -> str:
    """构建回复生成 Prompt"""
    
    style_guide = {
        "稳妥版": "稳重得体，不会出错",
        "轻松版": "轻松俏皮，带点幽默",
        "升温版": "热情主动，拉近距离"
    }
    
    emotion_note = f"\n当前对方情绪：{emotion}" if emotion else ""
    context_note = f"\n对话背景：{context_note}" if context_note else ""
    
    # 添加 Few-Shot 示例
    few_shot = ""
    if relation in FEW_SHOT_EXAMPLES:
        examples = FEW_SHOT_EXAMPLES[relation][:2]  # 取 2 个示例
        few_shot = "\n【参考示例】\n"
        for ex in examples:
            few_shot += f"对话：{ex['history']}\n回复:\n{ex['replies']}\n\n"
    
    prompt = f"""{few_shot}【当前对话】
历史对话:
{recent_history if recent_history else "首次对话"}

对方刚说：{current_message}

【回复要求】
关系：{relation}
风格：{style} - {style_guide.get(style, "")}{emotion_note}{context_note}

生成 3 条回复，每行一条："""
    
    return prompt


# ==================== 回复解析器 ====================

class ReplyParser:
    """大模型回复解析器 - 严格过滤"""
    
    # 需要过滤的关键词
    FILTER_WORDS = [
        "让我", "我来", "想一想", "想想", "分析一下", "首先", "其次",
        "第一", "第二", "第三", "1.", "2.", "3.", "①", "②", "③",
        "回复:", "回复：", "答案:", "答案：", "如下:", "如下：",
        "希望", "应该", "可能", "大概", "也许", "仅供参考", "希望能帮到你",
        "总之", "总的来说", "综上所述", "希望这些", "以上就是",
        "亲爱的用户", "您好", "你好", "AI 助手", "作为 AI",
    ]
    
    # 需要清理的前缀
    PREFIX_PATTERNS = [
        r'^[\d 一二三四五六七八九十 0-9]+[.、:：)]\s*',  # 编号
        r'^["""\'\'""\'""\'"""]+',  # 引号
        r'^[-\*\•]\s*',  # 列表符号
        r'^回复\s*\d*[:：]?',  # "回复 1:"
        r'^选项\s*\d*[:：]?',  # "选项 1:"
    ]
    
    @classmethod
    def parse(cls, raw_text: str) -> List[str]:
        """解析大模型返回的原始文本"""
        if not raw_text:
            return []
        
        replies = []
        
        # 步骤 1: 按行分割
        lines = raw_text.strip().split('\n')
        
        # 步骤 2: 清理每一行
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 跳过包含过滤词的行
            if any(kw in line for kw in cls.FILTER_WORDS):
                continue
            
            # 清理前缀
            for pattern in cls.PREFIX_PATTERNS:
                line = re.sub(pattern, '', line)
            line = line.strip()
            
            # 检查长度
            if 6 <= len(line) <= 25:
                replies.append(line)
        
        # 步骤 3: 去重
        seen = set()
        unique_replies = []
        for r in replies:
            if r not in seen and r not in cls.FILTER_WORDS:
                seen.add(r)
                unique_replies.append(r)
        
        # 步骤 4: 确保最多 3 条
        return unique_replies[:3]
    
    @classmethod
    def validate(cls, replies: List[str]) -> Tuple[bool, str]:
        """验证回复是否合格"""
        if not replies:
            return False, "回复为空"
        
        if len(replies) < 3:
            return False, f"回复数量不足 3 条 (仅{len(replies)}条)"
        
        for i, reply in enumerate(replies):
            if len(reply) < 6:
                return False, f"第{i+1}条回复太短 ({len(reply)}字)"
            if len(reply) > 25:
                return False, f"第{i+1}条回复太长 ({len(reply)}字)"
            if any(kw in reply for kw in cls.FILTER_WORDS):
                return False, f"第{i+1}条回复包含过滤词"
        
        return True, "验证通过"


# ==================== 主函数 ====================

def generate_reply(
    message: str,
    relation: str,
    style: str,
    conversation_history: str,
    api_key: str,
    model: str = "MiniMax-M2.7"
) -> Tuple[List[str], str]:
    """
    生成高情商回复（调用大模型）
    
    Args:
        message: 对方消息
        relation: 关系类型
        style: 回复风格
        conversation_history: 对话历史
        api_key: API Key
        model: 模型名称
    
    Returns:
        (回复列表，调试信息)
    """
    import requests
    
    # 构建 Prompt
    prompt = build_generation_prompt(
        relation=relation,
        style=style,
        recent_history=conversation_history,
        current_message=message
    )
    
    # 调用 API
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,  # 增加 tokens 避免截断
        "temperature": 0.8,
        "top_p": 0.9,
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        
        result = resp.json()
        api_msg = result.get("choices", [{}])[0].get("message", {})
        
        # 优先使用 content，如果没有则使用 reasoning_content
        raw_content = api_msg.get("content", "")
        if not raw_content:
            raw_content = api_msg.get("reasoning_content", "")
        
        # 如果还是为空，检查 finish_reason
        finish_reason = result.get("choices", [{}])[0].get("finish_reason", "")
        if not raw_content and finish_reason == "length":
            # 被长度限制截断了，增加 tokens 重试
            data["max_tokens"] = 300
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            result = resp.json()
            raw_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 解析回复
        replies = ReplyParser.parse(raw_content)
        
        # 验证
        is_valid, msg = ReplyParser.validate(replies)
        
        # 如果验证失败但有一些回复，尝试补充
        if not is_valid and len(replies) > 0 and len(replies) < 3:
            # 尝试用兜底回复补充
            fallback = _get_fallback_replies(relation, style)
            for fb in fallback:
                if fb not in replies:
                    replies.append(fb)
                    if len(replies) >= 3:
                        break
            is_valid = len(replies) >= 3
            msg = f"补充后:{len(replies)}条"
        
        if not is_valid:
            # 如果验证失败，返回兜底回复
            replies = _get_fallback_replies(relation, style)
        
        debug_info = f"[原始返回:{len(raw_content)}字] [解析后:{len(replies)}条] [验证:{msg}]"
        
        return replies, debug_info
        
    except Exception as e:
        # 异常时返回兜底回复
        return _get_fallback_replies(relation, style), f"[错误:{str(e)}]"


def _get_fallback_replies(relation: str, style: str) -> List[str]:
    """获取兜底回复"""
    fallbacks = {
        "恋人": ["在呢宝贝~", "想你啦！", "怎么啦？"],
        "朋友": ["在在在", "咋啦兄弟", "你说"],
        "同事": ["在的请说", "您好", "什么事"],
        "客户": ["您好请讲", "在的", "请问有什么可以帮您"],
        "家人": ["在呢爸妈", "咋啦", "你说"],
        "追求者": ["在的", "什么事呀", "请说"],
        "海王": ["在忙", "晚点说", "嗯"],
        "高冷": ["嗯", "说", "哦"]
    }
    return fallbacks.get(relation, ["收到~", "好的", "知道啦"])


# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试用（需要填入真实 API Key）
    API_KEY = ""  # 填入你的 API Key
    
    if not API_KEY:
        print("请填入 API Key 后测试")
        exit()
    
    print("=" * 60)
    print("高情商回复助手 V11.0 - 大模型测试")
    print("=" * 60)
    
    # 模拟连续对话
    history = ""
    messages = [
        "在吗",
        "干嘛呢",
        "想你了",
        "有多想",
        "周末见面吗",
    ]
    
    for msg in messages:
        replies, info = generate_reply(
            message=msg,
            relation="恋人",
            style="升温版",
            conversation_history=history,
            api_key=API_KEY
        )
        
        print(f"\nQ: {msg}")
        print(f"   {info}")
        print(f"   A: {replies[0] if replies else '无回复'}")
        if len(replies) > 1:
            print(f"   备选：{replies[1]} | {replies[2] if len(replies) > 2 else ''}")
        
        # 更新历史
        if history:
            history += "\n"
        history += f"TA: {msg}\n我：{replies[0] if replies else ''}"
    
    print("\n" + "=" * 60)
