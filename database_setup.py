import sqlite3

DB_NAME = "afl_stats.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            home_team TEXT,
            away_team TEXT,
            winner TEXT,
            date TEXT,
            round INTEGER,
            year INTEGER
        )
    """)

    # Add other tables if needed: players, stats, lineups...

    conn.commit()
    conn.close()
    print("✅ Tables created.")
