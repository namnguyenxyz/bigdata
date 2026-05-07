from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from database import DEFAULT_DB_PATH, init_database

MIN_COMMENT_LENGTH = 10
MIN_UNIX_TIMESTAMP = 1_100_000_000
MAX_UNIX_TIMESTAMP = 4_102_444_800


def validate_comment(comment: dict[str, Any]) -> bool:
    if not isinstance(comment, dict):
        return False

    comment_id = str(comment.get("id", "")).strip()
    text = str(comment.get("text", "")).strip()
    subreddit = str(comment.get("subreddit", "")).strip()
    created_utc = comment.get("created_utc")
    score = comment.get("score", 0)

    if not comment_id or not text or len(text) < MIN_COMMENT_LENGTH or not subreddit:
        return False

    try:
        created_utc_int = int(created_utc)
    except (TypeError, ValueError):
        return False
    if created_utc_int < MIN_UNIX_TIMESTAMP or created_utc_int > MAX_UNIX_TIMESTAMP:
        return False

    try:
        int(score)
    except (TypeError, ValueError):
        return False

    author = comment.get("author")
    if author is not None and not isinstance(author, str):
        return False

    return True


def compute_data_hash(
    author: str | None,
    text: str,
    created_utc: int,
    submission_id: str | None = None,
    subreddit: str | None = None,
) -> str:
    payload = "|".join(
        [
            (author or "").strip(),
            text.strip(),
            str(int(created_utc)),
            (submission_id or "").strip(),
            (subreddit or "").strip(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_comment(comment: dict[str, Any]) -> dict[str, Any]:
    author = comment.get("author")
    if author is not None:
        author = str(author).strip() or None

    submission_id = comment.get("submission_id")
    if submission_id is not None:
        submission_id = str(submission_id).strip() or None

    subreddit = str(comment.get("subreddit", "")).strip()
    text = str(comment.get("text", "")).strip()
    created_utc = int(comment.get("created_utc", 0))
    score = int(comment.get("score", 0))
    upvote_ratio = comment.get("upvote_ratio")
    if upvote_ratio is not None:
        upvote_ratio = float(upvote_ratio)

    data_hash = compute_data_hash(author, text, created_utc, submission_id, subreddit)

    return {
        "id": str(comment.get("id", "")).strip(),
        "text": text,
        "author": author,
        "submission_id": submission_id,
        "subreddit": subreddit,
        "created_utc": created_utc,
        "score": score,
        "upvote_ratio": upvote_ratio,
        "data_hash": data_hash,
        "is_deleted": int(bool(comment.get("is_deleted", False))),
        "is_archived": int(bool(comment.get("is_archived", False))),
    }


def store_comments(db_path: str = str(DEFAULT_DB_PATH), comments_list: list[dict[str, Any]] | None = None) -> dict[str, int]:
    init_database(db_path)
    comments = comments_list or []

    inserted = 0
    duplicates = 0
    errors = 0

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()

        cursor.execute("SELECT id, data_hash FROM comments")
        existing_ids = {row[0] for row in cursor.fetchall()}
        existing_hashes = {row[1] for row in cursor.fetchall()} if False else set()

        cursor.execute("SELECT data_hash FROM comments")
        existing_hashes = {row[0] for row in cursor.fetchall()}

        for comment in comments:
            if not validate_comment(comment):
                errors += 1
                continue

            normalized = normalize_comment(comment)
            if normalized["id"] in existing_ids or normalized["data_hash"] in existing_hashes:
                duplicates += 1
                continue

            try:
                cursor.execute(
                    """
                    INSERT INTO comments (
                        id, text, author, submission_id, subreddit, created_utc,
                        score, upvote_ratio, data_hash, is_deleted, is_archived
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized["id"],
                        normalized["text"],
                        normalized["author"],
                        normalized["submission_id"],
                        normalized["subreddit"],
                        normalized["created_utc"],
                        normalized["score"],
                        normalized["upvote_ratio"],
                        normalized["data_hash"],
                        normalized["is_deleted"],
                        normalized["is_archived"],
                    ),
                )
            except sqlite3.IntegrityError:
                duplicates += 1
                continue

            existing_ids.add(normalized["id"])
            existing_hashes.add(normalized["data_hash"])
            inserted += 1

        connection.commit()

    return {"inserted": inserted, "duplicates": duplicates, "errors": errors}


def log_collection_run(
    db_path: str,
    subreddit: str,
    stats: dict[str, Any],
    run_timestamp: str | None = None,
) -> None:
    init_database(db_path)
    timestamp = run_timestamp or datetime.now(timezone.utc).isoformat()
    errors = stats.get("errors", "")
    if isinstance(errors, (list, tuple, set, dict)):
        errors = json.dumps(errors)
    else:
        errors = str(errors) if errors is not None else ""

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO collection_log (
                run_timestamp, subreddit, comments_fetched, comments_new,
                comments_duplicate, errors, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                subreddit,
                int(stats.get("comments_fetched", 0)),
                int(stats.get("comments_new", 0)),
                int(stats.get("comments_duplicate", 0)),
                errors,
                float(stats.get("duration_seconds", 0.0)),
            ),
        )
        connection.commit()
