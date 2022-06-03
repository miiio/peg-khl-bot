import json
import random

class ARAM():
    def __init__(self, players, admin):
        with open('./hero_list.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            self.hero_list = self.config['hero']
            self.reroll = {}

        self.players = players
        self.admin = admin
        self.reroll_cnt = 0
        self.per_hero_num = -1
        self.rep = 0


    def set_players(self, players):
        self.players = players

    def set_reroll_cnt(self, cnt):
        self.reroll_cnt = cnt

    def set_per_hero_num(self, num):
        self.per_hero_num = num

    def random_heros(self, hero_num=-1, rep=0):
        if hero_num == -1: hero_num = self.per_hero_num
        self.rep = rep
        self.per_hero_num = hero_num
        if rep==1:
            heros = []
            for i in range(len(self.players)):
                heros.extend(random.sample(self.hero_list, hero_num))
        else:
            heros = random.sample(self.hero_list, hero_num * len(self.players))

        self.pre_heros = heros
        self.reroll = {p:self.reroll_cnt for p in self.players}
        return {p:heros[i*hero_num:(i+1)*hero_num] for i,p in enumerate(self.players)}

    def re_roll(self, player):
        if self.reroll[player] <=0 :return
        self.reroll[player] -= 1
        heros = []
        while len(heros) < self.per_hero_num:
            hero = random.choice(self.hero_list)
            if hero not in heros:
                if self.rep == 1:
                    heros.append(hero)
                elif hero not in self.pre_heros:
                    heros.append(hero)
        
        self.pre_heros.extend(heros)
        return heros