import random
from inc.user import User

class ChimpTest:
    def __init__(self):
        self.numbers = 3
        self.answers_order = []
        self.player = User()
        self.visible_buttons = []

    def choose_buttons(self):
        self.visible_buttons = random.sample(range(64), self.numbers)
        return self.visible_buttons





