from npc import NPC

class Oak(NPC):
    def __init__(self):
        self.name   = "Oak"
        self.role   = "Professor"
        self.sprite = (4, 5)
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
    
    def interact(self):
        yield self.say("I see you have your running shoes already...")

class Quizmaster(NPC):
    def __init__(self):
        self.name = "Quizmaster"
        self.role = ""
        self.sprite = (5, 2)
        self.path = [(9, 8)]

    def interact(self):
        yield self.say("Stop!")
        yield self.say("Who approaches the bridge of death, must answer me these questions three, 'ere the other side he see.")
        
        self.correct = 0
        yield self.say("What is your name?")
        yield from self.question("name", "Sir Robin", ["King Arthur", "Sir Launcelot", "Sir Robin", "Sir Galahad"])
        yield self.say("What is your quest?")
        yield from self.question("game", "Find the grail", ["Fight the French", "Find the grail", "Find the sparrows", "Free the damsel"])
        yield self.say("What is the capital of Assyria?")
        yield from self.question("game", "Nineveh", ["Nineveh", "Babylon", "Sela", "I DON'T KNOW THAT!"])
        yield self.say(f"You got {self.correct} answers right.")
    
    def question(self, key, correct, options):
        yield self.choice(key, options)
        if self.vars[key] == correct:
            self.correct += 1
            yield self.say("That's correct!")
        else:
            yield self.say("Ouch, that's not correct!")
            yield self.say(f"The correct answer was {correct}")