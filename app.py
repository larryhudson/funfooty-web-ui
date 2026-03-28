"""Flask app for Fun Footy — random close finish AFL replays."""

import json
import random
import urllib.request
import urllib.parse

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

# Load close games into memory at startup
with open("close_games.json") as f:
    CLOSE_GAMES = json.load(f)

TEAMS = sorted({g["home_team"] for g in CLOSE_GAMES} | {g["away_team"] for g in CLOSE_GAMES})

AFL_API_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://www.afl.com.au",
}


def get_replay_url(match_id, season):
    """Fetch replay video URL from the AFL API."""
    url = (
        f"https://aflapi.afl.com.au/content/afl/video/EN/"
        f"?references=AFL_MATCH%3A{match_id}"
        f"&tagNames=ProgramCategory%3AMatch%20Replays&limit=30"
    )
    req = urllib.request.Request(url, headers=AFL_API_HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    videos = data.get("content", [])
    if not videos:
        return None

    if season >= 2022:
        # Single full match replay
        video = videos[0]
    else:
        # Multiple quarter replays — pick the one with the highest publishFrom
        # (Q4, or extra time if it exists)
        video = max(videos, key=lambda v: v["publishFrom"])

    video_id = video["id"]
    slug = video["titleUrlSegment"]
    publish_from = video["publishFrom"]
    return (
        f"https://www.afl.com.au/video/{video_id}/{slug}"
        f"?videoId={video_id}&modal=true&type=video&publishFrom={publish_from}"
    )


@app.route("/")
def index():
    return render_template("index.html", teams=TEAMS)


@app.route("/randomise", methods=["POST"])
def randomise():
    team = request.form.get("team", "")
    min_year = int(request.form.get("min_year", 2012))
    max_year = int(request.form.get("max_year", 2025))
    finals_only = request.form.get("finals_only") == "on"

    filtered = CLOSE_GAMES
    if team:
        filtered = [
            g for g in filtered
            if g["home_team"] == team or g["away_team"] == team
        ]
    filtered = [g for g in filtered if min_year <= g["season"] <= max_year]
    if finals_only:
        filtered = [g for g in filtered if "Round" not in g["round"]]

    if not filtered:
        return render_template("index.html", teams=TEAMS, error="No games match your filters. Try broadening your search.")

    game = random.choice(filtered)
    replay_url = get_replay_url(game["id"], game["season"])

    if not replay_url:
        return render_template("index.html", teams=TEAMS, error="Couldn't find a replay for that game. Try again!")

    return redirect(replay_url)
