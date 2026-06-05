# Phase 4 Plan: Frontend Dashboard & Visualization

## Phase Objective
Implement an MVP Streamlit dashboard that presents the Phase 3 leaderboard, sentiment distributions, and supporting comment evidence in a developer-friendly UI.

## Success criteria
1. The app displays a ranked model leaderboard with score, support counts, and top supporting comments.
2. Filters work for time window (`30d`, `all`) and subreddit.
3. Sentiment distribution charts are visible and descriptive.
4. The methodology and ranking formula are clearly explained.
5. The dashboard loads and responds quickly for MVP dataset sizes.

## Tasks

### T1: Build data access layer
- T1.1 Add `data_helpers.py` with SQLite queries for leaderboard and sentiment summaries.
- T1.2 Reuse `ranking.py` helpers or expose a wrapper for Streamlit.
- T1.3 Add caching for query results with `st.cache_data` if using Streamlit.
- T1.4 Add optional support for loading `top_supporting_comments` from the ranking payload.

### T2: Build leaderboard UI
- T2.1 Create `app.py` or `dashboard.py` as the Streamlit entrypoint.
- T2.2 Add sidebar controls: `subreddit`, `time window`, `limit`.
- T2.3 Render a leaderboard table with model name, score, support count, and sentiment totals.
- T2.4 Add per-model expanders for top supporting comments and score breakdown.

### T3: Build chart visualizations
- T3.1 Add sentiment distribution chart (positive/negative/neutral) for selected models.
- T3.2 Add a model score trend section comparing `30d` and `all` windows.
- T3.3 Add a chart or summary metric for comment volume and sentiment confidence.

### T4: Add methodology & documentation
- T4.1 Add a dashboard section explaining ranking logic, engagement weights, and source credibility.
- T4.2 Add a README snippet for `streamlit run app.py` and required dependencies.
- T4.3 Add a local data freshness indicator or note.

### T5: Add tests and validation
- T5.1 Add unit tests for `data_helpers.py` query helpers.
- T5.2 Add smoke tests for `ranking.py` integration with dashboard helpers.
- T5.3 Add a simple `pytest` check that `app.py` imports without error.
- T5.4 Add a manual checklist for dashboard run verification.

## Dependencies
- Streamlit
- pandas (optional for query result handling)
- `ranking.py` and existing SQLite schema

## Implementation notes
- Keep the UI simple and avoid custom JavaScript or CSS for MVP.
- Use existing SQLite indexes and window filters from Phase 3.
- If Streamlit is not already installed, add it to `requirements.txt`.
- Prefer built-in charts before pulling in Plotly or Altair.
- Keep the dashboard code modular so Phase 5 can integrate it with end-to-end tests.

## Verification plan
- Run `streamlit run app.py` locally and confirm the leaderboard renders.
- Validate filters and supporting comment sections with sample data.
- Confirm the methodology panel matches Phase 3 scoring decisions.
- Confirm app import passes: `python -m py_compile app.py`.

## Phase breakdown
- Sprint 1: Data querying and leaderboard page
- Sprint 2: Charting and supporting comment explainability
- Sprint 3: Documentation, tests, and local verification
