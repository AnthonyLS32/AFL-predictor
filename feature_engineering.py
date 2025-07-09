import sqlite3

DB_NAME = "afl_stats.db"

def get_team_recent_form(conn, team, current_match_id, window=5):
    cur = conn.cursor()
    cur.execute("SELECT year, round FROM matches WHERE match_id = ?", (current_match_id,))
    result = cur.fetchone()
    if not result:
        return 0
    year, round_num = result

    cur.execute("""
        SELECT winner FROM matches 
        WHERE (home_team = ? OR away_team = ?)
          AND (year < ? OR (year = ? AND round < ?))
        ORDER BY year DESC, round DESC
        LIMIT ?
    """, (team, team, year, year, round_num, window))

    matches = cur.fetchall()
    if not matches:
        return 0

    wins = sum(1 for (winner,) in matches if winner == team)
    return wins / window

def get_team_avg_player_stats(conn, team, current_match_id, window=5):
    cur = conn.cursor()
    cur.execute("SELECT year, round FROM matches WHERE match_id = ?", (current_match_id,))
    result = cur.fetchone()
    if not result:
        return {}

    year, round_num = result

    cur.execute("""
        SELECT match_id FROM matches
        WHERE (home_team = ? OR away_team = ?)
          AND (year < ? OR (year = ? AND round < ?))
        ORDER BY year DESC, round DESC
        LIMIT ?
    """, (team, team, year, year, round_num, window))

    match_ids = [row[0] for row in cur.fetchall()]
    if not match_ids:
        return {}

    placeholder= ','.join('?' for _ in match_ids)
    query = f"""
        SELECT AVG(kicks), AVG(marks), AVG(goals), AVG(disposals), AVG(hitouts), AVG(tackles)
        FROM player_stats
        WHERE match_id IN ({placeholder}) AND team = ?
    """
    params = match_ids + [team]
    cur.execute(query, params)
    result = cur.fetchone()
    keys = ['avg_kicks', 'avg_marks', 'avg_goals', 'avg_disposals', 'avg_hitouts', 'avg_tackles']
    return dict(zip(keys, result))

def generate_features_for_match(match_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT home_team, away_team, venue FROM matches WHERE match_id = ?", (match_id,))
    row = cur.fetchone()
    if not row:
        print(f"Match ID {match_id} not found")
        return None
    home_team, away_team, venue = row

    features = {}

    features['home_team_recent_form'] = get_team_recent_form(conn, home_team, match_id)
    features['away_team_recent_form'] = get_team_recent_form(conn, away_team, match_id)

    home_stats = get_team_avg_player_stats(conn, home_team, match_id)
    away_stats = get_team_avg_player_stats(conn, away_team, match_id)

    for k,v in home_stats.items():
        features[f'home_{k}'] = v if v is not None else 0
    for k,v in away_stats.items():
        features[f'away_{k}'] = v if v is not None else 0

    features['is_home_advantage'] = 1

    conn.close()
    return features

if __name__ == "__main__":
    # Example
    features = generate_features_for_match(1)
    print(features)
