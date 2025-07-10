import joblib
import os

MODEL_FILE = "afl_win_probability_model.pkl"

def load_model():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("❌ Model file not found. Run model_training.py first.")
    return joblib.load(MODEL_FILE)

def predict_win_probability(features):
    model = load_model()
    vector = [
        features["home_team_recent_form"],
        features["away_team_recent_form"],
        features["is_home_advantage"]
    ]
    prob = model.predict_proba([vector])[0][1]
    return prob
