import pickle, pygame
import asyncio
from keybinding import single_key_action
from visual_core import get_texture, render_text
from events import SayEvent, ChooseEvent, DamageEvent, StatusEvent
import typing

# Test event for debugging.
dummyEvent = SayEvent(
    ["Hello there!\nIt's so very nice to meet you!\nWelcome to the world of POKéMON!\n0123456789"],
    None
)


def take_words_until(s, n):
    return " ".join(s.split()[:n])


def take_words_from(s, n):
    return " ".join(s.split()[n:])


def fit_string_with_width(text, width):
    split_at_newlines = text.split('\n')
    s = split_at_newlines[0]
    s_surf = render_text(s)
    if s_surf.get_width() < width:
        return s_surf, '\n'.join(split_at_newlines[1:])
    for i in range(-1, -len(s.split()), -1):
        s_surf = render_text(take_words_until(s, i))
        if s_surf.get_width() < width:
            rest_text = take_words_from(s, i)
            break
    split_at_newlines[0] = rest_text
    return s_surf, '\n'.join(split_at_newlines)

class Dialogue:
    def __init__(self, pixel_screen):
        self.pixel_screen = pixel_screen
        self.active = False

        # Text box stuff
        self.text_box_textures = get_texture("dialogue box")
        self.current_text_box_texture = pygame.Surface((250, 44), pygame.SRCALPHA)
        self.current_text_box_texture.blit(self.text_box_textures, (0, 0), (1, 1, 250, 44))
        self.rest_text = ""
        
        # Positioning of the text box
        self.pos_rect = pygame.Rect(0, 0, self.current_text_box_texture.get_width(), self.current_text_box_texture.get_height())
        self.pos_rect.centerx = self.pixel_screen.get_width() / 2
        self.pos_rect.bottom = self.pixel_screen.get_height() - 2

        # Positioning of the text in the box
        self.text_rect = self.pos_rect.inflate(-self.pos_rect.width*0.1, -self.pos_rect.height*0.25)
        self.text_rect.move_ip(0, 2)
        self.text_rect.width -= 10
        self.text_top_rect = self.text_rect.copy()
        self.text_top_rect.height = self.text_rect.height//2
        self.text_bottom_rect = self.text_top_rect.copy().move(0, self.text_top_rect.height)

    def draw(self):
        if not self.active:
            return
        # Background
        self.pixel_screen.blit(self.current_text_box_texture, self.pos_rect)

        # Top row of the text
        text_top_surf, rest_text = fit_string_with_width(self.current_text, self.text_top_rect.width)
        self.pixel_screen.blit(text_top_surf, self.text_top_rect)

        # Bottom row of the text
        if rest_text:
            text_bottom_surf, self.rest_text = fit_string_with_width(rest_text, self.text_bottom_rect.width)
            self.pixel_screen.blit(text_bottom_surf, self.text_bottom_rect)

    def open(self, text, callback=None):
        self.active = True
        self.callback = callback
        self.text = iter(text)
        self.current_text = next(self.text)
    
    def next(self):
        if self.rest_text:
            self.current_text = self.rest_text
            self.rest_text = ""
        else:
            try:
                self.current_text = next(self.text)
            except StopIteration:
                return self.close()

    def close(self):
        self.active = False
        return self.callback

class Choice:
    def __init__(self, pixel_screen):
        self.pixel_screen = pixel_screen
        self.active = False

        # Choose box stuff
        self.box_texture = get_texture("choose box")
        self.selector_texture = get_texture("choose selector")
        self.box_active = False

        # Positioning of the text box
        self.pos_rect = pygame.Rect(0, 0, self.box_texture.get_width(), self.box_texture.get_height())
        self.pos_rect.centerx = self.pixel_screen.get_width() / 2
        self.pos_rect.bottom = self.pixel_screen.get_height() - 2

        self.box_rect = pygame.Rect(0, 0, self.box_texture.get_width(), self.box_texture.get_height())
        self.box_rect.bottomright = (self.pixel_screen.get_width(), self.pixel_screen.get_height())
        self.box_rect.move_ip(-1, -1)

        self.text_rect = self.box_rect.inflate(-self.pos_rect.width*0.1, -self.pos_rect.height*0.25)
        self.text_rect.move_ip(0, 2)
        self.text_rect.width -= 10
        self.topleft_rect = self.text_rect.copy()
        self.topleft_rect.height = self.topleft_rect.height//2
        self.topleft_rect.width = self.topleft_rect.width//2
        self.topright_rect = self.topleft_rect.move(self.topleft_rect.width, 0)
        self.bottomleft_rect = self.topleft_rect.move(0, self.topleft_rect.height)
        self.bottomright_rect = self.bottomleft_rect.move(self.topleft_rect.width, 0)
        self.selector_positions = []
        for rect in [self.topleft_rect, self.topright_rect, self.bottomleft_rect, self.bottomright_rect]:
            self.selector_positions.append(rect.topleft)
            rect.width -= 8
            rect.move_ip(8, 0)

    def draw(self):
        if not self.active:
            return
        
        # Background
        self.pixel_screen.blit(self.box_texture, self.box_rect)

        # Options
        topleft_surf = render_text(self.options[0])
        self.pixel_screen.blit(topleft_surf, self.topleft_rect)
        if len(self.options) > 1:
            topright_surf = render_text(self.options[1])
            self.pixel_screen.blit(topright_surf, self.topright_rect)
        if len(self.options) > 2:
            bottomleft_surf = render_text(self.options[2])
            self.pixel_screen.blit(bottomleft_surf, self.bottomleft_rect)
        if len(self.options) > 3:
            bottomright_surf = render_text(self.options[3])
            self.pixel_screen.blit(bottomright_surf, self.bottomright_rect)

        self.pixel_screen.blit(self.selector_texture, self.selector_positions[self.selection])

    def open(self, options, var_dict=None, var_key=None, callback=None, back_possible=False):
        self.active = True
        self.options = options
        self.callback = callback
        self.var_dict = var_dict
        self.var_key = var_key
        self.selection = 0
        self.back_possible = back_possible

    def close(self, value=None):
        self.active = False
        if self.var_dict != None and self.var_key != None:
            if value:
                self.var_dict[self.var_key] = value
            else:
                self.var_dict[self.var_key] = self.options[self.selection]
        return self.callback

