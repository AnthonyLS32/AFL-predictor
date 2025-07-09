import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

DB_NAME = "afl_stats.db"
MODEL_FILE = "afl_win_probability_model.pkl"

TEAM_HOME_GROUNDS = {
    "Geelong": ["GMHBA Stadium"],
    "Melbourne": ["MCG"],
    "Collingwood": ["MCG"],
    "Richmond": ["MCG"],
    "Carlton": ["MCG", "Marvel Stadium"],
}

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM matches WHERE winner IS NOT NULL", conn)
    conn.close()

    def is_home_advantage(row):
        return int(row["venue"] in TEAM_HOME_GROUNDS.get(row["home_team"], []))

    df["home_team_recent_form"] = 0.5  # Dummy — replace with real stats
    df["away_team_recent_form"] = 0.4
    df["is_home_advantage"] = df.apply(is_home_advantage, axis=1)
    df["home_team_won"] = (df["winner"] == df["home_team"]).astype(int)

    return df

def train_and_save():
    df = load_data()

    feature_cols = ["home_team_recent_form", "away_team_recent_form", "is_home_advantage"]
    X = df[feature_cols]
    y = df["home_team_won"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Model trained! Accuracy: {acc:.2%}")

    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model saved as {MODEL_FILE}")

if __name__ == "__main__":
    train_and_save()
