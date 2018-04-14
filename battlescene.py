import pokepy.pokemon as pkm
import pygame

dex = pkm.dex.Dex()

def getSprite(name, state='back'):
    if state == 'front':
        return pygame.image.load(f'textures/main-sprites/diamond-pearl/{dex.getIndex(name)}.png')
    elif state == 'back':
        return pygame.image.load(f'textures/main-sprites/diamond-pearl/back/{dex.getIndex(name)}.png')
    else:
        raise ValueError("Invalid state argument.")

class Background:
    def __init__(self, time='Day', place='Forest'):
        self.source = pygame.image.load('textures/20102.png').convert_alpha()
        self.times = None;
        self.time = time

    def get(self):
        dfg = pygame.Surface((256,146))
        dfg.blit(self.source, (0,0), (19,839,256,146))
        return dfg

class Battle:
    def __init__(self, screen, player, foe):
        self.player, self.foe = player, foe
        self.screen_surf = screen
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
        self.screen_surf.fill((0,0,0))
        self.screen_surf.blit( pygame.transform.scale(self.bg.get(), (self.screen_surf.get_width(),430)), (0,0) )
        self.screen_surf.blit( pygame.transform.scale(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'), (200,200)), (self.sp1Pos,100))
        self.friendSize = self.screen_surf.blit( pygame.transform.scale(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'), (200,200)).convert_alpha(), (self.sp2Pos,428-self.friendSize.height))
        pygame.draw.rect( self.screen_surf, (255,255,255), (0,433,600,170) )

        pygame.draw.rect( self.screen_surf, (170,0,0), (100,455,160,50) )
        pygame.draw.rect( self.screen_surf, (170,0,0), (340,455,160,50) )
        pygame.draw.rect( self.screen_surf, (170,0,0), (100,525,160,50) )
        pygame.draw.rect( self.screen_surf, (170,0,0), (340,525,160,50) )
