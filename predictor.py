import joblib
import os

MODEL_FILE = "model.pkl"

def load_model():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("❌ Model not found. Please train it first.")
    return joblib.load(MODEL_FILE)

def predict_win_probability(features: dict):
    model = load_model()
    X = [[
        features["home_team_recent_form"],
        features["away_team_recent_form"],
        features["is_home_advantage"]
    ]]
    prob = model.predict_proba(X)[0][1]
    return prob
