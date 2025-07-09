import sqlite3
import csv
import os

DB_NAME = "afl_stats.db"
CSV_FILE = "matches.csv"

def import_matches():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} not found!")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT OR REPLACE INTO matches
                (match_id, home_team, away_team, winner, date, round, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['match_id']),
                row['home_team'],
                row['away_team'],
                row['winner'],
                row['date'],
                int(row['round']),
                int(row['year'])
            ))

    conn.commit()
    conn.close()
    print("✅ Matches imported from matches.csv.")
