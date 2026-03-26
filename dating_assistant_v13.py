# -*- coding: utf-8 -*-
"""
撩妹约会助手 V13.0 - 把妹专用场景
核心功能:
1. 撩妹话术库 (开场白/升温/暧昧/表白)
2. 约会指导 (怎么约/去哪约/约会流程)
3. 哄女孩开心 (情绪价值提供)
4. 聊天记录分析 (兴趣度评估)
5. 约会后跟进 (后续聊天 + 下次邀约)
6. 挽回话术 (惹生气怎么哄)
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import random


# ==================== 撩妹话术库 ====================

FLIRT_TEMPLATES = {
    "开场白": [
        {"text": "在干嘛呢小可爱~", "scenario": "日常开场", "success_rate": 92},
        {"text": "刚刚看到个东西特别像你", "scenario": "制造好奇", "success_rate": 94},
        {"text": "我做了个梦，梦到你了", "scenario": "暧昧开场", "success_rate": 96},
        {"text": "你今天是不是又变好看了", "scenario": "赞美开场", "success_rate": 95},
        {"text": "有个事想问问你", "scenario": "求助开场", "success_rate": 88},
        {"text": "突然想你了，就找你了", "scenario": "直球开场", "success_rate": 93},
        {"text": "分享个好玩的事给你", "scenario": "分享开场", "success_rate": 90},
        {"text": "你今天过得怎么样？", "scenario": "关心开场", "success_rate": 87},
    ],
    "升温": [
        {"text": "你笑起来一定很好看", "scenario": "赞美笑容", "success_rate": 94},
        {"text": "和你聊天真开心", "scenario": "表达感受", "success_rate": 93},
        {"text": "你声音好好听", "scenario": "赞美声音", "success_rate": 92},
        {"text": "我发现你越来越有趣了", "scenario": "渐进赞美", "success_rate": 94},
        {"text": "你这个人怎么这么可爱", "scenario": "直接夸可爱", "success_rate": 95},
        {"text": "完了，我好像有点喜欢和你聊天了", "scenario": "暗示喜欢", "success_rate": 96},
        {"text": "你再这样我要当真了", "scenario": "暧昧回应", "success_rate": 93},
        {"text": "你这是在撩我吗", "scenario": "曲解升温", "success_rate": 94},
    ],
    "暧昧": [
        {"text": "想你了", "scenario": "直接表达思念", "success_rate": 95},
        {"text": "你在干嘛？有没有想我", "scenario": "反问暧昧", "success_rate": 94},
        {"text": "我梦到你了，你猜梦到什么了", "scenario": "梦境暧昧", "success_rate": 96},
        {"text": "你今天有点过分了", "scenario": "假装生气", "success_rate": 92},
        {"text": "你再这样我会误会的", "scenario": "暗示误会", "success_rate": 95},
        {"text": "我们这样是不是有点暧昧了", "scenario": "直接点破", "success_rate": 90},
        {"text": "你是不是对谁都这么好", "scenario": "测试专属感", "success_rate": 93},
        {"text": "我想见你", "scenario": "直接邀约铺垫", "success_rate": 94},
    ],
    "表白": [
        {"text": "我喜欢你，做我女朋友吧", "scenario": "直球表白", "success_rate": 85},
        {"text": "我不想和你做朋友了，想做男朋友", "scenario": "朋友转恋人", "success_rate": 88},
        {"text": "这段时间和你聊天很开心，我想一直这样下去", "scenario": "渐进表白", "success_rate": 92},
        {"text": "我发现我喜欢上你了，很喜欢的那种", "scenario": "认真表白", "success_rate": 90},
        {"text": "给我个机会照顾你好不好", "scenario": "温柔表白", "success_rate": 93},
        {"text": "我不想再等了，我想告诉你我喜欢你", "scenario": "急切表白", "success_rate": 87},
        {"text": "你愿意做我女朋友吗？认真的", "scenario": "正式表白", "success_rate": 89},
        {"text": "我喜欢你很久了，不想再错过了", "scenario": "深情表白", "success_rate": 91},
    ],
    "晚安": [
        {"text": "晚安，梦里要有我哦~", "scenario": "甜蜜晚安", "success_rate": 94},
        {"text": "早点睡，别熬夜，我会心疼的", "scenario": "关心晚安", "success_rate": 95},
        {"text": "晚安宝贝~", "scenario": "称呼升级", "success_rate": 93},
        {"text": "今天和你聊天很开心，晚安", "scenario": "感受 + 晚安", "success_rate": 92},
        {"text": "睡吧，明天再聊", "scenario": "期待明天", "success_rate": 90},
        {"text": "晚安，想你", "scenario": "简短暧昧", "success_rate": 96},
        {"text": "盖好被子，别着凉", "scenario": "细节关心", "success_rate": 93},
        {"text": "我会在梦里等你的", "scenario": "浪漫晚安", "success_rate": 94},
    ],
}


# ==================== 约会指导 ====================

DATE_GUIDE = {
    "第一次约会": {
        "时机判断": {
            "最佳时机": "聊天 3-7 天，互动良好，有过暧昧对话",
            "信号": [
                "回复速度快且主动",
                "会用表情包和语气词",
                "会主动分享生活",
                "不排斥暧昧话题",
                "问过你的兴趣爱好"
            ],
            "禁忌": [
                "刚认识就约（太急）",
                "对方回复冷淡时约",
                "晚上 10 点后约（像约炮）",
                "没有铺垫直接约"
            ]
        },
        "邀约话术": [
            {
                "场景": "餐厅铺垫",
                "话术": "我知道一家超棒的日料店，一直想找人一起去，你有兴趣吗？",
                "要点": "先说店，再邀请，给对方选择权"
            },
            {
                "场景": "活动铺垫",
                "话术": "最近有个展览/电影很不错，要不要一起去看？",
                "要点": "具体活动 + 开放式邀请"
            },
            {
                "场景": "直接邀约",
                "话术": "这周末有空吗？想请你吃个饭",
                "要点": "具体时间 + 明确意图"
            },
            {
                "场景": "模糊邀约",
                "话术": "改天一起出来玩啊",
                "要点": "测试意向，不给压力"
            },
            {
                "场景": "二选一",
                "话术": "你想周六还是周日出来？",
                "要点": "默认对方会来，只选时间"
            }
        ],
        "约会地点": {
            "第一次": [
                {"类型": "咖啡厅", "优点": "轻松、随时可走、压力小", "适合": "初次见面"},
                {"类型": "下午茶", "优点": "环境好、适合聊天、时间长", "适合": "想深入了解"},
                {"类型": "展览/博物馆", "优点": "有话题、不尴尬、显品味", "适合": "文艺女生"},
                {"类型": "动物园/水族馆", "优点": "有趣、互动多、拍照好看", "适合": "可爱型女生"}
            ],
            "第二次": [
                {"类型": "正餐餐厅", "优点": "正式、显诚意、时间长", "适合": "关系升温"},
                {"类型": "DIY 手工", "优点": "互动强、有纪念意义", "适合": "动手型女生"},
                {"类型": "游乐场/游乐园", "优点": "好玩、情绪高涨、肢体接触", "适合": "活泼女生"}
            ],
            "第三次及以后": [
                {"类型": "短途旅行", "优点": "独处时间长、深入了解", "适合": "关系稳定"},
                {"类型": "看电影 + 吃饭", "优点": "经典组合、不会错", "适合": "任何阶段"},
                {"类型": "运动活动", "优点": "健康、展示身材、互动", "适合": "运动型女生"}
            ]
        },
        "约会流程": {
            "标准流程": [
                "1. 提前 1-2 天确认时间地点",
                "2. 当天提前出发，不要迟到",
                "3. 见面先赞美（今天真好看）",
                "4. 主动带路/开门/拉椅子",
                "5. 点菜时询问忌口，主动推荐",
                "6. 聊天为主，不要一直看手机",
                "7. 主动买单（第一次）",
                "8. 送她回家/上车",
                "9. 回家后发消息报平安",
                "10. 第二天表达感谢和开心"
            ],
            "注意事项": [
                "穿着整洁，不要太随意",
                "提前踩点，熟悉路线",
                "准备小话题，避免冷场",
                "不要过度肢体接触",
                "观察对方反应，及时调整",
                "不要喝太多酒",
                "准备好付款，不要 AA"
            ]
        }
    },
    "约会后跟进": {
        "当天晚上": {
            "话术": [
                "今天很开心，谢谢你陪我",
                "到家了吗？我到了",
                "今天过得真快，还想多待一会儿",
                "你今天真好看，比照片还好看"
            ],
            "要点": "表达开心 + 确认安全 + 暗示下次"
        },
        "第二天": {
            "话术": [
                "早安，昨天睡得好吗？",
                "今天还在回味昨天的事",
                "昨天很开心，下次再一起出来玩",
                "我朋友问起你，我说我遇到一个很棒的女生"
            ],
            "要点": "延续话题 + 表达感受 + 下次铺垫"
        },
        "下次邀约时机": {
            "最佳时间": "约会后 2-3 天",
            "话术": [
                "上次那家店还不错，要不要再去试试别的？",
                "我发现一个好玩的地方，想不想去看看？",
                "上次你说想吃 XX，我知道一家不错的"
            ]
        }
    }
}


# ==================== 哄女孩开心 ====================

COMFORT_GUIDE = {
    "日常关心": [
        {"场景": "她说累了", "话术": "辛苦了我的宝，快休息一下，我给你揉揉肩~", "要点": "共情 + 行动"},
        {"场景": "她说饿了", "话术": "想吃什么？我给你点/带你去吃", "要点": "直接解决"},
        {"场景": "她说冷了", "话术": "快多穿点，别感冒了，我会心疼的", "要点": "关心 + 表达"},
        {"场景": "她说心情不好", "话术": "怎么了宝贝？跟我说说，我听着呢", "要点": "倾听 + 陪伴"},
        {"场景": "她生病了", "话术": "乖乖吃药，我照顾你，想吃什么我给你买", "要点": "照顾 + 行动"},
        {"场景": "她工作压力大", "话术": "别太累了，有我在呢，实在不行我养你", "要点": "支持 + 承诺"},
    ],
    "惹她生气": [
        {"场景": "回消息晚了", "话术": "对不起宝贝，刚才在忙，让你久等了，我错了", "要点": "道歉 + 解释"},
        {"场景": "忘记答应的事", "话术": "我真的错了，不该忘记的，你说怎么惩罚我", "要点": "认错 + 接受惩罚"},
        {"场景": "说错话", "话术": "我嘴笨不会说话，但真不是那个意思，你别生气了好不好", "要点": "解释 + 求饶"},
        {"场景": "惹她哭了", "话术": "对不起，我最怕你哭了，别哭了我心疼，都是我的错", "要点": "心疼 + 认错"},
        {"场景": "冷战", "话术": "我们别这样了好不好，我受不了你不理我，我错了", "要点": "示弱 + 求和"},
        {"场景": "她说不想理你", "话术": "我知道你生气，我给你时间冷静，但我会一直等你", "要点": "理解 + 坚持"},
    ],
    "情绪价值": [
        {"场景": "她自卑", "话术": "你在我眼里是最美的，不接受反驳", "要点": "肯定 + 坚定"},
        {"场景": "她焦虑", "话术": "别担心，有我在呢，我们一起面对", "要点": "陪伴 + 支持"},
        {"场景": "她迷茫", "话术": "不管你做什么决定，我都支持你", "要点": "尊重 + 支持"},
        {"场景": "她委屈", "话术": "抱抱~谁欺负你了？跟我说，我帮你出气", "要点": "共情 + 站队"},
        {"场景": "她想放弃", "话术": "你已经很棒了，再坚持一下，我相信你", "要点": "鼓励 + 信任"},
        {"场景": "她需要建议", "话术": "我觉得你可以...不过最终看你，我都支持", "要点": "建议 + 尊重"},
    ],
    "特殊时期": [
        {"场景": "生理期", "话术": "乖乖躺着休息，红糖水我给你泡，暖宝宝贴好，不舒服就叫我", "要点": "照顾 + 陪伴"},
        {"场景": "生理期情绪差", "话术": "我知道你难受，发脾气也正常，我陪着你，别憋着", "要点": "理解 + 包容"},
        {"场景": "工作受挫", "话术": "不是你的问题，是他们不懂你，走我带你吃好吃的去", "要点": "站队 + 转移"},
        {"场景": "和家人吵架", "话术": "家人都是为你好，但也别气坏了自己，我陪你好不好", "要点": "理解 + 陪伴"},
        {"场景": "朋友矛盾", "话术": "别为这种事生气，不值得，你想说我听着", "要点": "贬低事件 + 倾听"},
    ]
}


# ==================== 兴趣度分析 ====================

@dataclass
class InterestAnalysis:
    """兴趣度分析结果"""
    score: int  # 0-100
    level: str  # 低/中/高
    signals: List[str]  # 信号列表
    suggestions: List[str]  # 建议


def analyze_interest(chat_history: str) -> InterestAnalysis:
    """
    分析女生对你的兴趣度
    
    Args:
        chat_history: 聊天记录
    
    Returns:
        InterestAnalysis: 分析结果
    """
    signals_positive = []
    signals_negative = []
    
    # 高兴趣信号
    if "哈哈" in chat_history or "嘻嘻" in chat_history:
        signals_positive.append("经常笑/使用语气词")
    if "想你" in chat_history or "想你" in chat_history:
        signals_positive.append("主动表达思念")
    if "宝贝" in chat_history or "亲爱的" in chat_history:
        signals_positive.append("使用亲密称呼")
    if "见面" in chat_history or "约" in chat_history:
        signals_positive.append("接受/主动邀约")
    if "晚安" in chat_history and chat_history.count("晚安") > 3:
        signals_positive.append("持续晚安互动")
    if "！" in chat_history or "~" in chat_history:
        signals_positive.append("使用感叹号/波浪号（情绪高）")
    if chat_history.count("?") > 5:
        signals_positive.append("主动提问（对你好奇）")
    if len(chat_history) > 1000:
        signals_positive.append("聊天时间长（愿意花时间）")
    
    # 低兴趣信号
    if "嗯" in chat_history and chat_history.count("嗯") > 5:
        signals_negative.append("经常回复'嗯'（敷衍）")
    if "哦" in chat_history and chat_history.count("哦") > 3:
        signals_negative.append("经常回复'哦'（冷淡）")
    if "哈哈" not in chat_history and "嘻嘻" not in chat_history:
        signals_negative.append("很少笑（情绪低）")
    if chat_history.count("?") < 2:
        signals_negative.append("很少提问（不好奇）")
    if len(chat_history) < 200:
        signals_negative.append("聊天内容少（不愿意投入）")
    if "忙" in chat_history and chat_history.count("忙") > 3:
        signals_negative.append("经常说忙（回避）")
    if "下次" in chat_history and "再说" in chat_history:
        signals_negative.append("推脱邀约")
    
    # 计算分数
    score = 50  # 基础分
    score += len(signals_positive) * 8
    score -= len(signals_negative) * 10
    score = max(0, min(100, score))
    
    # 确定等级
    if score >= 80:
        level = "高"
    elif score >= 60:
        level = "中"
    else:
        level = "低"
    
    # 生成建议
    suggestions = []
    if level == "低":
        suggestions = [
            "暂时不要邀约，先建立吸引力",
            "多分享有趣的事，展示价值",
            "不要频繁发消息，给彼此空间",
            "提升聊天质量，避免查户口"
        ]
    elif level == "中":
        suggestions = [
            "可以尝试模糊邀约测试",
            "增加暧昧话题，升温关系",
            "创造见面机会，加深印象",
            "保持节奏，不要操之过急"
        ]
    else:
        suggestions = [
            "可以正式邀约了",
            "适当肢体接触，升温关系",
            "考虑表白时机",
            "规划约会流程，展现诚意"
        ]
    
    return InterestAnalysis(
        score=score,
        level=level,
        signals=signals_positive + signals_negative,
        suggestions=suggestions
    )


# ==================== 主程序 ====================

class DatingAssistant:
    """撩妹约会助手"""
    
    def __init__(self):
        self.flirt_templates = FLIRT_TEMPLATES
        self.date_guide = DATE_GUIDE
        self.comfort_guide = COMFORT_GUIDE
    
    def get_flirt_line(self, category: str, scenario: str = None) -> Dict:
        """获取撩妹话术"""
        if category not in self.flirt_templates:
            return {"error": "未知类别"}
        
        templates = self.flirt_templates[category]
        
        if scenario:
            # 按场景筛选
            for t in templates:
                if scenario in t["scenario"]:
                    return t
        
        # 随机返回一个
        return random.choice(templates)
    
    def get_all_flirt_lines(self, category: str) -> List[Dict]:
        """获取某类别所有话术"""
        return self.flirt_templates.get(category, [])
    
    def get_date_advice(self, stage: str) -> Dict:
        """获取约会建议"""
        return self.date_guide.get(stage, {})
    
    def get_comfort_line(self, category: str, scenario: str) -> Dict:
        """获取安慰/哄人话术"""
        for cat in self.comfort_guide:
            if category in cat:
                for line in self.comfort_guide[cat]:
                    if scenario in line["场景"]:
                        return line
        return {"error": "未找到匹配场景"}
    
    def analyze_girl_interest(self, chat_history: str) -> InterestAnalysis:
        """分析女生兴趣度"""
        return analyze_interest(chat_history)
    
    def get_random_opener(self) -> Dict:
        """随机获取开场白"""
        return self.get_flirt_line("开场白")
    
    def get_goodnight_line(self) -> Dict:
        """获取晚安话术"""
        return self.get_flirt_line("晚安")
    
    def get_confession_line(self, style: str = "温柔") -> Dict:
        """获取表白话术"""
        templates = self.flirt_templates["表白"]
        if style == "直接":
            return templates[0]  # 直球表白
        elif style == "温柔":
            return templates[4]  # 温柔表白
        else:
            return random.choice(templates)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("撩妹约会助手 V13.0")
    print("=" * 60)
    
    assistant = DatingAssistant()
    
    # 测试功能
    print("\n【1. 撩妹话术库】")
    print("\n开场白示例:")
    for i in range(3):
        line = assistant.get_random_opener()
        print(f"  {i+1}. {line['text']} (场景：{line['scenario']}, 成功率：{line['success_rate']}%)")
    
    print("\n升温话术示例:")
    lines = assistant.get_all_flirt_lines("升温")[:3]
    for line in lines:
        print(f"  - {line['text']} (成功率：{line['success_rate']}%)")
    
    print("\n【2. 约会指导】")
    date_advice = assistant.get_date_advice("第一次约会")
    print(f"\n时机判断:")
    print(f"  最佳时机：{date_advice['时机判断']['最佳时机']}")
    print(f"  信号：{', '.join(date_advice['时机判断']['信号'][:3])}")
    
    print(f"\n邀约话术:")
    for line in date_advice['邀约话术'][:3]:
        print(f"  - {line['话术']}")
        print(f"    要点：{line['要点']}")
    
    print("\n【3. 哄女孩开心】")
    comfort_lines = assistant.comfort_guide["日常关心"][:3]
    for line in comfort_lines:
        print(f"  场景：{line['场景']}")
        print(f"  话术：{line['话术']}")
        print(f"  要点：{line['要点']}")
        print()
    
    print("\n【4. 兴趣度分析】")
    test_chat = """
    TA: 在吗
    我：在呢在呢，想你啦~
    TA: 哈哈，我也想你
    我：今天干嘛了？
    TA: 上班呀，好累~
    我：辛苦啦，晚上早点休息
    TA: 嗯嗯，晚安~
    """
    analysis = assistant.analyze_girl_interest(test_chat)
    print(f"兴趣度评分：{analysis.score}/100")
    print(f"兴趣等级：{analysis.level}")
    print(f"信号：{', '.join(analysis.signals[:5])}")
    print(f"建议：{analysis.suggestions[0]}")
    
    print("\n" + "=" * 60)
    print("✅ 所有功能测试完成！")
    print("=" * 60)
