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
screen_rect = pygame.Rect(0, 0, 600, 600)
screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)
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
npcloader = npcloader.NPCLoader(console)
maploader = maploader.MapLoader()

#Maploader objects
mapToLoad = 'editmap'
currentMap = maploader.loadMapObject(mapToLoad)
#End Maploader objects

player = Player(currentMap.bounds, npcloader)
player.pos = currentMap.warps[0]

map_surface = pygame.Surface((200,200))
zoom = 3

#Menu vars
menublit = pygame.image.load('textures/menu.png')
menublit.convert_alpha()
menuselect = pygame.image.load('textures/menuselect.png')
menuselect.convert_alpha()
menu = False
menupos = 0
menuframes = 0
menudisp = 0
#End Menu vars

quickstart = True # turn on for quick debugging
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

npcloader.loadNPC('bob')
npcloader.loadNPC('will')

currentScene = 'World'
activeBattle = None #Actual BattleScene object

#Options menu vars
font = pygame.font.SysFont('arial', 30)
selected = 0; rowindex = 0
try: options = pickle.load(open('data\options.p','rb'))
except: options = {}
options = {'empty':0,'test':1}

menuitem = 0
while not done:
    console.executeNextEvent()
    zoom += 0 # @Terts: WHAT?!?!?! # @Roy dit laten we erin als cultureel erfgoed.
    map_surface = pygame.Surface((screen_rect.width/zoom, screen_rect.height/zoom))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            screen_rect.size = event.dict['size']
            screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if currentScene == 'World':
                if event.key == pygame.K_z:
                    zoom *= 1.1
                elif event.key == pygame.K_x:
                    zoom /= 1.1
                elif event.key == pygame.K_m:
                    if not menuframes:
                        menu = not menu
                        if menu:
                            menuframes = 10
                            menudisp = 200/45
                        else:
                            menuframes = 10
                            menudisp = -200/45
                elif event.key == pygame.K_BACKSLASH:
                    a = input("load map: ")
                    player.warp(a,[0,0])
                elif event.key == pygame.K_UP and menu:
                    menuitem = max(0, menuitem - 1)
                elif event.key == pygame.K_DOWN and menu:
                    menuitem = min(4, menuitem + 1)
                elif event.key == pygame.K_RETURN and menuitem == 0 and menu:
                    console.addEvent( Event('SAY','saving! please don\'t turn off the console!'))
                elif event.key == pygame.K_RETURN and menuitem == 1 and menu:
                    currentScene = 'Options'
                elif event.key == pygame.K_RETURN and not menu:
                    #player.activate()
                    pass;
            if currentScene == 'Options':
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                    print(selected)
                elif event.key == pygame.K_DOWN:
                    selected = min(len(rows), selected + 1)
                    print(selected)
                elif event.key == pygame.K_LEFT:
                    rowindex = max(0, rowindex - 1)
                elif event.key == pygame.K_RIGHT:
                    rowindex = min(len(rows[row])-1, rowindex + 1)
                elif event.key == pygame.K_RETURN and selected == len(rows):
                    pickle.dump(options, open('options.p','wb'))
                    currentScene = 'World'; selected = 0; rowindex = 0

    if currentScene == 'World': #scene outside battle
        drawx = map_surface.get_width()/2-player.pos[0]-8
        drawy = map_surface.get_height()/2+player.pos[1]

        map_surface.blit(currentMap.ground, (drawx,drawy)) #groundmap
        map_surface.blit(currentMap.beta, (drawx, drawy)) #betamap

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
        npcloader.update([int(player.pos[0]/16),-1*int(player.pos[1]/16)])
        for npc in npcloader.npcs:
            surface, position = npc.getDrawData()
            if position[1] * 16 + drawy - 13 > map_surface.get_height()/2-13 and drawPlayer:
                player.draw((map_surface.get_width()/2-10,map_surface.get_height()/2-13), map_surface)
                drawPlayer = False
            position = (position[0] * 16 + drawx - 1, position[1] * 16 + drawy - 13)
            map_surface.blit(surface, position)
        if drawPlayer: player.draw((map_surface.get_width()/2-10,map_surface.get_height()/2-13), map_surface)

        map_surface.blit(currentMap.alpha,(drawx, drawy)) #alphamap

        screen.blit(pygame.transform.scale(map_surface, screen_rect.size), (0,0))
        screen.blit(pygame.transform.scale(menublit,(200,2*184)), (screen_rect.width+menupos, 0))
        screen.blit(menuselect, (screen_rect.width+menupos, menuitem*70))

    if not player.moving and not menu and currentScene == 'World':
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            player.setMovement([0,-2],8,(0,-1))
            if not player.animName == 'walkdown':
                player.setAnimation('walkdown', 4)
        elif pygame.key.get_pressed()[pygame.K_UP]:
            player.setMovement([0,2],8,(0,1))
            if not player.animName == 'walkup':
                player.setAnimation('walkup', 4)
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            player.setMovement([2,0],8,(1,0))
            if not player.animName == 'walkright':
                player.setAnimation('walkright', 4)
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            player.setMovement([-2,0],8,(-1,0))
            if not player.animName == 'walkleft':
                player.setAnimation('walkleft', 4)
        else:
            if player.animName.startswith('walk'):
                player.setAnimation(player.animName.replace('walk', 'idle'), 4)

    if menuframes:
        menupos -= menudisp*(10-menuframes)
        menuframes -= 1

    if currentScene == 'Battle':
        activeBattle.update()
        activeBattle.draw() #scene in battle

    if currentScene == 'Options': #code is nu compleet shit, maar ik weet al hoe ik normaal ga maken
        screen.fill((255,255,255))
        
        if selected == len(rows): labelback = font.render("back",False,(255,0,0))
        else: labelback = font.render("back",False,(0,0,0))

        rows = {1: ['empty','test']}

        for row in rows:
            for label in rows[row]:
                if options[label]:
                    screen.blit(font.render(label, False, (255,0,0)), ((rows[row].index(label)+1)*screen_rect.width/(len(rows[row])+1),row*screen_rect.height/(1+len(rows.keys()))))
                else: screen.blit(font.render(label, False, (0,0,0)), ((rows[row].index(label)+1)*screen_rect.width/(len(rows[row])+1),row*screen_rect.height/(1+len(rows.keys()))))

        screen.blit(labelback,(0,screen_rect.height-50))

    warp = player.checkWarps(currentMap.warps)
    if warp:
        screen.fill((0,0,0))
        warp_map, warp_pos = warp
        currentMap = maploader.loadMapObject(warp_map)
        player.warp(currentMap, npcloader, warp_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
