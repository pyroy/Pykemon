import pygame
import os
import sys

from mapeditorgui.pygamesliders import Simpleslider
from mapeditorgui.pygamebuttons import Simplebutton

groundmap    = None
betamap      = None
alphamap     = None
boundmap     = None
objects      = None
encountermap = None


def draw_map(mapdata, surface):
    for y in range(len(mapdata) - 1):
        for x in range(len(mapdata[y + 1].split("."))):
            locx = int(mapdata[y + 1].split(".")[x].split(",")[0])
            locy = int(mapdata[y + 1].split(".")[x].split(",")[1])
            surface.blit(tileset, (x * 16, y * 16), (locx * 16, locy * 16, 16, 16))


def saveMap(layer, data, path):
    layer.close()
    layer = open(path, 'w+')
    print(f"Writing {len(data)} lines to {path}")
    for line in data:
        layer.write(line)


def saveAllMaps():
    saveMap(groundmap,    mapl,   f"maps/{name}/map.txt")
    saveMap(alphamap,     amapl,  f"maps/{name}/alpha.txt")
    saveMap(betamap,      bemapl, f"maps/{name}/beta.txt")
    saveMap(boundmap,     bmapl,  f"maps/{name}/bounds.txt")
    saveMap(objects,      omapl,  f"maps/{name}/objects.txt")
    saveMap(encountermap, emapl,  f"maps/{name}/encounters.txt")


def deleteAllMaps():
    os.remove(f"maps/{name}/map.txt")
    os.remove(f"maps/{name}/beta.txt")
    os.remove(f"maps/{name}/alpha.txt")
    os.remove(f"maps/{name}/bounds.txt")
    os.remove(f"maps/{name}/objects.txt")
    os.remove(f"maps/{name}/encounters.txt")


def openAllLayers(name, mode):
    global groundmap, betamap, alphamap, boundmap, objects, encountermap
    groundmap    = open(f"maps/{name}/map.txt",        mode)
    betamap      = open(f"maps/{name}/beta.txt",       mode)
    alphamap     = open(f"maps/{name}/alpha.txt",      mode)
    boundmap     = open(f"maps/{name}/bounds.txt",     mode)
    objects      = open(f"maps/{name}/objects.txt",    mode)
    encountermap = open(f"maps/{name}/encounters.txt", mode)


def closeAllLayers():
    groundmap.close()
    alphamap.close()
    betamap.close()
    objects.close()
    boundmap.close()
    encountermap.close()


