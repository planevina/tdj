import re
from hoshino import Service, util
from hoshino.typing import MessageSegment, CQEvent

sv_help = '''评分命令：[魂石评分 魂石数据] 
魂石属性简写为：
攻击、伤害、穿透、暴击、反伤、气血、物免、法免、物防、法防、暴抗
其中物攻法攻统称攻击，物伤法伤统称伤害
例如：魂石评分 天攻击4伤害10暴击4气血3
============================
预测命令：[魂石预测 词条列表]
例如：魂石预测 天攻击伤害暴击气血
============================
数据算法来自NGA作者“泡椒啊”的帖子
'''

sv = Service('天地劫魂石评分',help_=sv_help, bundle='天地劫')


ss_limit = {
    "天":{"攻击":10,"伤害":10,"穿透":10,"暴击":10,"反伤":10,"气血":5,"物免":5,"法免":5,"物防":5,"法防":5,"暴抗":5},
    "地":{"攻击":5,"伤害":5,"穿透":5,"暴击":5,"反伤":5,"气血":10,"物免":10,"法免":10,"物防":10,"法防":10,"暴抗":10},
    "荒":{"攻击":7,"伤害":7,"穿透":7,"暴击":7,"反伤":7,"气血":7,"物免":7,"法免":7,"物防":7,"法防":7,"暴抗":7}
}

ss_min = {
    "天":{"攻击":4,"伤害":4,"穿透":4,"暴击":4,"反伤":4,"气血":2,"物免":2,"法免":2,"物防":2,"法防":2,"暴抗":2},
    "地":{"攻击":2,"伤害":2,"穿透":2,"暴击":2,"反伤":2,"气血":4,"物免":4,"法免":4,"物防":4,"法防":4,"暴抗":4},
    "荒":{"攻击":3,"伤害":3,"穿透":3,"暴击":3,"反伤":3,"气血":3,"物免":3,"法免":3,"物防":3,"法防":3,"暴抗":3}
}

ss_score = {"攻击":11,"伤害":10,"穿透":6,"暴击":3,"反伤":0,"气血":7,"物免":5,"法免":5,"物防":1,"法防":1,"暴抗":0}


def ss_std(tp,score):
    if tp == "天":
        return "优质" if score > 164 else ("不错" if score > 109 else "一般")
    elif tp =="地":
        return "优质" if score > 143 else ("不错" if score > 92 else "一般")
    elif tp == "荒":
        return "优质" if score > 145 else ("不错" if score > 96 else "一般")
    else:
        return ""



@sv.on_fullmatch('评分帮助', only_to_me=False)
async def send_tdjchelp(bot, ev):
    await bot.send(ev, sv_help)


@sv.on_prefix(('魂石评分'))
async def ss_rate(bot, ev):
    txt = ev.message.extract_plain_text().strip()
    if not txt:
        await bot.finish(ev, '请在后面跟魂石数据\n示例：魂石评分 天攻击4伤害10暴击4气血3', at_sender=True)

    ss_type = txt[:1]
    if ss_type not in ss_limit.keys():
        await bot.finish(ev, '魂石数据不正确，缺少（天地荒）\n示例：魂石评分 天攻击4伤害10暴击4气血3', at_sender=True)
    score = 0
    errmsg = ''
    txt = txt[1:]
    while len(txt)>0:
        m = re.match(r'^(攻击|物攻|法攻|伤害|物伤|法伤|穿透|物穿|法穿|暴击|反伤|气血|物免|法免|物防|法防|暴抗)(10|[1-9])(\D|)',txt)
        if m is None:
            errmsg = "没有匹配到属性"
            break
        else:
            #判断属性是不是超了限制
            attr = m.group(1)
            if attr == "物攻" or attr == "法攻":
                attr = "攻击"
            elif attr == "物伤" or attr == "法伤":
                attr = "伤害"
            elif attr == "物穿" or attr == "法穿":
                attr = "穿透"

            if ss_limit[ss_type][attr] < int(m.group(2)) or ss_min[ss_type][attr] > int(m.group(2)):
                errmsg = f"{attr}词条的值{m.group(2)}不在{ss_type}魂石允许值范围内{ss_min[ss_type][attr]}-{ss_limit[ss_type][attr]}"
                break
            score += ss_score[attr]*int(m.group(2))
        txt = txt[len(attr)+len(m.group(2)):]

    if errmsg == '':
        await bot.finish(ev, f'\n得分：{score}\n评价：{ss_std(ss_type,score)}\n===评价标准===\n天：<110一般，110-164不错，165+优质\n地：<93一般，93-143不错，144+优质\n荒：<97一般，97-145不错，146+优质', at_sender=True)
    else:
        await bot.finish(ev, f'魂石数据不正确：{errmsg}\n示例：魂石评分 天攻击4伤害10暴击4气血3', at_sender=True)


@sv.on_prefix(('魂石预测'))
async def ss_yc(bot, ev):
    txt = ev.message.extract_plain_text().strip()
    if not txt:
        await bot.finish(ev, '请在后面跟魂石词条\n示例：魂石预测 天攻击伤害暴击气血', at_sender=True)

    ss_type = txt[:1]
    if ss_type not in ss_limit.keys():
        await bot.finish(ev, '魂石数据不正确，缺少（天地荒）\n示例：魂石预测 天攻击伤害暴击气血', at_sender=True)
    maxscore = 0
    minscore = 0
    avgscore = 0
    errmsg = ''
    txt = txt[1:]
    while len(txt)>0:
        m = re.match(r'^(攻击|物攻|法攻|伤害|物伤|法伤|穿透|物穿|法穿|暴击|反伤|气血|物免|法免|物防|法防|暴抗)',txt)
        if m is None:
            errmsg = "没有匹配到词条"
            break
        else:
            attr = m.group(1)
            if attr == "物攻" or attr == "法攻":
                attr = "攻击"
            elif attr == "物伤" or attr == "法伤":
                attr = "伤害"
            elif attr == "物穿" or attr == "法穿":
                attr = "穿透"
            maxscore +=ss_limit[ss_type][attr]*ss_score[attr]
            minscore +=ss_min[ss_type][attr]*ss_score[attr]
            avgscore +=(ss_limit[ss_type][attr]+ss_min[ss_type][attr])/2*ss_score[attr]
        txt = txt[len(attr):]

    if errmsg == '':
        await bot.finish(ev, f'\n===预测结果===\n最高分：{maxscore}，{ss_std(ss_type,maxscore)}\n平均分：{avgscore}，{ss_std(ss_type,avgscore)}\n最低分：{minscore}，{ss_std(ss_type,minscore)}\n===评价标准===\n天：<110一般，110-164不错，165+优质\n地：<93一般，93-143不错，144+优质\n荒：<97一般，97-145不错，146+优质', at_sender=True)
    else:
        await bot.finish(ev, f'魂石数据不正确：{errmsg}\n示例：魂石预测 天攻击伤害暴击气血', at_sender=True)
