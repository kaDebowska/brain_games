from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import url_for

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from inc.formula import Formula
from inc.colorCraze import ColorCraze
from inc.chimpTest import ChimpTest

import re

app = Flask(__name__)
app.secret_key = "74a7aaa8-81ef-4fcd-b5ad-a1d2134a7cca"

# db_username = config.db_username
# db_password = config.db_password
#
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://20_debowska:dbpass9321@limba.wzks.uj.edu.pl:3306/20_debowska'
#
# app.config['MYSQL_HOST'] = 'limba.wzks.uj.edu.pl'
# app.config['MYSQL_USER'] = '20_debowska'
# app.config['MYSQL_PASSWORD'] = 'dbpass9321'
# app.config['MYSQL_DB'] = '20_debowska'


db_username = 'root'
db_password = 'dbpassword'

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://{db_username}:{db_password}@localhost:3306/sys'

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registration',  methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        hashed_password = generate_password_hash(password)

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            error = "Użytkownik o tej nazwie już istnieje. Wybierz inną nazwę użytkownika."
            return render_template('registration.html', error=error)

        if repeat_password != password:
            error = "Wartości pól hasło i powtórz hasło muszą być takie same"
            return render_template('registration.html', error=error)

        new_user = Users(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('registration.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            error = 'Nazwa użytkownika lub hasło są niepoprawne'
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)


# CHIMP TEST ################################################################################################

# global chimpTest
chimpTest = ChimpTest()

@app.route('/chimpTest/start')
def chimp_test_start():
    chimpTest.player.chimpTest_score = 0
    chimpTest.numbers = 4
    return render_template('chimpTest/start.html')


@app.route('/chimpTest/task')
def chimp_test_task():
    chimpTest.player.chimpTest_score = len(chimpTest.player.chimpTest_answers)
    chimpTest.player.chimpTest_answers = []
    chimpTest.choose_buttons()
    return render_template('chimpTest/task.html', chimpTest=chimpTest)

@app.route('/chimpTest/answer/<int:value>')
def chimp_test_answer(value):
    referer = request.headers.get('Referer')
    if referer and referer.endswith('/chimpTest/task') and chimpTest.player.chimpTest_answers:
        return redirect(url_for('chimp_test_end'), code=302)
    chimpTest.player.give_chimp_answers(value)
    if len(chimpTest.player.chimpTest_answers) == len(chimpTest.visible_buttons):
        chimpTest.numbers += 1
        return redirect(url_for('chimp_test_task'))
    return redirect(url_for('chimp_test_check_answer'), code=302)

@app.route('/chimpTest/check_answer')
def chimp_test_check_answer():
    i = len(chimpTest.player.chimpTest_answers) - 1
    if chimpTest.player.chimpTest_answers[i] == chimpTest.visible_buttons[i]:
        return render_template('chimpTest/task.html', chimpTest=chimpTest)
    else:
        return redirect(url_for('chimp_test_end'), code=302)

@app.route('/chimpTest/end')
def chimp_test_end():
    return render_template('chimpTest/end.html', chimpTest=chimpTest)


# Color Craze ########################################################################################################
global colors
colors = ColorCraze()
# colors.choose_task_type()
# colors.choose_task()
# colors.choose_correct_answer()
# colors.generate_answers()


@app.route('/colors/start')
def colors_start():
    session['time_left'] = 30
    colors.player.colors_points = 0
    return render_template('colorCraze/start.html')

@app.route('/colors/question')
def colors_question():
    time_left = session.get('time_left')
    colors.task_type = ''
    colors.task = []
    colors.correct_answer = []
    colors.answers = {}

    colors.choose_task_type()
    colors.choose_task()
    colors.choose_correct_answer()
    colors.generate_answers()

    return render_template('colorCraze/question.html', colors=colors, time_left=time_left)

@app.route('/colors/answer/<key>')
def colors_answer(key):
    time_left = session.get('time_left')
    if key not in colors.answers.keys():
        return render_template('colorCraze/question.html', colors=colors, time_left=time_left)
    answer = [key, colors.answers[key]]
    colors.player.give_colors_answer(answer)
    print('colors.player.colors_answer', colors.player.colors_answer)
    if len(colors.player.colors_answer) == 2:
        print('tu powinno przejść do check')
        return redirect(url_for('colors_check_answer'), code=302)
    return redirect(url_for('colors_question'), code=302)


@app.route('/colors/check_answer')
def colors_check_answer():
    print('colors.player.colors_answer', colors.player.colors_answer)
    print('colors.correct_answer', colors.correct_answer)
    if sorted(colors.player.colors_answer) == sorted(colors.correct_answer):
        colors.player.colors_points += 1
        return redirect(url_for('colors_question'), code=302)
    print("bad answer")
    # session['last_page'] = 'check_answer'
    return render_template('colorCraze/wrong_answer.html', colors=colors)

@app.route('/colors/end')
def colors_end():
    return render_template('colorCraze/end.html', colors=colors)

# FORMULA #############################################################################################
global formula
formula = Formula()

@app.route('/formula/start')
def formula_start():
    session['time_left'] = 30
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

    session['last_page'] = 'answer'

    print("correct_answers", correct_answers)
    print("formula.all_answers", formula.all_answers)
    print("formula.result", formula.result)

    return render_template('formula/question.html', formula=formula, time_left=time_left)

@app.route('/update_time', methods=['POST'])
def update_time():
    time_left = request.json['time_left']
    session['time_left'] = time_left
    return "success"

@app.route('/formula/answer/<int:index>')
def formula_answer(index):
    time_left = session.get('time_left')
    # if session['last_page'] == 'check_answer':
    #     print('last page', session['last_page'])
    #     return redirect('/formula/question', code=302)
    if index > 3:
        return render_template('formula/question.html', formula=formula, time_left=time_left)
    if "?" in formula.player.formula_answers:
        formula.player.give_formula_answer(formula.all_answers[index])
        print('formula.player.formula_answers', formula.player.formula_answers)
        if "?" in formula.player.formula_answers:
            return render_template('formula/question.html', formula=formula, time_left=time_left)
        return redirect(url_for('formula_check_answer'), code=302)
    return redirect(url_for('formula_question'), code=302)


@app.route('/formula/check_answer')
def formula_check_answer():
    if sorted(formula.player.formula_answers) == sorted(formula.correct_answers):
        print('formula.player.formula_answers', formula.player.formula_answers)
        print('formula.correct_answers', formula.correct_answers)
        formula.player.formula_points += 1
        return redirect(url_for('formula_question'), code=302)
    print("bad answer")
    session['last_page'] = 'check_answer'
    return render_template('formula/wrong_answer.html', formula=formula)

@app.route('/formula/end')
def formula_end():
    return render_template('formula/end.html', formula=formula)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
