# Phase 2 Accuracy Validation

This document describes the manual test set and validation process for Phase 2.

## Purpose

Provide a reproducible validation step for the NLP pipeline’s sentiment classification and sarcasm handling. The goal is to verify that the Phase 2 pipeline meets the >80% accuracy requirement on a curated manual dataset.

## Manual Test Set

- File: `manual_test_set.json`
- Format: JSON object with a `test_cases` array
- Each test case includes:
  - `id`
  - `text`
  - `expected_sentiment`
  - optional `expected_confidence_min`
  - optional `expected_confidence_max`
  - `models_mentioned`
  - `sarcasm`
  - `notes`

## Validation Script

- File: `tests/test_accuracy_validation.py`
- This test loads `manual_test_set.json` and evaluates the pipeline using `NLPPipeline()`.
- It asserts:
  - overall sentiment accuracy >= 80%
  - sentiment confidence values are in [0.0, 1.0]
  - optional confidence thresholds are met

## Running Validation

```bash
.venv/bin/python -m pytest tests/test_accuracy_validation.py -q
```

## Notes

- This manual dataset is intentionally designed to include:
  - clear positive examples
  - clear negative examples
  - neutral statements
  - sarcasm cases
  - model mention variations (GPT-4, Claude, Llama, Mistral, etc.)

- The dataset is small but representative for phase validation. It can be expanded later to cover more domain-specific examples.
