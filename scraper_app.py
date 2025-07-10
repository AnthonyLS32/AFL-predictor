import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://afltables.com/afl/seas/"
START_YEAR = 2010
END_YEAR = 2024  # Update this to current year as needed

def scrape_matches():
    matches = []
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"{BASE_URL}{year}.html"
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
        except Exception as e:
            st.warning(f"Failed to load matches for {year}: {e}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        tables = soup.find_all("table", {"class": "sortable"})
        if not tables:
            st.warning(f"No match tables found for year {year}")
            continue

        for table in tables:
            rows = table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 7:
                    continue
                date = cells[0].text.strip()
                round_num = cells[1].text.strip()
                home_team = cells[2].text.strip()
                home_score = cells[3].text.strip()
                away_team = cells[4].text.strip()
                away_score = cells[5].text.strip()
                venue = cells[6].text.strip()
                match_id = f"{year}_{round_num}_{home_team}_vs_{away_team}"
                matches.append([
                    match_id, home_team, away_team, date, venue, home_score, away_score
                ])
        time.sleep(1)  # polite pause between requests
    return matches

def scrape_player_stats():
    players = []
    url = "https://afltables.com/afl/stats/alltime/players.html"
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
    except Exception as e:
        st.error(f"Failed to load player stats: {e}")
        return players

    soup = BeautifulSoup(res.content, "html.parser")
    table = soup.find("table")
    if table is None:
        st.error("Player stats table not found on page.")
        return players

    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        name = cells[0].text.strip()
        team = cells[1].text.strip()
        games = cells[2].text.strip()
        goals = cells[3].text.strip()
        try:
            games_played = int(games)
            goals_scored = int(goals)
            avg_goals = round(goals_scored / games_played, 2) if games_played > 0 else 0
        except:
            continue
        players.append([
            name, team, games_played, avg_goals
        ])
    return players

def save_csv(filename, rows, headers):
    try:
        with open(filename, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        st.success(f"✅ Saved {filename} ({len(rows)} records).")
    except Exception as e:
        st.error(f"Failed to save {filename}: {e}")

st.set_page_config(page_title="🏉 AFLTables Scraper", layout="centered")
st.title("🏉 AFLTables Historical Data Scraper")

if st.button("🚀 Run Scraper Now"):
    with st.spinner("Scraping matches..."):
        matches = scrape_matches()
    if matches:
        save_csv("matches.csv", matches, ["match_id", "home_team", "away_team", "date", "venue", "home_score", "away_score"])
    else:
        st.warning("No match data scraped.")

    with st.spinner("Scraping player stats..."):
        players = scrape_player_stats()
    if players:
        save_csv("player_stats.csv", players, ["player_name", "team", "games_played", "average_goals"])
    else:
        st.warning("No player stats scraped.")

    st.info("You can re-run the scraper anytime to refresh the data.")

st.markdown("""
---
**Notes:**
- Scrapes historical AFL matches from 2010 to current year.
- Scrapes all-time player stats from AFLTables.
- Make sure you have internet access.
- Polite pauses added to avoid overwhelming the server.
""")
