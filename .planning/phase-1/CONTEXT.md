# Phase 1 Context: Data Collection & Infrastructure

Source files relevant to Phase 1:
- crawler.py — subreddit crawler and PRAW integration
- batch_job.py — batch collection job orchestration
- reddit_auth.py — Reddit auth helpers
- storage.py / storage helpers — data persistence
- database.py — SQLite schema and DB helpers

Existing notes and artifacts:
- .planning/ROADMAP.md — phase objectives and deliverables
- manual_test_set.json — manual validation samples

Constraints & assumptions:
- Use local SQLite for MVP
- Aim to fetch ~5000 comments without duplicates
- Respect Reddit API rate limits with exponential backoff

Primary success criteria:
- Data persists in local SQLite
- No duplicate records
- Collection runs reliably (batch job)
