from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
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
