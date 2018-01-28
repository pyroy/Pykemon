import pygame
from collections import namedtuple

class Bounds:
    def __init__(self,b):
        self.bounds = b

    def checkBounds(self,x,y):
        y = -y
        if y in range(len(self.bounds)) and x in range(len(self.bounds[0])):
            if int(self.bounds[y][x]) == 1:
                return False
            else:
                return True

class Encounters:
    def __init__(self, e):
        self.encounters = e

    def checkEncounters(self,x,y):
        y = -y
        if y in range(len(self.encounters)) and x in range(len(self.encounters[0])):
            return int(self.encounters[y][x])

Map = namedtuple("Map", [
    "ground",
    "alpha",
    "beta",
    "bounds",
    "warps",
    "encounters"
])

class MapLoader:
    def __init__(self):
        self.tileset = pygame.image.load("textures/tileset-blackvolution.png")

    def loadMapObject(self, map):
        return Map(
            self.loadDrawMap(map, "map"),
            self.loadDrawMap(map, "alpha", transparent=True),
            self.loadDrawMap(map, "beta", transparent=True),
            self.loadBoundsMap(map),
            self.getWarpPoints(map),
            self.getEncounters(map)
        )

    def loadDrawMap(self,map,name,transparent=False):
        with open(f"maps/{map}/{name}.txt") as file:
            lines = file.readlines()
        drawmap = pygame.Surface((int(lines[0].split(".")[0]),int(lines[0].split(".")[1])))
        if transparent:
            drawmap.fill((255,0,255))
            drawmap.set_colorkey((255,0,255))
            drawmap.convert_alpha()
        else:
            drawmap.fill((255,255,255))

        for y,row in enumerate(lines[1:]):
            for x,tile in enumerate(row.split(".")):
                locx = int(tile.split(",")[0])
                locy = int(tile.split(",")[1])
                drawmap.blit(self.tileset,(x*16,y*16),(locx*16,locy*16,16,16))

        return drawmap

    def loadBoundsMap(self,map):
        with open(f"maps/{map}/bounds.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Bounds(lines)

    def getWarpPoints(self,map):
        with open(f"maps/{map}/objects.txt") as file:
            lines = file.readlines()
        sPos = eval(lines[0].split(';')[1])
        warps = [[sPos[0]*16,sPos[1]*-16]]
        for line in lines[1:]:
            p = line.split(';')
            if p[0] == 'objectWarp':
                warps.append([[eval(p[1])[0]*16,eval(p[1])[1]*-16],str(p[2]),[eval(p[3])[0]*16,eval(p[3])[1]*-16]])
        return warps

    def getEncounters(self, map):
        with open(f"maps/{map}/encounters.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Encounters(lines)
