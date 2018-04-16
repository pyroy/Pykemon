# Standard imports
import time
import random
import pickle
from collections import namedtuple

# Main imports
import maploader
import npcloader
import battlescene
from console import *
from keybinding import single_key_action, continuous_key_action
import pokepy.pokemon as pkm
from player import Player

# Pygame setup
import pygame
pygame.init()

# The pixel screen is the non-scaled surface on which you should blit
# It will be scaled to fit the screen while keeping its aspect ratio
pixel_screen_rect = pygame.Rect(0, 0, 256, 192)
pixel_screen = pygame.Surface(pixel_screen_rect.size)
screen_rect = pixel_screen_rect.inflate(pixel_screen_rect.size)
screen_rect.move_ip(-screen_rect.x, -screen_rect.y)

screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)
clock = pygame.time.Clock()
done = False

console = Console('data/globals.p', pixel_screen)# see console.py

# Pokemon dex data
dex = pkm.dex.Dex()
npcloader = npcloader.NPCLoader(console)
maploader = maploader.MapLoader()

# Maploader objects
mapToLoad = 'editmap'
currentMap = maploader.loadMapObject(mapToLoad)

player = Player(currentMap.bounds, npcloader) #see player.py
player.pos = currentMap.warps[0]

base_resolution = (256, 192)
map_surface = pygame.Surface((256, 192))
zoom = 1

# Menu vars
menublit = pygame.image.load('textures/menu.png')
menublit.convert_alpha()
menuselect = pygame.image.load('textures/menuselect.png')
menuselect.convert_alpha()
menu = False
menupos = 0
menuframes = 0
menudisp = 0 #integers are booleans right

quickstart = True  # turn on for quick debugging
if not quickstart:
    with open("credits.txt", "r") as file:
        creditscreen = map(lambda line: line.strip(), file.readlines())

    screen.fill((0,0,0))
    counter = 0
    f = pygame.font.SysFont("arial", 20)
    h = f.render('test', False, (255,255,255)).get_height() + 3
    for index, line in enumerate(creditscreen):
        screen.blit(f.render(line, False, (255,255,255)), (5, h*index))
    pygame.display.flip()
    time.sleep(2)

npcloader.loadNPC('bob') #placeholders? should be in maploader
npcloader.loadNPC('will')

currentScene = 'World'
activeBattle = None  # Actual BattleScene object

# Options menu vars
font = pygame.font.SysFont('arial', 30)
selected = 0
rowindex = 0
try:
    options = pickle.load(open('data\\options.p', 'rb'))
except (FileNotFoundError, EOFError):
    options = {}
options = {'empty': 0, 'test': 1} #revamp use lib

