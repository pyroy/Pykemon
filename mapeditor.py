import pygame,os

from mapeditorgui.pygamesliders import *
from mapeditorgui.pygamebuttons import *

def drawmap(mapdata):
    for y in range(len(mapdata) - 1):
        for x in range(len(mapdata[y + 1].split("."))):
            locx = int(mapdata[y + 1].split(".")[x].split(",")[0])
            locy = int(mapdata[y + 1].split(".")[x].split(",")[1])
            ttt.blit(tileset, (x * 16, y * 16), (locx * 16, locy * 16, 16, 16))

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
    groundmap    = open(f"maps/{name}/map.txt",     mode)
    betamap      = open(f"maps/{name}/beta.txt",    mode)
    alphamap     = open(f"maps/{name}/alpha.txt",   mode)
    boundmap     = open(f"maps/{name}/bounds.txt",  mode)
    objects      = open(f"maps/{name}/objects.txt", mode)
    encountermap = open(f"maps/{name}/encounters.txt", mode)

def closeAllLayers():
    groundmap.close()
    alphamap.close()
    betamap.close()
    objects.close()
    boundmap.close()
    encountermap.close()

a = input("load, create or delete? (l/c/d) >")
if a == 'l':
    name = input("load map: ")
    try:
        openAllLayers(name, "r+")
    except:
        print(f"Make sure the map '{name}' exists and has all the necessary files.")
        input()
        quit()

elif a == 'c':
    name = input("name of new map: ")
    if not os.path.exists(os.getcwd()+f'/maps/{name}/'):
        os.makedirs(os.getcwd()+f'/maps/{name}/')

    openAllLayers(name, "w+")
    width  = int(input("width = " ))*16
    height = int(input("height = "))*16
    groundmap.write(f'{width}.{height}\n')
    alphamap.write (f'{width}.{height}\n')
    betamap.write  (f'{width}.{height}\n')

    for layer, default, separator in [(groundmap, '0,1', '.'), (alphamap, '0,0', '.'), (betamap, '0,0', '.'), (boundmap, '0', ''), (encountermap, '0', '')]:
        for _ in range(int(height/16)):
            layer.write(separator.join([default] * int(width/16)) + '\n')

    encountermap.write('0;NONE')

    objects.write('objectPlayerPos;[0,0];\n')
    closeAllLayers()
    print(f"{name} has been created! please run again to edit it.")
    input()
    quit()

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

screen = pygame.display.set_mode((640+8*16*2,640))
pygame.display.set_caption("Map Editor")
clock = pygame.time.Clock()
done = False

campos = [0,0]
pointerpos = [0,0]

#textures
tileset   = pygame.image.load("textures/tileset-blackvolution.png").convert_alpha()
good      = pygame.image.load("textures/good.png").convert_alpha()
bad       = pygame.image.load("textures/bad.png").convert_alpha()
warp      = pygame.image.load("textures/warp.png").convert_alpha()
player    = pygame.image.load("textures/player-kaori.png").convert_alpha()

