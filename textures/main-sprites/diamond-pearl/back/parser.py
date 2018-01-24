from os import listdir
from os.path import isfile, join
import pygame
pygame.init()

mypath = 'Z:/pyg/PyCharmProjects/Pykemon/textures/main-sprites/diamond-pearl/back/'
files = [f for f in listdir(mypath) if f.endswith('.png')]

for file in files:
    fileSurface = pygame.image.load(mypath+file)
    fw = fileSurface.get_width()
    fh = fileSurface.get_height()
    breakLine = 0
    for y in range(fh):
        emptyLine = True
        for x in range(fw):
            if fileSurface.get_at((x,fh-1-y))[3] < 10:
                emptyLine = False; breakLine = y; break
        if not emptyLine: break;
    newSurface = pygame.Surface((fw,fh-breakLine), pygame.SRCALPHA, 32)
    newSurface.blit(fileSurface, (0,0), (0,0,fw,fh-breakLine))
    pygame.image.save(newSurface, mypath+file)
