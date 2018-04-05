import random
from collections import namedtuple

import pygame

class Bounds:
    def __init__(self,b):
        self.bounds = b

    def at_pos(self, x, y):
        return self.bounds[-y][x]

    def checkBounds(self, x, y, dir=(0, 0)):
        y = -y
        if y in range(len(self.bounds)) and x in range(len(self.bounds[0])):
            if self.bounds[y][x] == '1':
                return False
            elif self.bounds[y][x] == 'u' and not dir == ( 0, 1):
                return False
            elif self.bounds[y][x] == 'r' and not dir == ( 1, 0):
                return False
            elif self.bounds[y][x] == 'd' and not dir == ( 0,-1):
                return False
            elif self.bounds[y][x] == 'l' and not dir == (-1, 0):
                return False
            else:
                return True

class ChanceList:
    def __init__(self, items, chances):
        self.items, self.chances = items, chances
        self.accumulatedChances = [sum(self.chances[:i]) for i in range(1, len(self.chances)+1)]

    def choose(self):
        # Terts:
        # Not sure, but this might lead to some floating point rounding errors
        # Which is why I think this shouldn't fail silently
        if sum(self.chances) != 1:
            raise ValueError("Chances do not add up to 1")

        self.pick = random.random()
        for index, value in enumerate(self.accumulatedChances):
            if self.pick <= value:
                return self.items[index]
        raise Error("Well, this is awkward, this was not supposed to happen.")

class Encounters:
    def __init__(self, e):
        self.map =          e[:[i[1] for i in e].index(';') ]
        self.definitions =  e[ [i[1] for i in e].index(';'):]

        self.encounters = { }

        for encounterType in self.definitions:
            # Pokemon syntax:    {pokemon name}({list of levels},{list of chances})
            # Definition syntax: {name};{list of chances};{pokemon1}&{pokemon2}& etc.
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
        pokemon = self.encounters[encountertype].choose()
        level = pokemon[1].choose()
        return pokemon[0], level #name, level

    def getPokemonData(self, data):
        name, level_data = data.split('(')
        level_data = '(' + level_data
        level = ChanceList(*eval(level_data))
        return name, level

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

    def loadMapObject(self, mapname):
        return Map(
            self.loadDrawMap  (mapname, "map"),
            self.loadDrawMap  (mapname, "alpha", transparent=True),
            self.loadDrawMap  (mapname, "beta" , transparent=True),
            self.loadBoundsMap(mapname),
            self.getWarpPoints(mapname),
            self.getEncounters(mapname)
        )

    def loadDrawMap(self, mapname, layer, transparent=False):
        with open(f"maps/{mapname}/{layer}.txt") as file:
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

    def loadBoundsMap(self,mapname):
        with open(f"maps/{mapname}/bounds.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Bounds(lines)

    def getWarpPoints(self,mapname):
        with open(f"maps/{mapname}/objects.txt") as file:
            lines = file.readlines()
        sPos = eval(lines[0].split(';')[1])
        warps = [[sPos[0]*16,sPos[1]*-16]]
        for line in lines[1:]:
            p = line.split(';')
            if p[0] == 'objectWarp':
                warps.append([[eval(p[1])[0]*16,eval(p[1])[1]*-16],str(p[2]),[eval(p[3])[0]*16,eval(p[3])[1]*-16]])
        return warps

    def getEncounters(self, mapname):
        with open(f"maps/{mapname}/encounters.txt") as file:
            lines = file.readlines()
        for line in lines:
            line.strip()
        return Encounters(lines)
