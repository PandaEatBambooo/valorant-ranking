DEFAULT_WEIGHTS = {
    'acs': 0.30,
    'kd': 0.25,
    'kda': 0.20,
    'win_rate': 0.15,
    'headshot': 0.10
}

STAT_RANGES = {
    'acs':      (150, 380),
    'kd':       (0.5, 2.5),
    'kda':      (1.0, 6.0),
    'win_rate': (30,  80),
    'headshot': (5,   55)
}

TIERS = [
    ('Radiant',  90),
    ('Immortal', 75),
    ('Diamond',  60),
    ('Platinum', 45),
    ('Gold',     30),
    ('Iron',      0),
]

def normalize(value, min_val, max_val):
    """Normalize a stat to 0-100 scale."""
    return min(100, max(0, (value - min_val) / (max_val - min_val) * 100))

def calculate_score(acs, kd, kda, win_rate, headshot, weights=None):
    """
    Calculate overall player score using weighted normalized stats.
    
    Args:
        acs: Average Combat Score
        kd: Kill/Death ratio
        kda: Kill/Death/Assist ratio
        win_rate: Win percentage (0-100)
        headshot: Headshot percentage (0-100)
        weights: Optional dict to override default weights
    
    Returns:
        Float score between 0 and 100
    """
    w = weights if weights else DEFAULT_WEIGHTS

    scores = {
        'acs':      normalize(acs,      *STAT_RANGES['acs']),
        'kd':       normalize(kd,       *STAT_RANGES['kd']),
        'kda':      normalize(kda,      *STAT_RANGES['kda']),
        'win_rate': normalize(win_rate, *STAT_RANGES['win_rate']),
        'headshot': normalize(headshot, *STAT_RANGES['headshot'])
    }

    total_weight = sum(w.get(k, 0) for k in scores)
    if total_weight == 0:
        return 0

    weighted_sum = sum(scores[k] * w.get(k, 0) for k in scores)
    return weighted_sum / total_weight

def get_tier(score):
    """Return rank tier name based on score."""
    for tier_name, min_score in TIERS:
        if score >= min_score:
            return tier_name
    return 'Iron'
