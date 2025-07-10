def generate_features_for_match(match_row):
    features = {
        "home_team_recent_form": 1,  # Placeholder or calculate from matches.csv
        "away_team_recent_form": 0,
        "is_home_advantage": 1 if match_row["venue"] in match_row["home_ground"] else 0
    }
    return features
