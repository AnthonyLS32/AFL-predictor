import joblib

MODEL_FILE = "model.pkl"

def load_model():
    return joblib.load(MODEL_FILE)

def predict_win_probability(features):
    model = load_model()
    X = [[
        features.get('home_team_recent_form', 0),
        features.get('away_team_recent_form', 0),
        features.get('is_home_advantage', 0),
    ]]
    prob = model.predict_proba(X)[0][1]
    return round(prob, 2)
