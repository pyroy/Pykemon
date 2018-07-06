import random
from visual_core import get_texture
from moving_object import MovingObject, coordinates_to_direction
from pos import Pos
from events import SayEvent, ChooseEvent


class NPC(MovingObject):
    def setup(self, console, npcmanager):
        self.console = console
        self.npcmanager = npcmanager
        self.vars = {}
        self.path = [Pos(p) for p in self.path]
        self.abspos = self.path[0]
        self.pos = self.path[0]*16
        self.texturemap = get_texture("npcs\\npcsheet")
        self.textures = {
            'downidle'  : (64,  32),
            'down1'     : (64,  64),
            'down2'     : (64,  96),
            'upidle'    : (0,    0),
            'up1'       : (64,   0),
            'up2'       : (32,  96),
            'rightidle' : (32,   0),
            'right1'    : (32,  32),
            'right2'    : (32,  64),
            'leftidle'  : (0,   64),
            'left1'     : (0,   32),
            'left2'     : (0,   96),
        }
        self.textures = {key: (tex[0]+self.sprite[0]*96, tex[1]+self.sprite[1]*128) for (key, tex) in self.textures.items()}
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
        self.talking = False

    def update(self):
        # print(self.abspos, self.pos//16, self.abspos == self.pos//16)
        flag = super().update()
        if flag == "stopped moving":
            self.setAnimation('idle', 8)

    def new_movement(self, ppos):
        if self.talking:
            return
        
        tile_pos = self.pos // 16
        if random.random() < 0.5:  # walking
            if random.random() < 0.5:  # back on path
                if self.path.index(tile_pos) > 0:
                    newpos = self.path[self.path.index(tile_pos)-1]
                else:
                    newpos = tile_pos
            else:  # forwards on path
                if self.path.index(tile_pos) < len(self.path)-1:
                    newpos = self.path[self.path.index(tile_pos)+1]
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
    
    def interact_wrapper(self, func):
        def new_interact(player_pos):
            self.turn((player_pos - self.pos)//16)
            self.talking = True
            yield from func()
            self.talking = False
        return new_interact
    
    def say(self, *text):
        return lambda generator: SayEvent(text, callback=generator)
    
    def choice(self, key, options):
        return lambda generator: ChooseEvent(options, var_dict=self.vars, var_key=key, callback=generator)

class NPCManager:
    def __init__(self, console):
        self.npcs = []
        self.updates = 0
        self.console = console

    def set_npcs(self, currentMap):
        self.npcs.clear()
        for npc_class in currentMap.npcs:
            npc = npc_class()
            npc.setup(self.console, self)
            if hasattr(npc, "interact"):
                npc.interact = npc.interact_wrapper(npc.interact)
            else:
                npc.interact = None
            npc.currentMap = currentMap
            self.npcs.append(npc)

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
