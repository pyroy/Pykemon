import math, random
import pygame
import pokemon as pkm

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
        self.setAnimation('idledown', 1)
        self.displacement = [0,0]
        self.remainingDuration = 0
        self.bounds = bounds
        self.trainerdata = pkm.Trainer('Player')
        self.trainerdata.party.append(pkm.Pokemon('Starmie'))
        self.moving = False

    def draw(self, pos, surface):
        global battle, activeBattle
        surface.blit(self.texturemap, pos, self.textures[self.currentStance]+(20,25))

    def update(self, currentMap):
        flag = self.updatePosition(currentMap)
        self.updateAnimation()
        return flag

    def updatePosition(self, currentMap):
        if self.remainingDuration:
            self.pos[0] += self.displacement[0]
            self.pos[1] += self.displacement[1]
            self.remainingDuration -= 1
        else:
            self.moving = False
            return 'stopped moving'

    def updateAnimation(self):
        if len(self.anim) > 1:
            self.framesSinceStartAnim = (self.framesSinceStartAnim + 1) % (len(self.anim) * self.animDelay)
            self.currentStance = self.anim[math.floor(self.framesSinceStartAnim/self.animDelay)]
        else:
            self.currentStance = self.anim[0]

    def setAnimation(self,animName,delay):
        self.animName = animName
        self.anim = self.animations[animName]
        self.animDelay = delay
        self.framesSinceStartAnim = 0

    def setMovement(self,displacement,duration,dir,npcloader):
        if self.bounds.checkBounds( int(self.pos[0]/16)+dir[0],int(self.pos[1]/16)+dir[1] ):
            if npcloader.checkBounds( [int(self.pos[0]/16)+dir[0],-1*int(self.pos[1]/16)-dir[1]] ):
                self.remainingDuration = duration
                self.displacement = displacement
                self.moving = True

    def warp(self,map,pos):
        global currentMap
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
        for warp in warps[1:]:
            if self.pos == warp[0]:
                return (warp[1], warp[2])

    def resetAnimations(self):
        pass
