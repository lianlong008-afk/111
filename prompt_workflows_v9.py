# -*- coding: utf-8 -*-
"""
高情商回复助手 - Prompt 工作流 V9.0
优化：好友画像分析 + 高情商回复生成
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


# ==================== 好友画像分析 Prompt ====================

PROFILE_ANALYSIS_PROMPT = """【角色】你是一位资深的人际关系分析师，擅长通过聊天记录洞察人的性格和关系动态。

【任务】请根据提供的聊天记录，分析这个人的特点以及 TA 与用户的关系。

【分析维度】

## 1. 基础信息
- 称呼/昵称：从聊天中提取
- 关系类型：恋人/朋友/同事/客户/家人/追求者/暧昧/其他
- 互动频率：高频/中频/低频（根据消息密度判断）

## 2. 聊天风格分析
- 表达长度：长篇大论/简洁短句
- 语气特点：温柔/直接/幽默/严肃/撒娇/冷淡
- 表情使用：频繁使用表情包/很少用表情
- 回复速度：秒回/正常/较慢（根据上下文推断）
- 主动性：主动发起话题/被动回应/平衡

## 3. 性格特点画像
- 外向程度：外向活泼/内向沉稳
- 情绪表达：直接外露/含蓄内敛
- 决策风格：果断/犹豫/随和
- 社交需求：高/中/低

## 4. 重要事件提取
从聊天中提取关键事件：
- 生日/纪念日
- 工作变动（升职、跳槽、离职）
- 情感状态变化
- 健康状况
- 家庭事件
- 共同经历的重要时刻

## 5. 关系亲密度评估
- 称呼亲密度：宝贝/亲爱的/昵称/全名/职务
- 话题深度：日常琐事/情感交流/未来规划
- 互动质量：热情回应/敷衍应付/正常交流

【输出格式要求】
请用以下 JSON 格式输出（必须严格遵循）：

```json
{
  "basic_info": {
    "name": "称呼或昵称",
    "relation_type": "关系类型",
    "interaction_frequency": "高频/中频/低频"
  },
  "chat_style": {
    "expression_length": "长篇/简洁",
    "tone": "温柔/直接/幽默/严肃/撒娇/冷淡",
    "emoji_usage": "频繁/适中/很少",
    "response_speed": "秒回/正常/较慢",
    "initiative": "主动/被动/平衡"
  },
  "personality": {
    "extroversion": "外向/内向",
    "emotion_expression": "直接/含蓄",
    "decision_style": "果断/犹豫/随和",
    "social_need": "高/中/低"
  },
  "important_events": [
    {"event": "事件描述", "date": "时间（如有）", "type": "生日/工作/情感/健康/家庭/其他"}
  ],
  "relationship_intimacy": {
    "level": "非常亲密/比较亲密/一般/疏远",
    "evidence": "判断依据，如称呼、话题等"
  },
  "summary": "200 字以内的综合画像描述，像朋友间八卦聊天一样自然口语化"
}
```

【聊天记录】
{chat_history}

请开始分析："""


# ==================== 高情商回复生成 Prompt ====================

REPLY_GENERATION_PROMPT = """【角色】你是一位高情商聊天专家，擅长根据对方特点和情境给出得体、温暖的回复。

【核心原则】
1. 真诚第一：避免套路，用真心换真心
2. 共情优先：先理解对方情绪，再回应内容
3. 因人而异：根据关系和性格调整语气
4. 适度幽默：轻松但不轻浮，幽默但不冒犯
5. 留有余地：给对方继续话题的空间

【输入信息】

## 1. 对方画像
{friend_profile}

## 2. 关系类型及语气指导
- 关系：{relation}
- 语气要求：{tone_guide}

## 3. 最近聊天记忆（最近 5 轮对话）
{recent_memory}

## 4. 当前对话上下文
- 对方刚说：{current_message}
- 对话背景：{context}
- 时间情境：{time_context}

## 5. 回复风格要求
- 风格：{style}
- 风格说明：{style_description}

【回复策略】

## 情绪识别与回应
1. 识别对方情绪（开心/难过/生气/焦虑/期待/疲惫...）
2. 先共情再回应：
   - 开心时：一起庆祝，放大积极情绪
   - 难过时：理解安慰，不急于给建议
   - 生气时：先接纳情绪，不辩解
   - 焦虑时：给予支持，帮助分解
   - 期待时：积极回应，给予肯定
   - 疲惫时：表达关心，提供休息空间

