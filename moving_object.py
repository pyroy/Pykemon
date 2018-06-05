import math
from pos import Pos


def direction_to_coordinates(dir):
    coordinates = {
        'north': (0, -1),
        'east' : (1, 0),
        'south': (0, 1),
        'west' : (-1, 0),
    }
    try:
        return coordinates[dir]
    except KeyError:
        raise ValueError(f"Direction {dir} is invalid.")


def coordinates_to_direction(offset):
    coordinates = {
        (0, -1): 'north',
        (1,  0): 'east',
        (0,  1): 'south',
        (-1, 0): 'west',
    }
    try:
        return coordinates[offset]
    except KeyError:
        raise ValueError(f"Direction {offset} is invalid.")


class MovingObject:
    def draw(self, pos, surface):
        surface.blit(self.texturemap, pos, self.textures[self.currentStance] + (32, 32))

    def update(self):
        flag = self.updatePosition()
        self.updateAnimation()
        return flag

    def move(self, type, dir):
        if type == 'run':
            move_length = 4
        elif type == 'walk':
            move_length = 8
        else:
            raise ValueError(f"Invalid move type '{type}''")

        self.direction = dir.lower()
        move_dir = direction_to_coordinates(self.direction)

        self.setMovement(move_length, move_dir)
        if not self.anim_name == f'{type}_{dir}':
            self.setAnimation(f'{type}_{dir}', 8)

    def updatePosition(self):
        bounds = self.currentMap.bounds
        if self.remainingDuration:
            self.pos += self.displacement
            self.remainingDuration -= 1
        else:
            pos_div = self.pos//16
            if bounds.at_pos(*pos_div) == 'u':
                self.move('walk', 'north')
            elif bounds.at_pos(*pos_div) == 'r':
                self.move('walk', 'east')
            elif bounds.at_pos(*pos_div) == 'd':
                self.move('walk', 'south')
            elif bounds.at_pos(*pos_div) == 'l':
                self.move('walk', 'west')
            elif self.moving:
                self.moving = False
                return 'stopped moving'

    def updateAnimation(self):
        if len(self.anim) > 1:
            self.framesSinceStartAnim = (self.framesSinceStartAnim + 1) % (len(self.anim) * self.animDelay)
            self.currentStance = self.anim[self.framesSinceStartAnim//self.animDelay]
        else:
            self.currentStance = self.anim[0]

    def setAnimation(self, anim_name, delay):
        if anim_name == 'idle':
            anim_name = 'idle_' + self.anim_name.split('_')[1]
        self.anim_name = anim_name
        self.anim = self.animations[anim_name]
        self.animDelay = delay
        self.framesSinceStartAnim = 0

    def setMovement(self, duration, dir):
        dir = Pos(dir)
        new_x = self.pos[0]//16 + dir[0]
        new_y = self.pos[1]//16 + dir[1]
        if self.currentMap.bounds.checkBounds(new_x, new_y, dir) and self.npcloader.checkBounds(Pos(new_x, new_y)):
            self.remainingDuration = duration
            self.displacement = dir * 16 // duration
            self.moving = True

    @property
    def direction_vector(self):
        return direction_to_coordinates(self.direction)
