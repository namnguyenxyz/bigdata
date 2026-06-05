# Phase 4 Context: Frontend Dashboard & Visualization

## Phase
P4_FRONTEND_DASHBOARD

## Phase Name
Frontend Dashboard & Visualization

## Phase Goal
Build an MVP Streamlit dashboard that surfaces the ranked AI model leaderboard, sentiment distributions, and supporting Reddit comment evidence. The goal is to turn Phase 3 ranking outputs into an intuitive, explainable developer-facing visualization.

## What this phase consumes
- `ranking.py` leaderboard outputs and explainability payloads
- `comments` and `model_mentions` tables from Phase 1
- sentiment labels, scores, sarcasm flags, and processed timestamps from Phase 2
- Phase 3 scoring methodology, weights, and top-supporting comment context

## What this phase produces
- Streamlit app entrypoint (e.g. `app.py` or `dashboard.py`)
- Leaderboard view with model score, support counts, and filter controls
- Sentiment distribution charts (pie/bar) and trend summaries
- Sample comments supporting each ranked model
- Time-window and subreddit filtering
- Documentation of UI behavior and ranking methodology
- Basic local deployment/run instructions

## Locked Decisions
- D-01: Use Streamlit for MVP UI delivery.
- D-02: Keep the dashboard local and authentication-free for Phase 4.
- D-03: Build on the existing SQLite stack and query helpers rather than introducing a new backend.
- D-04: Support `30d` and `all` time windows for the leaderboard.
- D-05: Surface score explainability through top supporting comments and component breakdown.

## Success Criteria
- ✅ The app displays a ranked leaderboard from production data
- ✅ Filters work for subreddit and time window
- ✅ Sentiment distribution charts are visible and meaningful
- ✅ Top supporting comments are available for each ranked model
- ✅ App loads in under 2 seconds for MVP data volumes
- ✅ Phase 4 plan is documented and testable

## Constraints
- Must use existing Python stack and local SQLite database
- No complex frontend framework or authentication in MVP
- Must keep UI code simple and maintainable
- Must use existing ranking output shape to avoid duplicate computation

## Risks
- R-01: Streamlit chart rendering may require additional dependencies
- R-02: UI performance may degrade on larger comment sets without caching
- R-03: Ranking explainability may overwhelm the interface if too verbose
- R-04: Filter logic may diverge from backend ranking semantics if not centralized

## Mitigations
- Use built-in Streamlit charts and lightweight pandas queries
- Limit supporting comments to the top 3 per model in the MVP view
- Document how filters and windows are applied
- Keep the dashboard data access layer in a reusable helper module

## Phase 4 Handoff Notes
- Phase 5 should use this dashboard as the front-end integration target.
- Phase 4 should not change the ranking or sentiment data model; it should only visualize it.
- If additional computed fields are needed later, Phase 4 should expose a clear helper API, not hard-coded presentation logic.
