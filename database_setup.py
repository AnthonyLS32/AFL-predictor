import sqlite3

def create_tables(db_name="afl_stats.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER,
        round INTEGER,
        date TEXT,
        home_team TEXT,
        home_score INTEGER,
        away_team TEXT,
        away_score INTEGER,
        venue TEXT,
        crowd INTEGER,
        winner TEXT,
        margin INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        team TEXT,
        kicks INTEGER,
        marks INTEGER,
        goals INTEGER,
        disposals INTEGER,
        hitouts INTEGER,
        tackles INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lineups (
        lineup_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team TEXT,
        player_name TEXT,
        UNIQUE(match_id, team, player_name)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
