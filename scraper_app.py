import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://afltables.com/afl/seas/"
START_YEAR = 2010
END_YEAR = 2024  # Update this each season if needed

def scrape_matches():
    matches = []
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"{BASE_URL}{year}.html"
        try:
            res = requests.get(url, timeout=20)
            res.raise_for_status()
        except Exception as e:
            st.warning(f"Could not load matches for {year}: {e}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        tables = soup.find_all("table", {"class": "sortable"})
        if not tables:
            st.warning(f"No tables found for {year}")
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
        time.sleep(0.5)  # polite pause between years
    return matches


def scrape_player_stats():
    players = []
    index_url = "https://afltables.com/afl/stats/players.html"

    try:
        res = requests.get(index_url, timeout=30)
        res.raise_for_status()
    except Exception as e:
        st.error(f"Could not load players index: {e}")
        return players

    soup = BeautifulSoup(res.content, "html.parser")
    player_links = soup.select("table a")

    for link in player_links:
        player_name = link.text.strip()
        href = link.get("href")
        player_url = f"https://afltables.com/afl/stats/{href}"

        try:
            pres = requests.get(player_url, timeout=10)
            pres.raise_for_status()
            psoup = BeautifulSoup(pres.content, "html.parser")
            tables = psoup.find_all("table")
            if len(tables) < 2:
                continue

            rows = tables[-1].find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 5 and cells[0].text.strip() == "Career":
                    games_played = int(cells[1].text.strip())
                    goals = int(cells[4].text.strip())
                    avg_goals = round(goals / games_played, 2) if games_played > 0 else 0
                    players.append([player_name, "N/A", games_played, avg_goals])
                    break
            time.sleep(0.1)  # polite pause between players
        except Exception:
            continue

    return players


def save_csv(filename, rows, headers):
    try:
        with open(filename, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        st.success(f"✅ Saved {filename} ({len(rows)} records).")
    except Exception as e:
        st.error(f"Could not save {filename}: {e}")


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="🏉 AFLTables Historical Data Scraper", layout="centered")
st.title("🏉 AFLTables Historical Data Scraper")

st.markdown("""
Use this tool to:
- 🔄 Download AFL match results from 2010–now
- 📊 Download all-time player career stats
- 🗂️ Save data as `matches.csv` and `player_stats.csv`
- 📌 Use these files in your main predictor app!
""")

if st.button("🚀 Run Scraper Now"):
    with st.spinner("Scraping matches..."):
        matches = scrape_matches()
    if matches:
        save_csv("matches.csv", matches, ["match_id", "home_team", "away_team", "date", "venue", "home_score", "away_score"])
    else:
        st.warning("No match data scraped.")

    with st.spinner("Scraping player stats... (this may take several minutes)"):
        players = scrape_player_stats()
    if players:
        save_csv("player_stats.csv", players, ["player_name", "team", "games_played", "average_goals"])
    else:
        st.warning("No player stats scraped.")

    st.info("✅ Done! You can re-run this anytime to refresh your data.")
