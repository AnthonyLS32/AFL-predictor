import sqlite3

DB_NAME = "afl_stats.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            date TEXT,
            round INTEGER,
            year INTEGER,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            venue TEXT,
            winner TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_name TEXT,
            team TEXT,
            goals INTEGER,
            disposals INTEGER,
            marks INTEGER,
            tackles INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created.")
