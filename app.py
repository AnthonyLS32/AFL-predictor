import os
import sqlite3
import streamlit as st
from database_setup import create_tables
from data_import import import_matches
from predictor import predict_win_probability
from feature_engineering import generate_features_for_match

DB_NAME = "afl_stats.db"

# ✅ Streamlit resource cache ensures single setup run
@st.cache_resource
def ensure_database():
    if not os.path.exists(DB_NAME):
        st.info("🗂️ Creating new database...")
        create_tables()
        import_matches()
    else:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM matches")
            count = cur.fetchone()[0]
            if count == 0:
                st.warning("⚠️ Matches table empty, re-importing...")
                import_matches()
        except sqlite3.OperationalError:
            st.warning("⚠️ Matches table missing, creating...")
            create_tables()
            import_matches()
        conn.close()

ensure_database()

@st.cache_data
def get_upcoming_matches():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT match_id, home_team, away_team, date, round, year
        FROM matches
        ORDER BY year DESC, round DESC, date DESC
        LIMIT 50
    """)
    matches = cur.fetchall()
    conn.close()
    return matches

def main():
    st.title("🏉 AFL Win Probability Predictor")

    matches = get_upcoming_matches()
    if not matches:
        st.error("No matches found! Please check matches.csv.")
        return

    match = st.selectbox(
        "Select a match",
        matches,
        format_func=lambda x: f"{x[5]} R{x[4]}: {x[1]} vs {x[2]} ({x[3]})"
    )

    match_id = match[0]
    features = generate_features_for_match(match_id)
    if not features:
        st.error("Could not generate features.")
        return

    st.subheader("Match Features")
    st.json(features)

    prob = predict_win_probability(features)
    st.success(f"Predicted Home Team Win Probability: {prob:.2%}")

if __name__ == "__main__":
    main()
