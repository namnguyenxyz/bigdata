#!/usr/bin/env bash
# spark-submit wrapper for etl_spark.py
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--cluster] --input <path> [--format parquet|csv] [--output <path>] [--write-db]"
  exit 2
fi

# Detect special flags and build passthrough args
USE_CLUSTER=false
PASS_ARGS=()
for arg in "$@"; do
  if [ "$arg" = "--cluster" ]; then
    USE_CLUSTER=true
    continue
  fi
  PASS_ARGS+=("$arg")
done

# Choose master depending on cluster flag
if [ "$USE_CLUSTER" = true ]; then
  MASTER="spark://localhost:7078"
else
  MASTER="local[4]"
fi

# Build spark-submit command
SPARK_SUBMIT_CMD=(spark-submit --master "$MASTER" --deploy-mode client "${ROOT_DIR}/etl_spark.py")

echo "Running: ${SPARK_SUBMIT_CMD[*]} ${PASS_ARGS[*]}"
"${SPARK_SUBMIT_CMD[@]}" "${PASS_ARGS[@]}"
