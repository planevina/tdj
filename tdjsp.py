import re
import os
import random
import urllib.request,urllib.error
import string
from matplotlib import cm
from nonebot import MessageSegment as ms
from PIL import ImageDraw, Image, ImageFont


from hoshino import Service, util
from hoshino.typing import MessageSegment, CQEvent
from matplotlib import pyplot as plt
from hoshino.util import pic2b64
from .sp_data import ssrsp
FILE_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(FILE_PATH,'icon')

sv_help = '''
'''
plt.style.use('seaborn-pastel')
plt.rcParams['font.family'] = ['DejaVuSans', 'Microsoft YaHei', 'SimSun', ]
sv = Service('天地劫饰品制作',help_=sv_help, bundle='天地劫')


def getJob(job):
    jobArr = ['侠客','羽士','铁卫','咒师','祝由','御风']
    if job.find("0") == -1:
        return "全职业"
    else:
        rtn = []
        for i in range(len(job)):
            if job[i]=="1":
                rtn.append(jobArr[i])
        return "、".join(rtn)


def makePic(sp):
    img = Image.open(os.path.join(ICON_PATH, "bg.png"))
    if not os.path.exists(os.path.join(ICON_PATH, f"{sp['icon']}.png")):
        s=urllib.parse.quote(f"https://media.zlongame.com/media/news/cn/tdj/info/data/accessories/{sp['icon']}.png",safe=string.printable)
        urllib.request.urlretrieve(s,os.path.join(ICON_PATH, f"{sp['icon']}.png"))
    spicon = Image.open(os.path.join(ICON_PATH, f"{sp['icon']}.png")).resize((100, 100), Image.ANTIALIAS)
    draw = ImageDraw.Draw(img)
    ttfront = ImageFont.truetype('simkai',18)  # 设置字体暨字号
    titlefont = ImageFont.truetype('simkai',28)
    title_width, title_height = draw.textsize(sp["name"], titlefont)
    draw.text(((478-title_width)/2, 20), sp["name"], fill="#554241",font=titlefont)
    sum_width = 0
    line_count = 0
    duanluo = ""
    for char in sp["description"]:
        width, height = draw.textsize(char, ttfront)
        sum_width += width
        if sum_width > 414 or char=="\n": 
            draw.text((26, 205+line_count*22), duanluo, fill="#554241",font=ttfront)
            line_count += 1
            sum_width = 0
            duanluo = char if char != "\n" else ""
        else:
            duanluo += char
    if duanluo != "":
        draw.text((26, 205+line_count*22), duanluo, fill="#554241",font=ttfront)
    draw.text((16, 320), f'职业限定：{getJob(sp["job"])}', fill="#554241",font=ttfront)
    draw.text((16, 350), f'隐藏等级：绝{sp["lv"]*"+"}', fill="#554241",font=ttfront)
    img.paste(spicon,(190,70),spicon)
    return img

@sv.on_fullmatch('饰品帮助', only_to_me=False)
async def send_tdjchelp(bot, ev):
    await bot.send(ev, sv_help)


@sv.on_prefix(('饰品制作'))
async def ss_rate(bot, ev):
    txt = ev.message.extract_plain_text().strip()
    if not txt:
        await bot.finish(ev, '请在后面跟部位：头/身/腰/手', at_sender=True)
    pos = "0"
    if txt=="头":
        pos = "1"
    elif txt=="身":
        pos = "2"
    elif txt=="腰":
        pos = "3"
    elif txt=="手":
        pos = "4"

    if pos == "0":
        await bot.finish(ev, '请在后面跟部位：头/身/腰/手', at_sender=True)
    r = random.randint(1,100)
    splv = 0 if r<80 else (1 if r <99 else 2)
    sppool = [x for x in ssrsp if x["position"]==pos and x["lv"] == splv]
    if len(sppool)<=0:
        await bot.finish(ev, '出错了，获取饰品数据失败', at_sender=True)
    
    sp = random.choice(sppool)
    #生成饰品图片
    sppic = makePic(sp)
    res = pic2b64(sppic)
    await bot.finish(ev, f'\n{ms.image(res)}', at_sender=True)