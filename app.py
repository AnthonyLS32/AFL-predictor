"""
app.py
AFL Win Probability Predictor — Streamlit app
- Scrapes AFLTables data automatically on first run if needed
- Builds SQLite database from scraped data
- Predicts win probabilities using trained model
"""

import os
import sqlite3
import streamlit as st
import csv
from bs4 import BeautifulSoup
import requests
from predictor import predict_win_probability
from feature_engineering import generate_features_for_match

DB_NAME = "afl_stats.db"
MATCHES_CSV = "matches.csv"
PLAYER_STATS_CSV = "player_stats.csv"

def run_scraper():
    """
    Scrape match results and player stats from AFLTables for 2010-current.
    Saves to matches.csv and player_stats.csv.
    """
    st.info("Starting AFL data scrape (this may take several minutes)...")
    BASE_URL = "https://afltables.com/afl/seas/"
    YEARS = range(2010, 2025)

    match_id_counter = 1

    matches_file = open(MATCHES_CSV, mode="w", newline="", encoding="utf-8")
    matches_writer = csv.writer(matches_file)
    matches_writer.writerow([
        "match_id", "date", "round", "year",
        "home_team", "away_team",
        "home_score", "away_score",
        "venue", "winner"
    ])

    player_stats_file = open(PLAYER_STATS_CSV, mode="w", newline="", encoding="utf-8")
    player_stats_writer = csv.writer(player_stats_file)
    player_stats_writer.writerow([
        "match_id", "player_name", "team",
        "goals", "disposals", "marks", "tackles"
    ])

    def parse_score(score_str):
        if "(" in score_str:
            return int(score_str.split("(")[-1].split(")")[0])
        return 0

    def clean_name(name):
        return name.strip().replace('\xa0', ' ')

    progress_bar = st.progress(0)
    total_years = len(YEARS)
    for idx, year in enumerate(YEARS):
        url = f"{BASE_URL}{year}.html"
        try:
            res = requests.get(url, timeout=20)
            res.raise_for_status()
        except Exception as e:
            st.warning(f"Warning: failed to fetch data for {year} ({e}), skipping.")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 10:
                    date = cells[0].text.strip()
                    round_num = cells[1].text.strip().replace("Round ", "")
                    home_team = clean_name(cells[2].text)
                    home_score = parse_score(cells[3].text)
                    away_team = clean_name(cells[6].text)
                    away_score = parse_score(cells[7].text)
                    venue = clean_name(cells[9].text)
                    winner = home_team if home_score > away_score else away_team

                    matches_writer.writerow([
                        match_id_counter, date, round_num, year,
                        home_team, away_team,
                        home_score, away_score,
                        venue, winner
                    ])

                    link = cells[10].find("a")
                    if link and "href" in link.attrs:
                        match_url = "https://afltables.com/afl/stats/" + link["href"]
                        try:
                            match_res = requests.get(match_url, timeout=20)
                            match_res.raise_for_status()
                        except Exception as e:
                            st.warning(f"Warning: failed to fetch match stats for match {match_id_counter} ({e}), skipping player stats.")
                            match_id_counter += 1
                            continue

                        match_soup = BeautifulSoup(match_res.text, "html.parser")
                        stat_tables = match_soup.find_all("table", {"class": "sortable"})

                        for stat_table in stat_tables[:2]:
                            team_header = stat_table.find_previous("b")
                            team_name = clean_name(team_header.text) if team_header else "Unknown"
                            stat_rows = stat_table.find_all("tr")[2:]

                            for stat_row in stat_rows:
                                stat_cells = stat_row.find_all("td")
                                if len(stat_cells) > 10:
                                    player_name = clean_name(stat_cells[1].text)
                                    try:
                                        goals = int(stat_cells[6].text)
                                        disposals = int(stat_cells[9].text)
                                        marks = int(stat_cells[10].text)
                                        tackles = int(stat_cells[12].text)
                                    except:
                                        goals = disposals = marks = tackles = 0

                                    player_stats_writer.writerow([
                                        match_id_counter, player_name, team_name,
                                        goals, disposals, marks, tackles
                                    ])

                    match_id_counter += 1

        progress_bar.progress((idx + 1) / total_years)

    matches_file.close()
    player_stats_file.close()
    st.success("✅ Scraping complete: matches.csv and player_stats.csv saved.")

@st.cache_data(show_spinner=False)
def ensure_data():
    """
    Checks if CSV files exist, otherwise runs scraper.
    """
    if not (os.path.exists(MATCHES_CSV) and os.path.exists(PLAYER_STATS_CSV)):
        run_scraper()

@st.cache_data(show_spinner=False)
def setup_database():
    """
    Creates database and imports CSV data.
    """
    import database_setup
    import data_import

    database_setup.create_tables()
    data_import.import_matches(MATCHES_CSV)
    data_import.import_player_stats(PLAYER_STATS_CSV)

def get_matches():
    """
    Loads all matches from DB.
    """
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

    with st.spinner("Checking and preparing data... this can take several minutes initially"):
        ensure_data()
        setup_database()

    matches = get_matches()
    if not matches:
        st.error("❌ No matches found in the database after setup.")
        st.stop()

    match_options = [f"{row[5]} R{row[4]}: {row[1]} vs {row[2]} ({row[3]})" for row in matches]
    selected = st.selectbox("Select a match", options=match_options)
    selected_match_id = matches[match_options.index(selected)][0]

    features = generate_features_for_match(selected_match_id)
    st.subheader("Match Features")
    st.json(features)

    prob = predict_win_probability(features)
    home_team = matches[match_options.index(selected)][1]
    st.markdown(f"### Probability {home_team} (home team) wins: **{prob:.2%}**")

if __name__ == "__main__":
    main()
