import sqlite3

DB_NAME = "afl_stats.db"

TEAM_HOME_GROUNDS = {
    "Geelong": ["GMHBA Stadium"],
    "Melbourne": ["MCG"],
    "Collingwood": ["MCG"],
    "Richmond": ["MCG"],
    "Carlton": ["MCG", "Marvel Stadium"],
    # Extend as needed
}

def generate_features_for_match(match_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT home_team, away_team, venue
        FROM matches
        WHERE match_id = ?
    """, (match_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    home_team, away_team, venue = row

    # Dummy form: static placeholder, replace later
    home_team_form = 0.5
    away_team_form = 0.4

    is_home_advantage = int(venue in TEAM_HOME_GROUNDS.get(home_team, []))

    features = {
        "home_team_recent_form": home_team_form,
        "away_team_recent_form": away_team_form,
        "is_home_advantage": is_home_advantage
    }

    return features
