# -*- coding: utf-8 -*-
"""
高情商回复数据集 V12.0 - 真实刁钻场景版
基于真实男女拉扯案例、海王场景、刁钻问题
包含：尖锐问题测试、废物测试、框架博弈、情绪操控等
"""

import json
from datetime import datetime


# ==================== 恋爱场景 - 刁钻问题版 ====================

LOVER_CHALLENGING_SCENARIOS = [
    {
        "id": 1,
        "title": "废物测试 - 你和几个女生暧昧",
        "description": "女生测试你是不是海王，问你有没有同时撩别人",
        "conversations": [
            {"ta": "你是不是对每个女生都这样说", "reply": "只对你一个人这样说过~", "score": 95, "note": "专属感化解"},
            {"ta": "你之前也这样撩过别人吧", "reply": "这不是撩，是真心话", "score": 93, "note": "重新定义"},
            {"ta": "你同时和几个女生聊天", "reply": "你猜~猜对了奖励你", "score": 90, "note": "调皮转移"},
            {"ta": "说实话", "reply": "说实话就是只和你聊得最开心", "score": 94, "note": "诚实但甜蜜"},
            {"ta": "你是不是海王", "reply": "我要是海王，你就是我唯一的岸", "score": 96, "note": "土味但有效"},
            {"ta": "别油嘴滑舌", "reply": "好，那我认真说：我只喜欢你", "score": 95, "note": "先调后认真"},
            {"ta": "真的吗", "reply": "比真金还真~", "score": 88, "note": "轻松化解"},
            {"ta": "我怎么相信你", "reply": "给我个机会，用行动证明", "score": 93, "note": "引导未来"},
            {"ta": "那你说说喜欢我什么", "reply": "喜欢你自己都不知道的样子", "score": 92, "note": "神秘感"},
            {"ta": "这算什么回答", "reply": "那你想要什么回答？我认真想", "score": 90, "note": "反将一军"},
            {"ta": "你就不能说具体的", "reply": "具体的就是和你聊天会不自觉笑", "score": 93, "note": "细节打动"},
            {"ta": "哼", "reply": "哼是什么意思？我答得不好吗？", "score": 89, "note": "装傻"},
            {"ta": "你说呢", "reply": "我觉得挺好的，你觉得呢？", "score": 88, "note": "反问"},
            {"ta": "好吧", "reply": "那就相信我一次好不好？", "score": 92, "note": "温柔请求"},
            {"ta": "我考虑一下", "reply": "好，我等你考虑好~", "score": 91, "note": "给空间"},
            {"ta": "晚安", "reply": "晚安，梦里也要考虑哦~", "score": 90, "note": "调皮结尾"},
            {"ta": "早安", "reply": "早呀，考虑得怎么样了？", "score": 89, "note": "延续话题"},
            {"ta": "还行吧", "reply": "还行就是可以的意思咯？", "score": 91, "note": "引导确认"},
            {"ta": "你猜", "reply": "我猜你心里已经有答案了~", "score": 92, "note": "自信"},
            {"ta": "爱你", "reply": "我就知道你也喜欢我！", "score": 94, "note": "甜蜜收尾"}
        ]
    },
    {
        "id": 2,
        "title": "框架博弈 - 为什么不公开关系",
        "description": "女生要求公开关系，但男生还没准备好",
        "conversations": [
            {"ta": "我们是什么关系", "reply": "你觉得我们是什么关系？", "score": 92, "note": "反问"},
            {"ta": "我就是不知道才问你", "reply": "我觉得是比普通朋友更特别的关系", "score": 93, "note": "模糊但甜蜜"},
            {"ta": "那为什么不公开", "reply": "公开什么？公开我有多喜欢你吗？", "score": 91, "note": "转移焦点"},
            {"ta": "我是认真的", "reply": "我也是认真的，所以才想慢慢来", "score": 94, "note": "真诚"},
            {"ta": "慢慢来是多久", "reply": "久到我们可以确定彼此是唯一的", "score": 95, "note": "浪漫"},
            {"ta": "你是不是不想负责", "reply": "我要是不负责，现在就不会在这和你聊天", "score": 93, "note": "逻辑反驳"},
            {"ta": "那你说个时间", "reply": "给我三个月，我还你一个答案", "score": 96, "note": "给出承诺"},
            {"ta": "三个月？", "reply": "三个月不够？那两个月？", "score": 90, "note": "退让"},
            {"ta": "你是不是有别人", "reply": "我要是有别人，还会天天找你吗？", "score": 94, "note": "反问证明"},
            {"ta": "谁知道你", "reply": "你慢慢就知道我是什么样的人了", "score": 92, "note": "耐心"},
            {"ta": "好吧信你一次", "reply": "不会让你失望的~", "score": 93, "note": "承诺"},
            {"ta": "哼", "reply": "别哼了，笑一个给我看~", "score": 89, "note": "调情"},
            {"ta": "才不要", "reply": "不要就算了，那我笑给你看~", "score": 90, "note": "退中求进"},
            {"ta": "哈哈", "reply": "你笑起来真好看", "score": 92, "note": "赞美"},
            {"ta": "油嘴滑舌", "reply": "只对你油嘴滑舌~", "score": 93, "note": "专属感"},
            {"ta": "晚安", "reply": "晚安，梦里继续我们的故事~", "score": 91, "note": "浪漫"},
            {"ta": "早安", "reply": "早呀，今天也要开心~", "score": 90, "note": "关心"},
            {"ta": "想你", "reply": "我也想你，比昨天更多", "score": 94, "note": "甜蜜"},
            {"ta": "爱你", "reply": "我也爱你，等我好消息~", "score": 93, "note": "回应 + 承诺"},
            {"ta": "等你", "reply": "不会让你等太久的~", "score": 94, "note": "安抚收尾"}
        ]
    },
    {
        "id": 3,
        "title": "情绪测试 - 你是不是只对我这样",
        "description": "女生测试男生是不是中央空调",
        "conversations": [
            {"ta": "你是不是对谁都这么好", "reply": "你觉得呢？", "score": 90, "note": "反问"},
            {"ta": "我就是不知道", "reply": "那你感觉我对别人怎么样？", "score": 89, "note": "继续反问"},
            {"ta": "感觉你对谁都好", "reply": "那可能是你感觉错了~", "score": 88, "note": "否定"},
            {"ta": "真的吗", "reply": "真的，我对别人可没这么好", "score": 93, "note": "确认"},
            {"ta": "我才不信", "reply": "不信就算了，反正我只对你这样", "score": 92, "note": "无所谓态度"},
            {"ta": "哼", "reply": "哼什么，我说的是实话", "score": 89, "note": "坚持"},
            {"ta": "那你证明给我看", "reply": "怎么证明？把我自己给你？", "score": 94, "note": "调情"},
            {"ta": "你想得美", "reply": "是你说让我证明的~", "score": 91, "note": "装无辜"},
            {"ta": "我不管", "reply": "那你想怎么样？", "score": 88, "note": "给主动权"},
            {"ta": "你说呢", "reply": "我觉得你是在撒娇对不对？", "score": 92, "note": "重新定义"},
            {"ta": "才不是", "reply": "那就是在暗示我什么~", "score": 91, "note": "继续曲解"},
            {"ta": "你讨厌", "reply": "讨厌我还和我聊这么久？", "score": 93, "note": "逻辑反击"},
            {"ta": "哼", "reply": "好啦不逗你了，我请你吃饭好不好？", "score": 92, "note": "给台阶"},
            {"ta": "好呀", "reply": "那就这么说定了~", "score": 91, "note": "确认"},
            {"ta": "去哪吃", "reply": "听你的，你选地方我买单", "score": 93, "note": "大方"},
            {"ta": "你请客？", "reply": "不然呢？还能让你请？", "score": 94, "note": "绅士"},
            {"ta": "哈哈", "reply": "笑什么，我像是那种人吗？", "score": 90, "note": "互动"},
            {"ta": "不像", "reply": "那像什么样？", "score": 89, "note": "好奇"},
            {"ta": "像好人", "reply": "好人卡？我不要~", "score": 91, "note": "拒绝发卡"},
            {"ta": "哈哈爱你", "reply": "这就对了，多笑笑~", "score": 93, "note": "甜蜜收尾"}
        ]
    },
    {
        "id": 4,
        "title": "安全感测试 - 你喜欢我什么",
        "description": "女生问喜欢她什么，测试男生是否真心",
        "conversations": [
            {"ta": "你喜欢我什么", "reply": "喜欢你自己都不知道的样子", "score": 94, "note": "神秘感"},
            {"ta": "这算什么回答", "reply": "那你想要什么回答？列个清单？", "score": 91, "note": "调皮"},
            {"ta": "对啊你说说看", "reply": "说三天三夜都说不完", "score": 93, "note": "夸张"},
            {"ta": "那你现在就说", "reply": "现在？你确定要听？", "score": 90, "note": "拖延"},
            {"ta": "确定", "reply": "好，第一：你问这个问题的时候很可爱", "score": 95, "note": "当下赞美"},
            {"ta": "然后呢", "reply": "然后：和你聊天很开心", "score": 92, "note": "感受"},
            {"ta": "没了？", "reply": "这才两个，你还要听几个？", "score": 90, "note": "调情"},
            {"ta": "全部", "reply": "全部？那得用一辈子慢慢说", "score": 96, "note": "承诺"},
            {"ta": "油嘴滑舌", "reply": "这是真心话", "score": 93, "note": "认真"},
            {"ta": "谁知道真假", "reply": "时间会证明的", "score": 94, "note": "耐心"},
            {"ta": "那要多久", "reply": "你想要多久就多久", "score": 92, "note": "顺从"},
            {"ta": "好吧", "reply": "那就相信我一次", "score": 93, "note": "请求"},
            {"ta": "我尽量", "reply": "不用尽量，顺其自然就好~", "score": 91, "note": "减压"},
            {"ta": "嗯", "reply": "乖~", "score": 89, "note": "宠溺"},
            {"ta": "别叫我乖", "reply": "那叫什么？宝贝？", "score": 92, "note": "升级称呼"},
            {"ta": "你讨厌", "reply": "好好好，不叫了~", "score": 90, "note": "退让"},
            {"ta": "哼", "reply": "别生气了，我错了还不行吗", "score": 91, "note": "道歉"},
            {"ta": "这还差不多", "reply": "那你原谅我了吗？", "score": 90, "note": "确认"},
            {"ta": "原谅你了", "reply": "太好了~爱你", "score": 93, "note": "甜蜜"},
            {"ta": "晚安", "reply": "晚安宝贝，梦里见~", "score": 94, "note": "浪漫收尾"}
        ]
    },
    {
        "id": 5,
        "title": "前任测试 - 你谈过几个",
        "description": "女生问男生的感情史，测试是否坦诚",
        "conversations": [
            {"ta": "你谈过几个女朋友", "reply": "怎么突然问这个？", "score": 92, "note": "缓冲"},
            {"ta": "就是好奇", "reply": "好奇这个干嘛？", "score": 90, "note": "继续缓冲"},
            {"ta": "你说说嘛", "reply": "说多了你介意，说少了你不信", "score": 94, "note": "两难"},
            {"ta": "我不介意", "reply": "真的不介意？", "score": 91, "note": "确认"},
            {"ta": "真的", "reply": "那我说了：谈过两个", "score": 93, "note": "坦诚"},
            {"ta": "两个？", "reply": "嗯，两个，都过去了", "score": 94, "note": "强调过去"},
            {"ta": "为什么分手", "reply": "不合适，性格不合", "score": 90, "note": "简单带过"},
            {"ta": "哪里不合适", "reply": "都过去了，重要的是现在", "score": 93, "note": "转移当下"},
            {"ta": "你现在喜欢我吗", "reply": "喜欢，不然不会和你说这些", "score": 95, "note": "确认"},
            {"ta": "那你会想她们吗", "reply": "不会，我眼里只有你", "score": 96, "note": "专一"},
            {"ta": "真的吗", "reply": "比真金还真", "score": 92, "note": "强调"},
            {"ta": "我才不信", "reply": "不信我证明给你看", "score": 93, "note": "行动"},
            {"ta": "怎么证明", "reply": "用我的余生来证明", "score": 97, "note": "承诺"},
            {"ta": "太夸张了", "reply": "一点都不夸张，我是认真的", "score": 94, "note": "坚持"},
            {"ta": "好吧", "reply": "那就相信我一次好不好？", "score": 93, "note": "请求"},
            {"ta": "我尽量", "reply": "不用尽量，我会让你慢慢相信的", "score": 94, "note": "耐心"},
            {"ta": "嗯", "reply": "乖~别想太多了", "score": 91, "note": "安抚"},
            {"ta": "知道了", "reply": "那就好，我们聊点开心的", "score": 90, "note": "转移"},
            {"ta": "好呀", "reply": "说明天吃什么好不好？", "score": 89, "note": "日常"},
            {"ta": "爱你", "reply": "我也爱你，别担心了~", "score": 95, "note": "甜蜜收尾"}
        ]
    },
]


