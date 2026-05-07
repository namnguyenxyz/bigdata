import sqlite3

from database import init_database


def test_schema_exists(tmp_path):
    db_path = tmp_path / "comments.db"
    init_database(db_path)

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert {"comments", "model_mentions", "collection_log"}.issubset(tables)

    cursor.execute("PRAGMA table_info(comments)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {"id", "text", "author", "subreddit", "created_utc", "data_hash", "score"}
    assert expected.issubset(columns)

    cursor.execute("PRAGMA journal_mode")
    assert cursor.fetchone()[0].lower() == "wal"

    connection.close()
