from __future__ import annotations

import argparse
import math
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from database import DEFAULT_DB_PATH, get_db_connection, init_database

DEFAULT_SUBREDDIT_WEIGHTS = {
    "r/machinelearning": 1.0,
    "r/chatgpt": 1.0,
    "r/localllama": 1.0,
}

WINDOW_DAY_COUNTS = {
    "30d": 30,
    "all": None,
}


@dataclass
class RankingConfig:
    min_support: int = 1
    engagement_ratio_weight: float = 0.5
    engagement_score_weight: float = 0.2
    subreddit_weights: dict[str, float] = field(default_factory=lambda: DEFAULT_SUBREDDIT_WEIGHTS.copy())
    top_supporting_comments: int = 3

    def subreddit_weight(self, subreddit: str | None) -> float:
        if subreddit is None:
            return 1.0
        return float(self.subreddit_weights.get(subreddit.lower(), 1.0))


def sentiment_value(label: str) -> int:
    normalized = label.strip().lower()
    if normalized == "positive":
        return 1
    if normalized == "negative":
        return -1
    if normalized == "neutral":
        return 0
    raise ValueError(f"Unexpected sentiment label: {label}")


def compute_engagement_weight(
    score: int | None,
    upvote_ratio: float | None,
    ratio_weight: float = 0.5,
    score_weight: float = 0.2,
) -> float:
    ratio = float(upvote_ratio) if upvote_ratio is not None else 0.0
    comment_score = float(score) if score is not None else 0.0
    return 1.0 + ratio_weight * ratio + score_weight * math.log1p(abs(comment_score))


def compute_comment_contribution(row: sqlite3.Row, config: RankingConfig) -> dict[str, Any]:
    sentiment_label = row["sentiment_label"]
    sentiment_score = float(row["sentiment_score"])
    polarity = sentiment_value(sentiment_label)
    base_sentiment = polarity * sentiment_score
    engagement = compute_engagement_weight(
        score=row["comment_score"],
        upvote_ratio=row["upvote_ratio"],
        ratio_weight=config.engagement_ratio_weight,
        score_weight=config.engagement_score_weight,
    )
    subreddit_weight = config.subreddit_weight(row["subreddit"])
    weighted_contribution = base_sentiment * engagement * subreddit_weight

    return {
        "comment_id": row["comment_id"],
        "model_name": row["model_name"],
        "comment_text": row["text"],
        "subreddit": row["subreddit"],
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "base_sentiment": base_sentiment,
        "engagement_weight": engagement,
        "subreddit_weight": subreddit_weight,
        "contribution": weighted_contribution,
        "supporting_score": abs(weighted_contribution),
    }


def _build_window_clause(window: str) -> tuple[str, list[Any]]:
    if window not in WINDOW_DAY_COUNTS:
        raise ValueError(f"Unsupported window: {window}")
    day_count = WINDOW_DAY_COUNTS[window]
    if day_count is None:
        return "", []

    cutoff = int(datetime.now(timezone.utc).timestamp()) - day_count * 86400
    return "AND c.created_utc >= ?", [cutoff]


def _row_to_mapping(cursor: sqlite3.Cursor, row: sqlite3.Row | tuple[Any, ...]) -> dict[str, Any]:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    columns = [col[0] for col in cursor.description or []]
    return dict(zip(columns, row))


def get_ranked_model_rows(
    db_conn: sqlite3.Connection | None = None,
    window: str = "30d",
    subreddit: str | None = None,
    config: RankingConfig | None = None,
) -> list[dict[str, Any]]:
    config = config or RankingConfig()
    connection = db_conn or get_db_connection(DEFAULT_DB_PATH)
    try:
        window_clause, params = _build_window_clause(window)
        query = f"""
            SELECT
                mm.model_name,
                c.id AS comment_id,
                c.text,
                c.subreddit,
                c.created_utc,
                c.score AS comment_score,
                c.upvote_ratio,
                c.sentiment_label,
                c.sentiment_score
            FROM model_mentions mm
            JOIN comments c ON c.id = mm.comment_id
            WHERE c.sentiment_label IS NOT NULL
            {window_clause}
        """
        if subreddit:
            query += " AND LOWER(c.subreddit) = LOWER(?)"
            params.append(subreddit)

        cursor = connection.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [compute_comment_contribution(_row_to_mapping(cursor, row), config) for row in rows]
    finally:
        if db_conn is None:
            connection.close()


