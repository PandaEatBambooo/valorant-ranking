from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    players = db.relationship('Player', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    agent = db.Column(db.String(50), default='Unknown')
    acs = db.Column(db.Float, nullable=False)
    kd = db.Column(db.Float, nullable=False)
    kda = db.Column(db.Float, nullable=False)
    win_rate = db.Column(db.Float, nullable=False)
    headshot = db.Column(db.Float, nullable=False)
    matches = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Player {self.name}>'
