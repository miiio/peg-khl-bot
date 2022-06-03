from time import sleep
from xmlrpc.client import boolean
from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
import json
import logging
import random
from aram import ARAM
import asyncio

arams = {}
cur_channel = None

# init Bot
with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
bot = Bot(token=config['token'])

# register command, send `/hello` in channel to invoke
@bot.command(name='h')
async def help(msg: Message):
    card_help = Card(
        Module.Header('划水娱乐群Bot-命令手册'), 
        Module.Divider(),
        Module.Section(Struct.Paragraph(3, Element.Text("**当前版本**\nV0.0.1", type="kmarkdown"), Element.Text("**全部命令**\n     -", type="kmarkdown"), Element.Text("**Github**\n[peg-khl-bot](https://github.com/miiio/peg-khl-bot)", type="kmarkdown"))),
        Module.Divider(),
        Module.Section('指令说明'),
        Module.Section(Element.Text("`/aram-init <@用户>` 初始化参与的玩家\n`/aram-rr <重随次数>` 设置每位玩家每回合重随次数\n`/aram-go <英雄数量> <是否允许重复0/1>` 开始生成随机英雄", type="kmarkdown")),
        Module.Divider(),
        Module.Context('划水娱乐群Bot v0.0.1')
    )
    await msg.ctx.channel.send(CardMessage(card_help))


@bot.command(name='aram-go')
async def aram_go(msg: Message, hero_num: int, rep: int=0):
    if msg.author_id not in arams:
        await msg.reply("请先使用 /aram-player 命令设置参与的玩家。")
        return
    aram = arams[msg.author_id]
    result = aram.random_heros(hero_num, rep)
    for player in result.keys():
        heros = result[player]
        heros_pic = [Element.Image(h['pic_url']) for h in heros]
        reroll_cnt = aram.reroll[player]
        card_args = [
            Module.ImageGroup(*heros_pic),
        ]
        if reroll_cnt > 0:
            card_args.extend([
                Module.Divider(),
                Module.Section("Re-roll (剩余%d次机会)"%reroll_cnt, mode=Types.SectionMode.RIGHT, accessory=Element.Button("Re-roll",value="reroll:"+msg.author_id, theme="primary"))
            ])
        card_sj = Card(*card_args, size=Types.Size.SM)
        await msg.ctx.channel.send(CardMessage(card_sj), temp_target_id=player)

@bot.command(name='aram-init')
async def aram_player(msg: Message, *players):
    admin = msg.author_id
    ps = []
    for p in players:
        id_str = p.replace('(met)','')
        if not id_str.isalnum(): continue
        ps.append(id_str)
    print(ps, admin)
    aram = ARAM(ps, admin)
    arams[admin] = aram
    global cur_channel
    cur_channel = msg.ctx.channel
    await msg.reply("共%d位玩家参与大乱斗"%len(ps))


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def btn(_: Bot, e: Event):
    player = e.body['user_id'] #点击按钮的用户id
    # print(f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill''')
    if "reroll:" in e.body['value']:
        admin = e.body['value'][7:] #创建这次大乱斗的用户id
        # re-roll
        if admin not in arams:
            return
        aram = arams[admin]
        heros = aram.re_roll(player)
        heros_pic = [Element.Image(h['pic_url']) for h in heros]
        reroll_cnt = aram.reroll[player]
        card_args = [
            Module.ImageGroup(*heros_pic),
        ]
        if reroll_cnt > 0:
            card_args.extend([
                Module.Divider(),
                Module.Section("Re-roll (剩余%d次机会)"%reroll_cnt, mode=Types.SectionMode.RIGHT, accessory=Element.Button("Re-roll",value="reroll:"+admin, theme="primary"))
            ])
        card_sj = Card(*card_args, size=Types.Size.SM)
        global cur_channel
        if cur_channel is not None:
            await cur_channel.send(CardMessage(card_sj), temp_target_id=player)


@bot.command(name='aram-rr')
async def aram_rr(msg: Message, cnt:int=0):
    if msg.author_id not in arams:
        await msg.reply("请先使用 /aram-player 命令设置参与的玩家。")
        return
    aram = arams[msg.author_id]
    aram.set_reroll_cnt(cnt)
    await msg.reply("设置每人每局re-roll次数为：%d"%cnt)

@bot.command(name='aram-hc')
async def aram_hc(msg: Message, cnt:int=0):
    if msg.author_id not in arams:
        await msg.reply("请先使用 /aram-player 命令设置参与的玩家。")
        return
    aram = arams[msg.author_id]
    aram.set_per_hero_num(cnt)
    await msg.reply("设置每人每局可选英雄数为：%d"%cnt)

# everything done, go ahead now!
logging.basicConfig(level='INFO')
bot.command.update_prefixes('.', '/')
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)