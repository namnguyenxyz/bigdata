# Phase 2 Context: NLP Pipeline & Sentiment Analysis

Relevant modules:
- nlp_pipeline.py — pipeline orchestration
- sentiment_analyzer.py — sentiment classification logic
- sarcasm_detector.py — sarcasm heuristics/model
- sentiment_pipeline.py — end-to-end processing
- model_extractor.py — extract model mentions

Existing test assets:
- manual_test_set.json
- tests/test_sentiment_analyzer.py
- tests/test_sarcasm_detector.py

Constraints & assumptions:
- Use VADER or lightweight model for MVP; transformer optional
- Performance target: process 5000 comments in <5 minutes
