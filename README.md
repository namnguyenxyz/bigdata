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

## Project Layout

- `reddit_auth.py` - Reddit API client creation
- `database.py` - SQLite schema initialization
- `storage.py` - persistence, validation, and deduplication
- `crawler.py` - subreddit comment fetcher
- `batch_job.py` - end-to-end collection orchestration
- `tests/` - offline validation tests

## Phase 2 Handoff

Phase 2 will consume the `comments` table and the `model_mentions` table, both of which are created by Phase 1.
