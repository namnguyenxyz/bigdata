import json

import pytest

from nlp_pipeline import NLPPipeline


def load_manual_test_set(path: str = "manual_test_set.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


class TestAccuracyValidation:
    @pytest.fixture(scope="module")
    def pipeline(self):
        return NLPPipeline()

    @pytest.fixture(scope="module")
    def test_set(self):
        return load_manual_test_set()

    def test_sentiment_accuracy(self, pipeline, test_set):
        correct = 0
        total = len(test_set)
        failures = []

        for test_case in test_set:
            result = pipeline.process(test_case["id"], test_case["text"])
            if result.sentiment_label == test_case["expected_sentiment"]:
                correct += 1
            else:
                failures.append(
                    {
                        "id": test_case["id"],
                        "expected": test_case["expected_sentiment"],
                        "got": result.sentiment_label,
                        "text": test_case["text"],
                    }
                )

        accuracy = correct / total
        print(f"\nSentiment Accuracy: {accuracy:.1%} ({correct}/{total})")

        if failures:
            print(f"\nFailures ({len(failures)}):")
            for failure in failures[:10]:
                print(
                    f"  - {failure['id']}: expected {failure['expected']}, got {failure['got']}"
                )
                print(f"    {failure['text'][:80]}...")

        assert accuracy >= 0.80, f"Accuracy {accuracy:.1%} below 80% target"

    def test_confidence_score_validity(self, pipeline, test_set):
        for test_case in test_set:
            result = pipeline.process(test_case["id"], test_case["text"])
            assert 0.0 <= result.sentiment_score <= 1.0

            if "expected_confidence_min" in test_case:
                assert result.sentiment_score >= test_case["expected_confidence_min"], (
                    f"Confidence {result.sentiment_score} below min "
                    f"{test_case['expected_confidence_min']} for {test_case['id']}"
                )

            if "expected_confidence_max" in test_case:
                assert result.sentiment_score <= test_case["expected_confidence_max"], (
                    f"Confidence {result.sentiment_score} above max "
                    f"{test_case['expected_confidence_max']} for {test_case['id']}"
                )
