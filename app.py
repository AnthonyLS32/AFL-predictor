import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from predictor import predict_win_probability
from feature_engineering import generate_features_for_match

DB_NAME = "afl_stats.db"

@st.cache_data(ttl=3600)
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

def format_match_label(match):
    match_id, home, away, date, rnd, year = match
    return f"{year} R{rnd} | {date} | {home} vs {away}"

@st.cache_data(ttl=3600)
def get_players_for_team(team_name):
    conn = sqlite3.connect(DB_NAME)
    df = conn.execute("""
        SELECT DISTINCT players.name FROM players
        JOIN player_stats ON players.player_id = player_stats.player_id
        WHERE player_stats.team = ?
        ORDER BY players.name
    """, (team_name,)).fetchall()
    conn.close()
    return [row[0] for row in df]

@st.cache_data(ttl=3600)
def get_lineup(match_id, team_name):
    conn = sqlite3.connect(DB_NAME)
    df = conn.execute("""
        SELECT player_name FROM lineups WHERE match_id = ? AND team = ?
    """, (match_id, team_name)).fetchall()
    conn.close()
    return [row[0] for row in df]

def update_lineup(match_id, team_name, selected_players):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineups (
            lineup_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            team TEXT,
            player_name TEXT,
            UNIQUE(match_id, team, player_name)
        )
    """)
    cursor.execute("DELETE FROM lineups WHERE match_id = ? AND team = ?", (match_id, team_name))
    for player in selected_players:
        cursor.execute("INSERT OR IGNORE INTO lineups (match_id, team, player_name) VALUES (?, ?, ?)",
                       (match_id, team_name, player))
    conn.commit()
    conn.close()

def plot_recent_form(match_id, home_team, away_team):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    def get_form(team):
        cur.execute("""
            SELECT winner FROM matches 
            WHERE (home_team = ? OR away_team = ?)
            ORDER BY year DESC, round DESC
            LIMIT 10
        """, (team, team))
        results = cur.fetchall()
        return [1 if w[0]==team else 0 for w in results]

    home_form = get_form(home_team)
    away_form = get_form(away_team)
    conn.close()

    fig, ax = plt.subplots()
    ax.plot(range(1, len(home_form)+1), home_form, label=home_team, marker='o')
    ax.plot(range(1, len(away_form)+1), away_form, label=away_team, marker='o')
    ax.set_xlabel("Last 10 Games (Most Recent Right)")
    ax.set_ylabel("Win (1) or Loss (0)")
    ax.set_title("Recent Team Form")
    ax.legend()
    st.pyplot(fig)

def main():
    st.title("AFL Win Probability Predictor")

    matches = get_upcoming_matches()
    match_options = {format_match_label(m): m[0] for m in matches}
    selected_match_label = st.selectbox("Select a match:", list(match_options.keys()))
    selected_match_id = match_options[selected_match_label]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT home_team, away_team FROM matches WHERE match_id = ?", (selected_match_id,))
    home_team, away_team = cur.fetchone()
    conn.close()

    st.subheader(f"Select lineup for {home_team}")
    home_players = get_players_for_team(home_team)
    current_home_lineup = get_lineup(selected_match_id, home_team)
    selected_home_players = st.multiselect("Home Team Players:", options=home_players, default=current_home_lineup)

    st.subheader(f"Select lineup for {away_team}")
    away_players = get_players_for_team(away_team)
    current_away_lineup = get_lineup(selected_match_id, away_team)
    selected_away_players = st.multiselect("Away Team Players:", options=away_players, default=current_away_lineup)

    if st.button("Update Lineups"):
        update_lineup(selected_match_id, home_team, selected_home_players)
        update_lineup(selected_match_id, away_team, selected_away_players)
        st.success("Lineups updated!")

    if st.button("Predict Win Probability"):
        with st.spinner("Calculating..."):
            try:
                probs = predict_win_probability(selected_match_id)
                st.success("Prediction complete!")
                st.write(f"**Home Team Win Probability:** {probs['home_team_win_probability']:.2%}")
                st.write(f"**Away Team Win Probability:** {probs['away_team_win_probability']:.2%}")

                plot_recent_form(selected_match_id, home_team, away_team)
            except Exception as e:
                st.error(f"Error during prediction: {e}")

if __name__ == "__main__":
    main()
