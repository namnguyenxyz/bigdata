# Phase 2 Plan: NLP Pipeline & Sentiment Analysis

Goal: Extract model mentions and classify sentiment reliably, handling sarcasm.

Tasks:
1. Verify `model_extractor.py` extracts model mentions from text.
2. Run and validate `sentiment_analyzer.py` on `manual_test_set.json`.
3. Evaluate `sarcasm_detector.py` against test set and adjust heuristics.
4. Integrate components into `nlp_pipeline.py` and `sentiment_pipeline.py`.
5. Run unit tests: `tests/test_sentiment_analyzer.py`, `tests/test_sarcasm_detector.py`.

Commands:
 - `PYTHONPATH=. /home/nhnam/workspace/uit_learning/bigdata/.venv-1/bin/pytest tests/test_sentiment_analyzer.py -q`
 - `PYTHONPATH=. /home/nhnam/workspace/uit_learning/bigdata/.venv-1/bin/pytest tests/test_sarcasm_detector.py -q`

Acceptance Criteria:
 - Tests pass
 - Sentiment accuracy on manual set >80%
 - Sarcasm samples handled or flagged
