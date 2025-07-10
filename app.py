import streamlit as st
import pandas as pd
from predictor import predict_win_probability

matches = pd.read_csv("matches.csv")

def generate_features_for_match(match_id):
    match = matches[matches['match_id'] == match_id].iloc[0]
    is_home_advantage = 1
    features = {
        "home_team_recent_form": 1,
        "away_team_recent_form": 0,
        "is_home_advantage": is_home_advantage
    }
    return features

st.set_page_config(page_title="🏉 AFL Predictor", layout="centered")
st.title("🏉 AFL Win Probability Predictor")

match_options = matches[['match_id', 'home_team', 'away_team', 'date']].drop_duplicates()
match_options['label'] = match_options.apply(lambda x: f"{x['date']}: {x['home_team']} vs {x['away_team']}", axis=1)
selected = st.selectbox("Select a match", match_options['label'].tolist())

match_id = match_options[match_options['label'] == selected]['match_id'].values[0]

features = generate_features_for_match(match_id)

st.subheader("Match Features")
st.json(features)

if st.button("Predict Win Probability"):
    prob = predict_win_probability(features)
    st.success(f"🏉 Predicted Home Win Probability: {prob * 100:.1f}%")
