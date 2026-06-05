# Local Spark via Docker Compose

Files:
- `docker/docker-compose.yml` — master + worker using `bitnami/spark` image.

Start cluster:

```
docker compose -f docker/docker-compose.yml up -d
```

Check master UI: http://localhost:8080

Run ETL with `spark-submit` (on host or inside container):

```
./scripts/spark_submit.sh --input /path/to/data/injected.parquet --format parquet --write-db
```

Notes:
- The `bitnami/spark` image provides `spark-submit` inside the container — you can also exec into it and run `spark-submit` there.
- If Docker is not available in your environment, run the ETL locally (pandas fallback) using `python etl_spark.py`.
