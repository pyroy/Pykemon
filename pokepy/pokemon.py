#####################################
#/---------------------------------\#
#| pokemon.py v3.4 by Roy Prins    |#
#|                                 |#
#| requires (in same folder):      |#
#|   - m_db.py                     |#
#|                                 |#
#| use module_help() for           |#
#| instructions on how to use      |#
#| this module, have fun! :)       |#
#\---------------------------------/#
#####################################

import pickle, random
import pokepy.m_db as m_db
import pokepy.dex as dex

compiled = False


STATS = ['HP', 'ATK', 'DEF', 'SPATK', 'SPDEF', 'SPD']


# Determines the amount of XP needed to reach the next level WIP, see Pokemon.addxp()
def xpfunc(lvl):
    return int(lvl*10*1.5**(lvl/10))


# Determines is a move is Super effective or not, this is used in damage calculations i.e. Pokemon.dealdamage()
effectiveness_chart = pickle.load(open('data\\POKEMONTYPES.dat', 'rb'))


def getmodifier(type1, types):
    if len(types) == 2:
        return effectiveness_chart[type1][types[0]]*effectiveness_chart[type1][types[1]]
    else:
        return effectiveness_chart[type1][types[0]]


# Event queue to make pokepy more universally usable.
class EventQueue:
    def __init__(self):
        self.queue = []

    def addEvent(self, *args):
        self.queue.append(args)

    def getEvents(self):
        a = self.queue[:]
        self.queue = []
        return a


m_db.EventQueue = EventQueue = EventQueue()