class Console:
    def __init__(self, data, pixel_screen):
        self.state = 0
        self.queue = [dummyEvent]
        self.datapath = data
        self.data = pickle.load(open(data, 'rb'))
        self.dialogue = Dialogue(pixel_screen)
        self.choice = Choice(pixel_screen)

    def dialogue_continue(self):
        if self.rest_text:
            self.current_dialogue_text = self.rest_text
            self.rest_text = ""
        else:
            try:
                self.current_dialogue_text = next(self.dialogue_text)
            except StopIteration:
                if self.text_callback:
                    self.text_callback()
                self.dialogue_active = False
    
    def activate_callback(self, callback, data=None):
        if callable(callback):
            callback = callback(self.choice.options[self.choice.selection])
        if isinstance(callback, typing.Generator):
            try:
                func = next(callback)
                self.add_events(func(callback))
            except StopIteration:
                pass

    def execute_events(self):
        for e in self.queue:
            if type(e) is SayEvent:
                self.dialogue.open(e.text, e.callback)
            elif type(e) is ChooseEvent:
                # Open the selection text box with the options from data.
                self.choice.open(e.options, e.var_dict, e.var_key, e.callback, e.back_possible)
            elif type(e) is DamageEvent:
                e.attacking.dealdamage(e.defending, e.move)
                self.activate_callback(e.callback)
            elif type(e) is StatusEvent:
                e.defending.status = e.status
                self.activate_callback(e.callback)
            elif e.event == 'SET':
                self.data[e.data[0]] = e.data[1]
                pickle.dump(self.data, open(self.datapath, 'wb'))
            elif e.event == 'IF':
                if self.data[e.data[0]]:
                    self.add_events[self.interpret(e.data[1][0])]
                else:
                    self.add_events[self.interpret(e.data[1][1])]
            else:
                raise ValueError(f'Event {e} is not recognized!')
        self.queue.clear()
    
    def draw(self):
        self.dialogue.draw()
        self.choice.draw()

    def add_events(self, *events):
        for event in events:
            self.state += 1
            event.id = self.state
            self.queue.append(event)

    def add_generator(self, generator):
        func = next(generator)
        self.add_events(func(generator))

    def say(self, *text, callback=None):
        return self.add_events(SayEvent(text, callback))

    def choose(self, options, var_dict=None, var_key=None, callback=None):
        return self.add_events(ChooseEvent(options, var_dict=var_dict, var_key=var_key, callback=callback))

    def execute_script(self, script_path):
        with open(script_path) as file:
            lines = file.readlines()
        for line in lines:
            self.add_events(self.interpret(line))

    def interpret(self, data):
        commands = data.split(';')
        toReturn = []
        for command in commands:
            commandType = command.split(':')[0]
            commandData = eval(command.split(':')[1])
            toReturn.append(commandType, commandData)

    def handle_single_key_action(self, key):
        if self.choice.active:
            if single_key_action(key, 'Menu', 'up') or single_key_action(key, 'Menu', 'down'):
                self.choice.selection = (self.choice.selection + 2) % 4
            elif single_key_action(key, 'Menu', 'right') or single_key_action(key, 'Menu', 'left'):
                if self.choice.selection % 2 == 0:
                    self.choice.selection += 1
                else:
                    self.choice.selection -= 1
            elif single_key_action(key, 'Menu', 'select'):
                callback = self.choice.close()
                self.activate_callback(callback, data=self.choice.options[self.choice.selection])
            elif self.choice.back_possible and single_key_action(key, 'Menu', 'back'):
                callback = self.choice.close('back')
                self.activate_callback(callback, data='back')
        elif self.dialogue.active:
            if single_key_action(key, 'Dialogue', 'continue'):
                callback = self.dialogue.next()
                self.activate_callback(callback)

