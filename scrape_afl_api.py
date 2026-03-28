"""Fetch AFL match results from the AFL API for seasons 2012-2025."""

import json
import time
import urllib.request

API_BASE = "https://aflapi.afl.com.au/afl/v2"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "account": "afl",
    "Origin": "https://www.afl.com.au",
}

# Season ID mapping from the compseasons API
COMP_SEASONS = {
    2012: 2,
    2013: 4,
    2014: 5,
    2015: 7,
    2016: 9,
    2017: 11,
    2018: 14,
    2019: 18,
    2020: 20,
    2021: 34,
    2022: 43,
    2023: 52,
    2024: 62,
    2025: 73,
}


def api_get(path):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_season(year, comp_season_id):
    print(f"Fetching {year} (compSeasonId={comp_season_id})...")
    data = api_get(f"/matches?pageSize=300&competitionId=1&compSeasonId={comp_season_id}")
    matches = []
    for m in data["matches"]:
        if m["status"] != "CONCLUDED":
            continue
        home = m["home"]
        away = m["away"]
        home_score = home["score"]["totalScore"]
        away_score = away["score"]["totalScore"]
        margin = abs(home_score - away_score)

        matches.append({
            "id": m["id"],
            "season": year,
            "round": m["round"]["name"],
            "round_number": m["round"]["roundNumber"],
            "home_team": home["team"]["name"],
            "away_team": away["team"]["name"],
            "home_score": home_score,
            "away_score": away_score,
            "home_goals_behinds": f"{home['score']['goals']}.{home['score']['behinds']}",
            "away_goals_behinds": f"{away['score']['goals']}.{away['score']['behinds']}",
            "margin": margin,
            "venue": m["venue"]["name"],
            "date": m["utcStartTime"],
            "url": f"https://www.afl.com.au/afl/matches/{m['id']}",
        })

    print(f"  Found {len(matches)} completed matches")
    return matches


def main():
    all_matches = []
    for year, comp_season_id in sorted(COMP_SEASONS.items()):
        matches = fetch_season(year, comp_season_id)
        all_matches.extend(matches)
        time.sleep(1)

    print(f"\nTotal matches: {len(all_matches)}")

    with open("matches.json", "w") as f:
        json.dump(all_matches, f, indent=2)
    print("Saved to matches.json")

    close_games = [m for m in all_matches if m["margin"] <= 12 and m["home_score"] + m["away_score"] > 0]
    close_games.sort(key=lambda m: m["margin"])
    with open("close_games.json", "w") as f:
        json.dump(close_games, f, indent=2)
    print(f"Close games (<=12 pts): {len(close_games)}")
    print("Saved to close_games.json")


if __name__ == "__main__":
    main()
