import pokepy.pokemon as pkm
import pygame

dex = pkm.dex.Dex()

def getSprite(name, state):
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
        dfg.blit(self.source, (0,0), (15,566,256,146))
        return dfg

class Battle:
    def __init__(self, screen, player, foe):
        self.player, self.foe = player, foe
        self.screen_surf = screen
        self.screen_rect = screen.get_rect()
        self.visuals_rect = self.screen_rect.copy()
        self.visuals_rect.height = 146

        self.menu_rect = self.screen_rect.copy()
        self.menu_rect.y = self.visuals_rect.height
        self.menu_rect.height = self.screen_rect.height - self.visuals_rect.height

        self.inFieldFriend = self.player.party[0]
        self.inFieldFoe = self.foe.party[0]
        self.state = 0
        self.sp1Pos = self.screen_rect.width
        self.sp2Pos = -100
        self.bg = Background()
        self.friendSize = pygame.Rect(0,0,80,80)

    def update(self):
        if self.state < 40:
            self.state += 1
            self.sp1Pos -= 3
            self.sp2Pos += 3

    def draw(self):
        self.screen_surf.fill((0,0,0))
        self.screen_surf.blit(self.bg.get(), (0,0))
        self.screen_surf.blit(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'), (self.sp1Pos,10))
        self.friendSize = self.screen_surf.blit(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'), (self.sp2Pos,self.visuals_rect.height-self.friendSize.height))

        pygame.draw.rect(self.screen_surf, (255,255,255), self.menu_rect)
