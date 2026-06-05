from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from database import DEFAULT_DB_PATH, get_db_connection
from ranking import get_leaderboard, RankingConfig


def get_available_subreddits(db_path: str | Path = DEFAULT_DB_PATH) -> list[str]:
    with get_db_connection(db_path) as connection:
        cursor = connection.execute(
            "SELECT DISTINCT subreddit FROM comments ORDER BY LOWER(subreddit)"
        )
        return [row[0] for row in cursor.fetchall() if row[0]]


def load_leaderboard(
    window: str = "30d",
    subreddit: str | None = None,
    limit: int | None = 10,
    db_path: str | Path = DEFAULT_DB_PATH,
    config: RankingConfig | None = None,
) -> list[dict[str, Any]]:
    config = config or RankingConfig()
    with get_db_connection(db_path) as connection:
        return get_leaderboard(
            db_conn=connection,
            window=window,
            subreddit=subreddit,
            limit=limit,
            config=config,
        )


def build_sentiment_chart_data(leaderboard: list[dict[str, Any]]) -> dict[str, list[int]]:
    return {
        "positive": [item["positive_count"] for item in leaderboard],
        "negative": [item["negative_count"] for item in leaderboard],
        "neutral": [item["neutral_count"] for item in leaderboard],
    }


def build_leaderboard_table(leaderboard: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": rank + 1,
            "model_name": item["model_name"],
            "score": round(item["score"], 4),
            "support_count": item["support_count"],
            "positive_count": item["positive_count"],
            "negative_count": item["negative_count"],
            "neutral_count": item["neutral_count"],
        }
        for rank, item in enumerate(leaderboard)
    ]