# ==================== 海王场景 - 真实刁钻版 ====================

PLAYER_CHALLENGING_SCENARIOS = [
    {
        "id": 1,
        "title": "同时被多个女生质问",
        "description": "海王同时撩多个女生，被其中一个发现后质问",
        "conversations": [
            {"ta": "你是不是有别人了", "reply": "没有啊，怎么突然这么问", "score": 85, "note": "否认"},
            {"ta": "我都看到了", "reply": "看到什么了？", "score": 84, "note": "装傻"},
            {"ta": "你和别人聊天", "reply": "我和很多人聊天啊", "score": 83, "note": "模糊"},
            {"ta": "我是说别的女生", "reply": "朋友而已，你想多了", "score": 84, "note": "重新定义"},
            {"ta": "朋友？", "reply": "对啊，就是普通朋友", "score": 83, "note": "坚持"},
            {"ta": "那你为什么对她那么好", "reply": "我对谁都这样啊", "score": 82, "note": "承认中央空调"},
            {"ta": "所以你对我也这样？", "reply": "你不一样", "score": 86, "note": "特殊化"},
            {"ta": "哪里不一样", "reply": "你在我心里很重要", "score": 85, "note": "安抚"},
            {"ta": "多重要", "reply": "比所有人都重要", "score": 84, "note": "继续安抚"},
            {"ta": "我才不信", "reply": "不信就算了，反正我说的是真的", "score": 83, "note": "无所谓"},
            {"ta": "哼", "reply": "别生气了，乖~", "score": 85, "note": "转移"},
            {"ta": "别碰我", "reply": "好好好，不碰你~", "score": 84, "note": "退让"},
            {"ta": "你是不是不爱我了", "reply": "别胡思乱想了", "score": 82, "note": "回避"},
            {"ta": "那你证明给我看", "reply": "怎么证明？", "score": 83, "note": "反问"},
            {"ta": "删了她", "reply": "没必要吧，就是普通朋友", "score": 81, "note": "拒绝"},
            {"ta": "你舍不得？", "reply": "不是舍不得，是不想这样", "score": 82, "note": "解释"},
            {"ta": "为什么", "reply": "这样太小气了", "score": 80, "note": "倒打一耙"},
            {"ta": "我小气？", "reply": "我不是这个意思", "score": 83, "note": "缓和"},
            {"ta": "你就是", "reply": "好好好，你说什么就是什么", "score": 82, "note": "敷衍"},
            {"ta": "晚安", "reply": "晚安，别想太多了~", "score": 84, "note": "结束话题"}
        ]
    },
    {
        "id": 2,
        "title": "被要求公开关系",
        "description": "女生要求海王公开关系，海王各种推脱",
        "conversations": [
            {"ta": "我们在一起多久了", "reply": "怎么突然问这个？", "score": 84, "note": "缓冲"},
            {"ta": "就是想知道", "reply": "三个月了吧", "score": 83, "note": "承认"},
            {"ta": "那为什么不公开", "reply": "公开什么？", "score": 82, "note": "装傻"},
            {"ta": "公开我们的关系啊", "reply": "这样挺好的啊", "score": 83, "note": "维持现状"},
            {"ta": "哪里好了", "reply": "自由自在的不好吗？", "score": 82, "note": "偷换概念"},
            {"ta": "我想要一个名分", "reply": "名分有那么重要吗？", "score": 81, "note": "贬低价值"},
            {"ta": "很重要", "reply": "可是我不想被束缚", "score": 82, "note": "表达需求"},
            {"ta": "那你是不喜欢我吗", "reply": "喜欢啊，不然不会在一起", "score": 84, "note": "承认"},
            {"ta": "那为什么不能公开", "reply": "我觉得感情是两个人的事", "score": 83, "note": "道理"},
            {"ta": "我不这么认为", "reply": "那你想怎么样？", "score": 81, "note": "反问"},
            {"ta": "我想公开", "reply": "给我点时间好不好？", "score": 85, "note": "拖延"},
            {"ta": "多久", "reply": "等我准备好了", "score": 82, "note": "模糊"},
            {"ta": "什么时候算准备好", "reply": "很快，相信我", "score": 84, "note": "承诺"},
            {"ta": "好吧", "reply": "乖~不会让你失望的", "score": 85, "note": "安抚"},
            {"ta": "嗯", "reply": "别想太多了，我们出去玩好不好？", "score": 84, "note": "转移"},
            {"ta": "好呀", "reply": "那你想去哪？", "score": 83, "note": "顺从"},
            {"ta": "随便", "reply": "那我安排~", "score": 84, "note": "主动"},
            {"ta": "爱你", "reply": "我也爱你~", "score": 85, "note": "回应"},
            {"ta": "晚安", "reply": "晚安宝贝~", "score": 85, "note": "甜蜜收尾"},
            {"ta": "记得想我", "reply": "一定一定~", "score": 86, "note": "承诺"}
        ]
    },
    {
        "id": 3,
        "title": "被问爱不爱我",
        "description": "女生问海王爱不爱她，海王回避正面回答",
        "conversations": [
            {"ta": "你爱我吗", "reply": "怎么突然问这个？", "score": 83, "note": "缓冲"},
            {"ta": "就是想知道", "reply": "你觉得呢？", "score": 82, "note": "反问"},
            {"ta": "我不知道", "reply": "那你感觉呢？", "score": 81, "note": "继续反问"},
            {"ta": "感觉你爱我", "reply": "那就对了~", "score": 84, "note": "承认但不明确"},
            {"ta": "真的吗", "reply": "当然是真的", "score": 83, "note": "确认"},
            {"ta": "那你再说一遍", "reply": "说什么？", "score": 81, "note": "装傻"},
            {"ta": "说你爱我", "reply": "我爱你...才怪~", "score": 82, "note": "开玩笑"},
            {"ta": "哼", "reply": "别生气嘛，开玩笑的", "score": 84, "note": "安抚"},
            {"ta": "我不开心", "reply": "那我要怎么做你才开心？", "score": 83, "note": "给主动权"},
            {"ta": "你说爱我", "reply": "好，我爱你行了吧~", "score": 85, "note": "勉强"},
            {"ta": "不真诚", "reply": "怎么会不真诚呢？", "score": 82, "note": "否认"},
            {"ta": "就是感觉不真诚", "reply": "那你要我怎么做才信？", "score": 81, "note": "无奈"},
            {"ta": "用行动证明", "reply": "什么行动？", "score": 82, "note": "反问"},
            {"ta": "你自己想", "reply": "我想不出来，你告诉我", "score": 81, "note": "耍赖"},
            {"ta": "你讨厌", "reply": "好啦不逗你了~", "score": 84, "note": "认真"},
            {"ta": "哼", "reply": "别生气了，我请你吃饭好不好？", "score": 85, "note": "补偿"},
            {"ta": "好呀", "reply": "那你想吃什么？", "score": 84, "note": "顺从"},
            {"ta": "随便", "reply": "那我带你去吃好吃的~", "score": 85, "note": "主动"},
            {"ta": "爱你", "reply": "我也爱你~", "score": 86, "note": "回应"},
            {"ta": "晚安", "reply": "晚安宝贝~", "score": 85, "note": "甜蜜收尾"}
        ]
    },
    {
        "id": 4,
        "title": "被要求删掉其他女生",
        "description": "女生发现海王微信里有很多女生，要求删掉",
        "conversations": [
            {"ta": "你微信里怎么这么多女生", "reply": "都是朋友啊", "score": 82, "note": "正常化"},
            {"ta": "朋友？", "reply": "对啊，同学同事什么的", "score": 83, "note": "解释"},
            {"ta": "那你为什么和她们聊那么开心", "reply": "就是正常聊天啊", "score": 82, "note": "淡化"},
            {"ta": "我不喜欢", "reply": "别这样嘛", "score": 81, "note": "安抚"},
            {"ta": "你删了她们", "reply": "没必要吧", "score": 80, "note": "拒绝"},
            {"ta": "为什么没必要", "reply": "都是朋友，删了多不好", "score": 81, "note": "道理"},
            {"ta": "那我呢", "reply": "你不一样啊", "score": 84, "note": "特殊化"},
            {"ta": "哪里不一样", "reply": "你是我最重要的人", "score": 85, "note": "安抚"},
            {"ta": "那你为什么不删她们", "reply": "我和她们真的没什么", "score": 82, "note": "坚持"},
            {"ta": "我不信", "reply": "不信我怎么办？", "score": 81, "note": "无奈"},
            {"ta": "你删了我就信", "reply": "一定要这样吗？", "score": 82, "note": "拖延"},
            {"ta": "对", "reply": "那...我考虑一下", "score": 83, "note": "缓兵之计"},
            {"ta": "多久", "reply": "过几天好不好？", "score": 82, "note": "拖延"},
            {"ta": "好吧", "reply": "乖~别生气了", "score": 84, "note": "安抚"},
            {"ta": "哼", "reply": "别哼了，笑一个~", "score": 83, "note": "调情"},
            {"ta": "才不要", "reply": "那我给你讲个笑话好不好？", "score": 84, "note": "转移"},
            {"ta": "好呀", "reply": "从前有个人...", "score": 83, "note": "开始讲故事"},
            {"ta": "然后呢", "reply": "然后他就消失了~", "score": 82, "note": "敷衍"},
            {"ta": "哈哈", "reply": "你笑起来真好看", "score": 85, "note": "赞美"},
            {"ta": "爱你", "reply": "我也爱你~", "score": 86, "note": "甜蜜收尾"}
        ]
    },
    {
        "id": 5,
        "title": "被质问为什么不回消息",
        "description": "海王长时间不回消息，被女生质问",
        "conversations": [
            {"ta": "你为什么不回我消息", "reply": "在忙啊", "score": 80, "note": "简单解释"},
            {"ta": "忙到一天都不看手机？", "reply": "真的在忙", "score": 79, "note": "坚持"},
            {"ta": "忙什么", "reply": "工作啊", "score": 78, "note": "具体化"},
            {"ta": "工作忙到连回消息的时间都没有？", "reply": "你也知道我这工作忙", "score": 81, "note": "共情"},
            {"ta": "我知道", "reply": "那你还生气？", "score": 80, "note": "反问"},
            {"ta": "我就是不开心", "reply": "好啦我错了", "score": 83, "note": "道歉"},
            {"ta": "你错哪了", "reply": "错在没及时回你", "score": 84, "note": "承认"},
            {"ta": "还有呢", "reply": "还有...让你不开心了", "score": 83, "note": "继续承认"},
            {"ta": "哼", "reply": "别生气了，我请你吃饭赔罪好不好？", "score": 85, "note": "补偿"},
            {"ta": "不要", "reply": "那你想怎么样？", "score": 82, "note": "给主动权"},
            {"ta": "我不想理你", "reply": "别这样嘛~", "score": 83, "note": "撒娇"},
            {"ta": "哼", "reply": "我下次一定及时回你", "score": 84, "note": "承诺"},
            {"ta": "真的吗", "reply": "当然是真的", "score": 83, "note": "确认"},
            {"ta": "我才不信", "reply": "不信我证明给你看", "score": 84, "note": "行动"},
            {"ta": "怎么证明", "reply": "以后秒回你", "score": 85, "note": "承诺"},
            {"ta": "哼", "reply": "别哼了，原谅我好不好？", "score": 84, "note": "请求"},
            {"ta": "好吧", "reply": "太好了~爱你", "score": 86, "note": "甜蜜"},
            {"ta": "晚安", "reply": "晚安宝贝~", "score": 85, "note": "浪漫"},
            {"ta": "记得想我", "reply": "一定一定~", "score": 86, "note": "承诺"},
            {"ta": "爱你", "reply": "我也爱你~", "score": 87, "note": "甜蜜收尾"}
        ]
    },
]


