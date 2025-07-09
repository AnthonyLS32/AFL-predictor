import sqlite3
import pandas as pd

DB_NAME = "afl_stats.db"

def find_match_id(year, round_num, team_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT match_id FROM matches
        WHERE year = ? AND round = ? AND (home_team = ? OR away_team = ?)
    """, (year, round_num, team_name, team_name))
    
    results = cursor.fetchall()
    conn.close()

    if len(results) == 1:
        return results[0][0]
    elif len(results) > 1:
        return results[0][0]
    else:
        return None

def import_match_results(csv_file):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_csv(csv_file)

    df['crowd'] = pd.to_numeric(df['Crowd'].str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    year = int(csv_file.split('_')[1])
    df['Round'] = df['Round'].astype(str).str.extract('(\d+)').astype(int)

    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO matches (year, round, date, home_team, home_score, away_team, away_score, venue, crowd, winner, margin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (year, row['Round'], row['Date'], row['Home Team'], int(row['Home Score']),
              row['Away Team'], int(row['Away Score']), row['Venue'], row['crowd'], row['Winner'], int(row['Margin'])))

    conn.commit()
    conn.close()
    print(f"Imported match results from {csv_file}")

def import_player_stats(csv_file, year, round_number):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_csv(csv_file)
    df['Player'] = df['Player'].str.strip()

    for _, row in df.iterrows():
        conn.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (row['Player'],))
        player_id = conn.execute("SELECT player_id FROM players WHERE name = ?", (row['Player'],)).fetchone()[0]

        match_id = find_match_id(year, round_number, row['Team'])
        if match_id is None:
            print(f"WARNING: No match found for player {row['Player']} in team {row['Team']} round {round_number} year {year}")
            continue

        conn.execute("""
            INSERT INTO player_stats (match_id, player_id, team, kicks, marks, goals, disposals, hitouts, tackles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            player_id,
            row.get('Team', None),
            int(row.get('Kicks', 0)),
            int(row.get('Marks', 0)),
            int(row.get('Goals', 0)),
            int(row.get('Disposals', 0)),
            int(row.get('Hitouts', 0)),
            int(row.get('Tackles', 0)),
        ))

    conn.commit()
    conn.close()
    print(f"Imported player stats from {csv_file}")

if __name__ == "__main__":
    # Example usage:
    # import_match_results("afl_2023_match_results.csv")
    # import_player_stats("afl_2023_round1_player_stats.csv", 2023, 1)
    pass
