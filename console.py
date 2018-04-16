import pickle, pygame
from collections import namedtuple

# Console
Event = namedtuple("Event", ["event", "data"])
dummyEvent = Event("SAY", [
    "Hello there!\nIt's so very nice to meet you!\nWelcome to the world of Pokémon!"
])

def fit_and_center_surface(a, b):
    a_rect = a.get_rect()
    b_rect = b.get_rect()
    a_rect_scaled = a_rect.fit(b_rect)
    a_scaled = pygame.transform.scale(a, a_rect_scaled.size)
    coordinates = ((b_rect.width - a_rect_scaled.width)//2, (b_rect.height - a_rect_scaled.height)//2)
    b.blit(a_scaled, coordinates)


def take_words_until(s, n):
    return " ".join(s.split()[:n])


def take_words_from(s, n):
    return " ".join(s.split()[n:])


def fit_string_with_width(text, font, width):
    split_at_newlines = text.split('\n')
    s = split_at_newlines[0]
    s_surf = font.render(s, False, (0,0,0))
    if s_surf.get_width() < width:
        return s_surf, '\n'.join(split_at_newlines[1:])
    for i in range(-1, -len(s.split()), -1):
        s_surf = font.render(
            take_words_until(s, i),
            False,
            (0,0,0)
        )
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
        self.text_box_textures = pygame.image.load("textures/dialogue box.png").convert_alpha()
        self.current_text_box_texture = pygame.Surface((250, 44), pygame.SRCALPHA)
        self.current_text_box_texture.blit(self.text_box_textures, (0, 0), (1, 1, 250, 44))
        self.font = pygame.font.Font("PKMNRSEU.FON", 14)
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

    def dialogBox(self, text):
        self.dialogue_active = True
        self.dialogue_text = iter(text)
        self.current_dialogue_text = next(self.dialogue_text)
        print(self.current_dialogue_text)
        print(text, 'ID:'+str(self.state))

    def draw_dialogue(self):
        if not self.dialogue_active:
            return

        # Background
        self.pixel_screen.blit(self.current_text_box_texture, self.pos_rect)

        # Top row of the text
        text_top_surf, rest_text = fit_string_with_width(self.current_dialogue_text, self.font, self.text_top_rect.width)
        self.pixel_screen.blit(text_top_surf, self.text_top_rect)

        # Bottom row of the text
        if rest_text:
            text_bottom_surf, self.rest_text = fit_string_with_width(rest_text, self.font, self.text_bottom_rect.width)
            self.pixel_screen.blit(text_bottom_surf, self.text_bottom_rect)

    def dialogue_continue(self):
        if self.rest_text:
            self.current_dialogue_text = self.rest_text
            self.rest_text = ""
        else:
            try:
                self.current_dialogue_text = next(self.dialogue_text)
            except StopIteration:
                self.dialogue_active = False

    def execute_events(self):
        while self.queue:
            self.execute_next_event()

    def execute_next_event(self):
        if self.queue:
            eventToExecute = self.queue.pop(0)
            self.state += 1
            if eventToExecute.event == 'SAY':
                self.dialogBox(eventToExecute.data)
            if eventToExecute.event == 'SET':
                self.data[eventToExecute.data[0]] = eventToExecute.data[1]
                pickle.dump(self.data, open(self.datapath, 'wb'))
            if eventToExecute.event == 'IF':
                if self.data[eventToExecute.data[0]]:
                    self.addEvent[self.interpret(eventToExecute.data[1][0])]
                else:
                    self.addEvent[self.interpret(eventToExecute.data[1][1])]

    def addEvent(self, command, data):
        event = Event(command, data)
        if type(event) == list:
            self.queue.extend(event)
        else:
            self.queue.append(event)

    def execute_script(self, scriptPath):
        with open(scriptPath) as file:
            lines = file.readlines()
        for line in lines:
            self.addEvent(self.interpret(line))

    def interpret(self, data):
        commands = data.split(';')
        toReturn = []
        for command in commands:
            commandType = command.split(':')[0]
            commandData = eval(command.split(':')[1])
            toReturn.append(commandType, commandData)