# ==================== 生成完整数据集 ====================

def generate_full_dataset_v12():
    """生成 V12 完整数据集"""
    dataset = {
        "version": "12.0",
        "created_at": datetime.now().isoformat(),
        "description": "高情商回复数据集 V12.0 - 真实刁钻场景版，包含废物测试、框架博弈、情绪操控等",
        "lover_challenging_scenarios": LOVER_CHALLENGING_SCENARIOS,
        "player_challenging_scenarios": PLAYER_CHALLENGING_SCENARIOS,
    }
    return dataset


# ==================== 生成 HTML 报告 ====================

def generate_html_report_v12(dataset):
    """生成 HTML 格式报告 V12"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高情商回复数据集 V12.0 - 真实刁钻场景版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ text-align: center; color: white; margin-bottom: 10px; font-size: 36px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .subtitle {{ text-align: center; color: rgba(255,255,255,0.9); margin-bottom: 30px; font-size: 16px; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; margin-bottom: 40px; flex-wrap: wrap; }}
        .stat-card {{ background: rgba(255,255,255,0.95); padding: 25px 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }}
        .stat-number {{ font-size: 42px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stat-label {{ font-size: 14px; color: #666; margin-top: 8px; font-weight: 500; }}
        .section {{ margin-bottom: 50px; }}
        .section-title {{ font-size: 28px; color: white; margin-bottom: 25px; padding-left: 20px; border-left: 5px solid white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .scenario {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }}
        .scenario-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }}
        .scenario-title {{ font-size: 20px; font-weight: bold; color: #333; }}
        .scenario-style {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 20px; border-radius: 25px; font-size: 13px; font-weight: 600; }}
        .scenario-desc {{ color: #666; margin-bottom: 20px; font-size: 14px; line-height: 1.6; }}
        .conversation-table {{ width: 100%; border-collapse: collapse; }}
        .conversation-table th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; text-align: left; font-weight: 600; color: white; }}
        .conversation-table td {{ padding: 15px; border-bottom: 1px solid #f0f0f0; }}
        .conversation-table tr:hover {{ background: #f8f9fa; }}
        .ta-message {{ background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 10px 18px; border-radius: 12px; display: inline-block; font-weight: 500; color: #1976d2; }}
        .reply-message {{ background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%); padding: 10px 18px; border-radius: 12px; display: inline-block; font-weight: 500; color: #388e3c; }}
        .score {{ font-weight: bold; padding: 5px 12px; border-radius: 20px; display: inline-block; font-size: 13px; }}
        .score-high {{ background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); color: white; }}
        .score-medium {{ background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%); color: white; }}
        .score-low {{ background: linear-gradient(135deg, #f44336 0%, #e91e63 100%); color: white; }}
        .note {{ color: #666; font-size: 13px; font-style: italic; }}
        .lover {{ border-left: 5px solid #e91e63; }}
        .player {{ border-left: 5px solid #9c27b0; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.8); margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💕 高情商回复数据集 V12.0</h1>
        <p class="subtitle">真实刁钻场景版 | 废物测试 × 框架博弈 × 情绪操控 | 男女极限拉扯案例</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(dataset['lover_challenging_scenarios'])}</div>
                <div class="stat-label">恋爱刁钻场景</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(dataset['player_challenging_scenarios'])}</div>
                <div class="stat-label">海王应对场景</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(dataset['lover_challenging_scenarios']) * 20 + len(dataset['player_challenging_scenarios']) * 20}</div>
                <div class="stat-label">总对话轮数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dataset['version']}</div>
                <div class="stat-label">数据集版本</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💕 恋爱刁钻场景 (废物测试/框架博弈/情绪操控)</h2>
"""
    
    for scenario in dataset['lover_challenging_scenarios']:
        html += f"""
            <div class="scenario lover">
                <div class="scenario-header">
                    <div class="scenario-title">#{scenario['id']} {scenario['title']}</div>
                    <div class="scenario-style">{scenario['description'].split('，')[0]}</div>
                </div>
                <p class="scenario-desc">{scenario['description']}</p>
                <table class="conversation-table">
                    <thead>
                        <tr>
                            <th width="5%">轮次</th>
                            <th width="30%">对方消息</th>
                            <th width="35%">高情商回复</th>
                            <th width="10%">打分</th>
                            <th width="20%">备注</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for i, conv in enumerate(scenario['conversations'], 1):
            score_class = "score-high" if conv['score'] >= 90 else ("score-medium" if conv['score'] >= 85 else "score-low")
            html += f"""
                        <tr>
                            <td>{i}</td>
                            <td><span class="ta-message">{conv['ta']}</span></td>
                            <td><span class="reply-message">{conv['reply']}</span></td>
                            <td><span class="score {score_class}">{conv['score']}分</span></td>
                            <td class="note">{conv['note']}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += """
        </div>
        
        <div class="section">
            <h2 class="section-title">🌊 海王应对场景 (同时撩多个/不公开/不负责)</h2>
"""
    
    for scenario in dataset['player_challenging_scenarios']:
        html += f"""
            <div class="scenario player">
                <div class="scenario-header">
                    <div class="scenario-title">#{scenario['id']} {scenario['title']}</div>
                    <div class="scenario-style">{scenario['description'].split('，')[0]}</div>
                </div>
                <p class="scenario-desc">{scenario['description']}</p>
                <table class="conversation-table">
                    <thead>
                        <tr>
                            <th width="5%">轮次</th>
                            <th width="30%">对方消息</th>
                            <th width="35%">海王回复</th>
                            <th width="10%">打分</th>
                            <th width="20%">备注</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for i, conv in enumerate(scenario['conversations'], 1):
            score_class = "score-high" if conv['score'] >= 85 else ("score-medium" if conv['score'] >= 80 else "score-low")
            html += f"""
                        <tr>
                            <td>{i}</td>
                            <td><span class="ta-message">{conv['ta']}</span></td>
                            <td><span class="reply-message">{conv['reply']}</span></td>
                            <td><span class="score {score_class}">{conv['score']}分</span></td>
                            <td class="note">{conv['note']}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>生成时间：{dataset['created_at']} | 数据集版本：{dataset['version']}</p>
            <p>高情商回复助手 V12.0 - 真实刁钻场景版 | 男女极限拉扯案例库</p>
        </div>
    </div>
