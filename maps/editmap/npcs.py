from npc import NPC
from events import say, choose

class Oak(NPC):
    def __init__(self):
        self.name   = "Oak"
        self.role   = "Professor"
        self.sprite = (4, 5)
        self.path   = [(5, 2), (5, 3), (6, 3)]

    def interact(self):
        responses = {}
        yield say("You got your first Pokémon already?")
        yield say("WHO GAVE IT TO YOU?")
        yield choose(
            ["Roy", "Terts", "Your mom!", "Bugger off!"],
            responses, "person"
        )
        if responses["person"] in ["Roy", "Terts"]:
            yield say("Oh, that expains a lot.")
        else:
            yield say("What is this profanity?!")
            yield say("Goodbye!")

class Mom(NPC):
    def __init__(self):
        self.name = "Mom"
        self.role = ""
        self.sprite = (8, 6)
        self.path = [(11, 4), (11, 5), (10, 5)]
    
    def interact(self):
        yield say("I see you have your running shoes already...")

class Quizmaster(NPC):
    def __init__(self):
        self.name = "Quizmaster"
        self.role = ""
        self.sprite = (5, 2)
        self.path = [(9, 8)]

    def interact(self):
        yield say("Stop!")
        yield say("Who approaches the bridge of death, must answer me these questions three, 'ere the other side he see.")
        
        self.correct = 0
        yield say("What is your name?")
        yield from self.question("Sir Robin", ["King Arthur", "Sir Launcelot", "Sir Robin", "Sir Galahad"])
        yield say("What is your quest?")
        yield from self.question("Find the grail", ["Fight the French", "Find the grail", "Find the sparrows", "Free the damsel"])
        yield say("What is the capital of Assyria?")
        yield from self.question("Nineveh", ["Nineveh", "Babylon", "Sela", "I DON'T KNOW THAT!"])
        yield say(f"You got {self.correct} answers right.")
    
    def question(self, correct, options):
        responses = {}
        yield choose(options, responses, 'question')
        if responses['question'] == correct:
            self.correct += 1
            yield say("That's correct!")
        else:
            yield say("Ouch, that's not correct!")
            yield say(f"The correct answer was {correct}")