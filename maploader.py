import random
from collections import namedtuple

import pygame

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

class ChanceList:
    def __init__(self, list1, list2):
        self.list1, self.list2 = list1, list2

    def choose(self):
        if sum(self.list2) != 1:
            return None

        self.accumulatedList2 = [sum(self.list2[:i]) for i in range(len(self.list2))]
        self.pick = random.random()
        for i in self.accumulatedList2[::-1]:
            if self.pick > i:
                return self.list1[ self.accumulatedList2.index(i) ]

class Encounters:
    def __init__(self, e):
        self.map =          e[:[i[1] for i in e].index(';') ]
        self.definitions =  e[ [i[1] for i in e].index(';'):]

        self.encounters = { }

        for encounterType in self.definitions:
            key, *rest = [x.strip() for x in encounterType.split(';')]
            chances = rest[0]
            if len(rest) == 2:
                pokemon = rest[1].split('&')

            if chances.upper() == 'NONE':
                self.encounters[key] = None
            else:
                self.encounters[key] = ChanceList(
                    [self.getPokemonData(p) for p in pokemon],
                    eval(chances)
                )


    def checkEncounters(self,x,y):
        return int(self.map[-y][x]) #no need for extra bound check since player is always in bounds.

    def generateEncounter(self, encountertype): #is actually an int in a string but since we're passing from a text file I'm keeping it a string. This way we can bind it to letters as well.
        pokemon = self.encounters[ encountertype ].choose()
        level = pokemon[1].choose()
        return pokemon[0], level #name, level

    def getPokemonData(self, data):
        self.name = data.split(':')[0]
        self.level = ChanceList(*eval(data.split(':')[1]))
        return self.name, self.level

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

    def loadMapObject(self, groundmap):
        return Map(
            self.loadDrawMap(groundmap, "map"),
            self.loadDrawMap(groundmap, "alpha", transparent=True),
            self.loadDrawMap(groundmap, "beta", transparent=True),
            self.loadBoundsMap(groundmap),
            self.getWarpPoints(groundmap),
            self.getEncounters(groundmap)
        )

    def loadDrawMap(self,groundmap,name,transparent=False):
        with open(f"maps/{groundmap}/{name}.txt") as file:
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

    def loadBoundsMap(self,groundmap):
        with open(f"maps/{groundmap}/bounds.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Bounds(lines)

    def getWarpPoints(self,groundmap):
        with open(f"maps/{groundmap}/objects.txt") as file:
            lines = file.readlines()
        sPos = eval(lines[0].split(';')[1])
        warps = [[sPos[0]*16,sPos[1]*-16]]
        for line in lines[1:]:
            p = line.split(';')
            if p[0] == 'objectWarp':
                warps.append([[eval(p[1])[0]*16,eval(p[1])[1]*-16],str(p[2]),[eval(p[3])[0]*16,eval(p[3])[1]*-16]])
        return warps

    def getEncounters(self, groundmap):
        with open(f"maps/{groundmap}/encounters.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Encounters(lines)
