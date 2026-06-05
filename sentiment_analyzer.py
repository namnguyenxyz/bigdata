from __future__ import annotations

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import NamedTuple

POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05


class SentimentResult(NamedTuple):
    label: str
    score: float
    raw_compound: float


class SentimentAnalyzer:
    def __init__(self):
        try:
            self.sia = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
            self.sia = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> SentimentResult:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")

        scores = self.sia.polarity_scores(text)
        compound = float(scores["compound"])

        if compound >= POSITIVE_THRESHOLD:
            label = "positive"
        elif compound <= NEGATIVE_THRESHOLD:
            label = "negative"
        else:
            label = "neutral"

        return SentimentResult(
            label=label,
            score=abs(compound),
            raw_compound=compound,
        )


def analyze_sentiment(text: str) -> SentimentResult:
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(text)