#pokeball sprites
encounterSprites = {}
src = pygame.image.load("textures/pokeballs.png").convert_alpha()
for i in range(25):
    blankSlate = pygame.Surface((64,64), pygame.SRCALPHA)
    blankSlate.blit(src, (0,0), ((i%5)*64,(i//5)*64,64,64))
    encounterSprites[str(i+1)] = pygame.transform.scale(blankSlate, (16,16))

mapl   = groundmap.readlines()
bmapl  = boundmap.readlines()
bemapl = betamap.readlines()
amapl  = alphamap.readlines()
omapl  = objects.readlines()
emapl  = encountermap.readlines()

font  = pygame.font.SysFont("arial",30)
font2 = pygame.font.SysFont("arial",15)
stateblit = font.render("editing groundmap",False,(255,255,255))
state = 'groundmap'

zoom = 4
scrollpos = 0

#buttons for encounter
addEncounterButton = Simplebutton(200,50,(60,60,60),"Add Encounter...",pygame.font.Font("jackeyfont.ttf",20))
addEncounterButton.border = 1
addEncounterButton.pos = (700,400)
addEncounterButton.textcolor = (255,255,255)

#main loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_SPACE]: #Selecting tiles
                if pygame.key.get_pressed()[pygame.K_r]:
                    if event.key == pygame.K_UP:
                        scrollpos += 640
                        pointerpos[1] -= 20
                        if pointerpos[1] < 0:
                            pointerpos[1] = 0 #pointerpos is the position of the selection sprite
                            scrollpos = 0 #and scrollpos is which 'page' you are on
                    if event.key == pygame.K_DOWN:
                        scrollpos -= 640
                        pointerpos[1] += 20
                        if pointerpos[1] > 99:
                            pointerpos[1] = 99
                            scrollpos = -640*4
                else:
                    if event.key == pygame.K_UP:
                        pointerpos[1] -= 1
                        if pointerpos[1] < 40:
                            scrollpos = -640
                        if pointerpos[1] < 20:
                            scrollpos = 0
                        if pointerpos[1] < 0:
                            pointerpos[1] = 0
                    if event.key == pygame.K_DOWN:
                        pointerpos[1] += 1
                        if pointerpos[1] > 19:
                            scrollpos = -640
                        if pointerpos[1] > 39:
                            scrollpos = -640*2
                        if pointerpos[1] > 59:
                            scrollpos = -640 * 3
                        if pointerpos[1] > 79:
                            scrollpos = -640 * 4
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
                    campos = [campos[0]*1.1 + 320*(1-1.1), campos[1]*1.1 + 320*(1-1.1)]
                if event.key == pygame.K_x:
                    zoom /= 1.1
                    # Below is hard math for keeping the camera centered. It works, I think...
                    campos = [campos[0]/1.1 + 320*(1-1/1.1), campos[1]/1.1 + 320*(1-1/1.1)]
                if event.key == pygame.K_c:
                    # Below is hard math for keeping the camera centered. It works, I think...
                    campos = [campos[0]*4/zoom + 320*(1-4/zoom), campos[1]*4/zoom + 320*(1-4/zoom)]
                    zoom = 4
                if event.key == pygame.K_UP:
                    campos[1] += 16 * zoom
                if event.key == pygame.K_DOWN:
                    campos[1] -= 16 * zoom
                if event.key == pygame.K_LEFT:
                    campos[0] += 16 * zoom
                if event.key == pygame.K_RIGHT:
                    campos[0] -= 16 * zoom
                if event.key == pygame.K_s:
                    saveAllMaps()
                    print("saved!")
                if event.key == pygame.K_g:
                    state = 'groundmap'
                    stateblit = font.render("editing groundmap", False, (255, 255, 255))
                if event.key == pygame.K_b:
                    state = 'betamap'
                    stateblit = font.render("editing betamap", False, (255, 255, 255))
                if event.key == pygame.K_n:
                    state = 'boundmap'
                    stateblit = font.render("editing boundmap", False, (255, 255, 255))
                if event.key == pygame.K_a:
                    state = 'alphamap'
                    stateblit = font.render("editing alphamap", False, (255, 255, 255))
                if event.key == pygame.K_o:
                    state = 'objectmap'
                    stateblit = font.render("editing objects", False, (255, 255, 255))
                if event.key == pygame.K_e:
                    state = 'encountermap'
                    stateblit = font.render("editing encounters", False, (255, 255, 255))
        if event.type == pygame.MOUSEBUTTONDOWN:
            #button check
            addEncounterButton.push(event)
            #tile check
            x = int((event.pos[0]-campos[0])/16/zoom)
            y = int((event.pos[1]-campos[1])/16/zoom)
            if state == 'groundmap':
                try:
                    f = mapl[y+1].split(".")
                    if x == len(f)-1:
                        f[x] = '{},{}\n'.format(pointerpos[0],pointerpos[1])
                    else:
                        f[x] = '{},{}'.format(pointerpos[0], pointerpos[1])
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
                    f[x] = str((int(f[x])+1)%2)
                    bmapl[y] = "".join(f)
                except:
                    pass
            elif state == 'betamap':
                try:
                    f = bemapl[y+1].split(".")
                    if x == len(f)-1:
                        f[x] = '{},{}\n'.format(pointerpos[0],pointerpos[1])
                    else:
                        f[x] = '{},{}'.format(pointerpos[0], pointerpos[1])
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
                        f[x] = '{},{}\n'.format(pointerpos[0],pointerpos[1])
                    else:
                        f[x] = '{},{}'.format(pointerpos[0], pointerpos[1])
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
                        f[x] = str((int(f[x])+1)%2)
                    elif event.button == 0:
                        f[x] = str((int(f[x])-1)%2)
                    emapl[y] = "".join(f)
                except:
                    pass

    width,height = int(mapl[0].split(".")[0]),int(mapl[0].split(".")[1])
    ttt = pygame.Surface((width,height))

    drawmap(mapl)
    drawmap(bemapl)
    e = eval(omapl[0].split(";")[1])
    ttt.blit(player, (e[0]*16-2,e[1]*-16-17), (0,0,20,25))
    drawmap(amapl)

    if state == 'boundmap':
        for y in range(len(bmapl)):
            for x in range(len(bmapl[y])):
                if bmapl[y][x] == '0':
                    ttt.blit(good, (x * 16, y * 16))
                if bmapl[y][x] == '1':
                    ttt.blit(bad, (x * 16, y * 16))
    elif state == 'encountermap':
        for y in range(len(emapl)):
            for x in range(len(emapl[y])):
                if emapl[y][x] in encounterSprites.keys():
                    ttt.blit(encounterSprites[ emapl[y][x] ], (x * 16, y * 16))

    for i in omapl[1:]:
        if i.split(';')[0] == 'objectWarp':
            p = eval(i.split(';')[1])
            ttt.blit(warp, (p[0]*16,p[1]*16))
            f = pygame.font.SysFont("arial",10).render("to {}".format(i.split(';')[2]), False, (255,0,0))
            ttt.blit(f,(8+p[0]*16-f.get_width()/2,p[1]*16+f.get_height()))

    screen.fill((0,0,20))
    screen.blit(pygame.transform.scale(ttt, (int(width*zoom),int(height*zoom))), (campos[0],campos[1]))
    if state in ["groundmap", "betamap", "alphamap"]:
        pygame.draw.rect(screen, (255,0,255), (640,0,640+8*16*2-640,640))
        screen.blit(pygame.transform.scale(tileset, (8*16*2,tileset.get_height()*2)), (640,scrollpos))
        pygame.draw.rect(screen, (255,0,0), (640+pointerpos[0]*32,pointerpos[1]*32+scrollpos,32,32), 2)
    if state == "boundmap":
        pygame.draw.rect(screen, (20,20,20), (640,0,640+8*16*2-640,640))
        screen.blit(pygame.transform.scale(good, (100,100)), (720,130))
        screen.blit(pygame.transform.scale(bad, (100,100)), (720,420))
        screen.blit(font.render("no collision",True,(200,255,200)),(700,250))
        screen.blit(font.render("collision",True,(255,200,200)),(715,550))
    if state == "encountermap":
        screen.blit(font.render("WIP",True,(255,255,255)),(740,300))
        addEncounterButton.draw(screen)
    pygame.draw.line(screen,(0,255,0),(640,0),(640,640),3)
    screen.blit(stateblit,(0,0))

    p = pygame.mouse.get_pos()
    x = int((p[0] - campos[0]) / 16 / zoom)
    y = int((p[1] - campos[1]) / 16 / zoom)

    posblit = font2.render("{}, {}".format(x,y), False, (255, 255, 255), (0,0,0))
    screen.blit(posblit, (p[0]+15,p[1]))

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
closeAllLayers()
