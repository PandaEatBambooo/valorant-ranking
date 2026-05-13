# Valorant Player Ranking System

An ML-powered web app that ranks Valorant players based on their match statistics using a weighted scoring model.

---

## Features
- Rank up to 15 players based on ACS, K/D, KDA, Win Rate, and Headshot %
- Automatic tier assignment (Radiant, Immortal, Diamond, Platinum, Gold, Iron)
- Adjustable ML model weights
- Add and remove players
- Deployable on Railway for public access

---

## Project Structure

```
valorant-ranking/
├── backend/
│   ├── app.py          # Flask API
│   ├── model.py        # ML scoring logic
│   └── database.py     # SQLAlchemy models
├── frontend/
│   ├── index.html      # Rankings leaderboard
│   ├── add_player.html # Add player form
│   └── model.html      # Weight tuner
├── Procfile            # Railway start command
├── railway.toml        # Railway config
└── requirements.txt    # Python dependencies
```

---

## Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Flask backend
```bash
cd backend
python app.py
```

### 3. Open the app
Visit: http://localhost:5000

---

## Deploying on Railway

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/valorant-ranking.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to https://railway.app and sign in
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `valorant-ranking` repository
4. Railway auto-detects the Procfile and deploys

### Step 3 — Add a database (optional for persistence)
1. In Railway, click **+ New** → **Database** → **PostgreSQL**
2. Copy the `DATABASE_URL` from the PostgreSQL service
3. Add it as an environment variable in your app service:
   - Key: `DATABASE_URL`
   - Value: (paste the URL)

### Step 4 — Get your public URL
Railway will give you a URL like: `https://valorant-ranking.up.railway.app`

---

## Scoring Formula

Each stat is normalized to a 0–100 scale, then multiplied by its weight:

```
Score = (ACS × 0.30) + (K/D × 0.25) + (KDA × 0.20) + (Win Rate × 0.15) + (HS% × 0.10)
```

Weights can be adjusted via the Model Weights page.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/players | Get all players (sorted by score) |
| POST | /api/players | Add a new player |
| DELETE | /api/players/:id | Delete a player |
| GET | /api/players/count | Get current player count |
| POST | /api/score | Compute score for given stats |
