import sqlite3
import csv
import os

DB_NAME = "afl_stats.db"

def import_matches(file_path="matches.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT OR REPLACE INTO matches
                (match_id, date, round, year, home_team, away_team, home_score, away_score, venue, winner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["match_id"]),
                row["date"],
                int(row["round"]),
                int(row["year"]),
                row["home_team"],
                row["away_team"],
                int(row["home_score"]),
                int(row["away_score"]),
                row["venue"],
                row["winner"]
            ))
    conn.commit()
    conn.close()
    print("✅ Matches imported.")

def import_player_stats(file_path="player_stats.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO player_stats
                (match_id, player_name, team, goals, disposals, marks, tackles)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["match_id"]),
                row["player_name"],
                row["team"],
                int(row["goals"]),
                int(row["disposals"]),
                int(row["marks"]),
                int(row["tackles"])
            ))
    conn.commit()
    conn.close()
    print("✅ Player stats imported.")
