# Phase 1 Plan: Data Collection & Infrastructure

Goal: Implement reliable Reddit data collection and persistence.

Tasks:
1. Verify Reddit credentials and `reddit_auth.py` usage.
2. Inspect and run `crawler.py` for a small sample fetch.
3. Implement/verify deduplication in `storage.py`/`database.py`.
4. Add exponential backoff / rate-limit handling in `crawler.py`.
5. Create or verify a `batch_job.py` workflow to fetch 1000 posts/comments per subreddit.
6. Run relevant unit tests: `tests/test_crawler.py`, `tests/test_data_validation.py`.

Commands:
 - Activate virtualenv: `source .venv-1/bin/activate`
 - Run crawler sample: `python3 crawler.py --sample 100`
 - Run tests: `pytest tests/test_crawler.py::test_crawler_fetch -q`

Acceptance Criteria:
 - Successful sample fetch (no exceptions)
 - Data stored in SQLite per schema
 - Tests covering crawler and deduplication pass

Notes:
 - If Reddit credentials are missing, mock network calls for tests.
