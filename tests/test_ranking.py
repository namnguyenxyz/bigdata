import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

from database import init_database
from ranking import (
    RankingConfig,
    compute_engagement_weight,
    compute_comment_contribution,
    get_leaderboard,
    get_ranked_model_rows,
)


def _create_comment(
    conn,
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
    conn.execute(
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


def _create_mention(conn, comment_id, model_name):
    conn.execute(
        "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
        (comment_id, model_name, 1.0, "sample"),
    )


def test_engagement_weight_increases_with_votes():
    weight_low = compute_engagement_weight(score=0, upvote_ratio=0.0)
    weight_high = compute_engagement_weight(score=100, upvote_ratio=0.9)
    assert weight_high > weight_low
    assert weight_low >= 1.0


def test_compute_comment_contribution_returns_weights():
    config = RankingConfig()
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute(
            "INSERT INTO comments (id, text, author, subreddit, created_utc, data_hash, score, upvote_ratio, sentiment_label, sentiment_score, processed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "c1",
                "I love this model.",
                "tester",
                "r/chatgpt",
                int(datetime.now(timezone.utc).timestamp()),
                "hash1",
                10,
                0.8,
                "positive",
                0.9,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.execute(
            "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
            ("c1", "ChatGPT", 1.0, "ChatGPT"),
        )
        conn.commit()

        cursor = conn.execute(
            "SELECT mm.model_name, c.id AS comment_id, c.text, c.subreddit, c.created_utc, c.score AS comment_score, c.upvote_ratio, c.sentiment_label, c.sentiment_score FROM model_mentions mm JOIN comments c ON c.id = mm.comment_id"
        )
        row = cursor.fetchone()
        contribution = compute_comment_contribution(row, config)
        assert contribution["model_name"] == "ChatGPT"
        assert contribution["engagement_weight"] > 1.0
        assert contribution["contribution"] > 0
    finally:
        conn.close()
        Path(db_path).unlink()


def test_get_leaderboard_ranks_models_by_weighted_sentiment():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        _create_comment(conn, "c1", "This model is amazing.", "r/chatgpt", 1, 20, 0.9, "positive", 0.9)
        _create_mention(conn, "c1", "ChatGPT")
        _create_comment(conn, "c2", "This model is terrible.", "r/machinelearning", 1, 5, 0.4, "negative", 0.8)
        _create_mention(conn, "c2", "Claude")
        _create_comment(conn, "c3", "Good, but could be faster.", "r/chatgpt", 2, 3, 0.7, "positive", 0.7)
        _create_mention(conn, "c3", "Claude")
        conn.commit()

        leaderboard = get_leaderboard(db_conn=conn, window="30d", config=RankingConfig(min_support=1))
        assert leaderboard[0]["model_name"] == "ChatGPT"
        assert leaderboard[0]["support_count"] == 1
        assert leaderboard[1]["model_name"] == "Claude"
        assert leaderboard[1]["support_count"] == 2
    finally:
        conn.close()
        Path(db_path).unlink()


def test_get_leaderboard_respects_window_filter():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        _create_comment(conn, "c1", "Recent positive comment.", "r/chatgpt", 1, 10, 0.9, "positive", 0.9)
        _create_mention(conn, "c1", "ChatGPT")
        _create_comment(conn, "c2", "Old negative comment.", "r/chatgpt", 40, 10, 0.9, "negative", 0.9)
        _create_mention(conn, "c2", "ChatGPT")
        conn.commit()

        leaderboard_30d = get_leaderboard(db_conn=conn, window="30d", config=RankingConfig(min_support=1))
        assert len(leaderboard_30d) == 1
        assert leaderboard_30d[0]["support_count"] == 1
    finally:
        conn.close()
        Path(db_path).unlink()
