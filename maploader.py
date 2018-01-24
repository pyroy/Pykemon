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

Map = namedtuple("Map", [
    "ground",
    "alpha",
    "beta",
    "bounds",
    "warps"
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
            self.getWarpPoints(map)
        )

    def loadDrawMap(self,map,name,transparent=False):
        map = open(f"maps\{map}\{name}.txt").readlines()
        drawmap = pygame.Surface((int(map[0].split(".")[0]),int(map[0].split(".")[1])))
        if transparent:
            drawmap.fill((255,0,255))
            drawmap.set_colorkey((255,0,255))
            drawmap.convert_alpha()
        else:
            drawmap.fill((255,255,255))

        for y,row in enumerate(map[1:]):
            for x,tile in enumerate(row.split(".")):
                locx = int(tile.split(",")[0])
                locy = int(tile.split(",")[1])
                drawmap.blit(self.tileset,(x*16,y*16),(locx*16,locy*16,16,16))

        return drawmap

    def loadBoundsMap(self,map):
        map = open("maps\{}\\bounds.txt".format(map)).readlines()
        for line in map:
            line.strip()
        return Bounds(map)

    def getWarpPoints(self,map):
        map = open("maps\{}\objects.txt".format(map)).readlines()
        sPos = eval(map[0].split(';')[1])
        warps = [[sPos[0]*16,sPos[1]*-16]]
        for i in range(1,len(map)):
            p = map[i].split(';')
            if p[0] == 'objectWarp':
                warps.append([[eval(p[1])[0]*16,eval(p[1])[1]*-16],str(p[2]),[eval(p[3])[0]*16,eval(p[3])[1]*-16]])
        return warps
