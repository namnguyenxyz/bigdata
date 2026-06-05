# Post-ingest Plan: Spark ETL -> DB -> Ranking

Goal: Finish ETL integration, persist sentiment & mentions to the DB, and run `ranking.py` for the leaderboard.

Tasks:
1. Enable DB writes and model_mention inserts in `etl_spark.py` (pandas path already supports this).
2. Run ETL against a representative injected dataset and verify `comments` and `model_mentions` updated in `data/comments.db`.
3. Run `python ranking.py` (or `python -m ranking`) to produce the leaderboard; validate results.
4. Add tests: `tests/test_etl.py` to validate end-to-end processing (use small sample and temporary DB).
5. Document commands in `.planning/post-ingest/README.md` or add to project `README.md`.
6. Optional: package PySpark job for cluster runs (spark-submit) and add a small Dockerfile for reproducible runs.

Commands (local/pandas smoke):
```
PYTHONPATH=. .venv-1/bin/python etl_spark.py --input data/sample_comments.csv --format csv --output data/processed_sample.parquet --write-db
PYTHONPATH=. .venv-1/bin/python ranking.py --db-path data/comments.db --window 30d
```

Acceptance criteria:
- `comments` table has `sentiment_label` and `sentiment_score` set for sampled rows.
- `model_mentions` populated for rows mentioning models.
- `ranking.py` runs and prints a sensible leaderboard for the sample.
