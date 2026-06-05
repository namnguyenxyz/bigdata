from __future__ import annotations

import logging
from typing import NamedTuple

from model_extractor import ModelExtractor, ModelMention
from sentiment_analyzer import SentimentAnalyzer, SentimentResult
from sarcasm_detector import SarcasmDetector, SarcasmDetection

logger = logging.getLogger(__name__)


class NLPResult(NamedTuple):
    comment_id: str
    text: str
    sentiment_label: str
    sentiment_score: float
    model_mentions: list[ModelMention]
    sarcasm_detected: bool
    sarcasm_patterns: list[str]


class NLPPipeline:
    def __init__(
        self,
        model_names: list[str] | None = None,
        sarcasm_patterns: list[tuple[str, str]] | None = None,
    ):
        self.extractor = ModelExtractor(model_names)
        self.analyzer = SentimentAnalyzer()
        self.sarcasm_detector = SarcasmDetector(sarcasm_patterns)
        logger.info("NLP pipeline initialized")

    def process(self, comment_id: str, comment_text: str) -> NLPResult:
        if not isinstance(comment_text, str) or not comment_text.strip():
            raise ValueError("Comment text cannot be empty")

        mentions = self.extractor.extract(comment_text)
        sentiment = self.analyzer.analyze(comment_text)
        sarcasm = self.sarcasm_detector.detect(comment_text)

        sentiment_label = sentiment.label
        if sarcasm.detected:
            if sentiment_label == "positive":
                sentiment_label = "negative"
            elif sentiment_label == "negative":
                sentiment_label = "positive"

        logger.debug(
            "Processed %s: sentiment=%s sarcasm=%s models=%s",
            comment_id,
            sentiment_label,
            sarcasm.detected,
            len(mentions),
        )

        return NLPResult(
            comment_id=comment_id,
            text=comment_text,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment.score,
            model_mentions=mentions,
            sarcasm_detected=sarcasm.detected,
            sarcasm_patterns=sarcasm.patterns_matched,
        )

    def process_batch(self, comments: list[dict[str, str]]) -> list[NLPResult]:
        results: list[NLPResult] = []
        for comment in comments:
            try:
                results.append(self.process(comment["id"], comment["text"]))
            except Exception as exc:
                logger.error("Error processing %s: %s", comment.get("id"), exc)
        return results
