# Post-ingest Context: Spark ETL

Scope: We ignore crawling and focus on processing injected comment data (batch). The project now includes a PySpark-capable ETL with a pandas fallback: `etl_spark.py`.

Key artifacts and inputs:
- `etl_spark.py` — ETL script (PySpark UDFs + pandas fallback)
- `model_extractor.py`, `sentiment_analyzer.py`, `sarcasm_detector.py` — extraction and NLP logic
- `sentiment_storage.py`, `database.py` — SQLite schema and DB helpers
- `ranking.py` — leaderboard generation from DB
- Data locations: Parquet/CSV inputs (injection point). Example: `data/sample_comments.csv` produced during smoke test.

Assumptions:
- Running on a single-host Spark or local pandas fallback for testing.
- DB writes use existing SQLite schema at `data/comments.db`.
