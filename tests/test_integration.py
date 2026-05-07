from batch_job import run_batch_job


class FakeAuthor:
    def __init__(self, name):
        self.name = name


class FakeSubredditInfo:
    def __init__(self, display_name):
        self.display_name = display_name


class FakeComment:
    def __init__(self, comment_id, body, subreddit, author_name="user", score=5):
        self.id = comment_id
        self.body = body
        self.author = FakeAuthor(author_name)
        self.subreddit = FakeSubredditInfo(subreddit)
        self.created_utc = 1_700_000_000
        self.score = score
        self.upvote_ratio = 0.9
        self.link_id = "t3_submission123"
        self.archived = False


class FakeSubreddit:
    def __init__(self, comments):
        self._comments = comments

    def comments(self, limit=None):
        for comment in self._comments[:limit]:
            yield comment


class FakeReddit:
    def __init__(self):
        self.subreddit_map = {
            "MachineLearning": FakeSubreddit([FakeComment("c1", "This is a valid comment body.", "MachineLearning")]),
            "ChatGPT": FakeSubreddit([FakeComment("c2", "This is another valid comment body.", "ChatGPT")]),
        }

    def subreddit(self, name):
        return self.subreddit_map[name]


def test_run_batch_job_offline(tmp_path, monkeypatch):
    fake_reddit = FakeReddit()
    monkeypatch.setattr("batch_job.get_reddit_client", lambda: fake_reddit)

    config = {
        "db_path": str(tmp_path / "comments.db"),
        "subreddits": ["MachineLearning", "ChatGPT"],
        "comments_per_subreddit": 1,
        "request_interval_seconds": 0,
        "retry_max_attempts": 1,
        "retry_base_delay_seconds": 0,
    }

    summary = run_batch_job(config)
    assert summary["total_fetched"] == 2
    assert summary["total_inserted"] == 2
    assert summary["total_duplicates"] == 0
    assert summary["subreddits"]["MachineLearning"]["inserted"] == 1
    assert summary["subreddits"]["ChatGPT"]["inserted"] == 1
