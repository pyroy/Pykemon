import random
import pygame


class NPC:
    def __init__(self, console, name, state, sprite, pathdata, dialogdata):
        self.console = console
        self.name = name
        self.state = state
        self.sprite = [-1*eval(sprite)[0], -1*eval(sprite)[1]]
        self.spriteimg = pygame.Surface([18, 25], pygame.SRCALPHA, 32)
        self.spriteimg.blit(pygame.image.load('textures/npcs/npcsheet.png'), self.sprite)
        self.pathdata = pathdata
        self.dialogdata = dialogdata
        self.pos = eval(self.pathdata[1])
        self.looking = 0
        self.frames = 0
        self.abspos = self.pos

    def getDrawData(self):
        return (self.spriteimg, self.pos)

    def update(self, ppos):
        if random.random() < 0.5:  # walking
            if random.random() < 0.5:  # back on path
                if self.pathdata.index(str(self.pos).replace(' ', '')) > 1:
                    newpos = eval(self.pathdata[self.pathdata.index(str(self.pos).replace(' ', ''))-1])
                    if newpos == ppos:
                        newpos = self.pos
                    self.abspos = newpos
                    self.updateMovement([(newpos[0]-self.pos[0])/8, (newpos[1]-self.pos[1])/8], 8)

            else:  # forwards on path
                if self.pathdata.index(str(self.pos).replace(' ', '')) < len(self.pathdata)-1:
                    newpos = eval(self.pathdata[self.pathdata.index(str(self.pos).replace(' ', ''))+1])
                    if newpos == ppos:
                        newpos = self.pos
                    self.abspos = newpos
                    self.updateMovement([(newpos[0]-self.pos[0])/8, (newpos[1]-self.pos[1])/8],8)

    def updateMovement(self, disp, frames):
        self.disp = disp
        self.frames = frames

    def updateFrames(self):
        if self.frames:
            self.frames -= 1
            self.pos = [self.pos[0]+self.disp[0], self.pos[1]+self.disp[1]]

    def action(self):
        self.console.command(bob.dialogdata[bob.state][1][:-1])


class NPCLoader:
    def __init__(self, console):
        self.path = 'npcs/'
        self.npcs = []
        self.updates = 0
        self.console = console

    def loadNPC(self, file):
        with open(self.path + file + '.txt') as npcfile:
            self.npcdata = npcfile.readlines()
        self.npcs.append(
            NPC(self.console,
                self.npcdata[0].split(';')[0],
                int(self.npcdata[0].split(';')[1]),
                self.npcdata[1].split(';')[0],
                self.npcdata[2].split(';')[:-1],
                [n.split(':') for n in self.npcdata[4:]] ) )
        return len(self.npcs)-1

    def update(self,ppos):
        self.updates = (self.updates + 1)%30
        if not self.updates:
            for npc in self.npcs:
                npc.update(ppos)
        for npc in self.npcs:
            npc.updateFrames()

    def checkBounds(self, pos):
        for npc in self.npcs:
            if pos == npc.abspos:
                return False
        return True
