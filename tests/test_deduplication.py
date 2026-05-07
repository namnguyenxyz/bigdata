from database import init_database
from storage import compute_data_hash, store_comments


def test_compute_data_hash_is_stable():
    first = compute_data_hash("user", "This is a test comment", 1_700_000_000, "abc", "MachineLearning")
    second = compute_data_hash("user", "This is a test comment", 1_700_000_000, "abc", "MachineLearning")
    third = compute_data_hash("user", "Different text", 1_700_000_000, "abc", "MachineLearning")

    assert first == second
    assert first != third


def test_store_comments_deduplicates_on_second_insert(tmp_path):
    db_path = tmp_path / "comments.db"
    init_database(db_path)

    comments = [
        {
            "id": "c1",
            "text": "This is a sufficiently long test comment.",
            "author": "user1",
            "subreddit": "MachineLearning",
            "created_utc": 1_700_000_000,
            "score": 10,
        },
        {
            "id": "c2",
            "text": "This is a sufficiently long test comment.",
            "author": "user1",
            "subreddit": "MachineLearning",
            "created_utc": 1_700_000_000,
            "score": 10,
        },
    ]

    first_result = store_comments(str(db_path), comments)
    second_result = store_comments(str(db_path), comments)

    assert first_result["inserted"] == 1
    assert first_result["duplicates"] == 1
    assert second_result["inserted"] == 0
    assert second_result["duplicates"] == 2
