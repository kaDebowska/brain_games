import random

from inc.user import User


class Formula:
    def __init__(self):
        self.correct_answers = []
        self.all_answers = []
        self.result = 0
        self.operator = ''
        self.player = User()

    def choose_correct_answers(self):
        for i in range(2):
            self.correct_answers.append(random.randint(1, 50))
        return self.correct_answers

    def choose_operator(self):
        operator = random.randint(1, 2)
        if operator == 1:
            operator = '-'
        else:
            operator = '+'
        self.operator = operator
        return self.operator

    def calculate_result(self, correct_answers, operator):
        if operator == '-':
            c = correct_answers[0] - correct_answers[1]
        else:
            c = correct_answers[0] + correct_answers[1]
        self.result = c
        return self.result

    def generate_all_answers(self):
        counter = 0
        while counter < 2:
            answer = random.randint(1, 50)
            if answer not in self.correct_answers:
                self.all_answers.append(answer)
            if len(self.all_answers) == 2 and \
                    (self.all_answers[0] + self.all_answers[1] == self.correct_answers[0] + self.correct_answers[1] or
                     abs(self.all_answers[0] - self.all_answers[1]) == abs(self.correct_answers[0] - self.correct_answers[1])):
                self.all_answers.pop(0)
                self.all_answers.append(random.randint(1, 50))
            counter += 1
        self.all_answers.extend(self.correct_answers)
        random.shuffle(self.all_answers)
        return self.all_answers
