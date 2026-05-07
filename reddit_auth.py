from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RedditCredentials:
    client_id: str
    client_secret: str
    user_agent: str


class RedditAuthError(RuntimeError):
    """Raised when the Reddit client cannot be constructed or authenticated."""


def load_credentials() -> RedditCredentials:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:  # pragma: no cover - dependency error path
        raise RedditAuthError(
            "python-dotenv is required to load Reddit credentials. Install dependencies first."
        ) from exc

    load_dotenv()

    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    user_agent = os.getenv("REDDIT_USER_AGENT", "").strip()

    missing = [
        name
        for name, value in {
            "REDDIT_CLIENT_ID": client_id,
            "REDDIT_CLIENT_SECRET": client_secret,
            "REDDIT_USER_AGENT": user_agent,
        }.items()
        if not value
    ]
    if missing:
        raise RedditAuthError(f"Missing required Reddit credentials: {', '.join(missing)}")

    return RedditCredentials(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def get_reddit_client() -> Any:
    try:
        import praw
    except ImportError as exc:  # pragma: no cover - dependency error path
        raise RedditAuthError(
            "praw is required to access Reddit. Install dependencies with pip install -r requirements.txt."
        ) from exc

    credentials = load_credentials()
    return praw.Reddit(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        user_agent=credentials.user_agent,
    )


def test_connection() -> Any:
    reddit = get_reddit_client()
    user = reddit.user.me()
    if user is None:
        raise RedditAuthError("Authentication succeeded but Reddit returned no user identity.")
    print(f"Authenticated as: {user.name}")
    return reddit
