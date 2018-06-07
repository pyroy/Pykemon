class Oak:
    def __init__(self):
        self.name = "Oak"
        self.role = "Professor"
        self.sprite = (10, 1)
        self.path = [(5, 2), (5, 3), (6, 3)]

    def interact(self, game_state):
        yield self.say("You got your first Pokémon already?")
        yield self.say("WHO GAVE IT TO YOU?")