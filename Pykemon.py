# Standard imports
import time
import random
import pickle

# Pygame setup
import pygame
pygame.init()

# Main imports
import eventqueue
import maploader
import npc
from battlescene import BattleScene
from console import Dialogue, Choice
from keybinding import single_key_action
from visual_core import get_texture
import pokepy.pokemon as pkm
from player import Player
from pos import Pos


def fit_and_center_surface(a, b):
    a_rect = a.get_rect()
    b_rect = b.get_rect()
    a_rect_scaled = a_rect.fit(b_rect)
    a_scaled = pygame.transform.scale(a, a_rect_scaled.size)
    coordinates = ((b_rect.width - a_rect_scaled.width)//2, (b_rect.height - a_rect_scaled.height)//2)
    b.blit(a_scaled, coordinates)


# The pixel screen is the non-scaled surface on which you should blit
# It will be scaled to fit the screen while keeping its aspect ratio
# Resulting in black bars on the sides.
pixel_screen_rect = pygame.Rect(0, 0, 256, 192)
pixel_screen = pygame.Surface(pixel_screen_rect.size)

# The screen size will default to to twice the size of the pixel screen
screen_rect = pixel_screen_rect.inflate(pixel_screen_rect.size)
screen_rect.move_ip(-screen_rect.x, -screen_rect.y)
screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)

clock = pygame.time.Clock()
done = False

# Maploader objects
mapToLoad = 'editmap'
maploader = maploader.MapLoader()
npcmanager = npc.NPCManager()
currentMap = maploader.loadMapObject(mapToLoad)
npcmanager.set_npcs(currentMap)

# Pokemon dex data
dex = pkm.dex.Dex()


player = Player(currentMap, npcmanager)
player.pos = Pos(currentMap.warps[0])

base_resolution = (256, 192)
map_surface = pygame.Surface(base_resolution)
zoom = 1

# Menu vars
menublit = get_texture('menu2')
menuselect = get_texture('menuselect2')
menu = False
menupos = 0
menuframes = 0
menudisp = 0

quickstart = True  # set to true for quick(er) debugging
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

current_scene = 'World'
activeBattle = None  # BattleScene object

dialogue = Dialogue(pixel_screen)
choice = Choice(pixel_screen)

scenes = {
    'dialogue': dialogue,
    'choice': choice
}

menuitem = 0
while not done:
    zoom += 0  # @Terts: WHAT?!?!?! # @Roy dit laten we erin als cultureel erfgoed.
    map_surface = pygame.Surface((base_resolution[0]//zoom, base_resolution[1]//zoom))
    pressed_keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # exit button
            done = True
        elif event.type == pygame.VIDEORESIZE:  # update screen when resizing
            screen_rect.size = event.dict['size']
            screen = pygame.display.set_mode(screen_rect.size, pygame.RESIZABLE)

        # Single key actions
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if current_scene == 'World':
                # TODO: Zooming is all fucked up now.... (zooms with topleft as anchor ans some other weirdness)
                # Question: Should we even allow zoom?
                if key == pygame.K_z:
                    zoom *= 1.1
                elif key == pygame.K_x:
                    zoom /= 1.1
                elif key == pygame.K_c:
                    zoom = 1
                elif key == pygame.K_m:
                    if not menuframes:
                        menu = not menu
                        menuframes = 4
                        if menu:
                            menudisp = -4
                        else:
                            menudisp = 4
                elif key == pygame.K_BACKSLASH:
                    a = input("load map: ")
                    player.warp(a, [0, 0])
                elif key == pygame.K_UP and menu:
                    menuitem = max(0, menuitem - 1)
                elif key == pygame.K_DOWN and menu:
                    menuitem = min(4, menuitem + 1)
                elif key == pygame.K_RETURN and menuitem == 0 and menu:
                    dialogue.open("Saving! Please don't turn off the console!")
                elif key == pygame.K_RETURN and menuitem == 1 and menu:
                    current_scene = 'Options'
                elif single_key_action(key, 'World', 'select') and not (dialogue.active or choice.active or player.moving):
                    pos_to_check = player.pos//16 + player.direction_vector
                    for sign in currentMap.signs:
                        if pos_to_check == sign.pos:
                            dialogue.open(*sign.text)
                            break
                    for npc in npcmanager.npcs:
                        if pos_to_check == npc.pos//16:
                            if npc.interact:
                                generator = npc.interact(player.pos)
                                func = next(generator)
                                print(func(generator).text)
                                eventqueue.add_events(func(generator))
                            break

            c = dialogue.handle_single_key_action(key)
            eventqueue.activate_callback(c)
            c = choice.handle_single_key_action(key)
            eventqueue.activate_callback(c)

            if current_scene == 'Options':
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
                    current_scene = 'World'
                    selected = 0
                    rowindex = 0

            if current_scene == 'Battle':
                pass

    # Continuous key actions
    if not menu and current_scene == 'World' and not dialogue.active and not choice.active:
        player.handle_continuous_key_action(pressed_keys)

    eventqueue.execute_events(scenes)

    # Drawing the frame
    if current_scene == 'World':
        drawx = map_surface.get_width()/2-player.pos[0]-8
        drawy = map_surface.get_height()/2-player.pos[1]

        map_surface.blit(currentMap.ground, (drawx, drawy))
        map_surface.blit(currentMap.beta, (drawx, drawy))

        flag = player.update()
        if flag == 'stopped moving':
            encounterTile = currentMap.encounters.checkEncounters(player.pos[0]//16, player.pos[1]//16)
            if encounterTile > 0:
                if random.randint(0, 10) == 0:
                    EncounterData = currentMap.encounters.generateEncounter(str(encounterTile))
                    foe = pkm.Trainer('Damion')
                    foe.party.append(pkm.Pokemon(EncounterData[0]))
                    foe.party[0].setlevel(EncounterData[1])
                    activeBattle = BattleScene(pixel_screen, player.trainerdata, foe)
                    scenes['battle'] = activeBattle
                    current_scene = 'Battle'

        c = npcmanager.update(player.pos//16)
        eventqueue.activate_callback(c)

        drawPlayer = True
        for npc in npcmanager.npcs:
            if npc.pos[1] + drawy > map_surface.get_height()/2 and drawPlayer:
                player.draw((map_surface.get_width()//2-16, map_surface.get_height()//2-16), map_surface)
                drawPlayer = False
            npc.draw((npc.pos[0] + drawx - 9, npc.pos[1] + drawy - 16), map_surface)
        if drawPlayer:
            player.draw((map_surface.get_width()//2-16, map_surface.get_height()//2-16), map_surface)

        map_surface.blit(currentMap.alpha, (drawx, drawy))
        pixel_screen.blit(map_surface, (0, 0))
        pixel_screen.blit(menublit, (pixel_screen_rect.width+menupos, 0))
        pixel_screen.blit(menuselect, (pixel_screen_rect.width+menupos, menuitem*14))

    elif current_scene == 'Battle':
        c = activeBattle.update()
        eventqueue.activate_callback(c)
        activeBattle.draw()
        if not activeBattle.active:
            current_scene = 'World'

    if menuframes:  # animating the menu in and out animation
        menupos -= menudisp*-menuframes
        menuframes -= 1

    dialogue.draw()
    choice.draw()

    warp = player.checkWarps(currentMap.warps)
    if warp:
        screen.fill((0,0,0))
        warp_map, warp_pos = warp
        currentMap = maploader.loadMapObject(warp_map)
        player.warp(currentMap, npcmanager, warp_pos)
        npcmanager.new_map(currentMap)

    fit_and_center_surface(pixel_screen, screen)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
