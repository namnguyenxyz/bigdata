import sqlite3
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from database import init_database
from data_helpers import get_available_subreddits, load_leaderboard


def _create_comment(
    connection,
    comment_id,
    text,
    subreddit,
    created_offset_days,
    score,
    upvote_ratio,
    sentiment_label,
    sentiment_score,
):
    created_utc = int((datetime.now(timezone.utc) - timedelta(days=created_offset_days)).timestamp())
    connection.execute(
        """
        INSERT INTO comments (id, text, author, subreddit, created_utc, data_hash, score, upvote_ratio, sentiment_label, sentiment_score, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            comment_id,
            text,
            "tester",
            subreddit,
            created_utc,
            f"hash-{comment_id}",
            score,
            upvote_ratio,
            sentiment_label,
            sentiment_score,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def _create_mention(connection, comment_id, model_name):
    connection.execute(
        "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
        (comment_id, model_name, 1.0, model_name),
    )


def test_get_available_subreddits_returns_distinct_values():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        _create_comment(conn, "c1", "Sample.", "r/chatgpt", 1, 1, 0.5, "neutral", 0.5)
        _create_comment(conn, "c2", "Another sample.", "r/machinelearning", 1, 2, 0.7, "positive", 0.7)
        conn.commit()

        subreddits = get_available_subreddits(db_path)
        assert "r/chatgpt" in subreddits
        assert "r/machinelearning" in subreddits
    finally:
        conn.close()
        Path(db_path).unlink()


def test_load_leaderboard_returns_ranked_models():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        _create_comment(conn, "c1", "I love this model.", "r/chatgpt", 1, 10, 0.8, "positive", 0.9)
        _create_mention(conn, "c1", "ChatGPT")
        _create_comment(conn, "c2", "This model is bad.", "r/machinelearning", 1, 2, 0.4, "negative", 0.8)
        _create_mention(conn, "c2", "Claude")
        conn.commit()

        leaderboard = load_leaderboard(window="30d", db_path=db_path)
        assert len(leaderboard) == 2
        assert leaderboard[0]["score"] >= leaderboard[1]["score"]
    finally:
        conn.close()
        Path(db_path).unlink()