menuitem = 0
while not done:
    console.execute_events()
    zoom += 0  # @Terts: WHAT?!?!?! # @Roy dit laten we erin als cultureel erfgoed.
    map_surface = pygame.Surface((base_resolution[0]//zoom, base_resolution[1]//zoom))
    pressed_keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #exit button
            done = True
        if event.type == pygame.VIDEORESIZE: #update screen when resizing
            screen_rect.size = event.dict['size']
            screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)

        # Single key actions
        if event.type == pygame.KEYDOWN:
            key = event.key
            if currentScene == 'World':
                if key == pygame.K_z:
                    zoom *= 1.1
                elif key == pygame.K_x:
                    zoom /= 1.1
                elif key == pygame.K_m:
                    if not menuframes:
                        menu = not menu
                        menuframes = 10
                        if menu:
                            menudisp = 200/45
                        else:
                            menudisp = -200/45
                elif key == pygame.K_BACKSLASH:
                    a = input("load map: ")
                    player.warp(a, [0, 0])
                elif key == pygame.K_UP and menu:
                    menuitem = max(0, menuitem - 1)
                elif key == pygame.K_DOWN and menu:
                    menuitem = min(4, menuitem + 1)
                elif key == pygame.K_RETURN and menuitem == 0 and menu:
                    console.addEvent('SAY', "saving! please don't turn off the console!")
                elif key == pygame.K_RETURN and menuitem == 1 and menu:
                    currentScene = 'Options'
                elif single_key_action(key, 'World', 'select') and not console.dialogue_active and not player.moving:
                    for sign in currentMap.signs:
                        dir = player.get_direction_coordinates()
                        if player.pos[0]//16 + dir[0] == sign.pos[0] and player.pos[1]//16 + dir[1] == sign.pos[1]:
                            console.addEvent("SAY", sign.text)
                            break

            if console.dialogue_active:
                if single_key_action(key, 'Dialogue', 'continue'):
                    console.dialogue_continue()

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
                    pickle.dump(options, open('options.p', 'wb'))
                    currentScene = 'World'
                    selected = 0
                    rowindex = 0

            if currentScene == 'Battle':
                activeBattle.process_single_key_event(key)

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
    if currentScene == 'World':
        drawx = map_surface.get_width()/2-player.pos[0]-8
        drawy = map_surface.get_height()/2-player.pos[1]

        map_surface.blit(currentMap.ground, (drawx, drawy))
        map_surface.blit(currentMap.beta, (drawx, drawy))

        flag = player.update(currentMap)
        if flag == 'stopped moving':
            encounterTile = currentMap.encounters.checkEncounters(player.pos[0]//16, player.pos[1]//16)
            if encounterTile > 0:
                if random.randint(0, 10) == 0:
                    battle = True
                    EncounterData = currentMap.encounters.generateEncounter(str(encounterTile))
                    foe = pkm.Trainer('Damion')
                    foe.party.append(pkm.Pokemon(EncounterData[0]))
                    foe.party[0].setlevel(EncounterData[1])
                    activeBattle = battlescene.Battle(pixel_screen, console, player.trainerdata, foe)
                    currentScene = 'Battle'

        drawPlayer = True
        npcloader.update([player.pos[0]//16, player.pos[1]//16])
        for npc in npcloader.npcs:
            surface, position = npc.getDrawData()
            if position[1] * 16 + drawy - 13 > map_surface.get_height()/2-13 and drawPlayer:
                player.draw((map_surface.get_width()/2-10, map_surface.get_height()/2-13), map_surface)
                drawPlayer = False
            position = (position[0] * 16 + drawx - 1, position[1] * 16 + drawy - 13)
            map_surface.blit(surface, position)
        if drawPlayer:
            player.draw((map_surface.get_width()/2-10, map_surface.get_height()/2-13), map_surface)

        map_surface.blit(currentMap.alpha, (drawx, drawy))
        pixel_screen.blit(map_surface, (0, 0))
        pixel_screen.blit(pygame.transform.scale(menublit, (200, 2*184)), (pixel_screen_rect.width+menupos, 0))
        pixel_screen.blit(menuselect, (pixel_screen_rect.width+menupos, menuitem*70))

    elif currentScene == 'Battle':
        activeBattle.update()
        activeBattle.draw()

    # Code is nu compleet shit, maar ik weet al hoe ik normaal ga maken -> i am idiot i must implement library
    elif currentScene == 'Options':
        screen.fill((255,255,255))

        if selected == len(rows):
            labelback = font.render("back", False, (255,0,0))
        else:
            labelback = font.render("back", False, (0,0,0))

        rows = {1: ['empty', 'test']}

        for row in rows:
            for label in rows[row]:
                if options[label]:
                    screen.blit(font.render(label, False, (255,0,0)), ((rows[row].index(label)+1)*screen_rect.width/(len(rows[row])+1), row*screen_rect.height/(1+len(rows.keys()))))
                else:
                    screen.blit(font.render(label, False, (0,0,0)), ((rows[row].index(label)+1)*screen_rect.width/(len(rows[row])+1), row*screen_rect.height/(1+len(rows.keys()))))

        screen.blit(labelback, (0, screen_rect.height-50))

    if menuframes: #animating the menu in and out animation
            menupos -= menudisp*(10-menuframes)
            menuframes -= 1

    console.draw_dialogue()

    warp = player.checkWarps(currentMap.warps)
    if warp:
        screen.fill((0,0,0))
        warp_map, warp_pos = warp
        currentMap = maploader.loadMapObject(warp_map)
        player.warp(currentMap, npcloader, warp_pos)

    fit_and_center_surface(pixel_screen, screen)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
