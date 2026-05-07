from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    author TEXT,
    submission_id TEXT,
    subreddit TEXT NOT NULL,
    created_utc INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    upvote_ratio REAL,
    collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
    data_hash TEXT NOT NULL UNIQUE,
    is_deleted INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS model_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    confidence REAL,
    extracted_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(comment_id) REFERENCES comments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    comments_fetched INTEGER DEFAULT 0,
    comments_new INTEGER DEFAULT 0,
    comments_duplicate INTEGER DEFAULT 0,
    errors TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_comments_subreddit_created
    ON comments(subreddit, created_utc DESC);
CREATE INDEX IF NOT EXISTS idx_comments_score
    ON comments(score DESC);
CREATE INDEX IF NOT EXISTS idx_model_mentions_comment_id
    ON model_mentions(comment_id);
CREATE INDEX IF NOT EXISTS idx_model_mentions_model_name
    ON model_mentions(model_name);
CREATE INDEX IF NOT EXISTS idx_collection_log_run_timestamp
    ON collection_log(run_timestamp DESC);
"""

DEFAULT_DB_PATH = Path("./data/comments.db")


def ensure_parent_directory(db_path: str | Path) -> Path:
    database_path = Path(db_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return database_path


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(str(db_path))
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def init_database(db_path: str | Path = DEFAULT_DB_PATH) -> Path:
    """Create the SQLite database and apply the Phase 1 schema."""
    database_path = ensure_parent_directory(db_path)
    connection = sqlite3.connect(str(database_path))
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.executescript(SCHEMA_SQL)
        connection.commit()
    finally:
        connection.close()
    return database_path


def list_tables(db_path: str | Path = DEFAULT_DB_PATH) -> list[str]:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize the Phase 1 SQLite database.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="Path to the SQLite database")
    args = parser.parse_args(list(argv) if argv is not None else None)

    database_path = init_database(args.db_path)
    print(f"Initialized database at {database_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
