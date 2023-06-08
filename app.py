from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import url_for
from flask import flash


import plotly.graph_objects as go

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from inc.formula import Formula
from inc.colorCraze import ColorCraze
from inc.chimpTest import ChimpTest
from inc.models import Users, Games, Results, db

from datetime import datetime
import re

import config

app = Flask(__name__)

app.secret_key = "74a7aaa8-81ef-4fcd-b5ad-a1d2134a7cca"

db_username = config.db_username
db_password = config.db_password

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://{db_username}:{db_password}@localhost:3306/sys'

db.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/about_page')
def about_page():
    return render_template('about_page.html')


@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        hashed_password = generate_password_hash(password)

        if not username or not email or not password or not repeat_password:
            flash('Wypełnij wszystkie pola.')
            return render_template('registration.html')

        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash("Użytkownik o tej nazwie już istnieje. Wybierz inną nazwę użytkownika.")
            return render_template('registration.html')

        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            flash("Podaj poprawny adres email.")
            return render_template('registration.html')

        if len(password) < 8:
            flash("Hało powinno mieć minimum 8 znaków.")
            return render_template('registration.html')

        if repeat_password != password:
            flash("Wartości pól hasło i powtórz hasło muszą być takie same.")
            return render_template('registration.html')

        new_user = Users(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Rejestracja przebiegła pomyślnie. Zaloguj się na swoje konto.')
        return redirect(url_for('login'))
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('user_id', None)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Nazwa użytkownika lub hasło są niepoprawne.')
            return render_template('login.html')
    return render_template('login.html')


@app.context_processor
def inject_variables():
    user_id = session.get('user_id', 0)
    return dict(user_id=user_id)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Musisz się zalogować, aby skorzystać z tej strony.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Zostałeś poprawnie wylogowany.')
    return redirect(url_for('login'), code=302)






# Color Craze ########################################################################################################

colors = ColorCraze()


@app.route('/colors/start')
@login_required
def colors_start():
    session['time_left'] = 30
    session['game_id'] = 1
    colors.player.colors_points = 0
    return render_template('colorCraze/start.html')


@app.route('/colors/question')
@login_required
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
@login_required
def colors_answer(key):
    time_left = session.get('time_left')
    if key not in colors.answers.keys():
        return render_template('colorCraze/question.html', colors=colors, time_left=time_left)
    answer = [key, colors.answers[key]]
    colors.player.give_colors_answer(answer)
    if len(colors.player.colors_answer) == 2:
        return redirect(url_for('colors_check_answer'), code=302)
    return redirect(url_for('colors_question'), code=302)


@app.route('/colors/check_answer')
@login_required
def colors_check_answer():
    if sorted(colors.player.colors_answer) == sorted(colors.correct_answer):
        colors.player.colors_points += 1
        return redirect(url_for('colors_question'), code=302)
    return render_template('colorCraze/wrong_answer.html', colors=colors)


@app.route('/colors/end')
@login_required
def colors_end():
    user_id = session.get('user_id')
    game_id = session.get('game_id')

    if user_id and game_id:
        end_time = datetime.now()
        result = Results(colors.player.colors_points, end_time, user_id, game_id)
        db.session.add(result)
        db.session.commit()
        plot = create_plot()
        return render_template('colorCraze/end.html', colors=colors, plot=plot)
    else:
        return redirect(url_for('home'), code=302)


# CHIMP TEST ################################################################################################

# global chimpTest
chimpTest = ChimpTest()


@app.route('/chimpTest/start')
@login_required
def chimp_test_start():
    session['game_id'] = 2
    chimpTest.player.chimpTest_score = 0
    chimpTest.numbers = 4
    return render_template('chimpTest/start.html')


@app.route('/chimpTest/task')
@login_required
def chimp_test_task():
    if chimpTest.numbers > 4:
        chimpTest.player.chimpTest_score = len(chimpTest.player.chimpTest_answers)
    chimpTest.player.chimpTest_answers = []
    chimpTest.choose_buttons()
    return render_template('chimpTest/task.html', chimpTest=chimpTest)


@app.route('/chimpTest/answer/<int:value>')
@login_required
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
@login_required
def chimp_test_check_answer():
    i = len(chimpTest.player.chimpTest_answers) - 1
    if chimpTest.player.chimpTest_answers[i] == chimpTest.visible_buttons[i]:
        return render_template('chimpTest/task.html', chimpTest=chimpTest)
    else:
        return redirect(url_for('chimp_test_end'), code=302)


@app.route('/chimpTest/end')
@login_required
def chimp_test_end():
    user_id = session.get('user_id')
    game_id = session.get('game_id')

    if user_id and game_id:
        end_time = datetime.now()
        result = Results(chimpTest.player.chimpTest_score, end_time, user_id, game_id)
        db.session.add(result)
        db.session.commit()
        plot = create_plot()
        return render_template('chimpTest/end.html', chimpTest=chimpTest, plot=plot)
    else:
        return redirect(url_for('home'), code=302)




# FORMULA #############################################################################################

formula = Formula()


@app.route('/formula/start')
@login_required
def formula_start():
    session['time_left'] = 1000
    session['game_id'] = 3
    formula.player.formula_points = 0
    return render_template('formula/start.html')


@app.route('/formula/question')
@login_required
def formula_question():
    time_left = session.get('time_left')
    formula.correct_answers = []
    formula.all_answers = []
    formula.player.formula_answers = ['?', '?']

    correct_answers = formula.choose_correct_answers()
    operator = formula.choose_operator()
    formula.calculate_result(correct_answers, operator)
    formula.generate_all_answers()

    return render_template('formula/question.html', formula=formula, time_left=time_left)


@app.route('/update_time', methods=['POST'])
@login_required
def update_time():
    time_left = request.json['time_left']
    session['time_left'] = time_left
    return "success"


@app.route('/formula/answer/<int:index>')
@login_required
def formula_answer(index):
    time_left = session.get('time_left')
    if index > 3:
        return render_template('formula/question.html', formula=formula, time_left=time_left)
    if "?" in formula.player.formula_answers:
        formula.player.give_formula_answer(formula.all_answers[index])
        if "?" in formula.player.formula_answers:
            return render_template('formula/question.html', formula=formula, time_left=time_left)
        return redirect(url_for('formula_check_answer'), code=302)
    return redirect(url_for('formula_question'), code=302)


@app.route('/formula/check_answer')
@login_required
def formula_check_answer():
    if sorted(formula.player.formula_answers) == sorted(formula.correct_answers):
        formula.player.formula_points += 1
        return redirect(url_for('formula_question'), code=302)
    return render_template('formula/wrong_answer.html', formula=formula)


@app.route('/formula/end')
@login_required
def formula_end():
    user_id = session.get('user_id')
    game_id = session.get('game_id')

    if user_id and game_id:
        end_time = datetime.now()
        result = Results(formula.player.formula_points, end_time, user_id, game_id)
        db.session.add(result)
        db.session.commit()
        plot = create_plot()
        return render_template('formula/end.html', formula=formula, plot=plot)
    else:
        return redirect(url_for('home'), code=302)

def create_plot():
    user_results = Results.query.filter_by(user_id=session.get('user_id'), game_id=session.get('game_id')).all()
    time = [result.result_time for result in user_results]
    result = [result.result for result in user_results]
    fig = go.Figure(data=go.Scatter(x=time, y=result))
    plot = fig.to_html(full_html=False)
    return plot


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


