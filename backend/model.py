"""
model.py — drop-in replacement

Keeps the EXACT same function signatures your app.py already calls:

    calculate_score(p.acs, p.kd, p.kda, p.win_rate, p.headshot)
    get_tier(score)

...so nothing in app.py needs to change just to install this file.

New, optional capability: pass mode="ai" to use the trained regression
model instead of the fixed weighted formula. Existing calls (which don't
pass mode) are completely unaffected and keep using the same weighted
formula as before.
"""

import os
import joblib
import pandas as pd

BOUNDS = {
    "acs": (100, 350),
    "kd": (0.5, 2.0),
    "kda": (0.5, 2.5),
    "win_rate": (0, 100),
    "headshot": (0, 60),
}
FEATURES = ["acs", "kd", "kda", "win_rate", "headshot"]

DEFAULT_WEIGHTS = {
    "acs": 0.30,
    "kd": 0.25,
    "kda": 0.20,
    "win_rate": 0.15,
    "headshot": 0.10,
}

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "score_model.pkl")
_ai_bundle = None


def _load_ai_model():
    global _ai_bundle
    if _ai_bundle is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                "score_model.pkl not found in backend/ — AI mode unavailable "
                "until it's trained and placed there. Falling back is the "
                "caller's responsibility."
            )
        _ai_bundle = joblib.load(_MODEL_PATH)
    return _ai_bundle


def _normalize(value, lo, hi):
    return max(0, min(100, (value - lo) / (hi - lo) * 100))


def calculate_score(acs, kd, kda, win_rate, headshot, mode="custom", weights=None):
    """
    Backward compatible with existing calls like:
        calculate_score(p.acs, p.kd, p.kda, p.win_rate, p.headshot)
    (mode defaults to "custom", so behavior is unchanged unless you
    explicitly pass mode="ai" or a custom `weights` dict.)
    """
    stats = {"acs": acs, "kd": kd, "kda": kda, "win_rate": win_rate, "headshot": headshot}
    norm = {k: _normalize(v, *BOUNDS[k]) for k, v in stats.items()}

    if mode == "ai":
        bundle = _load_ai_model()
        model = bundle["model"]
        X = pd.DataFrame([[norm[f] / 100.0 for f in FEATURES]], columns=FEATURES)
        score = model.predict(X)[0]
        return round(max(0, min(100, score)), 1)

    w = weights or DEFAULT_WEIGHTS
    score = sum(norm[f] * w[f] for f in FEATURES)
    return round(score, 1)


def get_tier(score):
    """Matches the tier ranges in the proposal report."""
    if score < 30:
        return "Iron"
    elif score < 45:
        return "Gold"
    elif score < 60:
        return "Platinum"
    elif score < 75:
        return "Diamond"
    elif score < 90:
        return "Immortal"
    else:
        return "Radiant"
