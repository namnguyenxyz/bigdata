from storage import validate_comment


def test_validate_comment_accepts_valid_payload():
    assert validate_comment(
        {
            "id": "c1",
            "text": "This is a valid comment body.",
            "author": "user1",
            "subreddit": "ChatGPT",
            "created_utc": 1_700_000_000,
            "score": 3,
        }
    )


def test_validate_comment_rejects_missing_fields():
    assert not validate_comment({"text": "This is a valid comment body.", "subreddit": "ChatGPT", "created_utc": 1_700_000_000})
    assert not validate_comment({"id": "c1", "text": "short", "subreddit": "ChatGPT", "created_utc": 1_700_000_000})
    assert not validate_comment({"id": "c1", "text": "This is a valid comment body.", "subreddit": "", "created_utc": 1_700_000_000})
