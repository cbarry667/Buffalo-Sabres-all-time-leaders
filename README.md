# Panthers DataBase

This project builds a FastAPI website that scrapes the Buffalo Sabres career leaders page from Hockey Reference and stores the results in a local SQLite database.

## Features

- Scrapes career leader categories from `https://www.hockey-reference.com/teams/FLA/leaders_career.html`
- Stores scraped leader data in `panthers_db_leaders.db`
- Serves an HTML dashboard with all leader categories
- Provides a JSON API at `/api/leaders`
- Supports manual refresh via `/api/scrape`

## Install

Create and activate a Python environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Start the FastAPI app with Uvicorn:

```bash
uvicorn main:app --reload
```

Then open:

- `http://127.0.0.1:8000/` for the website
- `http://127.0.0.1:8000/api/leaders` for JSON data
- `http://127.0.0.1:8000/api/scrape` to refresh the scraper manually
