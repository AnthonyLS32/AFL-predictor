import sqlite3

DB_NAME = "afl_stats.db"

TEAM_HOME_GROUNDS = {
    "Geelong": ["GMHBA Stadium"],
    "Melbourne": ["MCG"],
    "Collingwood": ["MCG"],
    "Richmond": ["MCG"],
    "Carlton": ["MCG", "Marvel Stadium"],
}

def get_team_recent_form(team, match_date):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT winner FROM matches
        WHERE (home_team = ? OR away_team = ?)
          AND date < ?
          AND year >= 2010
        ORDER BY date DESC
        LIMIT 5
    """, (team, team, match_date))
    results = cur.fetchall()
    conn.close()

    if not results:
        return 0.5

    wins = sum(1 for r in results if r[0] == team)
    return wins / len(results)

def generate_features_for_match(match_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT home_team, away_team, venue, date FROM matches WHERE match_id = ?
    """, (match_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "home_team_recent_form": 0.5,
            "away_team_recent_form": 0.5,
            "is_home_advantage": 0
        }

    home_team, away_team, venue, match_date = row

    home_form = get_team_recent_form(home_team, match_date)
    away_form = get_team_recent_form(away_team, match_date)
    is_home_advantage = int(venue in TEAM_HOME_GROUNDS.get(home_team, []))

    return {
        "home_team_recent_form": home_form,
        "away_team_recent_form": away_form,
        "is_home_advantage": is_home_advantage
    }
