import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import db, Player
from model import calculate_score, get_tier

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///players.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

MAX_PLAYERS = 15

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/players', methods=['GET'])
def get_players():
    players = Player.query.all()
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
    if Player.query.count() >= MAX_PLAYERS:
        return jsonify({'error': 'Player limit reached (15/15)'}), 400

    data = request.json
    required = ['name', 'acs', 'kd', 'kda', 'win_rate', 'headshot']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    player = Player(
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
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify({'message': 'Player deleted'})

@app.route('/api/players/count', methods=['GET'])
def player_count():
    count = Player.query.count()
    return jsonify({'count': count, 'max': MAX_PLAYERS})

@app.route('/api/score', methods=['POST'])
def compute_score():
    data = request.json
    weights = data.get('weights', None)
    score = calculate_score(
        data['acs'], data['kd'], data['kda'],
        data['win_rate'], data['headshot'],
        weights=weights
    )
    return jsonify({'score': round(score, 1), 'tier': get_tier(score)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
