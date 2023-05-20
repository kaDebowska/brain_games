from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    results = db.relationship('Results', backref='users', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=False)
    trained_function = db.Column(db.String(45))
    description = db.Column(db.Text)
    results = db.relationship('Results', backref='games', lazy=True)


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    result = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    def __init__(self, result, user_id, game_id):
        self.result = result
        self.user_id = user_id
        self.game_id = game_id

