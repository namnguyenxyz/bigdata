# spark-submit Usage for `etl_spark.py`

This file documents how to run the ETL on a Spark cluster or locally with `spark-submit`.

Local spark-submit wrapper:

```
./scripts/spark_submit.sh --input /path/to/injected_data.parquet --format parquet --write-db
```

Notes:
- The script runs `spark-submit --master local[4]` by default for local testing.
- Ensure PySpark is available on the target environment or cluster.
- For cluster runs, remove `--master local[4]` and set appropriate cluster master/submit options.

If `spark-submit` is not available locally, the `etl_spark.py` script will fall back to a pandas-based processor (suitable for small datasets and smoke tests).
