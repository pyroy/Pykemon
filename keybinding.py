import configparser
import pygame

controls_filename = "controls.ini"


def single_key_action(key, scene, action):
    """Returns whether a key matches an action.
       Should be used in the event loop."""
    return string_to_key[keybinding[scene][action]] == key


def continuous_key_action(pressed, scene, action):
    """Returns whether the key matching an action is pressed.
       Should be used in the main loop."""
    return pressed[string_to_key[keybinding[scene][action]]]


def create_default_config():
    config = configparser.ConfigParser()
    config.read_dict({
        'World': {
            'north': 'up',
            'south': 'down',
            'east': 'right',
            'west': 'left',
            'run': 'lshift',
            'menu': 'm',
            'select': 'return',
        },
        'Menu': {
            'up': 'up',
            'right': 'right',
            'down': 'down',
            'left': 'left',
            'select': 'return'
        },
        'Dialogue': {
            'continue': 'return'
        }
    })
    with open(controls_filename, 'w') as configfile:
        config.write(configfile)


string_to_key = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'lshift': pygame.K_LSHIFT,
    'rshift': pygame.K_RSHIFT,
    'lcrtl': pygame.K_LCTRL,
    'rcrtl': pygame.K_RCTRL,
    'lalt': pygame.K_LALT,
    'ralt': pygame.K_RALT,
    'return': pygame.K_RETURN,
    'a': pygame.K_a,
    'b': pygame.K_b,
    'c': pygame.K_c,
    'd': pygame.K_d,
    'e': pygame.K_e,
    'f': pygame.K_f,
    'g': pygame.K_g,
    'h': pygame.K_h,
    'i': pygame.K_i,
    'j': pygame.K_j,
    'k': pygame.K_k,
    'l': pygame.K_l,
    'm': pygame.K_m,
    'n': pygame.K_n,
    'o': pygame.K_o,
    'p': pygame.K_p,
    'q': pygame.K_q,
    'r': pygame.K_r,
    's': pygame.K_s,
    't': pygame.K_t,
    'u': pygame.K_u,
    'v': pygame.K_v,
    'w': pygame.K_w,
    'x': pygame.K_x,
    'y': pygame.K_y,
    'z': pygame.K_z,
    '1': pygame.K_1,
    '2': pygame.K_2,
    '3': pygame.K_3,
    '4': pygame.K_4,
    '5': pygame.K_5,
    '6': pygame.K_6,
    '7': pygame.K_7,
    '8': pygame.K_8,
    '9': pygame.K_9,
    '0': pygame.K_0,
    'f1': pygame.K_F1,
    'f2': pygame.K_F2,
    'f3': pygame.K_F3,
    'f4': pygame.K_F4,
    'f5': pygame.K_F5,
    'f6': pygame.K_F6,
    'f7': pygame.K_F7,
    'f8': pygame.K_F8,
    'f9': pygame.K_F9,
}

keybinding = configparser.ConfigParser()
keybinding.read(controls_filename)
if len(keybinding.sections()) == 0:  # if the file does not exist
    print(f"Created default config file '{controls_filename}'")
    create_default_config()
    keybinding.read(controls_filename)
