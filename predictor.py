import sqlite3
import joblib
import numpy as np
from feature_engineering import generate_features_for_match, get_team_recent_form, get_team_avg_player_stats

DB_NAME = "afl_stats.db"
MODEL_FILE = "afl_win_probability_model.pkl"

def load_model():
    return joblib.load(MODEL_FILE)

def predict_win_probability(match_id):
    model = load_model()
    features = generate_features_for_match(match_id)

    feature_order = ['home_team_recent_form', 'away_team_recent_form',
                     'home_avg_kicks', 'home_avg_marks', 'home_avg_goals', 'home_avg_disposals', 'home_avg_hitouts', 'home_avg_tackles',
                     'away_avg_kicks', 'away_avg_marks', 'away_avg_goals', 'away_avg_disposals', 'away_avg_hitouts', 'away_avg_tackles',
                     'is_home_advantage']

    X = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)

    prob_home_win = model.predict_proba(X)[0][1]
    prob_away_win = 1 - prob_home_win

    return {
        'home_team_win_probability': prob_home_win,
        'away_team_win_probability': prob_away_win
    }

if __name__ == "__main__":
    test_match_id = 1
    probs = predict_win_probability(test_match_id)
    print(f"Home Team Win Probability: {probs['home_team_win_probability']:.2%}")
    print(f"Away Team Win Probability: {probs['away_team_win_probability']:.2%}")
