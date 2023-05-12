class User:
    def __init__(self):
        self.formula_answers = ["?", "?"]
        self.formula_points = 0
        self.colors_answer = []
        self.colors_points = 0
        self.chimpTest_score = 0
        self.remembered_numbers = 0
        self.chimpTest_answers = []

    def give_formula_answer(self, answer):
        self.formula_answers[self.formula_answers.index("?")] = answer
        return self.formula_answers

    def give_colors_answer(self, answer):
        self.colors_answer = answer
        return self.colors_answer

    def give_chimp_answers(self, answer):
        self.chimpTest_answers.append(answer)
        return self.chimpTest_answers
