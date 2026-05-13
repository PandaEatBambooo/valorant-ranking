import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from database import db, Player, User
from model import calculate_score, get_tier

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'valrank-secret-key-2024')
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///players.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

MAX_PLAYERS = 15

# ── Auth routes ──────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('../frontend', 'login.html')

@app.route('/rankings')
def rankings():
    return send_from_directory('../frontend', 'index.html')

@app.route('/add')
def add():
    return send_from_directory('../frontend', 'add_player.html')

@app.route('/model')
def model():
    return send_from_directory('../frontend', 'model.html')

@app.route('/register')
def register_page():
    return send_from_directory('../frontend', 'register.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'message': 'Account created!', 'username': user.username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid username or password'}), 401
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'message': 'Logged in!', 'username': user.username})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'username': session['username'], 'user_id': session['user_id']})

# ── Player routes ─────────────────────────────────────────

def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@app.route('/api/players', methods=['GET'])
def get_players():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    players = Player.query.filter_by(user_id=user.id).all()
    result = []
    for p in players:
        score = calculate_score(p.acs, p.kd, p.kda, p.win_rate, p.headshot)
        result.append({
            'id': p.id,
            'name': p.name,
            'agent': p.agent,
            'acs': p.acs,
            'kd': p.kd,
            'kda': p.kda,
            'win_rate': p.win_rate,
            'headshot': p.headshot,
            'matches': p.matches,
            'score': round(score, 1),
            'tier': get_tier(score)
        })
    result.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(result)

@app.route('/api/players', methods=['POST'])
def add_player():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    if Player.query.filter_by(user_id=user.id).count() >= MAX_PLAYERS:
        return jsonify({'error': 'Player limit reached (15/15)'}), 400

    data = request.json
    required = ['name', 'acs', 'kd', 'kda', 'win_rate', 'headshot']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    player = Player(
        user_id=user.id,
        name=data['name'],
        agent=data.get('agent', 'Unknown'),
        acs=float(data['acs']),
        kd=float(data['kd']),
        kda=float(data['kda']),
        win_rate=float(data['win_rate']),
        headshot=float(data['headshot']),
        matches=int(data.get('matches', 0))
    )
    db.session.add(player)
    db.session.commit()
    return jsonify({'message': f"{player.name} added successfully!"}), 201

@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    player = Player.query.filter_by(id=player_id, user_id=user.id).first_or_404()
    db.session.delete(player)
    db.session.commit()
    return jsonify({'message': 'Player deleted'})

@app.route('/api/players/count', methods=['GET'])
def player_count():
    user = get_current_user()
    if not user:
        return jsonify({'count': 0, 'max': MAX_PLAYERS})
    count = Player.query.filter_by(user_id=user.id).count()
    return jsonify({'count': count, 'max': MAX_PLAYERS})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
