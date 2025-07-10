import streamlit as st
import pandas as pd
import os
from predictor import predict_win_probability, load_model
from feature_engineering import generate_features_for_match
from scraper_utils import scrape_fixture, save_fixture, load_fixture

# -------------------------
# App Config
# -------------------------
MODEL_FILE = "model.pkl"

# -------------------------
# App Start
# -------------------------
st.set_page_config(page_title="🏉 AFL Win Probability Predictor", layout="centered")

st.title("🏉 AFL Win Probability Predictor")

# -------------------------
# Scrape Fixture or Load Cache
# -------------------------
if not os.path.exists("static/fixture.json"):
    fixture = scrape_fixture()
    save_fixture(fixture)
else:
    fixture = load_fixture()

matches_df = pd.read_json("static/fixture.json")

# -------------------------
# Pick or Upload
# -------------------------
st.sidebar.header("📅 Select Match or Upload")

match = st.sidebar.selectbox(
    "Select a match",
    matches_df["match_label"].tolist()
)

uploaded_file = st.sidebar.file_uploader("Or upload your lineup CSV", type="csv")

if uploaded_file:
    custom_lineup = pd.read_csv(uploaded_file)
    st.write("✅ Uploaded Lineup:")
    st.dataframe(custom_lineup)
else:
    match_row = matches_df[matches_df["match_label"] == match].iloc[0]
    match_id = match_row["match_id"]

    st.subheader("Selected Match")
    st.write(f"{match_row['match_label']}")
    features = generate_features_for_match(match_row)

    st.subheader("Match Features")
    st.json(features)

    if os.path.exists(MODEL_FILE):
        prob = predict_win_probability(features)
        st.success(f"🏆 **Predicted Home Win Probability:** {prob:.2%}")
    else:
        st.error("❌ No model found. Please run training to generate `model.pkl`.")
