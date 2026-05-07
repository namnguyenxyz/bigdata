from __future__ import annotations

import argparse
import os
from typing import Any

from crawler import DEFAULT_SUBREDDITS, fetch_subreddit_comments
from database import DEFAULT_DB_PATH, init_database
from reddit_auth import get_reddit_client
from storage import log_collection_run, store_comments


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase 1 Reddit data collection batch job.")
    parser.add_argument("--db-path", default=None, help="Override the database path")
    parser.add_argument("--subreddits", default=None, help="Comma-separated list of subreddits")
    parser.add_argument("--comments-per-subreddit", type=int, default=None, help="Number of comments to fetch per subreddit")
    parser.add_argument("--request-interval-seconds", type=float, default=None, help="Delay between request batches")
    return parser.parse_args(argv)


def load_runtime_config(args: argparse.Namespace) -> dict[str, Any]:
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None

    if load_dotenv is not None:
        load_dotenv()

    db_path = args.db_path or os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))
    subreddit_value = args.subreddits or os.getenv("TARGET_SUBREDDITS", ",".join(DEFAULT_SUBREDDITS))
    subreddits = [sub.strip() for sub in subreddit_value.split(",") if sub.strip()]
    comments_per_subreddit = args.comments_per_subreddit or int(os.getenv("COMMENTS_PER_SUBREDDIT", "100"))
    request_interval_seconds = args.request_interval_seconds if args.request_interval_seconds is not None else float(
        os.getenv("REQUEST_INTERVAL_SECONDS", "1.0")
    )
    retry_max_attempts = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
    retry_base_delay_seconds = float(os.getenv("RETRY_BASE_DELAY_SECONDS", "2"))

    return {
        "db_path": db_path,
        "subreddits": subreddits,
        "comments_per_subreddit": comments_per_subreddit,
        "request_interval_seconds": request_interval_seconds,
        "retry_max_attempts": retry_max_attempts,
        "retry_base_delay_seconds": retry_base_delay_seconds,
    }


def fetch_comments_with_retry(
    reddit: Any,
    subreddit: str,
    comments_per_subreddit: int,
    request_interval_seconds: float,
    retry_max_attempts: int,
    retry_base_delay_seconds: float,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None

    for attempt in range(1, retry_max_attempts + 1):
        try:
            return fetch_subreddit_comments(
                reddit,
                subreddit,
                limit=comments_per_subreddit,
                request_interval_seconds=request_interval_seconds,
            )
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            last_error = exc
            if attempt >= retry_max_attempts:
                break
            delay_seconds = retry_base_delay_seconds * (2 ** (attempt - 1))
            if delay_seconds > 0:
                import time

                time.sleep(delay_seconds)

    if last_error is not None:
        raise last_error
    return []


def run_batch_job(
    config: dict[str, Any] | None = None,
    reddit_client: Any | None = None,
) -> dict[str, Any]:
    if config is None:
        config = load_runtime_config(parse_arguments([]))

    db_path = config["db_path"]
    subreddits = config["subreddits"]
    comments_per_subreddit = config["comments_per_subreddit"]
    request_interval_seconds = config["request_interval_seconds"]
    retry_max_attempts = config["retry_max_attempts"]
    retry_base_delay_seconds = config["retry_base_delay_seconds"]

    init_database(db_path)
    reddit = reddit_client or get_reddit_client()

    batch_summary: dict[str, Any] = {
        "total_fetched": 0,
        "total_inserted": 0,
        "total_duplicates": 0,
        "total_errors": 0,
        "subreddits": {},
    }

    for subreddit in subreddits:
        try:
            comments = fetch_comments_with_retry(
                reddit,
                subreddit,
                comments_per_subreddit,
                request_interval_seconds,
                retry_max_attempts,
                retry_base_delay_seconds,
            )
            result = store_comments(db_path, comments)
            log_collection_run(
                db_path,
                subreddit,
                {
                    "comments_fetched": len(comments),
                    "comments_new": result["inserted"],
                    "comments_duplicate": result["duplicates"],
                    "errors": result["errors"],
                    "duration_seconds": 0.0,
                },
            )

            batch_summary["total_fetched"] += len(comments)
            batch_summary["total_inserted"] += result["inserted"]
            batch_summary["total_duplicates"] += result["duplicates"]
            batch_summary["total_errors"] += result["errors"]
            batch_summary["subreddits"][subreddit] = result
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            batch_summary["total_errors"] += 1
            batch_summary["subreddits"][subreddit] = {"inserted": 0, "duplicates": 0, "errors": 1}
            log_collection_run(
                db_path,
                subreddit,
                {
                    "comments_fetched": 0,
                    "comments_new": 0,
                    "comments_duplicate": 0,
                    "errors": str(exc),
                    "duration_seconds": 0.0,
                },
            )

    return batch_summary


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    config = load_runtime_config(args)
    summary = run_batch_job(config)
    print("Collection batch completed successfully")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
