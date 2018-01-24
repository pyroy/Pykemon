#standard imports
import math, time

#main imports
import maploader, npcloader
import battlescene
import pokepy.pokemon as pkm

#pygame setup
import pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
done = False

#Player class
class Player:
    def __init__(self,bounds):
        self.pos = [0,0]
        self.texturemap = pygame.image.load("textures/player-kaori.png").convert_alpha()
        self.textures = {
            'downidle'  : (0,0),
            'down1'     : (20,0),
            'down2'     : (40,0),
            'upidle'    : (0,25),
            'up1'       : (20,25),
            'up2'       : (40,25),
            'rightidle' : (0,50),
            'right1'    : (20,50),
            'right2'    : (40,50),
            'leftidle'  : (0,75),
            'left1'     : (20,75),
            'left2'     : (40,75)
        }
        self.animations = {
            'idledown'  : ['downidle'],
            'idleup'    : ['upidle'],
            'idleright' : ['rightidle'],
            'idleleft'  : ['leftidle'],
            'walkdown'  : ['downidle','down2','downidle','down1'],
            'walkup'    : ['upidle','up2','upidle','up1'],
            'walkright' : ['rightidle','right2','rightidle','right1'],
            'walkleft'  : ['leftidle','left2','leftidle','left1']
        }
        self.currentStance = 'downidle'
        self.updateAnim('idledown', 1)
        self.displacement = [0,0]
        self.remainingDuration = 0
        self.bounds = bounds
        self.trainerdata = pkm.Trainer('Player')
        self.trainerdata.party.append(pkm.Pokemon('Starmie'))

    def draw(self,pos):
        if len(self.anim) > 1:
            self.framesSinceStartAnim = (self.framesSinceStartAnim + 1) % (len(self.anim) * self.animDelay)
            self.currentStance = self.anim[math.floor(self.framesSinceStartAnim/self.animDelay)]
        else:
            self.currentStance = self.anim[0]
        ttt.blit(self.texturemap, pos, self.textures[self.currentStance]+(20,25))
        if self.remainingDuration:
            self.pos[0] += self.displacement[0]
            self.pos[1] += self.displacement[1]
            self.remainingDuration -= 1
        else:
            self.moving = False

    def updateAnim(self,animName,delay):
        self.animName = animName
        self.anim = self.animations[animName]
        self.animDelay = delay
        self.framesSinceStartAnim = 0

    def updateMovement(self,displacement,duration,dir):
        if self.bounds.checkBounds( int(self.pos[0]/16)+dir[0],int(self.pos[1]/16)+dir[1] ):
            if nl.checkBounds( [int(self.pos[0]/16)+dir[0],-1*int(self.pos[1]/16)-dir[1]] ):
                self.remainingDuration = duration
                self.displacement = displacement
                self.moving = True

    def warp(self,map,pos):
        global currentMap
        screen.fill((0,0,0))
        # loadblit = pygame.font.Font('jackeyfont.ttf',60).render('LOADING',False,(255,255,255),(0,0,0))
        # loadblitja = pygame.font.Font('jackeyfont.ttf',60).render('読み込み中', False, (255, 255, 255), (0, 0, 0))
        # screen.blit(loadblit,(300-loadblit.get_width()/2,int(285-loadblit.get_height())))
        # screen.blit(loadblitja, (300 - loadblitja.get_width() / 2, 315))
        # pygame.display.flip()
        currentMap = ml.loadMapObject(map)
        self.bounds = currentMap.bounds
        self.pos = currentMap.warps[0]
        self.resetAnimations()

    def checkWarps(self,warps):
        for i in range(1,len(warps)):
            if player.pos == warps[i][0]:
                player.warp(warps[i][1],warps[i][2])
                break

    def resetAnimations(self):
        self.remainingDuration = 0
        self.animFrame = 0
        self.animDelay = 0

#Console
class Console:
    def __init__(self):
        self.state = 0

    def command(self,command):
        subCommands = command.split(';')
        for action in subCommands:
            if action.startswith('SAY'):
                self.dialogBox(action.split(',')[1])

    def dialogBox(self, text):
        print(text, 'ID:'+str(self.state))
        self.state += 1

