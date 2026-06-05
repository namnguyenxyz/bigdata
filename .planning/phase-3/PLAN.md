# Phase 3 Plan: Ranking Algorithm & Metrics

Goal: Implement leaderboard generation from sentiment data.

Tasks:
1. Review `ranking.py` and configuration for subreddit weights.
2. Run `tests/test_ranking.py` and address any failing cases.
3. Implement historical snapshots export if missing.
4. Add explainability: surface top comments per model.

Commands:
 - `PYTHONPATH=. /home/nhnam/workspace/uit_learning/bigdata/.venv-1/bin/pytest tests/test_ranking.py -q`

Acceptance Criteria:
 - Ranking tests pass
 - Leaderboard sorts models by weighted score
