from __future__ import annotations

import re
from typing import NamedTuple


class SarcasmDetection(NamedTuple):
    detected: bool
    patterns_matched: list[str]


SARCASM_PATTERNS: list[tuple[str, str]] = [
    (r"\byeah\s+right\b", "yeah-right"),
    (r"\boh\s+(?:great|wonderful|perfect)\b", "oh-exclamation"),
    (r"\bsure\s+(?:buddy|jan|thing|boss)\b", "sure-buddy"),
    (r"\bjust\s+wonderful\b", "just-wonderful"),
    (r"\bso\s+helpful\b", "so-helpful"),
    (r"\bi[\'m]*\s+sure\b", "im-sure"),
    (r"\bobviously\b", "obviously"),
    (r"[?!]{2,}", "multiple-punctuation"),
    (r"\bright\?\s*$", "right-question-end"),
    (r"\bgreat\s+idea\b", "great-idea-sarcasm"),
]


class SarcasmDetector:
    def __init__(self, patterns: list[tuple[str, str]] | None = None):
        self.patterns = patterns or SARCASM_PATTERNS
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> list[tuple[str, re.Pattern]]:
        compiled: list[tuple[str, re.Pattern]] = []
        for pattern_str, pattern_name in self.patterns:
            compiled.append((pattern_name, re.compile(pattern_str, re.IGNORECASE)))
        return compiled

    def detect(self, text: str) -> SarcasmDetection:
        if not isinstance(text, str):
            return SarcasmDetection(detected=False, patterns_matched=[])

        matched: list[str] = []
        for pattern_name, compiled in self.compiled_patterns:
            if compiled.search(text):
                matched.append(pattern_name)

        return SarcasmDetection(detected=bool(matched), patterns_matched=matched)


def detect_sarcasm(text: str, patterns: list[tuple[str, str]] | None = None) -> SarcasmDetection:
    return SarcasmDetector(patterns).detect(text)
