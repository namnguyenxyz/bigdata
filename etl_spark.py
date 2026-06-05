from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from model_extractor import extract_mentions
from sentiment_analyzer import analyze_sentiment
from sarcasm_detector import detect_sarcasm


try:
    from pyspark.sql import SparkSession, functions as F, types as T
    SPARK_AVAILABLE = True
except Exception:
    SPARK_AVAILABLE = False


def process_with_spark(input_path: str, output_path: str | None, fmt: str, write_db: bool) -> None:
    spark = SparkSession.builder.appName("etl_spark").getOrCreate()

    if fmt == "parquet":
        df = spark.read.parquet(input_path)
    else:
        df = spark.read.option("header", "true").csv(input_path)

    # Define UDFs
    @F.udf(returnType=T.StringType())
    def sentiment_label_udf(text: str) -> str:
        try:
            return analyze_sentiment(text).label
        except Exception:
            return None

    @F.udf(returnType=T.DoubleType())
    def sentiment_score_udf(text: str) -> float:
        try:
            return float(analyze_sentiment(text).score)
        except Exception:
            return None

    @F.udf(returnType=T.BooleanType())
    def sarcasm_detected_udf(text: str) -> bool:
        try:
            return bool(detect_sarcasm(text).detected)
        except Exception:
            return False

    @F.udf(returnType=T.StringType())
    def sarcasm_patterns_udf(text: str) -> str:
        try:
            patterns = detect_sarcasm(text).patterns_matched
            return json.dumps(patterns)
        except Exception:
            return None

    processed = (
        df.withColumn("sentiment_label", sentiment_label_udf(F.col("text")))
        .withColumn("sentiment_score", sentiment_score_udf(F.col("text")))
        .withColumn("sarcasm_detected", sarcasm_detected_udf(F.col("text")))
        .withColumn("sarcasm_patterns", sarcasm_patterns_udf(F.col("text")))
    )

    if output_path:
        processed.write.mode("overwrite").parquet(output_path)

    if write_db:
        # collect to driver and write to SQLite using existing helpers
        rows = processed.select("id", "text", "sentiment_label", "sentiment_score", "sarcasm_detected", "sarcasm_patterns").collect()
        from sentiment_storage import insert_sentiment_result
        from database import get_db_connection, init_database

        init_database()  # ensure schema
        conn = get_db_connection()
        with conn:
            for r in rows:
                comment_id = r["id"]
                text = r["text"]
                sentiment_label = r["sentiment_label"]
                sentiment_score = float(r["sentiment_score"]) if r["sentiment_score"] is not None else 0.0
                sarcasm_detected = bool(r["sarcasm_detected"]) if r["sarcasm_detected"] is not None else False
                sarcasm_patterns = json.loads(r["sarcasm_patterns"]) if r["sarcasm_patterns"] else None
                insert_sentiment_result(
                    comment_id=comment_id,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score,
                    sarcasm_detected=sarcasm_detected,
                    sarcasm_patterns=sarcasm_patterns,
                    db_conn=conn,
                )

                # insert model mentions
                mentions = extract_mentions(text or "")
                if mentions:
                    for m in mentions:
                        conn.execute(
                            "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
                            (comment_id, m.model_name, float(m.confidence), m.raw_text),
                        )

        conn.commit()

    spark.stop()


def process_with_pandas(input_path: str, output_path: str | None, fmt: str, write_db: bool) -> None:
    import pandas as pd
    from sentiment_storage import insert_sentiment_result
    from database import init_database, get_db_connection

    if fmt == "parquet":
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    # apply functions
    df["sentiment"] = df["text"].apply(lambda t: analyze_sentiment(t))
    df["sentiment_label"] = df["sentiment"].apply(lambda s: s.label)
    df["sentiment_score"] = df["sentiment"].apply(lambda s: float(s.score))
    df["sarcasm"] = df["text"].apply(lambda t: detect_sarcasm(t))
    df["sarcasm_detected"] = df["sarcasm"].apply(lambda s: bool(s.detected))
    df["sarcasm_patterns"] = df["sarcasm"].apply(lambda s: json.dumps(s.patterns_matched))

    if output_path:
        # drop complex object columns before writing (pyarrow cannot serialize namedtuples)
        df_out = df.drop(columns=[c for c in ("sentiment", "sarcasm") if c in df.columns])
        df_out.to_parquet(output_path, index=False)

    if write_db:
        init_database()
        conn = get_db_connection()
        with conn:
            for _, row in df.iterrows():
                # Ensure comment exists (insert if missing)
                conn.execute(
                    "INSERT OR IGNORE INTO comments (id, text, author, submission_id, subreddit, created_utc, score, upvote_ratio, data_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        row.get("id"),
                        row.get("text"),
                        row.get("author"),
                        row.get("submission_id"),
                        row.get("subreddit"),
                        int(row.get("created_utc") or 0),
                        int(row.get("score") or 0),
                        float(row.get("upvote_ratio") or 0.0),
                        row.get("data_hash") or None,
                    ),
                )

                insert_sentiment_result(
                    comment_id=row["id"],
                    sentiment_label=row["sentiment_label"],
                    sentiment_score=float(row["sentiment_score"]),
                    sarcasm_detected=bool(row["sarcasm_detected"]),
                    sarcasm_patterns=json.loads(row["sarcasm_patterns"]) if row["sarcasm_patterns"] else None,
                    db_conn=conn,
                )
                mentions = extract_mentions(row["text"] or "")
                for m in mentions:
                    conn.execute(
                        "INSERT INTO model_mentions (comment_id, model_name, confidence, extracted_text) VALUES (?, ?, ?, ?)",
                        (row["id"], m.model_name, float(m.confidence), m.raw_text),
                    )
        conn.commit()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ETL pipeline using Spark (with pandas fallback).")
    parser.add_argument("--input", required=True, help="Input path (parquet or csv)")
    parser.add_argument("--format", choices=["parquet", "csv"], default="parquet")
    parser.add_argument("--output", help="Optional output path for processed data (parquet)")
    parser.add_argument("--write-db", action="store_true", help="Write sentiment and mentions to SQLite DB")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if SPARK_AVAILABLE:
        process_with_spark(args.input, args.output, args.format, args.write_db)
    else:
        print("PySpark not available — falling back to pandas processing.")
        process_with_pandas(args.input, args.output, args.format, args.write_db)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
