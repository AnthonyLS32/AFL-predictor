import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load the scraped data
matches = pd.read_csv('matches.csv')
players = pd.read_csv('player_stats.csv')

# --- Basic feature engineering ---

def clean_score(score):
    try:
        return int(score)
    except:
        return np.nan

# Clean numeric scores
matches['home_score'] = matches['home_score'].apply(clean_score)
matches['away_score'] = matches['away_score'].apply(clean_score)

# Only keep rows with valid scores
matches = matches.dropna(subset=['home_score', 'away_score'])

# Label: 1 if home team won, else 0
matches['home_win'] = (matches['home_score'] > matches['away_score']).astype(int)

# Basic recent form proxy: average margin last 5 games (dummy here)
# For real: you could compute rolling means, here we keep it simple

matches['home_margin'] = matches['home_score'] - matches['away_score']

# --- Features ---
# For this example: just simple features: home margin, home advantage

X = matches[['home_margin']]
y = matches['home_win']

# Fill NA with 0 for simplicity
X = X.fillna(0)

# --- Train/Test ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Evaluate ---
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {acc:.2%}")

# --- Save ---
joblib.dump(model, "model.pkl")
print("✅ model.pkl saved!")
