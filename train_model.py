import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

matches = pd.read_csv('matches.csv')

matches['home_score'] = pd.to_numeric(matches['home_score'], errors='coerce')
matches['away_score'] = pd.to_numeric(matches['away_score'], errors='coerce')

matches = matches.dropna(subset=['home_score', 'away_score'])

matches['home_win'] = (matches['home_score'] > matches['away_score']).astype(int)
matches['margin'] = matches['home_score'] - matches['away_score']

X = matches[['margin']].fillna(0)
y = matches['home_win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {acc:.2%}")

joblib.dump(model, "model.pkl")
print("✅ model.pkl saved!")
