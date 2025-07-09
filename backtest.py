import sqlite3
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from predictor import load_model
from feature_engineering import generate_features_for_match
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import joblib

DB_NAME = "afl_stats.db"
MODEL_FILE = "afl_win_probability_model.pkl"

def backtest_and_retrain(n_matches=1000):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Get recent matches with known results
    cur.execute("""
        SELECT match_id, home_team, winner 
        FROM matches 
        WHERE winner IS NOT NULL 
        ORDER BY year DESC, round DESC
        LIMIT ?
    """, (n_matches,))
    matches = cur.fetchall()
    conn.close()

    model = load_model()

    X_backtest = []
    y_true = []
    y_pred_probs = []
    y_pred = []

    for match_id, home_team, winner in matches:
        features = generate_features_for_match(match_id)
        if not features:
            continue

        feature_order = [
            'home_team_recent_form', 'away_team_recent_form',
            'home_avg_kicks', 'home_avg_marks', 'home_avg_goals', 'home_avg_disposals',
            'home_avg_hitouts', 'home_avg_tackles',
            'away_avg_kicks', 'away_avg_marks', 'away_avg_goals', 'away_avg_disposals',
            'away_avg_hitouts', 'away_avg_tackles',
            'is_home_advantage'
        ]

        X = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
        prob_home_win = model.predict_proba(X)[0][1]
        pred = 1 if prob_home_win >= 0.5 else 0
        actual = 1 if winner == home_team else 0

        X_backtest.append(list(features.values()))
        y_true.append(actual)
        y_pred_probs.append(prob_home_win)
        y_pred.append(pred)

    # Compute metrics
    acc = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_pred_probs)
    cm = confusion_matrix(y_true, y_pred)

    print(f"✅ Backtest on {len(y_true)} matches")
    print(f"Accuracy: {acc:.3f}")
    print(f"AUC: {auc:.3f}")
    print("Confusion Matrix:")
    print(cm)

    # Save predictions if you like:
    df = pd.DataFrame(X_backtest, columns=feature_order)
    df['actual'] = y_true
    df['predicted'] = y_pred
    df['predicted_prob'] = y_pred_probs
    df.to_csv("backtest_results.csv", index=False)
    print("📄 Saved detailed backtest results to backtest_results.csv")

    # ✅ Retrain the model using *all* matches with known results:
    print("🔄 Retraining final model on ALL data...")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT match_id, home_team, away_team, winner FROM matches WHERE winner IS NOT NULL")
    matches = cur.fetchall()
    conn.close()

    X_train = []
    y_train = []

    for match_id, home_team, away_team, winner in matches:
        features = generate_features_for_match(match_id)
        if not features:
            continue

        X_train.append([features.get(f, 0) for f in feature_order])
        y_train.append(1 if winner == home_team else 0)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    joblib.dump(clf, MODEL_FILE)
    print(f"✅ Updated model saved to {MODEL_FILE}")

if __name__ == "__main__":
    backtest_and_retrain(n_matches=1000)
