# Fun Footy

Watch a random close-finish AFL game with no spoilers.

The AFL website has full match replays going back to 2012. Fun Footy picks a random close game and sends you straight to the replay — so you can experience the tension of a close finish without knowing the result.

## How it works

1. A Python scraper (`scrape_afl_api.py`) fetches match results from the AFL's public API for every season since 2012 and saves them to `matches.json`. Close games (margin <= 12 points / 2 goals) are saved to `close_games.json`.

2. A Flask app (`app.py`) serves a simple HTML form with optional filters:
   - **Team** — only show games involving a specific team
   - **Year range** — restrict to certain seasons
   - **Finals only** — only finals matches

3. When you click "Randomise", the server picks a random game from the filtered list, fetches the replay video info from the AFL API, and redirects you to the video on afl.com.au.

For pre-2022 games, replays are split into quarters — the app picks the last quarter (Q4 or extra time). For 2022 onwards, there's a single full match replay.

## Running locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run flask --app app run
```

Then open http://localhost:5000.

## Updating match data

To re-scrape match results (e.g. to include a new season):

```bash
uv run python scrape_afl_api.py
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on hosting with Caddy + Gunicorn on a VPS.
