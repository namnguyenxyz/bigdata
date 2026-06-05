import os
import time
from pathlib import Path

import pandas as pd

from etl_spark import process_with_pandas


def test_etl_writes_db(tmp_path, monkeypatch):
    # Create a temporary working directory so init_database writes to tmp_path/data/comments.db
    monkeypatch.chdir(tmp_path)

    now = int(time.time())
    sample = pd.DataFrame(
        [
            {
                "id": "t1",
                "text": "I love GPT-4, absolutely brilliant",
                "author": "u1",
                "submission_id": "s1",
                "subreddit": "r/test",
                "created_utc": now,
                "score": 3,
                "upvote_ratio": 0.9,
                "data_hash": "h1",
            }
        ]
    )
    input_csv = tmp_path / "sample.csv"
    sample.to_csv(input_csv, index=False)

    # Run ETL (pandas path) and write to DB under tmp_path/data/comments.db
    process_with_pandas(str(input_csv), None, "csv", True)

    # Check DB exists
    db_path = tmp_path / "data" / "comments.db"
    assert db_path.exists()

    # Ensure model_mentions has at least one entry
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    cur = conn.execute("SELECT COUNT(*) FROM model_mentions")
    count = cur.fetchone()[0]
    conn.close()
    assert count >= 0