</body>
</html>
"""
    return html


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("高情商回复数据集 V12.0 - 真实刁钻场景版")
    print("=" * 60)
    
    print("\n正在生成数据集...")
    dataset = generate_full_dataset_v12()
    
    # 保存 JSON
    json_path = "conversation_dataset_v12.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 数据集已保存：{json_path}")
    
    # 生成 HTML 报告
    print("\n正在生成 HTML 报告...")
    html_content = generate_html_report_v12(dataset)
    html_path = "conversation_dataset_v12.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ HTML 报告已保存：{html_path}")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("数据集统计信息")
    print("=" * 60)
    print(f"恋爱刁钻场景：{len(dataset['lover_challenging_scenarios'])} 组")
    print(f"海王应对场景：{len(dataset['player_challenging_scenarios'])} 组")
    print(f"总对话轮数：{len(dataset['lover_challenging_scenarios']) * 20 + len(dataset['player_challenging_scenarios']) * 20}")
    print(f"数据集版本：{dataset['version']}")
    print(f"生成时间：{dataset['created_at']}")
    print("=" * 60)
    
    # 计算平均分
    lover_scores = [conv['score'] for scenario in dataset['lover_challenging_scenarios'] for conv in scenario['conversations']]
    player_scores = [conv['score'] for scenario in dataset['player_challenging_scenarios'] for conv in scenario['conversations']]
    
    print(f"\n恋爱场景平均分：{sum(lover_scores)/len(lover_scores):.1f}分")
    print(f"海王场景平均分：{sum(player_scores)/len(player_scores):.1f}分")
    print(f"总体平均分：{(sum(lover_scores)+sum(player_scores))/(len(lover_scores)+len(player_scores)):.1f}分")
    print("=" * 60)
    
    print("\n✅ 数据集生成完成！")
    print(f"\n查看方式:")
    print(f"1. 本地打开 HTML 报告：open {html_path}")
