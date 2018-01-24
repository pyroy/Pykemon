import pokepy.pokemon as pkm
import pygame

dex = pkm.dex.Dex()

def getSprite(name, state='back'):
    if state == 'front':
        return pygame.image.load('textures/main-sprites/diamond-pearl/{}.png'.format(dex.getIndex(name)))
    else: return pygame.image.load('textures/main-sprites/diamond-pearl/back/{}.png'.format(dex.getIndex(name)))

class Background:
    def __init__(self, time='Day', place='Forest'):
        self.source = pygame.image.load('textures/bgsource.png').convert_alpha()
        self.times = None;
        self.time = time
    def get(self):
        dfg = pygame.Surface((257,145))
        dfg.blit(self.source, (0,0), (259,147,257,145))
        return dfg

class Battle:
    def __init__(self, screen, player, foe):
        self.player, self.foe = player, foe
        self.draws = screen
        self.inFieldFriend = self.player.party[0]
        self.inFieldFoe = self.foe.party[0]
        self.state = 0
        self.sp1Pos = 600
        self.sp2Pos = -200
        self.bg = Background()
        self.friendSize = pygame.Rect(0,0,80,80)
    def update(self):
        if self.state < 40:
            self.state += 1
            self.sp1Pos -= 6
            self.sp2Pos += 6
    def draw(self):
        self.draws.fill((0,0,0))
        self.draws.blit( pygame.transform.scale(self.bg.get(), (600,430)), (0,0) )
        self.draws.blit( pygame.transform.scale(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'), (200,200)), (self.sp1Pos,100))
        self.friendSize = self.draws.blit( pygame.transform.scale(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'), (200,200)).convert_alpha(), (self.sp2Pos,428-self.friendSize.height))
        pygame.draw.rect( self.draws, (255,255,255), (0,433,600,170) )

        pygame.draw.rect( self.draws, (170,0,0), (100,455,160,50) )
        pygame.draw.rect( self.draws, (170,0,0), (340,455,160,50) )
        pygame.draw.rect( self.draws, (170,0,0), (100,525,160,50) )
        pygame.draw.rect( self.draws, (170,0,0), (340,525,160,50) )
