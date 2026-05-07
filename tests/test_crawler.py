from crawler import fetch_all_subreddits, fetch_subreddit_comments


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
    def __init__(self, name, comments):
        self.name = name
        self._comments = comments

    def comments(self, limit=None):
        for comment in self._comments[:limit]:
            yield comment


class FakeReddit:
    def __init__(self, subreddit_map):
        self.subreddit_map = subreddit_map

    def subreddit(self, name):
        return self.subreddit_map[name]


def test_fetch_subreddit_comments_transforms_comments():
    reddit = FakeReddit(
        {
            "MachineLearning": FakeSubreddit(
                "MachineLearning",
                [FakeComment("c1", "This is a valid comment body.", "MachineLearning") for _ in range(3)],
            )
        }
    )

    comments = fetch_subreddit_comments(reddit, "MachineLearning", limit=3, request_interval_seconds=0)
    assert len(comments) == 3
    assert comments[0]["subreddit"] == "MachineLearning"
    assert comments[0]["submission_id"] == "submission123"


def test_fetch_all_subreddits_collects_multiple_sources():
    reddit = FakeReddit(
        {
            "MachineLearning": FakeSubreddit(
                "MachineLearning",
                [FakeComment("c1", "This is a valid comment body.", "MachineLearning")],
            ),
            "ChatGPT": FakeSubreddit(
                "ChatGPT",
                [FakeComment("c2", "This is another valid comment body.", "ChatGPT")],
            ),
        }
    )

    comments, duration = fetch_all_subreddits(reddit, ["MachineLearning", "ChatGPT"], comments_per_sub=1, request_interval_seconds=0)
    assert len(comments) == 2
    assert duration >= 0
