import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib
from feature_engineering import generate_features_for_match, get_team_recent_form, get_team_avg_player_stats

DB_NAME = "afl_stats.db"

def get_training_data():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT match_id, home_team, away_team, winner FROM matches")
    matches = cur.fetchall()

    X = []
    y = []

    for match_id, home_team, away_team, winner in matches:
        if winner is None or winner == '':
            continue

        features = generate_features_for_match(match_id)
        if not features:
            continue

        label = 1 if winner == home_team else 0

        X.append(list(features.values()))
        y.append(label)

    conn.close()

    feature_names = list(features.keys())
    df = pd.DataFrame(X, columns=feature_names)
    df['label'] = y
    return df

if __name__ == "__main__":
    print("Fetching training data...")
    df = get_training_data()
    print(f"Training data shape: {df.shape}")

    X = df.drop(columns=['label'])
    y = df['label']

    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:,1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print(f"Accuracy: {acc:.3f}")
    print(f"AUC: {auc:.3f}")

    joblib.dump(clf, "afl_win_probability_model.pkl")
    print("Model saved as afl_win_probability_model.pkl")
