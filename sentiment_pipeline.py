from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone

from database import DEFAULT_DB_PATH, get_db_connection, init_database
from nlp_pipeline import NLPPipeline
from sentiment_storage import get_sentiment_stats, get_unprocessed_comments, insert_sentiment_result

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def run_sentiment_pipeline(batch_size: int = 500, limit: int | None = None, db_path: str | None = None) -> dict[str, object]:
    database_path = db_path or str(DEFAULT_DB_PATH)
    init_database(database_path)
    pipeline = NLPPipeline()
    connection = get_db_connection(database_path)

    total_processed = 0
    total_failed = 0
    start_time = time.time()

    try:
        while True:
            comments = get_unprocessed_comments(limit=batch_size, db_conn=connection)
            if not comments:
                break
            if limit is not None and total_processed >= limit:
                break

            if limit is not None and total_processed + len(comments) > limit:
                comments = comments[: max(0, limit - total_processed) ]

            results = pipeline.process_batch([
                {"id": comment["id"], "text": comment["text"]}
                for comment in comments
            ])

            for result in results:
                success = insert_sentiment_result(
                    comment_id=result.comment_id,
                    sentiment_label=result.sentiment_label,
                    sentiment_score=result.sentiment_score,
                    sarcasm_detected=result.sarcasm_detected,
                    sarcasm_patterns=result.sarcasm_patterns,
                    db_conn=connection,
                )
                if success:
                    total_processed += 1
                else:
                    total_failed += 1

            connection.commit()

    finally:
        connection.close()

    duration = time.time() - start_time
    stats_conn = get_db_connection(database_path)
    try:
        stats = get_sentiment_stats(db_conn=stats_conn)
    finally:
        stats_conn.close()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_processed": total_processed,
        "total_failed": total_failed,
        "duration_seconds": duration,
        "comments_per_second": total_processed / duration if duration > 0 else 0.0,
        "sentiment_distribution": stats,
    }


def print_summary(summary: dict[str, object]) -> None:
    print("\n" + "=" * 60)
    print("SENTIMENT PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {summary['timestamp']}")
    print(f"Total processed: {summary['total_processed']}")
    print(f"Total failed: {summary['total_failed']}")
    print(f"Duration: {summary['duration_seconds']:.2f}s")
    print(f"Rate: {summary['comments_per_second']:.1f} comments/sec")
    print("\nSentiment Distribution:")
    for label, values in summary["sentiment_distribution"].items():
        print(
            f"  {label}: {values['count']} (avg confidence: {values['avg_confidence']:.2f}, sarcasm: {values['sarcasm_count']})"
        )
    print("=" * 60 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run sentiment analysis on Reddit comments.")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger.info("Starting sentiment pipeline")

    try:
        summary = run_sentiment_pipeline(
            batch_size=args.batch_size,
            limit=args.limit,
            db_path=args.db_path,
        )
        print_summary(summary)
        return 0 if summary["total_failed"] == 0 else 1
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
