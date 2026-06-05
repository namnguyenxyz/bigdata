# Phase 3 Context: Ranking Algorithm & Metrics

Relevant modules:
- ranking.py — ranking and scoring algorithm
- sentiment_storage.py / sentiment_storage — aggregated sentiment data access
- database.py — historical snapshots and DB access

Test assets:
- tests/test_ranking.py

Constraints & assumptions:
- Use weighted scoring: sentiment + engagement + subreddit weights