## 关系适配
根据关系调整：
- 恋人：亲密、撒娇、专属昵称
- 朋友：轻松、调侃、讲义气
- 同事：专业、礼貌、有边界
- 客户：热情、专业、给台阶
- 家人：温暖、关心、报平安
- 追求者：友好但保持距离
- 海王：推拉、暧昧、不主动
- 高冷：简洁、不追问、留空间

## 话题延续
好的回复应该：
- 回应对方内容
- 表达自己感受
- 留有继续话题的钩子（提问/分享/邀请）

【输出要求】
1. 生成 3 条回复选项
2. 每条 8-20 字，符合微信聊天习惯
3. 只用中文，不要标点符号结尾（语气词除外）
4. 不要解释说明，只输出回复内容
5. 每行一条，格式如下：

回复选项 1
回复选项 2
回复选项 3

【开始生成】
请根据以上信息，生成 3 条高情商回复："""


# ==================== 关系语气指导配置 ====================

RELATION_TONE_GUIDES: Dict[str, Dict[str, str]] = {
    "恋人": {
        "general": "甜蜜亲密，体现关心和爱意，可以用亲昵称呼和撒娇语气",
        "checkin": "热情回应，表达想念，如'宝贝我在呢，想你啦'",
        "care": "焦急关心，主动提供帮助，如'心疼死我了，我来照顾你'",
        "complaint": "站在对方这边，一起吐槽，如'太过分了，抱抱我的宝贝'",
        "share": "积极回应，放大情绪，如'太棒了！不愧是我男朋友！'",
        "night": "温柔甜蜜，表达爱意，如'爱你哟，梦里见宝贝'"
    },
    "朋友": {
        "general": "自然轻松，可以调侃开玩笑，不用太客气",
        "checkin": "随意热情，如'在在在，咋啦兄弟'",
        "care": "真诚关心，如'咋了这是，有事跟我说'",
        "complaint": "一起吐槽，如'什么玩意儿，走喝酒去'",
        "share": "兴奋捧场，如'可以啊你！请客请客！'",
        "night": "简单随意，如'晚安晚安，明天聊'"
    },
    "同事": {
        "general": "专业礼貌，保持适当距离，但不过于生疏",
        "checkin": "礼貌回应，如'在的，请说'",
        "care": "适度关心，如'辛苦了，注意休息'",
        "complaint": "理解但不站队，如'确实不容易，加油'",
        "share": "友好回应，如'挺好的，恭喜'",
        "night": "礼貌结束，如'晚安，明天见'"
    },
    "客户": {
        "general": "商务专业，热情但不卑微，给客户台阶和面子",
        "checkin": "热情专业，如'您好，在的，请讲'",
        "care": "重视关心，如'您辛苦了，我们尽快处理'",
        "complaint": "先道歉再解决，如'非常抱歉，我马上处理'",
        "share": "积极祝贺，如'太棒了，恭喜您！'",
        "night": "礼貌祝福，如'晚安，祝您愉快'"
    },
    "家人": {
        "general": "亲情温暖，听话懂事，多关心多问候",
        "checkin": "亲切回应，如'爸妈我在呢，咋啦'",
        "care": "乖巧听话，如'好的知道了，你们也要注意身体'",
        "complaint": "理解安慰，如'别生气，我周末就回家'",
        "share": "开心回应，如'太好了，我也想吃家里的饭'",
        "night": "温暖关心，如'晚安爸妈，爱你们'"
    },
    "追求者": {
        "general": "友好得体，不伤害对方，但保持适当距离",
        "checkin": "友好但不过热，如'在的，什么事呀'",
        "care": "感谢但保持距离，如'谢谢关心，我挺好的'",
        "complaint": "理解但不深入，如'理解，希望你早点好起来'",
        "share": "礼貌回应，如'挺好的，恭喜呀'",
        "night": "简单结束，如'晚安，好梦'"
    },
    "海王": {
        "general": "若即若离，保持神秘感，不要太主动",
        "checkin": "简单回应，如'在忙，晚点说'",
        "care": "淡淡关心，如'嗯，你也是'",
        "complaint": "不深入参与，如'哦，那确实挺烦的'",
        "share": "不冷不热，如'挺好的'",
        "night": "简短结束，如'嗯，晚安'"
    },
    "高冷": {
        "general": "简洁冷淡，不主动延伸话题",
        "checkin": "极简回应，如'嗯'",
        "care": "简短回应，如'哦'",
        "complaint": "不参与，如'嗯'",
        "share": "简单回应，如'哦'",
        "night": "极简，如'嗯'"
    }
}


# ==================== 风格描述配置 ====================

STYLE_DESCRIPTIONS: Dict[str, str] = {
    "稳妥版": "稳重得体，不会出错，适合正式场合或不确定对方想法时",
    "轻松版": "轻松俏皮，带点幽默，适合熟悉的朋友或轻松氛围",
    "升温版": "热情主动，拉近距离，适合想进一步发展关系时"
}


# ==================== 时间情境配置 ====================

TIME_CONTEXT_PROMPTS = {
    "morning": "早上（6-10 点），可以问候早安，关心早餐",
    "noon": "中午（11-14 点），可以约午饭或问候休息",
    "afternoon": "下午（15-18 点），工作时间，关心是否忙碌",
    "evening": "晚上（19-22 点），休闲时间，可以闲聊或邀约",
    "night": "深夜（23-5 点），关心休息，不宜长聊",
    "weekday": "工作日，考虑对方可能在工作",
    "weekend": "周末/节假日，可以约见面或闲聊"
}


@dataclass
class PromptContext:
    """Prompt 上下文数据"""
    friend_profile: str  # 好友画像
    relation: str  # 关系类型
    tone_guide: str  # 语气指导
    recent_memory: str  # 最近聊天记忆
    current_message: str  # 当前消息
    context: str  # 对话背景
    time_context: str  # 时间情境
    style: str  # 回复风格
    style_description: str  # 风格描述


def build_profile_prompt(chat_history: str) -> str:
    """构建好友画像分析 Prompt"""
    return PROFILE_ANALYSIS_PROMPT.format(chat_history=chat_history)


def build_reply_prompt(context: PromptContext) -> str:
    """构建回复生成 Prompt"""
    return REPLY_GENERATION_PROMPT.format(
        friend_profile=context.friend_profile or "暂无详细画像",
        relation=context.relation,
        tone_guide=context.tone_guide,
        recent_memory=context.recent_memory or "暂无历史对话",
        current_message=context.current_message,
        context=context.context or "日常聊天",
        time_context=context.time_context or "不限时间",
        style=context.style,
        style_description=context.style_description
    )


def get_tone_guide(relation: str, intent: str = "general") -> str:
    """获取关系语气指导"""
    guides = RELATION_TONE_GUIDES.get(relation, RELATION_TONE_GUIDES["朋友"])
    return guides.get(intent, guides["general"])


def get_style_description(style: str) -> str:
    """获取风格描述"""
    return STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["稳妥版"])


def get_time_context(hour: int, is_weekend: bool = False) -> str:
    """根据时间获取情境描述"""
    if is_weekend:
        base = TIME_CONTEXT_PROMPTS["weekend"]
    else:
        base = TIME_CONTEXT_PROMPTS["weekday"]
    
    if 6 <= hour < 10:
        time_part = TIME_CONTEXT_PROMPTS["morning"]
    elif 10 <= hour < 11:
        time_part = ""
    elif 11 <= hour < 14:
        time_part = TIME_CONTEXT_PROMPTS["noon"]
    elif 14 <= hour < 15:
        time_part = ""
    elif 15 <= hour < 18:
        time_part = TIME_CONTEXT_PROMPTS["afternoon"]
    elif 18 <= hour < 19:
        time_part = ""
    elif 19 <= hour < 23:
        time_part = TIME_CONTEXT_PROMPTS["evening"]
    else:
        time_part = TIME_CONTEXT_PROMPTS["night"]
    
    return f"{base}，当前是{time_part}" if time_part else base


if __name__ == "__main__":
    # 测试 Prompt 构建
    context = PromptContext(
        friend_profile="性格开朗，喜欢发表情包，聊天热情",
        relation="恋人",
        tone_guide=get_tone_guide("恋人", "checkin"),
        recent_memory="TA 说：今天好累啊\n我说：辛苦啦，抱抱~",
        current_message="在吗",
        context="工作间隙聊天",
        time_context=get_time_context(15, False),
        style="升温版",
        style_description=get_style_description("升温版")
    )
    
    prompt = build_reply_prompt(context)
    print("生成的回复 Prompt:")
    print("-" * 50)
    print(prompt)
