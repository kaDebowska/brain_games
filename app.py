from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
import random
import time

app = Flask(__name__)
app.secret_key = "secret_key"

class User:
    def __init__(self):
        self.formula_answers = ["?", "?"]
        self.formula_points = 0

    def give_formula_answer(self, answer):
        self.formula_answers[self.formula_answers.index("?")] = answer
        return self.formula_answers


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
                counter += 1
        while self.all_answers[0] + self.all_answers[1] == self.correct_answers[0] + self.correct_answers[1] or \
                abs(self.all_answers[0] - self.all_answers[1]) == abs(self.correct_answers[0] - self.correct_answers[1]):
            self.all_answers.pop(0)
            self.all_answers.append(random.randint(1, 50))
        self.all_answers.extend(self.correct_answers)
        random.shuffle(self.all_answers)
        return self.all_answers

global formula
formula = Formula()
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/formula/start')
def formula_start():
    session['time_left'] = 10
    formula.player.formula_points = 0
    return render_template('formula/start.html')


@app.route('/formula/question')
def formula_question():
    time_left = session.get('time_left')
    formula.correct_answers = []
    formula.all_answers = []
    formula.player.formula_answers = ['?', '?']

    correct_answers = formula.choose_correct_answers()
    operator = formula.choose_operator()
    formula.calculate_result(correct_answers, operator)
    formula.generate_all_answers()

    print("correct_answers", correct_answers)
    print("formula.all_answers", formula.all_answers)
    print("formula.result", formula.result)

    return render_template('formula/question.html', formula=formula, time_left=time_left)

@app.route('/update_time', methods=['POST'])
def update_time():
    time_left = request.json['time_left']
    session['time_left'] = time_left
    print('time_left', time_left)

    return "success"
@app.route('/formula/answer/<int:index>')
def formula_answer(index):
    time_left = session.get('time_left')
    if "?" in formula.player.formula_answers:
        formula.player.give_formula_answer(formula.all_answers[index])
        print(formula.player.formula_answers)
        if "?" in formula.player.formula_answers:
            return render_template('formula/question.html', formula=formula, time_left=time_left)
        return redirect('/formula/check_answer', code=302)

@app.route('/formula/check_answer')
def formula_check_answer():
    if sorted(formula.player.formula_answers) == sorted(formula.correct_answers):
        print('formula.player.formula_answers', formula.player.formula_answers)
        print('formula.correct_answers', formula.correct_answers)
        formula.player.formula_points += 1
        return redirect('/formula/question', code=302)
    return render_template('formula/wrong_answer.html', formula=formula)

@app.route('/formula/end')
def formula_end():
    return render_template('formula/end.html', formula=formula)
if __name__ == '__main__':
    app.run(debug=True)