def create_map():
    name = input("name of new map: ")
    if not os.path.exists(os.getcwd()+f'/maps/{name}/'):
        os.makedirs(os.getcwd()+f'/maps/{name}/')

    openAllLayers(name, "w+")
    width  = int(input("width = " ))*16
    height = int(input("height = "))*16
    groundmap.write(f'{width}.{height}\n')
    alphamap .write(f'{width}.{height}\n')
    betamap  .write(f'{width}.{height}\n')

    for layer, default, separator in [(groundmap, '0,1', '.'), (alphamap, '0,0', '.'), (betamap, '0,0', '.'), (boundmap, '0', ''), (encountermap, '0', '')]:
        for _ in range(height//16):
            layer.write(separator.join([default] * width//16) + '\n')

    encountermap.write('0;NONE')

    objects.write('objectPlayerPos;[0,0];\n')
    closeAllLayers()


# LOAD CL ARGUMENT
if len(sys.argv) > 1:
    name = sys.argv[1]
    print(f"Loading map: {sys.argv}")
    while True:
        if name == "":
            print("No name is entered.")
            print("The program will quit.")
        try:
            openAllLayers(name, "r+")
            break
        except:
            print(f"Make sure the map '{name}' exists and has all the necessary files.")
            print("Hit enter without hitting a key to quit.")
            name = input("load map: ")
# MENU
else:
    a = ""
    while a not in ['l', 'c', 'd']:
        a = input("load, create or delete? (l/c/d) >")
        if a == 'l':
            while True:
                name = input("load map: ")
                if name == "":
                    print("No name is entered.")
                    print("The program will quit.")
                try:
                    openAllLayers(name, "r+")
                    break
                except:
                    print(f"Make sure the map '{name}' exists and has all the necessary files.")
                    print("Hit enter without hitting a key to quit.")

        elif a == 'c':
            create_map()
            print(f"{name} has been created!")
            print("The edit screen will now be opened.")
            try:
                openAllLayers(name, "r+")
            except:
                # It'd be really weird to go here,
                # since you just created the necessary files
                assert False, "WTFFFFFFFF"

        elif a == 'd':
            name = input("delete map: ")
            if not name:
                quit()
            if name == input("Type the name of the map again to delete:"):
                deleteAllMaps()
                quit()
            else:
                print("Names did not match: map was not deleted.")
                quit()
        else:
            print("Input was not recognized.")
            input()
            quit()

pygame.init()

# Global variables
edit_rect = pygame.Rect(0, 0, 640, 640)
sidebar_rect = pygame.Rect(edit_rect.width, 0, 8*16*2, edit_rect.height)
screen = pygame.display.set_mode((edit_rect.width+sidebar_rect.width, edit_rect.height), pygame.RESIZABLE)
pygame.display.set_caption("Pykemon Map Editor")
clock = pygame.time.Clock()
done = False

campos = [0, 0]
pointerpos = [0, 0]

# Textures
tileset     = pygame.image.load("textures/tileset-blackvolution.png").convert_alpha()
good        = pygame.image.load("textures/good.png" ).convert_alpha()
bad         = pygame.image.load("textures/bad.png"  ).convert_alpha()
ledge_up    = pygame.image.load("textures/up.png"   ).convert_alpha()
ledge_right = pygame.image.load("textures/right.png").convert_alpha()
ledge_down  = pygame.image.load("textures/down.png" ).convert_alpha()
ledge_left  = pygame.image.load("textures/left.png" ).convert_alpha()
warp        = pygame.image.load("textures/warp.png" ).convert_alpha()
player      = pygame.image.load("textures/player-kaori.png").convert_alpha()

# Pokeball sprites
encounterSprites = {}
src = pygame.image.load("textures/pokeballs.png").convert_alpha()
for i in range(25):
    blankSlate = pygame.Surface((64, 64), pygame.SRCALPHA)
    blankSlate.blit(src, (0, 0), ((i%5)*64, (i//5)*64, 64, 64))
    encounterSprites[str(i+1)] = pygame.transform.scale(blankSlate, (16, 16))

mapl   = groundmap.readlines()
bmapl  = boundmap.readlines()
bemapl = betamap.readlines()
amapl  = alphamap.readlines()
omapl  = objects.readlines()
emapl  = encountermap.readlines()

font  = pygame.font.SysFont("arial", 30)
font2 = pygame.font.SysFont("arial", 15)
stateblit = font.render("editing groundmap", False, (255,255,255))
state = 'groundmap'

zoom = 4
scrollpos = 0

# Buttons for encounter
addEncounterButton = Simplebutton(200, 50, (60,60,60), "Add Encounter...", pygame.font.Font("jackeyfont.ttf", 20))
addEncounterButton.border = 1
addEncounterButton.pos = (680, 400)
addEncounterButton.textcolor = (255,255,255)


@addEncounterButton.link
def action1():
    print('I work!')
    # TODO: Right now even works when not visible!!!!!!!


boundmap_data = {
    'lines': bmapl,
    'selected tile': 'neg',
    'tileset': ['neg', 'u', 'r', 'd', 'l']
}


# Main loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            edit_rect.size = (event.dict["size"][0]-sidebar_rect.width, event.dict["size"][1])
            sidebar_rect = pygame.Rect(edit_rect.width, 0, 8*16*2, edit_rect.height)
            screen = pygame.display.set_mode(event.dict["size"], pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_SPACE]:  # Selecting tiles
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    if event.key == pygame.K_UP:
                        scrollpos += edit_rect.height
                        pointerpos[1] -= 20
                        if pointerpos[1] < 0:
                            pointerpos[1] = 0  # Pointerpos is the position of the selection sprite
                            scrollpos = 0  # And scrollpos is which 'page' you are on
                    if event.key == pygame.K_DOWN:
                        scrollpos -= edit_rect.height
                        pointerpos[1] += 20
                        if pointerpos[1] > 99:
                            pointerpos[1] = 99
                            scrollpos = -edit_rect.height*4
                else:
                    if event.key == pygame.K_UP:
                        pointerpos[1] -= 1
                        if pointerpos[1] < 40:
                            scrollpos = -edit_rect.height
                        if pointerpos[1] < 20:
                            scrollpos = 0
                        if pointerpos[1] < 0:
                            pointerpos[1] = 0
                    if event.key == pygame.K_DOWN:
                        pointerpos[1] += 1
                        if pointerpos[1] > 19:
                            scrollpos = -edit_rect.height
                        if pointerpos[1] > 39:
                            scrollpos = -edit_rect.height*2
                        if pointerpos[1] > 59:
                            scrollpos = -edit_rect.height * 3
                        if pointerpos[1] > 79:
                            scrollpos = -edit_rect.height * 4
                        if pointerpos[1] > 99:
                            pointerpos[1] = 99
                    if event.key == pygame.K_LEFT:
                        pointerpos[0] -= 1
                        if pointerpos[0] < 0:
                            pointerpos[0] = 0
                    if event.key == pygame.K_RIGHT:
                        pointerpos[0] += 1
                        if pointerpos[0] > 7:
                            pointerpos[0] = 7
            else:
                if event.key == pygame.K_z:
                    zoom *= 1.1
                    # Below is hard math for keeping the camera centered. It works, I think...
                    campos = [campos[0]*1.1 + edit_rect.width/2*(1-1.1), campos[1]*1.1 + edit_rect.height/2*(1-1.1)]
                elif event.key == pygame.K_x:
                    zoom /= 1.1
                    # Below is hard math for keeping the camera centered. It works, I think...
                    campos = [campos[0]/1.1 + edit_rect.width/2*(1-1/1.1), campos[1]/1.1 + edit_rect.height/2*(1-1/1.1)]
                elif event.key == pygame.K_c:
                    # Below is hard math for keeping the camera centered. It works, I think...
                    campos = [campos[0]*4/zoom + edit_rect.width/2*(1-4/zoom), campos[1]*4/zoom + edit_rect.height/2*(1-4/zoom)]
                    zoom = 4
                elif event.key == pygame.K_UP:
                    campos[1] += 16 * zoom
                elif event.key == pygame.K_DOWN:
                    campos[1] -= 16 * zoom
                elif event.key == pygame.K_LEFT:
                    campos[0] += 16 * zoom
                elif event.key == pygame.K_RIGHT:
                    campos[0] -= 16 * zoom
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    saveAllMaps()
                    print("saved!")
                elif event.key == pygame.K_1:
                    state = 'groundmap'
                    stateblit = font.render("editing groundmap", False, (255, 255, 255))
                elif event.key == pygame.K_2:
                    state = 'alphamap'
                    stateblit = font.render("editing alphamap", False, (255, 255, 255))
                elif event.key == pygame.K_3:
                    state = 'betamap'
                    stateblit = font.render("editing betamap", False, (255, 255, 255))
                elif event.key == pygame.K_4:
                    state = 'boundmap'
                    stateblit = font.render("editing boundmap", False, (255, 255, 255))
                elif event.key == pygame.K_5:
                    state = 'objectmap'
                    stateblit = font.render("editing objects", False, (255, 255, 255))
                elif event.key == pygame.K_6:
                    state = 'encountermap'
                    stateblit = font.render("editing encounters", False, (255, 255, 255))
                elif state == 'boundmap':
                    if event.key == pygame.K_w:
                        boundmap_data['selected tile'] = 'u'
                    elif event.key == pygame.K_d:
                        boundmap_data['selected tile'] = 'r'
                    elif event.key == pygame.K_s:
                        boundmap_data['selected tile'] = 'd'
                    elif event.key == pygame.K_a:
                        boundmap_data['selected tile'] = 'l'
                    elif event.key == pygame.K_q:
                        boundmap_data['selected tile'] = 'neg'
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Button check
            addEncounterButton.push(event)

            if edit_rect.collidepoint(event.pos[0], event.pos[1]):
                # Tile check
                x = int((event.pos[0]-campos[0])/16/zoom)
                y = int((event.pos[1]-campos[1])/16/zoom)
                if state == 'groundmap':
                    try:
                        f = mapl[y+1].split(".")
                        if x == len(f)-1:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}\n"
                        else:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}"
                        tF = ''
                        for i in f:
                            tF += '.'
                            tF += i
                        mapl[y+1] = tF[1:]
                    except IndexError:
                        pass
                elif state == 'boundmap':
                    try:
                        f = list(bmapl[y])
                        if boundmap_data['selected tile'] == 'neg':
                            if f[x] not in ['0', '1']:
                                f[x] = '0'
                            else:
                                f[x] = str((int(f[x])+1)%2)
                        else:
                            f[x] = boundmap_data['selected tile']
                        bmapl[y] = "".join(f)
                    except:
                        pass
                elif state == 'betamap':
                    try:
                        f = bemapl[y+1].split(".")
                        if x == len(f)-1:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}\n"
                        else:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}"
                        tF = ''
                        for i in f:
                            tF += '.'
                            tF += i
                        bemapl[y+1] = tF[1:]
                    except IndexError:
                        pass
                elif state == 'alphamap':
                    try:
                        f = amapl[y+1].split(".")
                        if x == len(f)-1:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}\n"
                        else:
                            f[x] = f"{pointerpos[0]},{pointerpos[1]}"
                        tF = ''
                        for i in f:
                            tF += '.'
                            tF += i
                        amapl[y+1] = tF[1:]
                    except IndexError:
                        pass
                elif state == 'encountermap':
                    try:
                        f = list(emapl[y])
                        if event.button == 1:
                            f[x] = str((int(f[x])+1) % 2)
                        elif event.button == 0:
                            f[x] = str((int(f[x])-1) % 2)
                        emapl[y] = "".join(f)
                    except:
                        pass

    width  = int(mapl[0].split(".")[0])
    height = int(mapl[0].split(".")[1])
    map_surface = pygame.Surface((width, height))

    draw_map(mapl, map_surface)
    draw_map(bemapl, map_surface)
    e = eval(omapl[0].split(";")[1])
    map_surface.blit(player, (e[0]*16-2, e[1]*-16-17), (0, 0, 20, 25))
    draw_map(amapl, map_surface)

    if state == 'boundmap':
        for y in range(len(bmapl)):
            for x in range(len(bmapl[y])):
                if bmapl[y][x] == '0':
                    map_surface.blit(good, (x * 16, y * 16))
                if bmapl[y][x] == '1':
                    map_surface.blit(bad, (x * 16, y * 16))
                if bmapl[y][x] == 'u':
                    map_surface.blit(ledge_up,    (x * 16, y * 16))
                if bmapl[y][x] == 'r':
                    map_surface.blit(ledge_right, (x * 16, y * 16))
                if bmapl[y][x] == 'd':
                    map_surface.blit(ledge_down,  (x * 16, y * 16))
                if bmapl[y][x] == 'l':
                    map_surface.blit(ledge_left,  (x * 16, y * 16))
    elif state == 'encountermap':
        for y in range(len(emapl)):
            for x in range(len(emapl[y])):
                if emapl[y][x] in encounterSprites.keys():
                    map_surface.blit(encounterSprites[emapl[y][x]], (x*16, y*16))

    for i in omapl[1:]:
        if i.split(';')[0] == 'objectWarp':
            p = eval(i.split(';')[1])
            warp_destination = i.split(';')[2]
            map_surface.blit(warp, (p[0]*16, p[1]*16))
            f = pygame.font.SysFont("arial", 10).render(f"to {warp_destination}", False, (255, 0, 0))
            map_surface.blit(f, (8+p[0]*16-f.get_width()/2, p[1]*16+f.get_height()))

    screen.fill((0, 0, 20))
    screen.blit(pygame.transform.scale(map_surface, (int(width*zoom), int(height*zoom))), (campos[0], campos[1]))

    # DRAW SIDEBAR
    if state in ["groundmap", "betamap", "alphamap"]:
        pygame.draw.rect(screen, (255, 0, 255), sidebar_rect)
        screen.blit(pygame.transform.scale(tileset, (sidebar_rect.width, tileset.get_height()*2)), (edit_rect.width, scrollpos))
        pygame.draw.rect(screen, (255, 0, 0), (edit_rect.width+pointerpos[0]*32, pointerpos[1]*32+scrollpos, 32, 32), 2)
    if state == "boundmap":
        pygame.draw.rect(screen, (20, 20, 20), sidebar_rect)
        screen.blit(pygame.transform.scale(good, (100, 100)), (edit_rect.width+80, 130))
        screen.blit(pygame.transform.scale(bad, (100, 100)), (edit_rect.width+80, 420))
        screen.blit(font.render("no collision", True, (200, 255, 200)), (edit_rect.width+80, 250))
        screen.blit(font.render("collision", True, (255, 200, 200)), (edit_rect.width+80, 550))
    if state == "encountermap":
        screen.blit(font.render("WIP", True, (255, 255, 255)), (740, 300))
        addEncounterButton.draw(screen)

    screen.blit(font2.render("1 - ground, 2 - alpha, 3 - beta, 4 - bounds, 5 - objects, 6 - encounters, z/x - zoom, c - reset camera, ctrl+s - save map",
                             False,
                             (255, 255, 255),
                             (0, 0, 0)
                             ),
                (0, edit_rect.height-18)
                )

    # DRAW "editing ..." text
    pygame.draw.line(screen, (0, 255, 0), (edit_rect.width, 0), (edit_rect.width, edit_rect.height), 3)
    screen.blit(stateblit, (0, 0))

    # DRAW MOUSE POSITION TEXT
    p = pygame.mouse.get_pos()
    x = int((p[0] - campos[0]) / 16 / zoom)
    y = int((p[1] - campos[1]) / 16 / zoom)

    posblit = font2.render(f"{x}, {y}", False, (255, 255, 255), (0, 0, 0))
    screen.blit(posblit, (p[0]+15, p[1]))

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
closeAllLayers()
