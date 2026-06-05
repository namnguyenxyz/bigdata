# AI Model Ranking via Reddit Sentiment Analysis

A Python + Streamlit project for ranking AI models using community sentiment from curated Reddit discussions.

## Phase 1 Scope

This repository currently contains the Phase 1 data collection and storage pipeline:
- Reddit API authentication via PRAW
- SQLite schema and persistence helpers
- Subreddit comment crawler
- Batch job runner
- Tests for schema and deduplication logic

## Quick Start

1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Fill in your Reddit credentials in `.env`
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Initialize the database:

```bash
python database.py
```

6. Run the batch job:

```bash
python batch_job.py
```

7. Run the Streamlit dashboard:

```bash
streamlit run app.py
```

## Phase 5 Runbook

Use the following order to validate the full MVP locally:

1. `python database.py`
2. `python batch_job.py`
3. `python sentiment_pipeline.py --db-path ./data/comments.db`
4. `streamlit run app.py`

Environment notes:
- Copy `.env.example` to `.env` and fill in Reddit API credentials if you plan to collect live data.
- The dashboard and ranking code both read from `./data/comments.db` by default.
- If you do not have Reddit credentials, you can still run the NLP, ranking, and dashboard steps against seeded sample data.

Verification checklist:
- `python -m py_compile app.py data_helpers.py ranking.py`
- `python -m pytest tests/test_phase5_integration.py -q`
- Confirm the dashboard loads and the leaderboard appears for the selected filters.

## Project Layout

- `reddit_auth.py` - Reddit API client creation
- `database.py` - SQLite schema initialization
- `storage.py` - persistence, validation, and deduplication
- `crawler.py` - subreddit comment fetcher
- `batch_job.py` - end-to-end collection orchestration
- `sentiment_pipeline.py` - NLP sentiment batch processing
- `ranking.py` - weighted leaderboard generation
- `data_helpers.py` - dashboard query helpers
- `app.py` - Streamlit dashboard entrypoint
- `tests/` - offline validation tests

## Phase 2 Handoff

Phase 2 will consume the `comments` table and the `model_mentions` table, both of which are created by Phase 1.
