from __future__ import annotations

import importlib
import importlib.util
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from database import init_database
from data_helpers import load_leaderboard
from sentiment_pipeline import run_sentiment_pipeline


def _insert_comment(connection: sqlite3.Connection, comment_id: str, text: str, subreddit: str) -> None:
    connection.execute(
        """
        INSERT INTO comments (id, text, author, subreddit, created_utc, data_hash, score, upvote_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            comment_id,
            text,
            "tester",
            subreddit,
            int(datetime.now(timezone.utc).timestamp()),
            f"hash-{comment_id}",
            10,
            0.85,
        ),
    )


def _insert_mention(connection: sqlite3.Connection, comment_id: str, model_name: str) -> None:
    connection.execute(
        "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
        (comment_id, model_name, 1.0, model_name),
    )


def test_end_to_end_pipeline_ranking_and_dashboard_import():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    connection: sqlite3.Connection | None = None
    try:
        init_database(db_path)
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        _insert_comment(connection, "c1", "I love ChatGPT for brainstorming.", "r/chatgpt")
        _insert_comment(connection, "c2", "Claude is great for long context.", "r/machinelearning")
        _insert_mention(connection, "c1", "ChatGPT")
        _insert_mention(connection, "c2", "Claude")
        connection.commit()

        summary = run_sentiment_pipeline(batch_size=10, db_path=db_path)
        assert summary["total_processed"] == 2
        assert summary["total_failed"] == 0

        leaderboard = load_leaderboard(window="30d", db_path=db_path, limit=10)
        assert len(leaderboard) == 2
        assert leaderboard[0]["support_count"] >= 1

        importlib.import_module("app")
    finally:
        if connection is not None:
            connection.close()
        Path(db_path).unlink()


def test_streamlit_import_if_available():
    if importlib.util.find_spec("streamlit") is None:
        return

    streamlit = importlib.import_module("streamlit")
    assert streamlit is not None
