import pokepy.pokemon as pkm
from visual_core import get_texture
from keybinding import continuous_key_action
from moving_object import MovingObject
from pos import Pos


class Player(MovingObject):
    def __init__(self, currentMap, npcmanager):
        self.pos = Pos(0, 0)
        self.texturemap = get_texture("player-kaori")
        self.textures = {
            'downidle'  : (0,   0),
            'down1'     : (32,  0),
            'down2'     : (64,  0),
            'upidle'    : (0,   32),
            'up1'       : (32,  32),
            'up2'       : (64,  32),
            'rightidle' : (0,   64),
            'right1'    : (32,  64),
            'right2'    : (64,  64),
            'leftidle'  : (0,   96),
            'left1'     : (32,  96),
            'left2'     : (64,  96),
            'run_down1' : (96,  0),
            'run_down2' : (128, 0),
            'run_down3' : (160, 0),
            'run_up1'   : (96,  32),
            'run_up2'   : (128, 32),
            'run_up3'   : (160, 32),
            'run_right1': (96,  64),
            'run_right2': (128, 64),
            'run_right3': (160, 64),
            'run_left1' : (96,  96),
            'run_left2' : (128, 96),
            'run_left3' : (160, 96),
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
            'run_north' : ['run_up2', 'run_up1', 'run_up3', 'run_up1'],
            'run_east'  : ['run_right2', 'run_right1', 'run_right3', 'run_right1'],
            'run_south' : ['run_down2', 'run_down1', 'run_down3', 'run_down1'],
            'run_west'  : ['run_left2', 'run_left1', 'run_left3', 'run_left1'],
        }
        self.currentStance = 'downidle'
        self.setAnimation('idle_south', 1)
        self.displacement = Pos(0, 0)
        self.remainingDuration = 0
        self.currentMap = currentMap
        self.npcmanager = npcmanager
        self.trainerdata = pkm.Trainer('Player')
        self.trainerdata.party.append(pkm.Pokemon('Charmander'))
        self.trainerdata.party[0].setlevel(4)
        self.moving = False
        self.direction = 'south'

    def warp(self, new_map, npcmanager, pos):
        self.currentMap = new_map
        self.npcmanager = npcmanager
        self.pos = Pos(new_map.warps[0])

    def checkWarps(self, warps):
        for warp in warps[1:]:
            if self.pos == warp[0]:
                return (warp[1], warp[2])

    def handle_continuous_key_action(self, pressed_keys):
        if self.moving:
            return

        if continuous_key_action(pressed_keys, 'World', 'run'):
            move_type = 'run'
        else:
            move_type = 'walk'

        if continuous_key_action(pressed_keys, 'World', 'north'):
            self.move(move_type, 'north')
        elif continuous_key_action(pressed_keys, 'World', 'east'):
            self.move(move_type, 'east')
        elif continuous_key_action(pressed_keys, 'World', 'south'):
            self.move(move_type, 'south')
        elif continuous_key_action(pressed_keys, 'World', 'west'):
            self.move(move_type, 'west')
        else:
            if self.anim_name.startswith('walk'):
                self.setAnimation('idle', 4)
            elif self.anim_name.startswith('run'):
                self.setAnimation('idle', 4)
