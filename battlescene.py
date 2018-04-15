import pokepy.pokemon as pkm
import pygame
from keybinding import single_key_action

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
        self.times = None
        self.time = time

    def get(self):
        dfg = pygame.Surface((256, 146))
        dfg.blit(self.source, (0, 0), (15, 566, 256, 146))
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

        # State will be either one of: "intro", "select", "animation"
        self.state = 'intro'
        self.intro_frame = 0
        self.foe_pos = -70
        self.friend_pos = self.screen_rect.width
        self.bg = Background()
        self.friendSize = pygame.Rect(0, 0, 80, 80)

        self.font = pygame.font.SysFont('arial', 14)

    def process_single_key_event(self, key):
        if self.state == 'select':
            if single_key_action('Battle', 'select up'):
                pass
            elif single_key_action('Battle', 'select right'):
                pass
            elif single_key_action('Battle', 'select down'):
                pass
            elif single_key_action('Battle', 'select left'):
                pass
            elif single_key_action('Battle', 'accept'):
                pass
            elif single_key_action('Battle', 'back'):
                pass

    def update(self):
        if self.state == 'intro':
            if self.intro_frame < 40:
                self.intro_frame += 1
                self.foe_pos += 6
                self.friend_pos -= 6
            else:
                self.state = 'select'

    def draw(self):
        self.screen_surf.fill((0, 0, 0))
        self.screen_surf.blit(self.bg.get(), (0, 0))
        self.screen_surf.blit(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'), (self.foe_pos, 10))
        self.friendSize = self.screen_surf.blit(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'), (self.friend_pos, self.visuals_rect.height-self.friendSize.height))

        if self.state == 'select':
            pygame.draw.rect(self.screen_surf, (255, 255, 255), self.menu_rect)
