#standard imports
import math, time, random
import pickle
from collections import namedtuple

#main imports
import maploader, npcloader
import battlescene
import pokepy.pokemon as pkm
from player import Player

#pygame setup
import pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
done = False

#Console

Event = namedtuple("Event", ["event","data"])
dummyEvent = Event("SAY","Hey, sexy ;)")

class Console:
    def __init__(self, data):
        self.state = 0
        self.queue = []
        self.datapath = data
        self.data = pickle.load(open(data,'rb'))

    def dialogBox(self, text):
        print(text, 'ID:'+str(self.state))

    def executeNextEvent(self):
        if self.queue:
            eventToExecute = self.queue.pop(0)
            self.state += 1
            if eventToExecute.event == 'SAY':
                self.dialogBox(eventToExecute.data)
            if eventToExecute.event == 'SET':
                self.data[ eventToExecute.data[0] ] = eventToExecute.data[1]
                pickle.dump( self.data, open(self.datapath, 'wb') )
            if eventToExecute.event == 'IF':
                if self.data[eventToExecute.data[0]]:
                    self.addEvent[ interpret(eventToExecute.data[1][0]) ]
                else: self.addEvent[ interpret(eventToExecute.data[1][1]) ]

    def addEvent(self, event):
        if type(event) == list:
            self.queue.extend(event)
        else: self.queue.append(event)

    def executeScript(self, scriptPath):
        with open(scriptPath) as file:
            lines = file.readlines()
        for line in lines: self.addEvent( interpret(line) )

    def interpret(self, data):
        commands = data.split(';')
        toReturn = []
        for command in commands:
            commandType = command.split(':')[0]
            commandData = eval(command.split(':')[1])
            toReturn.append( Event(commandType, commandData) )

console = Console('data/globals.p')

dex = pkm.dex.Dex() #Pokemon dex data
nl = npcloader.NPCLoader(console)
ml = maploader.MapLoader()

#Maploader objects
mapToLoad = 'editmap'
currentMap = ml.loadMapObject(mapToLoad)
#End Maploader objects

player = Player(currentMap.bounds)
player.pos = currentMap.warps[0]

ttt = pygame.Surface((200,200))
zoom = 1

#Menu vars
menublit = pygame.image.load('textures/menu.png')
menublit.convert_alpha()
menuselect = pygame.image.load('textures/menuselect.png')
menuselect.convert_alpha()
menu = False
menupos = 200
menuframes = 0
menudisp = 0
#End Menu vars

quickstart = True # nice to have for quicker debugging
if not quickstart:
    with open("credits.txt", "r") as file:
        creditscreen = map(lambda line: line.strip(), file.readlines())

    screen.fill((0,0,0))
    counter = 0
    f = pygame.font.SysFont("arial",20)
    h = f.render('test',False,(255,255,255)).get_height()+3
    for index, line in enumerate(creditscreen):
        screen.blit(f.render(line,False,(255,255,255)), (5,h*index))
    pygame.display.flip()
    time.sleep(2)

nl.loadNPC('bob')
nl.loadNPC('will')

battle = False
activeBattle = None

menuitem = 0
while not done:
    console.executeNextEvent()
    zoom += 0 # @Terts: WHAT?!?!?! # @Roy dit laten we erin als cultureel erfgoed.
    ttt = pygame.Surface((200/zoom, 200/zoom))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and not battle:
                zoom *= 1.1
            elif event.key == pygame.K_x and not battle:
                zoom /= 1.1
            elif event.key == pygame.K_m and not battle:
                if not menuframes:
                    menu = not menu
                    if menu:
                        menuframes = 10
                        menudisp = 200/45
                    else:
                        menuframes = 10
                        menudisp = -200/45
            elif event.key == pygame.K_BACKSLASH and not battle:
                a = input("load map: ")
                player.warp(a,[0,0])
            elif event.key == pygame.K_UP and not battle and menu:
                menuitem = max(0, menuitem - 1)
            elif event.key == pygame.K_DOWN and not battle and menu:
                menuitem = min(4, menuitem + 1)
            elif event.key == pygame.K_RETURN and not battle and menuitem == 0 and menu:
                console.addEvent( Event('SAY','saving! please don\'t turn off the console!'))
            elif event.key == pygame.K_RETURN and not battle and not menu:
                #player.activate()
                pass;

    if not battle: #scene outside battle
        drawx = ttt.get_width()/2-player.pos[0]-8
        drawy = ttt.get_height()/2+player.pos[1]

        ttt.blit(currentMap.ground, (drawx,drawy)) #groundmap
        ttt.blit(currentMap.beta, (drawx, drawy)) #betamap

        flag = player.update(currentMap)
        if flag == 'stopped moving':
            encounterTile = currentMap.encounters.checkEncounters(player.pos[0]//16,player.pos[1]//16)
            if encounterTile > 0:
                if random.randint(0, 10) == 0:
                    battle = True
                    EncounterData = currentMap.encounters.generateEncounter( str(encounterTile) )
                    foe = pkm.Trainer('Damion')
                    foe.party.append(pkm.Pokemon(EncounterData[0]))
                    foe.party[0].setlevel(EncounterData[1])
                    activeBattle = battlescene.Battle(screen, player.trainerdata, foe)

        drawPlayer = True
        nl.update([int(player.pos[0]/16),-1*int(player.pos[1]/16)])
        for npc in nl.npcs:
            surface, position = npc.getDrawData()
            if position[1] * 16 + drawy - 13 > ttt.get_height()/2-13 and drawPlayer:
                player.draw((ttt.get_width()/2-10,ttt.get_height()/2-13), ttt)
                drawPlayer = False
            position = (position[0] * 16 + drawx - 1, position[1] * 16 + drawy - 13)
            ttt.blit(surface, position)
        if drawPlayer: player.draw((ttt.get_width()/2-10,ttt.get_height()/2-13), ttt)

        ttt.blit(currentMap.alpha,(drawx, drawy)) #alphamap

        screen.blit(pygame.transform.scale(ttt, (600,600)), (0,0))
        screen.blit(pygame.transform.scale(menublit,(200,2*184)), (400+menupos, 0))
        screen.blit(menuselect, (400+menupos, menuitem*70))

    if not player.moving and not menu and not battle:
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            player.setMovement([0,-2],8,(0,-1), nl)
            if not player.animName == 'walkdown':
                player.setAnimation('walkdown', 4)
        elif pygame.key.get_pressed()[pygame.K_UP]:
            player.setMovement([0,2],8,(0,1), nl)
            if not player.animName == 'walkup':
                player.setAnimation('walkup', 4)
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            player.setMovement([2,0],8,(1,0), nl)
            if not player.animName == 'walkright':
                player.setAnimation('walkright', 4)
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            player.setMovement([-2,0],8,(-1,0), nl)
            if not player.animName == 'walkleft':
                player.setAnimation('walkleft', 4)
        else:
            if player.animName.startswith('walk'):
                player.setAnimation(player.animName.replace('walk', 'idle'), 4)

    if menuframes:
        menupos -= menudisp*(10-menuframes)
        menuframes -= 1

    if battle:
        activeBattle.update()
        activeBattle.draw() #scene in battle

    warp = player.checkWarps(currentMap.warps)
    if warp:
        screen.fill((0,0,0))
        player.warp(*warp)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
