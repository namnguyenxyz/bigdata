# Milestone Cleanup Notes

Date: 2026-06-05

Summary:
- Milestone artifacts consolidated under `.planning/`.
- ETL implementation (`etl_spark.py`) and tests validated in local environment (pandas fallback).
- Docker compose for local Spark retained at `docker/docker-compose.yml`.

Actions taken:
- Marked milestone as archived in `.planning/STATE.md`.
- Added `scripts/spark_submit.sh` and `scripts/spark_submit_container.sh` to support local and container-side submits.
- Left sample processed artifacts in `data/` for reproducibility; remove when storage cleanup desired.

Suggested follow-ups:
- Tag release `v1.0-mvp` and create a release note summarizing artifacts and how to reproduce the ETL locally.
- Optionally migrate DB to PostgreSQL if moving to production.
