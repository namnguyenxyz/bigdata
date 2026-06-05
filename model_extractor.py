from __future__ import annotations

import re
from typing import NamedTuple


class ModelMention(NamedTuple):
    model_name: str
    confidence: float
    raw_text: str | None = None
    position: int | None = None


DEFAULT_MODELS = [
    "GPT-4",
    "GPT-3.5",
    "GPT-3",
    "ChatGPT",
    "GPT",
    "OpenAI API",
    "Claude 3.5",
    "Claude 3",
    "Claude 2",
    "Claude",
    "Llama 3",
    "Llama 2",
    "Llama",
    "Gemini",
    "PaLM",
    "Bard",
    "Mistral 8x7B",
    "Mistral Large",
    "Mistral",
    "Falcon",
    "MPT",
    "T5",
    "BERT",
    "DistilBERT",
    "Alpaca",
    "Vicuna",
    "Cohere",
]


class ModelExtractor:
    def __init__(self, model_names: list[str] | None = None):
        self.model_names = model_names or DEFAULT_MODELS
        self.patterns = self._build_patterns()

    def _build_patterns(self) -> dict[str, re.Pattern]:
        patterns: dict[str, re.Pattern] = {}

        for model in self.model_names:
            escaped = re.escape(model)
            if any(char.isdigit() for char in model):
                flexible = escaped.replace(r"\-", r"[\s\-\.]*").replace(r"\.", r"[\s\-\.]*")
                pattern_str = rf"\b{flexible}\b"
            else:
                pattern_str = rf"\b{escaped}\b"
            patterns[model] = re.compile(pattern_str, re.IGNORECASE)
        return patterns

    def _spans_overlap(self, spans: list[tuple[int, int]], candidate: tuple[int, int]) -> bool:
        start, end = candidate
        return any(not (end <= a or start >= b) for a, b in spans)

    def extract(self, text: str) -> list[ModelMention]:
        mentions: list[ModelMention] = []
        used_spans: list[tuple[int, int]] = []

        for model_name in sorted(self.model_names, key=len, reverse=True):
            pattern = self.patterns[model_name]
            match = pattern.search(text)
            if not match:
                continue

            span = (match.start(), match.end())
            if self._spans_overlap(used_spans, span):
                continue

            mentions.append(
                ModelMention(
                    model_name=model_name,
                    confidence=1.0,
                    raw_text=match.group(0),
                    position=match.start(),
                )
            )
            used_spans.append(span)

        mentions.sort(key=lambda mention: mention.position or 0)
        return mentions


def extract_mentions(text: str, model_names: list[str] | None = None) -> list[ModelMention]:
    extractor = ModelExtractor(model_names)
    return extractor.extract(text)
