from npc import NPC

class Oak(NPC):
    def __init__(self):
        self.name   = "Oak"
        self.role   = "Professor"
        self.sprite = (10, 1)
        self.path   = [(5, 2), (5, 3), (6, 3)]

    def interact(self):
        yield self.say("You got your first Pokémon already?")
        yield self.say("WHO GAVE IT TO YOU?")
        yield self.choice("person", ["Roy", "Terts", "Your mom!", "Bugger off!"])
        if self.vars["person"] in ["Roy", "Terts"]:
            yield self.say("Oh, that expains a lot.")
        else:
            yield self.say("What is this profanity?!")
            yield self.say("Goodbye!")

class Mom(NPC):
    def __init__(self):
        self.name = "Mom"
        self.role = ""
        self.sprite = (8, 6)
        self.path = [(11, 4), (11, 5), (10, 5)]