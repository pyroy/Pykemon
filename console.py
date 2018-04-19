import pickle, pygame
from collections import namedtuple
from keybinding import single_key_action
from visual_core import get_texture, render_text

SayEvent = namedtuple("SayEvent", [
    "text",
    "callback"
])

ChooseEvent = namedtuple("ChooseEvent", [
    "options",
    "callback"
])

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


class Console:
    def __init__(self, data, pixel_screen):
        self.state = 0
        self.queue = [dummyEvent]
        self.datapath = data
        self.data = pickle.load(open(data, 'rb'))

        # Text box stuff
        self.text_box_textures = get_texture("dialogue box")
        self.current_text_box_texture = pygame.Surface((250, 44), pygame.SRCALPHA)
        self.current_text_box_texture.blit(self.text_box_textures, (0, 0), (1, 1, 250, 44))
        self.dialogue_active = False
        self.rest_text = ""

        # Positioning of the text box
        self.pixel_screen = pixel_screen
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

        # Choose box stuff
        self.choose_box_texture = get_texture("choose box")
        self.choose_selector_texture = get_texture("choose selector")
        self.choose_box_active = False

        self.choose_box_rect = pygame.Rect(0, 0, self.choose_box_texture.get_width(), self.choose_box_texture.get_height())
        self.choose_box_rect.bottomright = (self.pixel_screen.get_width(), self.pixel_screen.get_height())
        self.choose_box_rect.move_ip(-1, -1)

        self.choose_text_rect = self.choose_box_rect.inflate(-self.pos_rect.width*0.1, -self.pos_rect.height*0.25)
        self.choose_text_rect.move_ip(0, 2)
        self.choose_text_rect.width -= 10
        self.choose_topleft_rect = self.choose_text_rect.copy()
        self.choose_topleft_rect.height = self.choose_topleft_rect.height//2
        self.choose_topleft_rect.width = self.choose_topleft_rect.width//2
        self.choose_topright_rect = self.choose_topleft_rect.move(self.choose_topleft_rect.width, 0)
        self.choose_bottomleft_rect = self.choose_topleft_rect.move(0, self.choose_topleft_rect.height)
        self.choose_bottomright_rect = self.choose_bottomleft_rect.move(self.choose_topleft_rect.width, 0)
        self.choose_selector_positions = []
        for rect in [self.choose_topleft_rect, self.choose_topright_rect, self.choose_bottomleft_rect, self.choose_bottomright_rect]:
            self.choose_selector_positions.append(rect.topleft)
            rect.width -= 8
            rect.move_ip(8, 0)

    def open_dialog_box(self, text):
        self.dialogue_active = True
        self.dialogue_text = iter(text)
        self.current_dialogue_text = next(self.dialogue_text)
        print(self.current_dialogue_text)
        print(text, 'ID:'+str(self.state))

    def draw_dialog_box(self):
        if not self.dialogue_active:
            return

        # Background
        self.pixel_screen.blit(self.current_text_box_texture, self.pos_rect)

        # Top row of the text
        text_top_surf, rest_text = fit_string_with_width(self.current_dialogue_text, self.text_top_rect.width)
        self.pixel_screen.blit(text_top_surf, self.text_top_rect)

        # Bottom row of the text
        if rest_text:
            text_bottom_surf, self.rest_text = fit_string_with_width(rest_text, self.text_bottom_rect.width)
            self.pixel_screen.blit(text_bottom_surf, self.text_bottom_rect)

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

    def open_choose_box(self, options, callback):
        self.choose_box_active = True
        self.choose_options = options
        self.choose_selection = 0
        self.choose_callback = callback

    def draw_choose_box(self):
        if not self.choose_box_active:
            return

        # Background
        self.pixel_screen.blit(self.choose_box_texture, self.choose_box_rect)

        # Options
        choose_topleft_surf = render_text(self.choose_options[0])
        self.pixel_screen.blit(choose_topleft_surf, self.choose_topleft_rect)
        if len(self.choose_options) > 1:
            choose_topright_surf = render_text(self.choose_options[1])
            self.pixel_screen.blit(choose_topright_surf, self.choose_topright_rect)
        if len(self.choose_options) > 2:
            choose_bottomleft_surf = render_text(self.choose_options[2])
            self.pixel_screen.blit(choose_bottomleft_surf, self.choose_bottomleft_rect)
        if len(self.choose_options) > 3:
            choose_bottomright_surf = render_text(self.choose_options[3])
            self.pixel_screen.blit(choose_bottomright_surf, self.choose_bottomright_rect)

        self.pixel_screen.blit(self.choose_selector_texture, self.choose_selector_positions[self.choose_selection])

    def execute_events(self):
        while self.queue:
            self.execute_next_event()

    def execute_next_event(self):
        if self.queue:
            e = self.queue.pop(0)
            self.state += 1
            if type(e) is SayEvent:
                self.open_dialog_box(e.text)
                self.text_callback = e.callback
            elif type(e) is ChooseEvent:
                # Open a selection text box with the options from data.
                self.open_choose_box(e.options, e.callback)
            elif e.event == 'SET':
                self.data[e.data[0]] = e.data[1]
                pickle.dump(self.data, open(self.datapath, 'wb'))
            elif e.event == 'IF':
                if self.data[e.data[0]]:
                    self.add_event[self.interpret(e.data[1][0])]
                else:
                    self.add_event[self.interpret(e.data[1][1])]

    def add_event(self, *event):
        self.queue.extend(event)

    def say(self, *text, callback=None):
        self.add_event(SayEvent(text, callback))

    def choose(self, options, callback):
        self.add_event(ChooseEvent(options, callback))

    def execute_script(self, script_path):
        with open(script_path) as file:
            lines = file.readlines()
        for line in lines:
            self.add_event(self.interpret(line))

    def interpret(self, data):
        commands = data.split(';')
        toReturn = []
        for command in commands:
            commandType = command.split(':')[0]
            commandData = eval(command.split(':')[1])
            toReturn.append(commandType, commandData)

    def handle_single_key_action(self, key):
        if self.choose_box_active:
            if single_key_action(key, 'Menu', 'up') or single_key_action(key, 'Menu', 'down'):
                self.choose_selection += 2
                self.choose_selection = self.choose_selection % 4
            elif single_key_action(key, 'Menu', 'right') or single_key_action(key, 'Menu', 'left'):
                if self.choose_selection % 2 == 0:
                    self.choose_selection += 1
                else:
                    self.choose_selection -= 1
            elif single_key_action(key, 'Menu', 'select'):
                self.choose_box_active = False
                self.choose_callback(self.choose_options[self.choose_selection])
        elif self.dialogue_active:
            if single_key_action(key, 'Dialogue', 'continue'):
                self.dialogue_continue()