# PID class to retrieve information about a pokemon from a random or given number, only used in Pokemon.__init__()
class PID:
    def __init__(self, n=False):
        if not n:
            self.n = random.randint(0, 32**6)
        else:
            self.n = n

    def get_IVs(self):
        return [(self.n//32**n) % 32 for n in range(6)]

    def get_nature(self):
        return (self.n % 5, (self.n//5) % 5)

    def get_PID(self):
        return self.n

    def __int__(self):
        return self.n

# Moveset class to store for each pokemon which moves it has, moves are stored in m_db.py and you can edit them yourself!
class Moveset:
    def __init__(self, friend):
        self.moves = {}
        self.friend = friend

    def addmove(self, movename):
        move = m_db.DB.DATA[movename]
        self.moves[movename] = (move, move.pp)

    def deletemove(self, movename):
        del self.moves[movename]

    def replacemove(self, old_movename, new_movename):
        self.deletemove(old_movename)
        self.addmove(new_movename)
    
    def __getitem__(self, movename):
        return self.moves[movename]
    
    def get_moves(self):
        return [i[0] for i in self.moves.values()]
    
    def get_movenames(self):
        return list(self.moves.keys())


class Trainer:
    def __init__(self, name):
        self.name = name
        self.party = []
        self.bag = {'Key Items': [],
                    'Pokeballs': [],
                    'Berries': [],
                    'Medical': []}


# The big boy class
class Pokemon:
    def __init__(self, ID, p=None):  # Initiates standard variables
        self.id = ID
        self.PID = PID(p)
        self.baseData = pickle.load(open('data\\POKEMONDATA.dat', 'rb'))[ID]  # ID HAS TO be a string with the first letter being a capital, the rest lowercase.
        self.status = None  # Sleeping, Frozen etc.
        self.display_name = self.id.upper()
        self.custom_name = self.display_name[:]
        self.types = self.baseData['types']
        self.baseStats = {
            'HP':    self.baseData['stats']['hp'],
            'ATK':   self.baseData['stats']['attack'],
            'DEF':   self.baseData['stats']['defense'],
            'SPATK': self.baseData['stats']['special_attack'],
            'SPDEF': self.baseData['stats']['special_defense'],
            'SPD':   self.baseData['stats']['speed']
        }
        self.EVs = dict(zip(STATS, [0, 0, 0, 0, 0, 0]))
        self.IVs = dict(zip(STATS, self.PID.get_IVs()))
        self.nature = self.PID.get_nature()
        self.modifiers = dict(zip(STATS, [1, 1, 1, 1, 1]))
        self.modifiers[STATS[self.nature[0]]] += 0.1
        self.modifiers[STATS[self.nature[1]]] -= 0.1
        self.level = 1
        self.XP = 0
        self.goalXP = xpfunc(1)
        self.moveset = Moveset(self)
        self.moveset.addmove('Tackle')
        self.moveset.addmove('Ember')
        #self.moveset.addmove('Stand Guard')
        #self.moveset.addmove('Stat Sacrifice')
        #self.moveset.addmove('Struggle')
        self.calcstats()
        self.returnstats(True)
    
    @property
    def fainted(self):
        return self.currentStats['HP'] == 0

    def calcstats(self):  # Recalculates each max stat based on level, IV en EV
        self.stats = {}
        # HP and SPD have custom calculations
        self.stats['HP']  = round(self.modifiers['HP'] * (2*self.baseStats['HP'] + self.IVs['HP'] + self.EVs['HP']//4)*self.level//100 + self.level + 10)
        self.stats['SPD'] = (2*self.baseStats['SPD'] + self.IVs['SPD'] + self.EVs['SPD']//4)*self.level//100 + 5
        # ATK, DEF, SPATK and SPDEF all have the same calculation
        for stat in STATS[1:-1]:
            self.stats[stat] = round(self.modifiers[stat] * (2*self.baseStats[stat] + self.IVs[stat] + self.EVs[stat]//4)*self.level//100 + 5)

    def getstats(self):
        return self.currentStats

    def levelup(self):
        self.level += 1
        self.calcstats()
        self.returnstats()

    def setlevel(self, lvl):
        self.level = lvl
        self.calcstats()
        self.returnstats(True)
        self.XP = xpfunc(lvl-1)
        self.goalXP = xpfunc(lvl)

    def addxp(self, xp):
        self.XP += xp
        while self.XP > self.goalXP:
            self.levelup()
            self.goalXP = xpfunc(self.level)  # If given a lot of xp, multiple levels may be gained

    def dealdamage(self, pokemon, movedata):
        """Attacks a foe, movedata is passed by a Moveset.usemove() function."""
        mod = getmodifier(movedata['type'].lower(), pokemon.types)
        if movedata['category'].lower() == 'physical':
            damage = (((2*self.level/5+2)*movedata['power']*self.currentStats['ATK']/pokemon.currentStats['DEF'])/50+2)*mod
        if movedata['category'].lower() == 'special':
            damage = (((2*self.level/5+2)*movedata['power']*self.currentStats['SPATK']/pokemon.currentStats['SPDEF'])/50+2)*mod
        print(f"HP: {pokemon.currentStats['HP']}, Damage: {damage}")
        pokemon.takedamage(damage)
        if mod == 0:
            return [0, damage]
        if mod == 0.25:
            return [1, damage]
        if mod == 0.5:
            return [2, damage]
        if mod == 1:
            return [3, damage]
        if mod == 2:
            return [4, damage]
        if mod == 4:
            return [5, damage]

    def takedamage(self, amount):
        self.currentStats['HP'] -= round(amount)
        if self.currentStats['HP'] < 0:
            self.currentStats['HP'] = 0

    def raisestat(self, stat, amount):
        self.currentStats[stat] *= amount
        self.currentStats[stat] = max(1, self.currentStats[stat])
        return [stat, amount]

    def returnstats(self, hptoo=False):  # If you go out of battle, you dont want HP to magically restore as well
        if hptoo:
            self.currentStats = dict(self.stats)
        else:
            self.currentStats = dict(self.stats, HP=self.currentStats['HP'])


class Battle:
    def __init__(self, party1, party2, master, AI=True):
        self.player1 = party1
        self.player2 = party2
        self.master = master
        self.player1chosen = self.player2chosen = False
        self.player1action = self.player2action = None
        self.pok1 = self.player1.party[0]
        self.pok2 = self.player2.party[0]
        self.AI = AI
        self.battlestart = True
        self.actions = {
            'onturnend': None,
            'onplayer1win': None,
            'onplayer2win': None
        }

    def player1act(self, action):
        self.player1chosen = True
        if action[0] == 'usemove':
            self.player1action = [self.pok1.moveset.usemove, (action[1], self.pok2)]
        if self.AI:
            self.player2act(['usemove', random.randint(0, 3)])
            self.end_turn()

    def player2act(self, action):
        self.player2chosen = True
        if action[0] == 'usemove':
            self.player2action = [self.pok2.moveset.usemove, (action[1], self.pok1)]

    def check_endbattle(self):
        if int(self.pok1.currentStats['HP']) <= 0:
            if self.actions['onplayer2win']:
                self.actions['onplayer2win'](self, self.master)
            self.battlestart = False
            return True
        elif int(self.pok2.currentStats['HP']) <= 0:
            if self.actions['onplayer1win']:
                self.actions['onplayer1win'](self, self.master)
            self.battlestart = False
            return True
        return False

    def end_turn(self):
        if not self.battlestart:
            print('no.')
        else:
            if self.player1chosen and self.player2chosen:
                if self.pok1.cSPD > self.pok2.cSPD:
                    self.player1action[0](*self.player1action[1])
                    if not self.check_endbattle():
                        self.player2action[0](*self.player2action[1])
                        self.check_endbattle()
                        if self.actions['onturnend']:
                            self.actions['onturnend'](self, self.master)
            else:
                self.player2action[0](*self.player2action[1])
                if not self.check_endbattle():
                    self.player1action[0](*self.player1action[1])
                    self.check_endbattle()
                    if self.actions['onturnend']:
                        self.actions['onturnend'](self, self.master)
                        self.player1chosen = self.player2chosen = False
                    else:
                        print('Both players need to select an action')

    def showplayer1stats(self, foe=False):
        if foe:
            print(f"{self.pok1.display_name} HP: {self.pok1.currentStats['HP']}/{self.pok1.HP}")
        else:
            print(f"Active pokemon: {self.pok1.display_name}")
            print(f"LVL: {self.pok1.level}")
            print(f"HP: {self.pok1.currentStats['HP']}/{self.pok1.HP}")
            print("Moves:")
            for move in self.pok1.moveset.get_moves():
                print(f"{self.pok1.moveset.get_moves().index(move)}> {move}")

    def showplayer2stats(self, foe=False):
        if foe:
            print(f"{self.pok2.display_name} HP: {self.pok2.currentStats['HP']}/{self.pok2.currentStats['HP']}")
        else:
            print(f"Active pokemon: {self.pok2.display_name}")
            print(f"LVL: {self.pok2.level}")
            print(f"HP: {self.pok2.currentStats['HP']}/{self.pok2.HP}")
            print("Moves:")
            for move in self.pok2.moveset.get_moves():
                print(f"{self.pok2.moveset.get_moves().index(move)}> {move}")

    def get_afterbattledata(self):
        for pokemon in self.player1.party+self.player2.party:
            pokemon.returnstats()
        return [self.player1, self.player2]

# dm1 = Trainer('Joey',[Pokemon('Charmander')])
# dm1.party[0].setlevel(50)
# dm1.party[0].moveset.replacemove(2,'Fire Blast')
# dm1.party[0].moveset.replacemove(1,'Ignite')

# dm2 = Trainer('Gary',[Pokemon('Crobat')])
# dm2.party[0].setlevel(50)

# if __name__ == '__main__':
#         b = Battle(dm1,dm2)
#         while b.battlestart:
#                 print('----------start-turn-----------')
#                 b.showplayer2stats(True)
#                 print('\t')
#                 b.showplayer1stats()
#                 print('----------battle-----------')
#                 a = 5
#                 while a not in [0,1,2,3]: a = int(input("usemove>"))
#                 b.player1act(['usemove',a])
#         dm1,dm2 = b.get_afterbattledata()


def module_help():
    print("""
foo = Pokemon(\'Name\')
Pokemon class has attributes:
- HP,ATK,DEF,SPATK,SPDEF:\t Max stats
- cHP,cATK,cDEF... etc:\t\t current stats
- baseHP,baseATK... etc:\t base stats
- level, XP, goalXP:\t\t goalXP is XP needed to level up
- nature, EVs, IVs:\t\t nature is a tuple with the first number being
\t\t\t\t the ID of the boosted stat, and the second of the dropped stat
\t\t\t\t EVs and IVs are in standard [HP,ATK,DEF,SPATK,SPDEF,SPD] index
- display_name, status:\t\t status is Frozen, Sleeping... etc
- moveset:\t\t\t Moveset class, see pokemon.py

Pokemon class has functions:
- calcstats():\t\t\t recalculates max stats. used when leveling up.
- levelup():\t\t\t adds 1 level and calls calcstats()
- addxp(amount):\t\t adds amount xp and levels up accordingly
- dealdamage(foe,basedmg,md):\t damage calculations, see m_db.py
- raisestat(stat,amount):\t raises a stat with amount as a multiplier
- returnstats(hptoo=False):\t recovers stats, if hptoo is True will recover HP to
- getstats,getEVs,getIVs:\t returns appropriate data
""")
