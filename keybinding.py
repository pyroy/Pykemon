import configparser
from pygame import *

controls_filename = "controls.ini"

# Returns a function which checks whether the key corresponding with a action
# via the 'controls.ini' file. 
def get_action_pressed(key_dict, scene):
    def pressed(action):
        return all(key_dict[string_to_key[keybinding[scene][action_key]]] for action_key in action.split('+'))
    return pressed

def create_default_config():
    config  = configparser.ConfigParser()
    config.read_dict({
        'World':{
            'north': 'up',
            'south': 'down',
            'east': 'right',
            'west': 'left',
            'run': 'lshift',
            'menu':'m',
        },
        'Battle': {},
        'Menu': {},
    })
    with open(controls_filename, 'w') as configfile:
        config.write(configfile)

string_to_key = {
    'up': K_UP,
    'down': K_DOWN,
    'left': K_LEFT,
    'right': K_RIGHT,
    'lshift': K_LSHIFT,
    'rshift': K_RSHIFT,
    'lcrtl': K_LCTRL,
    'rcrtl': K_RCTRL,
    'lalt': K_LALT,
    'Ralt': K_RALT,
    'a': K_a,
    'b': K_b,
    'c': K_c,
    'd': K_d,
    'e': K_e,
    'f': K_f,
    'g': K_g,
    'h': K_h,
    'i': K_i,
    'j': K_j,
    'k': K_k,
    'l': K_l,
    'm': K_m,
    'n': K_n,
    'o': K_o,
    'p': K_p,
    'q': K_q,
    'r': K_r,
    's': K_s,
    't': K_t,
    'u': K_u,
    'v': K_v,
    'w': K_w,
    'x': K_x,
    'y': K_y,
    'z': K_z,
    '1': K_1,
    '2': K_2,
    '3': K_3,
    '4': K_4,
    '5': K_5,
    '6': K_6,
    '7': K_7,
    '8': K_8,
    '9': K_9,
    '0': K_0,
    'f1': K_F1,
    'f2': K_F2,
    'f3': K_F3,
    'f4': K_F4,
    'f5': K_F5,
    'f6': K_F6,
    'f7': K_F7,
    'f8': K_F8,
    'f9': K_F9,
}

keybinding = configparser.ConfigParser()
keybinding.read(controls_filename)
if len(keybinding.sections()) == 0: # if the file does not exist
    print(f"Created default config file '{controls_filename}'")
    create_default_config()
    keybinding.read(controls_filename)
