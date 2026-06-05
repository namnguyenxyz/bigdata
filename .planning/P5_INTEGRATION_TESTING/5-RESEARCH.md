# Phase 5 Research: Integration, Testing & Deployment

## Objective
Research the right MVP-level integration and deployment checks for a local Python + Streamlit project that spans Reddit data collection, NLP, ranking, and dashboard visualization.

## Key Research Questions
1. What integration points are most likely to fail when connecting the pipeline end-to-end?
2. How should local deployment and run instructions be structured for a reviewer?
3. What tests are most valuable for validating cross-component behavior without overbuilding?
4. Which existing project artifacts should be reused versus refactored for integration?
5. What documentation gaps remain for a clean handoff/demo?

## Findings

### Integration priority
- Validate that `database.py` initializes the SQLite schema and that `comments` and `model_mentions` tables are available for later phases.
- Confirm that `sentiment_pipeline.py` writes sentiment fields to comments and that `ranking.py` can compute a leaderboard from the same database.
- Validate that `app.py` can import and render using `data_helpers.py` and the same ranking helpers.
- Focus on the happy path first; add a small number of regression checks for previously discovered failure modes.

### Recommended tests
- End-to-end smoke test that initializes a fresh database, inserts sample comments and mentions, processes sentiment, computes leaderboard scores, and imports the dashboard module.
- Import-time test for `app.py` and `data_helpers.py` to catch UI integration issues early.
- Unit tests that verify the integration of `ranking.py` with `data_helpers.py` and the Streamlit helper path.
- A local CLI check for `streamlit run app.py` should be documented even if it is not executed in CI.

### Deployment guidance
- Document the minimal setup commands in `README.md` and include the new `streamlit` dependency.
- Provide a clear run order: initialize DB, fetch data, run sentiment pipeline, then launch dashboard.
- Include environment setup notes for `.env` and Reddit API credentials.
- Add a verification checklist for the dashboard and pipeline output.

### Artifact reuse
- Reuse `RankingConfig` and `get_leaderboard` from `ranking.py` rather than duplicating leaderboard logic.
- Reuse `app.py` import validation as a proxy for dashboard integration.
- Reuse existing tests in `tests/` for the new end-to-end scenario where possible.

## Recommendation
- Build Phase 5 around a small set of integration tests and a deployment checklist.
- Keep the deployment story local and developer-friendly.
- Use the existing SQLite database path and data schemas; do not introduce new storage layers.
- Add final verification artifacts that show the full path from raw comments to dashboard display.

## Validation criteria
- The integration plan can be executed with minimal setup.
- Runbook documentation clearly describes the end-to-end commands.
- Integration tests catch mismatches between the pipeline and dashboard.
- The project is demonstrable with one command to launch the Streamlit app after data setup.

## Open questions
- Should the README include sample data generation for reviewers with no Reddit creds? (Recommend yes if time allows.)
- Should integration tests be written against a temporary database or the repo's default data path? (Recommend temporary DB for CI safety.)
- Should the deployment docs include a direct `streamlit run app.py` example? (Yes.)
