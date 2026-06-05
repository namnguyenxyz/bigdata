# Phase 5 Plan: Integration, Testing & Deployment

## Phase Objective
Deliver a verified MVP by integrating the data pipeline, NLP, ranking, and dashboard into a coherent end-to-end workflow with clear local deployment instructions.

## Success criteria
1. End-to-end integration tests validate the pipeline from SQLite initialization through dashboard import.
2. The project README documents exact commands to run the database setup, pipeline, and Streamlit dashboard.
3. Any integration gaps are identified and fixed.
4. The project is ready for a reviewer to run locally with minimal effort.

## Tasks

### T1: Add integration tests
- T1.1 Create a temporary database integration test covering:
  - `database.py` initialization
  - sample comment and model mention insertion
  - `sentiment_pipeline.py` sentiment processing
  - `ranking.py` leaderboard generation
  - `app.py` import validation
- T1.2 Add a test that validates `data_helpers.py` can load leaderboard data from a fresh database.
- T1.3 Add a small smoke test for `streamlit` module import if installed.

### T2: Document the runbook
- T2.1 Update `README.md` with a Phase 5 section for end-to-end execution.
- T2.2 Document the run order:
  1. `python database.py`
  2. `python batch_job.py`
  3. `python sentiment_pipeline.py --db-path ./data/comments.db`
  4. `streamlit run app.py`
- T2.3 Include notes on required environment variables and setup.
- T2.4 Add a verification checklist for dashboard launch and data path validation.

### T3: Fix integration gaps
- T3.1 Validate that the dashboard reads from the same SQLite file used by the pipeline.
- T3.2 Ensure `sentiment_pipeline.py` and `ranking.py` use compatible `db_path` handling.
- T3.3 Fix any schema or import issues discovered during integration tests.
- T3.4 Add lightweight end-to-end logging or status output when needed.

### T4: Add deployment readiness
- T4.1 Confirm `requirements.txt` includes `streamlit` and other runtime dependencies.
- T4.2 Add a `deployment` section to `README.md` describing local MVP launch.
- T4.3 Add a note about the expected dataset and sample data if real Reddit credentials are unavailable.
- T4.4 Ensure the app can be imported via `python -m py_compile app.py`.

### T5: Verification and handoff
- T5.1 Produce a final `.planning/P5_INTEGRATION_TESTING/5-VERIFICATION.md` artifact after tests pass.
- T5.2 Add a summary note for the phase completion and handoff to documentation review.
- T5.3 If there are unresolved issues, capture them in the verification artifact with remediation steps.

## Implementation notes
- Use temporary SQLite databases in tests to avoid mutating the working data file.
- Use the existing `DEFAULT_DB_PATH` and allow `--db-path` overrides for all runnable scripts.
- Prefer a single integration test over many brittle end-to-end scenarios.
- Keep the deployment story local and clear; do not add cloud or CI-specific instructions for MVP.

## Phase breakdown
- Sprint 1: Integration test authoring and dashboard import validation
- Sprint 2: Readme deployment runbook and issue fixups
- Sprint 3: Verification artifact completion
