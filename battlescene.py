from math import ceil
import random
import pokepy.pokemon as pkm
import pygame
from visual_core import get_texture, crop_whitespace, render_number, render_text
import events

dex = pkm.dex.Dex()

hp_bar_textures = None
base_textures   = None


def getSprite(name, state):
    if state == 'front':
        return get_texture(f'main-sprites\\diamond-pearl\\{dex.getIndex(name)}')
    elif state == 'back':
        return get_texture(f'main-sprites\\diamond-pearl\\back\\{dex.getIndex(name)}')
    else:
        raise ValueError("Invalid state argument.")


class Background:
    def __init__(self, time='Day', place='Forest'):
        self.source = get_texture("20102")
        self.times = None
        self.time = time

    def get(self):
        dfg = pygame.Surface((256, 144))
        dfg.blit(self.source, (0, 0), (15, 566, 256, 144))
        return dfg


class BattleScene:
    def __init__(self, screen, console, player, foe):
        global hp_bar_textures, base_textures
        hp_bar_textures = get_texture("hpbars")
        base_textures   = get_texture("battlebases")
        self.base_selection = 2
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
        self.foe_pos = -50
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
                self.console.add_generator(self.battle_actions())
    
    def battle_actions(self):
        while True:
            yield from self.player_action_menu()
            if not self.active:
                return
            
            # The speed of the Pokémon will determine who goes first
            if self.inFieldFriend.currentStats['SPD'] >= self.inFieldFoe.currentStats['SPD']:
                yield from self.friend_action()
                if self.inFieldFriend.fainted or self.inFieldFoe.fainted:
                    break
                yield from self.foe_action()
                if self.inFieldFriend.fainted or self.inFieldFoe.fainted:
                    break
            else:
                yield from self.foe_action()
                if self.inFieldFriend.fainted or self.inFieldFoe.fainted:
                    break
                yield from self.friend_action()
                if self.inFieldFriend.fainted or self.inFieldFoe.fainted:
                    break
        
        # The player won
        if self.inFieldFoe.fainted:
            yield events.say(f'{self.inFieldFoe.custom_name} fainted!')
        # The opponent won
        else:
            yield events.say(f'{self.inFieldFriend.custom_name} fainted!')
        self.active = False


    
    def player_action_menu(self):
        v = {}
        yield events.choose(
            ['FIGHT', 'BAG', 'POKéMON', 'RUN'],
            v, 'main'
        )
        if v['main'] == 'FIGHT':
            yield events.choose(
                self.inFieldFriend.moveset.get_movenames(),
                v, 'attack'
            )
            self.friend_attack = v['attack']
        elif v['main'] == 'RUN':
            yield events.say('Got away safely!')
            self.close()
    
    def friend_action(self):
        yield events.say(f'{self.inFieldFriend.custom_name} used {self.friend_attack}!')
        yield from self.inFieldFriend.moveset[self.friend_attack][0].func(self.inFieldFriend, self.inFieldFoe)
    
    def foe_action(self):
        self.foe_attack = random.choice(list(self.inFieldFoe.moveset.moves.keys()))
        yield events.say(f'{self.inFieldFoe.custom_name} used {self.foe_attack}!')
        yield from self.inFieldFoe.moveset[self.foe_attack][0].func(self.inFieldFoe, self.inFieldFriend)

    def close(self):
        self.active = False

    def draw(self):
        self.screen_surf.fill((0,0,0))
        self.screen_surf.blit(self.bg.get(), (0, 0))
        self.screen_surf.blit(base_textures, (self.foe_pos-64, 56), pygame.Rect(257, 64*self.base_selection, 128, 64))
        self.screen_surf.blit(base_textures, (self.friend_pos-64, self.visuals_rect.height-32), pygame.Rect(0, 32*self.base_selection, 256, 32))

        # @SPEED: Calling this each frame is probably ridiculously slow
        # Update: its probably better now that its cached, still not perfect, though.
        friend_sprite, friend_rect = crop_whitespace(getSprite(self.inFieldFriend.display_name.capitalize(), 'back'))
        foe_sprite, foe_rect = crop_whitespace(getSprite(self.inFieldFoe.display_name.capitalize(), 'front'))
        foe_rect = foe_sprite.get_rect()
        foe_rect.midbottom = (self.foe_pos, 90)
        self.screen_surf.blit(foe_sprite, foe_rect)
        self.friendSize = self.screen_surf.blit(friend_sprite, (self.friend_pos, self.visuals_rect.height-self.friendSize.height))

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

    def new_pokemon(self, pokemon):
        self.pokemon = pokemon
        self.name   = pokemon.custom_name
        self.level  = pokemon.level
        self.status = pokemon.status
        self.max_hp = pokemon.stats['HP']
        self.cur_hp = pokemon.currentStats['HP']
        self.max_xp = pokemon.goalXP
        self.cur_xp = pokemon.XP
        self.gender = None

    def get_surface(self):
        self.textures = get_texture("hpbars")
        if self.gender == 'male':
            bg_texture_x = 0
        elif self.gender == 'female':
            bg_texture_x = 120
        else:
            bg_texture_x = 240
        hp_prop = self.pokemon.currentStats['HP'] / self.pokemon.stats['HP']

        # We use ceil because because we want to still show a pixel if the health
        # is reduced to something that would cause the hp bar to disappear if
        # we rounded down.
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

            nametag = render_text(self.pokemon.custom_name)
            background.blit(nametag, (13, 3))

            level_tag = render_number(self.pokemon.level)
            background.blit(level_tag, (94, 8))

            current_hp_tag = render_number(self.pokemon.currentStats['HP'])
            current_hp_tag_rect = current_hp_tag.get_rect()
            current_hp_tag_rect.topright = (87, 28)
            background.blit(current_hp_tag, current_hp_tag_rect)

            max_hp_tag = render_number(self.pokemon.stats['HP'])
            background.blit(max_hp_tag, (94, 28))

            background.blit(hp_texture, (62, 19))

            xp_prop = self.pokemon.XP / self.pokemon.goalXP
            xp_texture = pygame.Surface((xp_prop*90, 3), pygame.SRCALPHA)
            xp_texture.blit(self.textures, (0, 0), pygame.Rect(0, 92, xp_prop*90, 3))
            background.blit(xp_texture, (29, 38))

        elif self.side == 'foe':
            background = pygame.Surface((120, 30), pygame.SRCALPHA)
            background_rect = background.get_rect()
            background.blit(self.textures, (0, 0), background_rect.move(bg_texture_x, 0))

            nametag = render_text(self.pokemon.custom_name)
            background.blit(nametag, (2, 3))

            level_tag = render_number(self.pokemon.level)
            background.blit(level_tag, (82, 8))

            background.blit(hp_texture, (50, 19))
        else:
            raise ValueError(f"self.side '{self.side}' was not 'friend' or 'foe'.")
        return background
