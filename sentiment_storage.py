from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Iterable

from database import DEFAULT_DB_PATH, get_db_connection, init_database

VALID_SENTIMENT_LABELS = {"positive", "negative", "neutral"}


def _close_if_needed(connection: sqlite3.Connection, db_conn: sqlite3.Connection | None) -> None:
    if db_conn is None:
        connection.close()


def insert_sentiment_result(
    comment_id: str,
    sentiment_label: str,
    sentiment_score: float,
    sarcasm_detected: bool,
    sarcasm_patterns: Iterable[str] | None,
    db_conn: sqlite3.Connection | None = None,
) -> bool:
    if sentiment_label not in VALID_SENTIMENT_LABELS:
        raise ValueError(f"Invalid sentiment_label: {sentiment_label}")
    if not 0.0 <= float(sentiment_score) <= 1.0:
        raise ValueError(f"sentiment_score must be in [0.0, 1.0], got {sentiment_score}")

    connection = db_conn or get_db_connection(DEFAULT_DB_PATH)
    try:
        processed_at = datetime.now(timezone.utc).isoformat()
        patterns_json = json.dumps(list(sarcasm_patterns or [])) if sarcasm_patterns else None
        cursor = connection.execute(
            """
            UPDATE comments
            SET sentiment_label = ?,
                sentiment_score = ?,
                sarcasm_detected = ?,
                sarcasm_patterns = ?,
                processed_at = ?
            WHERE id = ?
            """,
            (
                sentiment_label,
                float(sentiment_score),
                int(bool(sarcasm_detected)),
                patterns_json,
                processed_at,
                comment_id,
            ),
        )
        return cursor.rowcount > 0
    finally:
        _close_if_needed(connection, db_conn)


def get_unprocessed_comments(
    limit: int | None = None,
    db_conn: sqlite3.Connection | None = None,
) -> list[dict[str, Any]]:
    connection = db_conn or get_db_connection(DEFAULT_DB_PATH)
    try:
        query = """
            SELECT id, text, author, subreddit, created_utc, score, upvote_ratio
            FROM comments
            WHERE processed_at IS NULL
            ORDER BY created_utc DESC
        """
        params: tuple[Any, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (int(limit),)

        cursor = connection.execute(query, params)
        rows = cursor.fetchall()
        if rows and isinstance(rows[0], sqlite3.Row):
            return [dict(row) for row in rows]

        columns = [col[0] for col in cursor.description or []]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        _close_if_needed(connection, db_conn)


def get_sentiment_stats(db_conn: sqlite3.Connection | None = None) -> dict[str, Any]:
    connection = db_conn or get_db_connection(DEFAULT_DB_PATH)
    try:
        cursor = connection.execute(
            """
            SELECT
                COALESCE(sentiment_label, 'unprocessed') AS sentiment_label,
                COUNT(*) AS count,
                AVG(sentiment_score) AS avg_score,
                SUM(CASE WHEN sarcasm_detected THEN 1 ELSE 0 END) AS sarcasm_count
            FROM comments
            WHERE processed_at IS NOT NULL
            GROUP BY COALESCE(sentiment_label, 'unprocessed')
            ORDER BY sentiment_label
            """
        )

        stats: dict[str, Any] = {}
        for row in cursor.fetchall():
            label = row[0]
            stats[label] = {
                "count": int(row[1]),
                "avg_confidence": float(row[2] or 0.0),
                "sarcasm_count": int(row[3] or 0),
            }
        return stats
    finally:
        _close_if_needed(connection, db_conn)


def reset_sentiment_fields(db_path: str = str(DEFAULT_DB_PATH)) -> None:
    init_database(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            UPDATE comments
            SET sentiment_label = NULL,
                sentiment_score = NULL,
                sarcasm_detected = 0,
                sarcasm_patterns = NULL,
                processed_at = NULL
            """
        )
        connection.commit()