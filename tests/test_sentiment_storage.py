import sqlite3
import tempfile
from pathlib import Path

from database import init_database
from sentiment_storage import get_sentiment_stats, get_unprocessed_comments, insert_sentiment_result


def test_sentiment_storage_insert_and_stats():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        init_database(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            INSERT INTO comments (id, text, author, subreddit, created_utc, data_hash, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("c1", "This is a test comment.", "tester", "testsub", 1700000000, "hash1", 10),
        )
        conn.commit()

        assert get_unprocessed_comments(db_conn=conn)

        success = insert_sentiment_result(
            comment_id="c1",
            sentiment_label="positive",
            sentiment_score=0.85,
            sarcasm_detected=False,
            sarcasm_patterns=[],
            db_conn=conn,
        )
        assert success is True

        stats = get_sentiment_stats(db_conn=conn)
        assert "positive" in stats
        assert stats["positive"]["count"] == 1
        assert stats["positive"]["sarcasm_count"] == 0
    finally:
        conn.close()
        Path(db_path).unlink()
