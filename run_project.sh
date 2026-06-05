#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
DB_PATH="${DB_PATH:-$ROOT_DIR/data/comments.db}"
RUN_DASHBOARD="${RUN_DASHBOARD:-1}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python executable not found at $PYTHON_BIN"
  echo "Create the virtual environment first: python -m venv .venv"
  exit 1
fi

cd "$ROOT_DIR"

echo "==> Initializing database"
"$PYTHON_BIN" database.py --db-path "$DB_PATH"

echo "==> Running Reddit collection batch"
"$PYTHON_BIN" batch_job.py --db-path "$DB_PATH"

echo "==> Running sentiment pipeline"
"$PYTHON_BIN" sentiment_pipeline.py --db-path "$DB_PATH"

if [[ "$RUN_DASHBOARD" == "1" ]]; then
  echo "==> Launching dashboard"
  if [[ -x "$ROOT_DIR/.venv/bin/streamlit" ]]; then
    exec "$ROOT_DIR/.venv/bin/streamlit" run app.py
  else
    exec "$PYTHON_BIN" -m streamlit run app.py
  fi
fi

echo "==> Project run complete"