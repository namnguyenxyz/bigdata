#!/usr/bin/env bash
set -euo pipefail

# Build and start the spark-client service, then run spark-submit inside it.
COMPOSE_FILE=docker/docker-compose.yml
SERVICE=spark-client

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 -- [spark-submit args]"
  echo "Example: $0 -- --master spark://spark:7077 /workspace/etl_spark.py --input /workspace/data/fake_injected.csv --write-db"
  exit 1
fi

ARGS=("${@}")

echo "Building and starting ${SERVICE}..."
docker compose -f "${COMPOSE_FILE}" up --build -d "${SERVICE}"

echo "Running spark-submit inside ${SERVICE}"
docker compose -f "${COMPOSE_FILE}" exec -T "${SERVICE}" /bin/bash -lc "export PYSPARK_PYTHON=python3; spark-submit ${ARGS[*]}"

echo "Done. To stop the client container: docker compose -f ${COMPOSE_FILE} down"
