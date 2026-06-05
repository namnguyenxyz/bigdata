#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--container <name>] [--master <spark-master-url>] --input <path> [other etl args]"
  exit 2
fi

# defaults
CONTAINER="docker-spark-1"
MASTER_URL="spark://spark:7077"
PASS_ARGS=()

# parse simple flags
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --container)
      CONTAINER="$2"
      shift 2
      ;;
    --master)
      MASTER_URL="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--container <name>] [--master <spark-master-url>] --input <path> [other etl args]"
      exit 0
      ;;
    *)
      PASS_ARGS+=("$1")
      shift
      ;;
  esac
done

echo "Preparing container-side submit to container=${CONTAINER}, master=${MASTER_URL}"

# copy workspace into container
echo "Copying workspace to container:/workspace (this may take a moment)"
docker exec "$CONTAINER" mkdir -p /workspace || true
docker cp "$ROOT_DIR/." "$CONTAINER":/workspace

# check spark-submit inside container
if docker exec "$CONTAINER" bash -lc "which spark-submit >/dev/null 2>&1"; then
  echo "spark-submit found inside ${CONTAINER}, running job..."
  CMD=("spark-submit" "--master" "$MASTER_URL" "--deploy-mode" "client" "/workspace/etl_spark.py")
  echo "docker exec $CONTAINER ${CMD[*]} ${PASS_ARGS[*]}"
  docker exec -it "$CONTAINER" bash -lc "${CMD[*]} ${PASS_ARGS[*]}"
else
  echo "spark-submit not found inside ${CONTAINER}."
  echo "You can either:"
  echo "  1) Install Spark into the container image used for ${CONTAINER}, or"
  echo "  2) Run a transient Spark client container that mounts this workspace and submits the job. Example:"
  echo
  echo "docker run --rm --network $(docker network ls --filter name=bridge -q | head -n1) -v \"$ROOT_DIR\":/workspace apache/spark:3.1.1 /bin/bash -lc \"spark-submit --master ${MASTER_URL} /workspace/etl_spark.py ${PASS_ARGS[*]}\""
  echo
  exit 3
fi
