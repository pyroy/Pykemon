from math import ceil
import random
import pokepy.pokemon as pkm
import pygame

dex = pkm.dex.Dex()

hp_bar_textures = None


def render_number(num):
    assert type(num) is int, f"The type of num should be int, it is {num}"
    digit_height = 7
    digit_x_pos = [0, 9, 17, 26, 35, 44, 53, 62, 71, 80, 89]
    digit_width = [digit_x_pos[i]-digit_x_pos[i-1] for i in range(1, len(digit_x_pos))]
    text = str(num)
    total_width = sum(digit_width[int(x)] for x in text)
    surf = pygame.Surface((total_width, digit_height), pygame.SRCALPHA)
    current_pos = 0
    for digit in text:
        surf.blit(
            hp_bar_textures,
            (current_pos, 0),
            pygame.Rect(digit_x_pos[int(digit)], 110, digit_width[int(digit)], digit_height)
        )
        current_pos += digit_width[int(digit)]
    return surf


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
        dfg = pygame.Surface((256, 144))
        dfg.blit(self.source, (0, 0), (15, 566, 256, 144))
        return dfg


class BattleScene:
    def __init__(self, screen, console, player, foe):
        global hp_bar_textures
        hp_bar_textures = pygame.image.load("textures\\hpbars.png").convert_alpha()
        self.active = True
        self.player, self.foe = player, foe
        self.console = console
        self.screen_surf = screen
        self.screen_rect = screen.get_rect()

        # Positioning of the visual components
        self.visuals_rect = self.screen_rect.copy()
        self.visuals_rect.height = 144

        self.menu_rect = self.screen_rect.copy()
        self.menu_rect.y = self.visuals_rect.height
        self.menu_rect.height = self.screen_rect.height - self.visuals_rect.height

        self.inFieldFriend = self.player.party[0]
        self.inFieldFoe = self.foe.party[0]
        self.status_bar_friend = StatusBar("friend", self.inFieldFriend)
        self.status_bar_foe    = StatusBar("foe", self.inFieldFoe)

        # State will be either one of: "intro", "select", "animation"
        self.state = 'intro'
        self.intro_frame = 0
        self.foe_pos = -70
        self.friend_pos = self.screen_rect.width
        self.bg = Background()
        self.friendSize = pygame.Rect(0, 0, 80, 80)

    def update(self):
        if self.state == 'intro':
            if self.intro_frame < 40:
                self.intro_frame += 1
                self.foe_pos += 6
                self.friend_pos -= 6
            else:
                self.state = 'select'
                self.console.say(f"What will\n{self.inFieldFriend.custom_name} do?")
                self.console.choose(["FIGHT", "BAG", "POKéMON", "RUN"], self.main_action_callback)

    def main_action_callback(self, selection):
        print(f"I'm a {type(self)} and the selection is {selection}")
        if selection == 'RUN':
            # @Terts: Should not always work, but I don't know what that depends on
            self.console.say("Got away safely!", callback=self.close)

    def close(self):
        self.active = False

    def draw(self):
        self.screen_surf.fill((0,0,0))
        self.screen_surf.blit(self.bg.get(), (0, 0))
        self.screen_surf.blit(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'), (self.foe_pos, 10))
        self.friendSize = self.screen_surf.blit(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'), (self.friend_pos, self.visuals_rect.height-self.friendSize.height))

        status_bar_surf_friend = self.status_bar_friend.get_surface()
        status_bar_rect_friend = status_bar_surf_friend.get_rect()
        status_bar_rect_friend.bottomright = self.visuals_rect.size
        status_bar_rect_friend.move_ip(0, -6)

        status_bar_surf_foe = self.status_bar_foe.get_surface()
        status_bar_rect_foe = status_bar_surf_foe.get_rect()
        status_bar_rect_foe.move_ip(0, 20)

        self.screen_surf.blit(status_bar_surf_friend, status_bar_rect_friend)
        self.screen_surf.blit(status_bar_surf_foe, status_bar_rect_foe)


class StatusBar:
    def __init__(self, side, pokemon):
        self.side = side
        self.new_pokemon(pokemon)
        self.namefont = pygame.font.Font("PKMNRSEU.FON", 14)
        self.hpfont   = pygame.font.Font("PKMNRSEU.FON", 10)

    def new_pokemon(self, pokemon):
        self.name   = pokemon.custom_name
        self.level  = pokemon.level
        self.status = pokemon.status
        self.max_hp = pokemon.stats['HP']
        self.cur_hp = pokemon.currentStats['HP']
        self.max_xp = pokemon.goalXP
        self.cur_xp = pokemon.XP
        self.gender = None

    def get_surface(self):
        self.textures = hp_bar_textures
        if self.gender == 'male':
            bg_texture_x = 0
        elif self.gender == 'female':
            bg_texture_x = 120
        else:
            bg_texture_x = 240
        hp_prop = self.cur_hp / self.max_hp

        # We use ceil because because we want to still show a pixel if the health
        # is reduced to something that would cause the hp bar to disappear if
        # we rounded normally.
        hp_texture = pygame.Surface((ceil(hp_prop*48), 7))
        if hp_prop >= 0.5:
            # Use green texture
            hp_texture_rect = pygame.Rect(0, 85, 48, 7)
        elif hp_prop > 0.25:
            # Use yellow texture
            hp_texture_rect = pygame.Rect(0, 78, 48, 7)
        else:
            # Use red texture
            hp_texture_rect = pygame.Rect(0, 71, 48, 7)
        hp_texture.blit(self.textures, (0, 0), hp_texture_rect)

        if self.side == 'friend':
            background = pygame.Surface((120, 41), pygame.SRCALPHA)
            background_rect = background.get_rect()
            background.blit(self.textures, (0, 0), background_rect.move(bg_texture_x, 30))

            nametag = self.namefont.render(self.name, False, (0,0,0))
            background.blit(nametag, (13, 3))

            level_tag = render_number(self.level)
            background.blit(level_tag, (94, 8))

            current_hp_tag = render_number(self.cur_hp)
            current_hp_tag_rect = current_hp_tag.get_rect()
            current_hp_tag_rect.topright = (87, 28)
            background.blit(current_hp_tag, current_hp_tag_rect)

            max_hp_tag = render_number(self.max_hp)
            background.blit(max_hp_tag, (94, 28))

            background.blit(hp_texture, (62, 19))

            xp_prop = self.cur_xp / self.max_xp
            xp_texture = pygame.Surface((xp_prop*90, 3), pygame.SRCALPHA)
            xp_texture.blit(self.textures, (0, 0), pygame.Rect(0, 92, xp_prop*90, 3))
            background.blit(xp_texture, (29, 38))

        elif self.side == 'foe':
            background = pygame.Surface((120, 30), pygame.SRCALPHA)
            background_rect = background.get_rect()
            background.blit(self.textures, (0, 0), background_rect.move(bg_texture_x, 0))

            nametag = self.namefont.render(self.name, False, (0,0,0))
            background.blit(nametag, (2, 3))

            level_tag = render_number(self.level)
            background.blit(level_tag, (82, 8))

            background.blit(hp_texture, (50, 19))

        else:
            raise ValueError(f"self.side '{self.side}' was not 'friend' or 'foe'.")
        return background
