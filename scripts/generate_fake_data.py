#!/usr/bin/env python3
"""Generate fake injected Reddit comment dataset for ETL testing."""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

SAMPLE_MODELS = ["GPT-4", "GPT-3.5", "Claude 3", "Llama 2", "Gemini"]
SAMPLE_SUBREDDITS = ["r/MachineLearning", "r/ChatGPT", "r/LocalLLaMA", "r/OpenAI"]


def random_text(model: str | None = None) -> str:
    if model and random.random() < 0.6:
        return f"I think {model} is great!"
    tokens = ["this", "is", "a", "test", "comment", "about", "models", "and", "AI"]
    return " ".join(random.choices(tokens, k=random.randint(5, 15)))


def make_row(i: int):
    model = random.choice(SAMPLE_MODELS + [None, None])
    text = random_text(model)
    now = int(datetime.now(timezone.utc).timestamp()) - random.randint(0, 86400 * 90)
    return {
        "id": f"fake_{i}",
        "text": text,
        "author": f"user{random.randint(1,200)}",
        "submission_id": f"sub_{random.randint(1,100)}",
        "subreddit": random.choice(SAMPLE_SUBREDDITS),
        "created_utc": now,
        "score": random.randint(0, 100),
        "upvote_ratio": round(random.random(), 2),
        "data_hash": f"h{i}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--out", default="data/fake_injected.csv")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [make_row(i) for i in range(args.count)]

    import csv

    with out.open("w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
