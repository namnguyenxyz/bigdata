# Phase 5 Plan: Integration, Testing & Deployment

Goal: Validate end-to-end pipeline and prepare MVP deployment and docs.

Tasks:
1. Run integration tests and fix issues.
2. Verify accuracy on `manual_test_set.json` and `test_accuracy_validation.py`.
3. Update `README.md` and `requirements.txt` if needed.
4. Tag repo for v1.0-mvp.

Commands:
 - `PYTHONPATH=. /home/nhnam/workspace/uit_learning/bigdata/.venv-1/bin/pytest tests/test_integration.py -q`
 - `PYTHONPATH=. /home/nhnam/workspace/uit_learning/bigdata/.venv-1/bin/pytest tests/test_phase5_integration.py -q`
