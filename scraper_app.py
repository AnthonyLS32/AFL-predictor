def scrape_player_stats():
    players = []
    url = "https://afltables.com/afl/stats/alltime/players.html"
    res = requests.get(url, timeout=20)
    soup = BeautifulSoup(res.content, "html.parser")
    table = soup.find("table")

    if table is None:
        raise ValueError("❌ Could not find player stats table on the page. Check the URL or page structure.")

    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        name = cells[0].text.strip()
        team = cells[1].text.strip()
        games = cells[2].text.strip()
        goals = cells[3].text.strip()
        try:
            games_played = int(games)
            goals_scored = int(goals)
            avg_goals = round(goals_scored / games_played, 2) if games_played > 0 else 0
        except:
            continue
        players.append([
            name, team, games_played, avg_goals
        ])
    return players
