#/---------------------------------------------------------------------------\
#| Hello! this is where you can create and edit the moves used in pokemon.py |
#| Format:                                                                   |
#|                                                                           |
#| def MOVEFUNCTION(friend,foe):                                             |
#|     {MOVECODE}                                                            |
#| DB.definemove('MOVENAME')(MOVEFUNCTION)                                   |
#|                                                                           |
#| 'friend' Is the pokemon using the move and 'foe' is the opponent pokemon. |
#| These arguments are always passed.                                        |
#I-------------------------------------------------------------I-------------/ 
#| N.B:                                                        |
#| When using Pokemon.dealdamage(), always pass the movedata!  |
#| It looks like this: ['physical'/'special','MOVETYPE']       |
#\-------------------------------------------------------------/
import random
from collections import namedtuple
import events

Move = namedtuple('Move', ['name', 'category', 'type', 'pp', 'power', 'accuracy', 'func'])

class DATABASE:
    def __init__(self):
        self.DATA = {}
    
    def define_move(self,name, category, type, pp, power, accuracy):
        # All this information does need to be defined here to correctly display information in the menus
        def inner(func):
            self.DATA[name] = Move(name, category, type, pp, power, accuracy, func)
        return inner

DB = DATABASE()

@DB.define_move('Tackle', 'Physical', 'Normal', 35, 40, 100)
def tackle(friend, foe):
    yield events.damage(friend, foe, 'Physical', 'Normal', 40, 100,)

# def fire_blast(friend,foe):
#     EventQueue.addEvent('dmg',friend,foe,'Fire blast',*friend.dealdamage(foe,45,['special','fire']))
# DB.definemove('Fire Blast',fire_blast)

# def stand_guard(friend,foe):
#     EventQueue.addEvent('raise',friend,*friend.raisestat('DEF',1.5))
# DB.definemove('Stand Guard',stand_guard)

# def riot(friend,foe):
#     EventQueue.addEvent('raise',friend,*friend.raisestat('ATK',1.5))
# DB.definemove('Riot',riot)

# def struggle(friend,foe):
#     EventQueue.addEvent('dmg',friend,foe,'Struggle',*friend.dealdamage(foe,50,['physical','normal']))
#     EventQueue.addEvent('raise',friend,*friend.raisestat('DEF',1/1.5))
# DB.definemove('Struggle',struggle)

# def ignite(friend,foe):
#     foe.status = 'Burn'
#     EventQueue.addEvent('stat','burn',foe)
# DB.definemove('Ignite',ignite)

# def stat_sacrifice(friend,foe):
#     a, b = ['ATK','DEF','SPATK','SPDEF','SPD'][random.randint(0,4)], ['ATK','DEF','SPATK','SPDEF','SPD'][random.randint(0,4)]
#     friend.raisestat(a,0)
#     foe.raisestat(b,0)
#     EventQueue.addEvent('msg',friend.custom_name + '\'s ' + a + ' stat was dropped to 1 and in return, ' + foe.custom_name + '\'s ' + b + ' stat dropped to 1.')
# DB.definemove('Stat Sacrifice',stat_sacrifice)
