import joblib

MODEL_FILE = "afl_win_probability_model.pkl"

def load_model():
    return joblib.load(MODEL_FILE)

def predict_win_probability(features):
    model = load_model()

    feature_vector = [
        features["home_team_recent_form"],
        features["away_team_recent_form"],
        features["is_home_advantage"]
    ]

    prob = model.predict_proba([feature_vector])[0][1]  # Home win prob
    return prob
