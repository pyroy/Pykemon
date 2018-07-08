class SayEvent:
    def __init__(self, text, callback):
        self.text = text
        self.callback = callback

class ChooseEvent:
    def __init__(self, options, callback=None, var_dict=None, var_key=None, back_possible=False):
        self.options = options
        self.callback = callback
        self.var_dict = var_dict
        self.var_key = var_key
        self.back_possible = back_possible

class DamageEvent:
    def __init__(self, attacking, defending, move, callback=None):
        self.attacking = attacking
        self.defending = defending
        self.move = move
        self.callback = callback

class StatusEvent:
    def __init__(self, attacking, defending, status, callback=None):
        self.attacking = attacking
        self.defending = defending
        self.status = status
        self.callback = callback

def say(*text):
    return lambda generator: SayEvent(text, callback=generator)

def choose(options, var_dict, var_key, back_possible=False):
    return lambda generator: ChooseEvent(options, callback=generator, var_dict=var_dict, var_key=var_key, back_possible=back_possible)

def menu(**options):
    def callback(selection):
        yield from options[selection]()
    return lambda _: ChooseEvent(
        list(options.keys()),
        callback=callback
    )

def damage(attacking, defending, category, type, power, accuracy):
    "Deals damage while taking into account the parameters most commonly used in the Pokémon games"
    movedata = {
        'category': category,
        'type': type,
        'power': power,
        'accuracy': accuracy
    }
    return lambda generator: DamageEvent(attacking, defending, movedata, callback=generator)

def status(attacking, defending, status):
    return lambda generator: StatusEvent(attacking, defending, status, callback=generator)