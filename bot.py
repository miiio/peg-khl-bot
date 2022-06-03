from time import sleep
from xmlrpc.client import boolean
from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
import json
import logging
import random
from dld import DLD
import asyncio

dlds = {}
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
        Module.Section(Struct.Paragraph(2, Element.Text("**当前版本**\nV0.0.1", type="kmarkdown"), Element.Text("**全部命令**\n     -", type="kmarkdown"))),
        Module.Divider(),
        Module.Section('指令说明'),
        Module.Section(Element.Text("`/dld-init <@用户>` 初始化参与的玩家\n`/dld-rr <重随次数>` 设置每位玩家每回合重随次数\n`/dld-go <英雄数量> <是否允许重复0/1>` 开始生成随机英雄", type="kmarkdown")),
        Module.Divider(),
        Module.Context('划水娱乐群Bot v0.0.1')
    )
    await msg.ctx.channel.send(CardMessage(card_help))


@bot.command(name='dld-go')
async def dld_sj(msg: Message, hero_num: int, rep: int=0):
    if msg.author_id not in dlds:
        await msg.reply("请先使用 /dld-player 命令设置参与的玩家。")
        return
    dld = dlds[msg.author_id]
    result = dld.random_heros(hero_num, rep)
    for player in result.keys():
        heros = result[player]
        heros_pic = [Element.Image(h['pic_url']) for h in heros]
        reroll_cnt = dld.reroll[player]
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

@bot.command(name='dld-init')
async def dld_player(msg: Message, *players):
    admin = msg.author_id
    ps = []
    for p in players:
        id_str = p.replace('(met)','')
        if not id_str.isalnum(): continue
        ps.append(id_str)
    print(ps, admin)
    dld = DLD(ps, admin)
    dlds[admin] = dld
    global cur_channel
    cur_channel = msg.ctx.channel


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def btn(_: Bot, e: Event):
    player = e.body['user_id'] #点击按钮的用户id
    # print(f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill''')
    if "reroll:" in e.body['value']:
        admin = e.body['value'][7:] #创建这次大乱斗的用户id
        # re-roll
        if admin not in dlds:
            return
        dld = dlds[admin]
        heros = dld.re_roll(player)
        heros_pic = [Element.Image(h['pic_url']) for h in heros]
        reroll_cnt = dld.reroll[player]
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


@bot.command(name='dld-rr')
async def dld_rr(msg: Message, cnt:int=0):
    if msg.author_id not in dlds:
        await msg.reply("请先使用 /dld-player 命令设置参与的玩家。")
        return
    dld = dlds[msg.author_id]
    dld.set_reroll_cnt(cnt)
    await msg.reply("设置每人每局re-roll次数为：%d"%cnt)

@bot.command(name='dld-hc')
async def dld_hc(msg: Message, cnt:int=0):
    if msg.author_id not in dlds:
        await msg.reply("请先使用 /dld-player 命令设置参与的玩家。")
        return
    dld = dlds[msg.author_id]
    dld.set_per_hero_num(cnt)
    await msg.reply("设置每人每局可选英雄数为：%d"%cnt)

# everything done, go ahead now!
logging.basicConfig(level='INFO')
bot.command.update_prefixes('.', '/')
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)