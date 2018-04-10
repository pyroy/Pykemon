import math, random
import pygame
import pokemon as pkm

class Player:
    def __init__(self,bounds, npc):
        self.pos = [0,0]
        self.texturemap = pygame.image.load("textures/player-kaori.png").convert_alpha()
        # @SPEED: We could 'map' these directly into the coordinates above for a slight speed improvement
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
            'left2'     : (40,75),
            'run_down1' : (60, 0),
            'run_down2' : (80, 0),
            'run_down3' : (100,0),
            'run_up1'   : (60, 25),
            'run_up2'   : (80, 25),
            'run_up3'   : (100,25),
            'run_right1': (60, 50),
            'run_right2': (80, 50),
            'run_right3': (100,50),
            'run_left1' : (60, 75),
            'run_left2' : (80, 75),
            'run_left3' : (100,75),
        }
        self.animations = {
            'idle_north': ['upidle'],
            'idle_east' : ['rightidle'],
            'idle_south': ['downidle'],
            'idle_west' : ['leftidle'],
            'walk_north': ['up2','upidle','up1','upidle'],
            'walk_east' : ['right2','rightidle','right1','rightidle'],
            'walk_south': ['down2','downidle','down1','downidle'],
            'walk_west' : ['left2','leftidle','left1','leftidle'],
            'run_north' : ['run_up2', 'run_up1', 'run_up3', 'run_up1'],
            'run_east'  : ['run_right2', 'run_right1', 'run_right3', 'run_right1'],
            'run_south' : ['run_down2', 'run_down1', 'run_down3', 'run_down1'],
            'run_west'  : ['run_left2', 'run_left1', 'run_left3', 'run_left1'],
        }
        self.currentStance = 'downidle'
        self.setAnimation('idle_south', 1)
        self.displacement = [0,0]
        self.remainingDuration = 0
        self.bounds = bounds
        self.npcloader = npc
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

    def move(self, type, dir):
        if type == 'run':
            move_length = 4
        elif type == 'walk':
            move_length = 8
        else:
            return Error(f"Invalid move type '{type}''")

        dir = dir.lower()
        if   dir == 'north':
            move_dir = (0,1)
        elif dir == 'east':
            move_dir = (1,0)
        elif dir == 'south':
            move_dir = (0,-1)
        elif dir == 'west':
            move_dir = (-1,0)
        else:
            return Error(f"Invalid direction ''{dir}''")

        self.setMovement(move_length, move_dir)
        if not self.animName == f'{type}_{dir}':
            self.setAnimation(f'{type}_{dir}', 8)


    def updatePosition(self, currentMap):
        if self.remainingDuration:
            self.pos[0] += self.displacement[0]
            self.pos[1] += self.displacement[1]
            self.remainingDuration -= 1
        else:
            pos_div = (int(self.pos[0]/16), int(self.pos[1]/16))
            if self.bounds.at_pos(*pos_div) == 'u':
                self.move('walk', 'north')
            elif self.bounds.at_pos(*pos_div) == 'r':
                self.move('walk', 'east')
            elif self.bounds.at_pos(*pos_div) == 'd':
                self.move('walk', 'south')
            elif self.bounds.at_pos(*pos_div) == 'l':
                self.move('walk', 'west')
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

    def setMovement(self, duration, dir):
        if self.bounds.checkBounds(int(self.pos[0]/16)+dir[0], int(self.pos[1]/16)+dir[1], dir):
            if self.npcloader.checkBounds( [int(self.pos[0]/16)+dir[0],-1*int(self.pos[1]/16)-dir[1]] ):
                self.remainingDuration = duration
                self.displacement = (dir[0] * 16 // duration, dir[1] * 16 // duration)
                self.moving = True

    def warp(self,new_map, npc,pos):
        self.bounds = new_map.bounds
        self.npcloader = npc
        self.pos = new_map.warps[0]

    def checkWarps(self,warps):
        for warp in warps[1:]:
            if self.pos == warp[0]:
                return (warp[1], warp[2])
