import random
from visual_core import get_texture
from moving_object import MovingObject, coordinates_to_direction
from pos import Pos


class NPC(MovingObject):
    def __init__(self, console, name, state, sprite, pathdata, dialogdata, npcloader):
        self.console = console
        self.name = name
        self.state = state
        self.pathdata = pathdata
        self.dialogdata = dialogdata
        self.npcloader = npcloader
        self.abspos = self.pathdata[0]
        self.pos = self.pathdata[0]*16
        self.texturemap = get_texture("npcs\\npcsheet")
        self.textures = {
            'downidle'  : (64,  32),
            'down1'     : (64,  64),
            'down2'     : (64,  96),
            'upidle'    : (0,    0),
            'up1'       : (70,   0),
            'up2'       : (32,  96),
            'rightidle' : (32,   0),
            'right1'    : (32,  32),
            'right2'    : (32,  64),
            'leftidle'  : (0,   64),
            'left1'     : (0,   33),
            'left2'     : (0,   96),
        }
        self.animations = {
            'idle_north': ['upidle'],
            'idle_east' : ['rightidle'],
            'idle_south': ['downidle'],
            'idle_west' : ['leftidle'],
            'walk_north': ['up2', 'upidle', 'up1', 'upidle'],
            'walk_east' : ['right2', 'rightidle', 'right1', 'rightidle'],
            'walk_south': ['down2', 'downidle', 'down1', 'downidle'],
            'walk_west' : ['left2', 'leftidle', 'left1', 'leftidle'],
        }
        self.currentStance = 'downidle'
        self.setAnimation('idle_south', 1)
        self.displacement = (0, 0)
        self.remainingDuration = 0
        self.moving = False

    def update(self):
        # print(self.abspos, self.pos//16, self.abspos == self.pos//16)
        flag = super().update()
        if flag == "stopped moving":
            self.setAnimation('idle', 8)

    def new_movement(self, ppos):
        tile_pos = self.pos // 16
        if random.random() < 0.5:  # walking
            if random.random() < 0.5:  # back on path
                if self.pathdata.index(tile_pos) > 0:
                    newpos = self.pathdata[self.pathdata.index(tile_pos)-1]
                else:
                    newpos = tile_pos
            else:  # forwards on path
                if self.pathdata.index(tile_pos) < len(self.pathdata)-1:
                    newpos = self.pathdata[self.pathdata.index(tile_pos)+1]
                else:
                    newpos = tile_pos
            if newpos == ppos:
                newpos = tile_pos
            offset = newpos - tile_pos
            if offset != (0, 0):
                direction = coordinates_to_direction(offset)
                self.move('walk', direction)
                if self.moving:
                    self.abspos += offset

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
                [Pos(eval(pos)) for pos in self.npcdata[2].split(';')[1:-1]],
                [n.split(':') for n in self.npcdata[4:]],
                self
            )
        )
        return len(self.npcs)-10

    def update(self, ppos):
        self.updates = (self.updates + 1) % 30
        if not self.updates:
            for npc in self.npcs:
                npc.new_movement(ppos)
        for npc in self.npcs:
            npc.update()

    def new_map(self, map):
        for npc in self.npcs:
            npc.currentMap = map

    def checkBounds(self, pos):
        return not any(pos == npc.abspos for npc in self.npcs)
