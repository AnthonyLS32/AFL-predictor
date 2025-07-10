import os
import sqlite3
import streamlit as st
from database_setup import create_tables
from data_import import import_matches, import_player_stats
from predictor import predict_win_probability
from feature_engineering import generate_features_for_match

DB_NAME = "afl_stats.db"

@st.cache_resource
def ensure_db():
    if not os.path.exists(DB_NAME):
        create_tables()
        if os.path.exists("matches.csv"):
            import_matches()
        else:
            st.warning("⚠️ matches.csv not found. Skipping matches import.")
        if os.path.exists("player_stats.csv"):
            import_player_stats()
        else:
            st.warning("⚠️ player_stats.csv not found. Skipping player stats import.")
    else:
        st.info("✅ Database ready.")

ensure_db()

@st.cache_data
def get_matches():
    if not os.path.exists(DB_NAME):
        st.error("❌ Database not found. Please create it first.")
        return []

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT match_id, home_team, away_team, date, round, year
        FROM matches
        WHERE year >= 2010
        ORDER BY year DESC, round DESC
    """)
    matches = cur.fetchall()
    conn.close()
    return matches

def main():
    st.title("🏉 AFL Win Probability Predictor")

    matches = get_matches()
    if not matches:
        st.error("❌ No matches found in DB.")
        return

    match = st.selectbox(
        "Pick a match",
        matches,
        format_func=lambda m: f"{m[5]} R{m[4]}: {m[1]} vs {m[2]} ({m[3]})"
    )
    match_id = match[0]

    features = generate_features_for_match(match_id)
    st.write("🔍 **Match Features:**", features)

    try:
        prob = predict_win_probability(features)
        st.success(f"🏆 Home Win Probability: {prob:.2%}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")

if __name__ == "__main__":
    main()