console = Console()

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

creditscreen = ['Pyroy proudly presents...',
                ' ',
                'Pykemon!',
                ' ',
                '-----[Credits]-----',
                'Font: Jackey @ nonty.net/font/',
                'Trainer Sprites: Kaori @ spriters-resource.net',
                'Tileset 1: Shinygold @ fanart.pokefans.net/tutorials/mapping/tilesets',
                'Pokemon Data: stefankendall @ github.com/stefankendall/pokemondatacollector/',
                ' ',
                '-----[Tools used to create this game]-----',
                '- Python 3.4.0',
                '- Pygame',
                '- paint.net',
                '- Py2exe',
                ' ',
                ' ',
                'This screen will disappear in 1 second...']

screen.fill((0,0,0))
counter = 0
f = pygame.font.SysFont("arial",20)
h = f.render('test',False,(255,255,255)).get_height()+3
for line in creditscreen:
    screen.blit(f.render(line,False,(255,255,255)), (5,h*counter))
    counter += 1
pygame.display.flip()
time.sleep(1)

nl.loadNPC('bob')
nl.loadNPC('will')

foe = pkm.Trainer('Damion')
foe.party.append(pkm.Pokemon('Numel'))

battle = False
activeBattle = battlescene.Battle(screen, player.trainerdata, foe)

menuitem = 0
while not done:
    zoom += 0
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
                console.dialogBox('saving! please don\'t turn off the console!')
            elif event.key == pygame.K_RETURN and not battle and not menu:
                #player.activate()
                pass;

    if not battle: #scene outside battle
        drawx = ttt.get_width()/2-player.pos[0]-8
        drawy = ttt.get_height()/2+player.pos[1]

        ttt.blit(currentMap.ground, (drawx,drawy)) #groundmap
        ttt.blit(currentMap.beta, (drawx, drawy)) #betamap

        drawPlayer = True
        nl.update([int(player.pos[0]/16),-1*int(player.pos[1]/16)])
        for npc in nl.npcs:
            surface, position = npc.getDrawData()
            if position[1] * 16 + drawy - 13 > ttt.get_height()/2-13 and drawPlayer:
                player.draw((ttt.get_width()/2-10,ttt.get_height()/2-13))
                drawPlayer = False
            position = (position[0] * 16 + drawx - 1, position[1] * 16 + drawy - 13)
            ttt.blit(surface, position)
        if drawPlayer: player.draw((ttt.get_width()/2-10,ttt.get_height()/2-13))

        ttt.blit(currentMap.alpha,(drawx, drawy)) #alphamap

        screen.blit(pygame.transform.scale(ttt, (600,600)), (0,0))
        screen.blit(pygame.transform.scale(menublit,(200,2*184)), (400+menupos, 0))
        screen.blit(menuselect, (400+menupos, menuitem*70))

    if not player.moving and not menu and not battle:
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            player.updateMovement([0,-2],8,(0,-1))
            if not player.animName == 'walkdown':
                player.updateAnim('walkdown', 4)
        elif pygame.key.get_pressed()[pygame.K_UP]:
            player.updateMovement([0,2],8,(0,1))
            if not player.animName == 'walkup':
                player.updateAnim('walkup', 4)
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            player.updateMovement([2,0],8,(1,0))
            if not player.animName == 'walkright':
                player.updateAnim('walkright', 4)
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            player.updateMovement([-2,0],8,(-1,0))
            if not player.animName == 'walkleft':
                player.updateAnim('walkleft', 4)
        else:
            if player.animName.startswith('walk'):
                player.updateAnim(player.animName.replace('walk', 'idle'), 4)

    if menuframes:
        menupos -= menudisp*(10-menuframes)
        menuframes -= 1

    if battle: activeBattle.update(); activeBattle.draw() #scene in battle

    player.checkWarps(currentMap.warps)

    pygame.display.flip()
    clock.tick(60)

pygame.display.quit()
