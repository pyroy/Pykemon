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

class DATABASE:
    def __init__(self): self.DATA = {}
    def definemove(self,key,func): self.DATA[key] = func

DB = DATABASE()
EventQueue = None

def tackle(friend,foe):
    EventQueue.addEvent('dmg',friend,foe,'Tackle',*friend.dealdamage(foe,35,['physical','normal']))
DB.definemove('Tackle',tackle)

def fire_blast(friend,foe):
    EventQueue.addEvent('dmg',friend,foe,'Fire blast',*friend.dealdamage(foe,45,['special','fire']))
DB.definemove('Fire Blast',fire_blast)

def stand_guard(friend,foe):
    EventQueue.addEvent('raise',friend,*friend.raisestat('DEF',1.5))
DB.definemove('Stand Guard',stand_guard)

def riot(friend,foe):
    EventQueue.addEvent('raise',friend,*friend.raisestat('ATK',1.5))
DB.definemove('Riot',riot)

def struggle(friend,foe):
    EventQueue.addEvent('dmg',friend,foe,'Struggle',*friend.dealdamage(foe,50,['physical','normal']))
    EventQueue.addEvent('raise',friend,*friend.raisestat('DEF',1/1.5))
DB.definemove('Struggle',struggle)

def ignite(friend,foe):
    foe.status = 'Burn'
    EventQueue.addEvent('stat','burn',foe)
DB.definemove('Ignite',ignite)

def stat_sacrifice(friend,foe):
    a, b = ['ATK','DEF','SPATK','SPDEF','SPD'][random.randint(0,4)], ['ATK','DEF','SPATK','SPDEF','SPD'][random.randint(0,4)]
    friend.raisestat(a,0)
    foe.raisestat(b,0)
    EventQueue.addEvent('msg',friend.custom_name + '\'s ' + a + ' stat was dropped to 1 and in return, ' + foe.custom_name + '\'s ' + b + ' stat dropped to 1.')
DB.definemove('Stat Sacrifice',stat_sacrifice)
