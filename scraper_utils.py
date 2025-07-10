import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def scrape_fixture():
    url = "https://www.afl.com.au/fixture"
    resp = requests.get(url, timeout=15)
    soup = BeautifulSoup(resp.content, "html.parser")
    matches = []
    for game in soup.select(".MatchFixture"):
        home = game.select_one(".HomeTeam").text.strip()
        away = game.select_one(".AwayTeam").text.strip()
        date = game.select_one(".MatchDate").text.strip()
        venue = game.select_one(".MatchVenue").text.strip()
        match_id = f"{home}_vs_{away}_{date.replace(' ', '_')}"
        matches.append({
            "match_id": match_id,
            "home_team": home,
            "away_team": away,
            "date": date,
            "venue": venue,
            "home_ground": venue,  # Simplified
            "match_label": f"{home} vs {away} ({date})"
        })
    return matches

def save_fixture(fixture):
    with open("static/fixture.json", "w") as f:
        json.dump(fixture, f)

def load_fixture():
    with open("static/fixture.json") as f:
        return pd.read_json(f)