def aggregate_model_scores(
    contributions: list[dict[str, Any]], config: RankingConfig | None = None
) -> list[dict[str, Any]]:
    config = config or RankingConfig()
    models: dict[str, dict[str, Any]] = {}
    for contribution in contributions:
        model = contribution["model_name"]
        bucket = models.setdefault(
            model,
            {
                "model_name": model,
                "contributions": [],
                "support_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "sum_contribution": 0.0,
                "total_weight": 0.0,
            },
        )

        bucket["contributions"].append(contribution)
        bucket["support_count"] += 1
        if contribution["base_sentiment"] > 0:
            bucket["positive_count"] += 1
        elif contribution["base_sentiment"] < 0:
            bucket["negative_count"] += 1
        else:
            bucket["neutral_count"] += 1
        bucket["sum_contribution"] += contribution["contribution"]
        bucket["total_weight"] += contribution["engagement_weight"] * contribution["subreddit_weight"]

    ranked_models: list[dict[str, Any]] = []
    for model_name, bucket in models.items():
        if bucket["support_count"] < config.min_support:
            continue

        score = bucket["sum_contribution"] / bucket["total_weight"] if bucket["total_weight"] > 0 else 0.0
        ranked_models.append(
            {
                "model_name": model_name,
                "score": score,
                "support_count": bucket["support_count"],
                "positive_count": bucket["positive_count"],
                "negative_count": bucket["negative_count"],
                "neutral_count": bucket["neutral_count"],
                "sum_contribution": bucket["sum_contribution"],
                "total_weight": bucket["total_weight"],
                "top_supporting_comments": sorted(
                    bucket["contributions"],
                    key=lambda item: item["supporting_score"],
                    reverse=True,
                )[: config.top_supporting_comments],
            }
        )

    ranked_models.sort(key=lambda item: item["score"], reverse=True)
    return ranked_models


def get_leaderboard(
    db_conn: sqlite3.Connection | None = None,
    window: str = "30d",
    subreddit: str | None = None,
    limit: int | None = None,
    config: RankingConfig | None = None,
) -> list[dict[str, Any]]:
    config = config or RankingConfig()
    all_rows = get_ranked_model_rows(db_conn=db_conn, window=window, subreddit=subreddit, config=config)
    leaderboard = aggregate_model_scores(all_rows, config=config)
    if limit is not None:
        return leaderboard[:limit]
    return leaderboard


def print_leaderboard(leaderboard: list[dict[str, Any]]) -> None:
    if not leaderboard:
        print("No ranked models available for the selected window and filters.")
        return

    for rank, model in enumerate(leaderboard, start=1):
        print(f"#{rank}: {model['model_name']} — score: {model['score']:.4f} ({model['support_count']} mentions)")
        print(f"  positive: {model['positive_count']}, negative: {model['negative_count']}, neutral: {model['neutral_count']}")
        for comment in model["top_supporting_comments"]:
            print(
                f"    - [{comment['subreddit']}] {comment['sentiment_label']} "
                f"score={comment['sentiment_score']:.2f} contribution={comment['contribution']:.4f} "
                f"{comment['comment_text'][:80]!r}"
            )
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a ranked leaderboard for AI models.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite database path")
    parser.add_argument("--window", default="30d", choices=list(WINDOW_DAY_COUNTS), help="Time window for leaderboard")
    parser.add_argument("--subreddit", help="Filter leaderboard by subreddit")
    parser.add_argument("--limit", type=int, help="Maximum number of models to return")
    parser.add_argument("--min-support", type=int, default=1, help="Minimum number of comments required to rank a model")
    args = parser.parse_args(argv if argv is not None else None)

    init_database(args.db_path)
    with get_db_connection(args.db_path) as connection:
        config = RankingConfig(min_support=args.min_support)
        leaderboard = get_leaderboard(
            db_conn=connection,
            window=args.window,
            subreddit=args.subreddit,
            limit=args.limit,
            config=config,
        )

    print_leaderboard(leaderboard)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
