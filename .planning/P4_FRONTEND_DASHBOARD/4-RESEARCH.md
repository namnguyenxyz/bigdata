# Phase 4 Research: Frontend Dashboard & Visualization

## Objective
Research the best UI patterns and Streamlit implementation approach for a model ranking dashboard that is easy to use, explainable, and efficient with SQLite-backed sentiment data.

## Key Research Questions
1. What Streamlit components provide the best leaderboard and filter UX?
2. How should sentiment distribution and ranking explainability be visualized?
3. Which data access patterns work best for SQLite in a Streamlit app?
4. What charting options are available without adding heavy dependencies?
5. How should methodology and bias disclosures be surfaced in the dashboard?

## Findings

### Recommended MVP UX
- Use a two-column layout: primary leaderboard on the left, supporting charts and filters on the right.
- Display a sortable table of ranked models with score, mention count, and trend indicators.
- Provide filter controls for `subreddit`, `time window`, and optional sentiment type.
- Add an expandable section per model for top supporting comments and score component details.
- Use a sidebar or header controls for global filters and explanation links.

### Data access approach
- Query SQLite directly from Streamlit using `sqlite3` or `pandas.read_sql_query`.
- Use a helper function to load the leaderboard from `ranking.py` and cache results with `st.cache_data`.
- Avoid expensive full-table scans by filtering on `processed_at` and `subreddit` in SQL.
- Keep chart data in memory after query to prevent repeated database hits on small MVP datasets.

### Charting strategy
- Use Streamlit's built-in `st.bar_chart` or `st.line_chart` for sentiment distribution and rank trend.
- Use `plotly` only if the built-in charts do not provide enough clarity for the leaderboard.
- Show a bar chart of positive/negative/neutral mentions per selected model or top N models.
- Add a simple trend summary line or delta metric when comparing `30d` vs `all-time` data.

### Explainability
- Show top 3 supporting comments per model, sorted by contribution magnitude.
- Display component values: raw sentiment score, engagement multiplier, subreddit weight, final contribution.
- Provide a methodology panel explaining how scores are computed and what filters mean.
- Document that rankings are based on Phase 3 weighted sentiment and may reflect subreddit bias.

### Implementation pattern
- Create `app.py` or `dashboard.py` as the main Streamlit entrypoint.
- Build `data_helpers.py` with `load_leaderboard`, `load_sentiment_distribution`, and `load_supporting_comments`.
- Use `RankingConfig` from `ranking.py` if additional configuration is needed.
- Add a README section on `streamlit run app.py` and dependency installation.

## Recommendation
- Use a single-page Streamlit app with sidebar filters and main content sections.
- Keep the MVP dashboard read-only, with no user authentication.
- Load data via SQLite and ranking helpers, then render charts with Streamlit built-ins.
- Add one documentation page inside the app that explains the scoring formula and caveats.

## Validation criteria
- Dashboard loads with no errors using the existing SQLite database.
- Filters update the leaderboard correctly.
- Charts display positive/negative/neutral breakdowns.
- Supporting comments are correctly associated with the ranked models.
- UI remains simple and performant on moderate dataset sizes.

## Open questions
- Should the app include a separate model comparison view, or keep it leaderboard-only for MVP?
- Should we support a manual refresh button for the dashboard data?
- Should the methodology panel include a link to `.planning/P3_RANKING_ALGORITHM/3-PLAN.md` for deeper detail?
