from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
import random
app = Flask(__name__)

class Formula:

    def __init__(self):
        self.start = False
        self.round = 0
        self.points = 0
        self.correct_answers = []
        self.all_answers = []

    def choose_correct_answers(self):
        for i in range(2):
            self.correct_answers.append(random.randint(1, 99))
        return self.correct_answers

    def choose_operator(self):
        operator = random.randint(1, 2)
        if operator == 1:
            operator = '-'
        else:
            operator = '+'
        return operator


    def result(self, correct_answers, operator):
        if operator == '-':
            c = correct_answers[0] - correct_answers[1]
        else:
            c = correct_answers[0] + correct_answers[1]
        return c

    def generate_all_answers(self):
        counter = 0
        while counter < 2:
            answer = random.randint(1, 99)
            if answer not in self.correct_answers:
                self.all_answers.append(answer)
                counter += 1
        if self.all_answers[0] + self.all_answers[1] == self.correct_answers[0] + self.correct_answers[1] or \
                abs(self.all_answers[0] - self.all_answers[1]) == abs(self.correct_answers[0] - self.correct_answers[1]):
            self.all_answers.pop(0)
            self.all_answers.append(random.randint(1, 99))
        self.all_answers.extend(self.correct_answers)
        random.shuffle(self.all_answers)
        return self.all_answers

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/formula/start')
def formula_start():
    return render_template('formula/start.html')

@app.route('/formula/question')
def formula_question():
    global formula
    formula = Formula()
    corect_answers = formula.choose_correct_answers()
    operator = formula.choose_operator()
    result = formula.result(corect_answers, operator)
    formula.generate_all_answers()

    return render_template('formula/question.html', formula=formula, operator=operator, result=result)


if __name__ == '__main__':
    app.run(debug=True)

