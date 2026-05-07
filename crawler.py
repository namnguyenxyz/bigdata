from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

DEFAULT_SUBREDDITS = ("MachineLearning", "ChatGPT", "LocalLLaMA", "OpenAI", "Claude")


def _safe_name(value: Any) -> str | None:
    if value is None:
        return None
    name = getattr(value, "name", None)
    if name:
        return str(name)
    value_str = str(value).strip()
    return value_str or None


def extract_comment_record(comment: Any) -> dict[str, Any] | None:
    body = getattr(comment, "body", "")
    if not body:
        return None

    subreddit = getattr(getattr(comment, "subreddit", None), "display_name", None)
    if subreddit is None:
        subreddit = getattr(comment, "subreddit_name_prefixed", None)
    if isinstance(subreddit, str) and subreddit.startswith("r/"):
        subreddit = subreddit[2:]

    created_utc = getattr(comment, "created_utc", None)
    if created_utc is None:
        return None

    submission_id = getattr(comment, "link_id", None)
    if isinstance(submission_id, str) and submission_id.startswith("t3_"):
        submission_id = submission_id[3:]

    return {
        "id": str(getattr(comment, "id", "")).strip(),
        "text": str(body).strip(),
        "author": _safe_name(getattr(comment, "author", None)),
        "submission_id": submission_id,
        "subreddit": str(subreddit).strip(),
        "created_utc": int(created_utc),
        "score": int(getattr(comment, "score", 0) or 0),
        "upvote_ratio": getattr(comment, "upvote_ratio", None),
        "is_deleted": str(getattr(comment, "author", "")) == "None",
        "is_archived": bool(getattr(comment, "archived", False)),
    }


def fetch_subreddit_comments(
    reddit: Any,
    subreddit_name: str,
    limit: int = 100,
    request_interval_seconds: float = 1.0,
    batch_size: int = 25,
) -> list[dict[str, Any]]:
    subreddit = reddit.subreddit(subreddit_name)
    records: list[dict[str, Any]] = []

    for index, comment in enumerate(subreddit.comments(limit=limit), start=1):
        record = extract_comment_record(comment)
        if record and record["id"] and record["text"]:
            records.append(record)
        if request_interval_seconds and batch_size > 0 and index % batch_size == 0:
            time.sleep(request_interval_seconds)
        if len(records) >= limit:
            break

    return records


def fetch_all_subreddits(
    reddit: Any,
    subreddit_names: list[str],
    comments_per_sub: int = 100,
    request_interval_seconds: float = 1.0,
) -> tuple[list[dict[str, Any]], float]:
    start = time.perf_counter()
    all_comments: list[dict[str, Any]] = []

    for index, subreddit_name in enumerate(subreddit_names, start=1):
        subreddit_comments = fetch_subreddit_comments(
            reddit,
            subreddit_name,
            limit=comments_per_sub,
            request_interval_seconds=request_interval_seconds,
        )
        all_comments.extend(subreddit_comments)
        if request_interval_seconds and index < len(subreddit_names):
            time.sleep(request_interval_seconds)

    duration_seconds = time.perf_counter() - start
    return all_comments, duration_seconds


def batch_fetch_summary(comments: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for comment in comments:
        subreddit = str(comment.get("subreddit", "unknown"))
        summary[subreddit] = summary.get(subreddit, 0) + 1
    return summary
