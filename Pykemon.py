#standard imports
import math, time, random
import pickle
from collections import namedtuple

#main imports
import maploader
import npcloader
import battlescene
from   keybinding import single_key_action, continuous_key_action
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
dummyEvent = Event("SAY",[
    "Hey, sexy ;)",
    "Isn't this lovely?",
    "yes sweetie",
    "it gets me all hot n' bothered"
])

class Console:
    def __init__(self, data):
        self.state = 0
        self.queue = [dummyEvent]
        self.datapath = data
        self.data = pickle.load(open(data,'rb'))
        self.dialogue_texture = pygame.image.load("textures/dialogue box.png").convert_alpha()
        self.font = pygame.font.SysFont("arial",30)
        self.dialogue_active = False

    def dialogBox(self, text):
        self.dialogue_active = True
        self.dialogue_text = iter(text)
        self.current_dialogue_text = next(self.dialogue_text)
        print(self.current_dialogue_text)
        print(text, 'ID:'+str(self.state))

    def draw_dialogue(self, screen):
        if not self.dialogue_active:
            return
        # First version of positioning
        # Should definitely be refined
        scaled = pygame.transform.scale(self.dialogue_texture, (screen.get_width(), self.dialogue_texture.get_height()*screen.get_width()//self.dialogue_texture.get_width()))
        pos_rect = pygame.Rect(0, 0, scaled.get_width(), scaled.get_height())
        pos_rect.centerx = screen.get_width() / 2
        pos_rect.bottom = screen.get_height()
        screen.blit(scaled, pos_rect)

        text_rect = pos_rect.inflate(-pos_rect.width*0.1, -pos_rect.height*0.3)
        screen.blit(self.font.render(self.current_dialogue_text, False, (255,255,255)), text_rect)

    def dialogue_continue(self):
        try:
            self.current_dialogue_text = next(self.dialogue_text)
            print(self.current_dialogue_text)
        except StopIteration:
            self.dialogue_active = False

    def execute_events(self):
        while self.queue:
            self.execute_next_event()

    def execute_next_event(self):
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

    def execute_script(self, scriptPath):
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
    console.execute_events()
    zoom += 0 # @Terts: WHAT?!?!?! # @Roy dit laten we erin als cultureel erfgoed.
    map_surface = pygame.Surface((screen_rect.width/zoom, screen_rect.height/zoom))
    pressed_keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            screen_rect.size = event.dict['size']
            screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)
        # Single key actions
        if event.type == pygame.KEYDOWN:
            key = event.key
            if console.dialogue_active:
                if single_key_action(key, 'Dialogue', 'continue'):
                    console.dialogue_continue()
            if currentScene == 'World':
                if key == pygame.K_z:
                    zoom *= 1.1
                elif key == pygame.K_x:
                    zoom /= 1.1
                elif key == pygame.K_m:
                    if not menuframes:
                        menu = not menu
                        if menu:
                            menuframes = 10
                            menudisp = 200/45
                        else:
                            menuframes = 10
                            menudisp = -200/45
                elif key == pygame.K_BACKSLASH:
                    a = input("load map: ")
                    player.warp(a,[0,0])
                elif key == pygame.K_UP and menu:
                    menuitem = max(0, menuitem - 1)
                elif key == pygame.K_DOWN and menu:
                    menuitem = min(4, menuitem + 1)
                elif key == pygame.K_RETURN and menuitem == 0 and menu:
                    console.addEvent( Event('SAY','saving! please don\'t turn off the console!'))
                elif key == pygame.K_RETURN and menuitem == 1 and menu:
                    currentScene = 'Options'
                elif single_key_action(key, 'World', 'select') and not console.dialogue_active and not player.moving:
                    print("Key action!")
                    for sign in currentMap.signs:
                        dir = player.get_direction_coordinates()
                        print("player.pos:", player.pos)
                        print("player.pos//16:", (player.pos[0] // 16, player.pos[1] // 16))
                        print("dir:", dir)
                        print("sign.pos", sign.pos)
                        if player.pos[0]//16 + dir[0] == sign.pos[0] and player.pos[1]//16 + dir[1] == sign.pos[1]:
                            print("Adding the event")
                            console.addEvent(Event("SAY", sign.text))
                            break

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

    # Continuous key actions
    if not player.moving and not menu and currentScene == 'World':
        if continuous_key_action(pressed_keys, 'World', 'run'):
            move_type = 'run'
        else:
            move_type = 'walk'

        if continuous_key_action(pressed_keys, 'World', 'north'):
            player.move(move_type, 'north')
        elif continuous_key_action(pressed_keys, 'World', 'east'):
            player.move(move_type, 'east')
        elif continuous_key_action(pressed_keys, 'World', 'south'):
            player.move(move_type, 'south')
        elif continuous_key_action(pressed_keys, 'World', 'west'):
            player.move(move_type, 'west')
        else:
            if player.animName.startswith('walk'):
                player.setAnimation(player.animName.replace('walk', 'idle'), 4)
            elif player.animName.startswith('run'):
                player.setAnimation(player.animName.replace('run', 'idle'), 4)

    # Drawing the frame
    if currentScene == 'World': #scene outside battle
        drawx = map_surface.get_width()/2-player.pos[0]-8
        drawy = map_surface.get_height()/2-player.pos[1]

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
                    currentScene = 'Battle'

        drawPlayer = True
        npcloader.update([player.pos[0]//16,1*player.pos[1]//16])
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

    elif currentScene == 'Battle':
        activeBattle.update()
        activeBattle.draw() #scene in battle

    elif currentScene == 'Options': #code is nu compleet shit, maar ik weet al hoe ik normaal ga maken
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

    if menuframes:
            menupos -= menudisp*(10-menuframes)
            menuframes -= 1

    console.draw_dialogue(screen)

    warp = player.checkWarps(currentMap.warps)
    if warp:
        screen.fill((0,0,0))
        warp_map, warp_pos = warp
        currentMap = maploader.loadMapObject(warp_map)
        player.warp(currentMap, npcloader, warp_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
