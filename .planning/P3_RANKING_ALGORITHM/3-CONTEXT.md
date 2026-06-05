# Phase 3 Context: Ranking Algorithm & Metrics

## Phase
P3_RANKING_ALGORITHM

## Phase Name
Ranking Algorithm & Metrics

## Phase Goal
Build a transparent, explainable leaderboard that ranks AI models by Reddit-derived community sentiment. Use Phase 2 sentiment and model-extraction outputs as the canonical input, and produce reproducible scores that can be filtered by time window, subreddit, and engagement.

## What this phase consumes
- `comments` table with sentiment_label, sentiment_score, sarcasm_detected, sarcasm_patterns, processed_at
- Model mention extraction results from Phase 2 (stored in `model_mentions` or derived from comments)
- Engagement metadata from Phase 1 comments (score, upvote_ratio, subreddit)
- Existing roadmap requirements and Phase 2 research/plan artifacts

## What this phase produces
- Ranking algorithm module(s) for weighted sentiment scoring
- Leaderboard generation logic and query helpers
- Score explainability data (top supporting comments, weight breakdown)
- Time-window filters and trend snapshot persistence
- Tests for ranking logic, explainability, and filtering
- Documentation of ranking methodology and tradeoffs

## Locked Decisions
- D-01: Use weighted sentiment score per model, not raw mention count.
- D-02: Engagement weight is based on upvote_ratio and score proxies.
- D-03: Source credibility is modeled through subreddit weight and comment recency.
- D-04: Ranking must be explainable by showing supporting comments and weight contributions.
- D-05: Use SQLite query-friendly design and keep leaderboard computation in Python modules.
- D-06: MVP covers 30-day and all-time windows; daily snapshots are optional but desirable.

## Success Criteria
- ✅ Ranked leaderboard sorts models by weighted community sentiment
- ✅ Algorithm returns explainable scores with supporting comments for each model
- ✅ Supports time-window filtering (`last 30 days`, `all-time`) and subreddit filters
- ✅ Ranking logic is unit-tested and reproducible
- ✅ Performance is acceptable for 5,000+ comments and leaderboard generation in <2s for MVP queries

## Constraints
- Must use existing Phase 1/2 database schema and SQLite stack
- No external ranking service or advanced ML model required for MVP
- Must preserve Phase 2 sentiment data integrity and avoid reprocessing Phase 1 data during ranking

## Risks
- R-01: Community bias skews leaderboard toward overrepresented subreddits
- R-02: Sentiment confidence values are noisy and may distort weighted scores
- R-03: Time-window filters may produce unstable rankings with sparse data
- R-04: Complex weight formulas reduce explainability
- R-05: SQLite query performance can degrade with naive joins on large comment sets

## Mitigations
- Use explicit subreddit credibility weights and document bias assumptions
- Normalize sentiment scores and cap engagement impact
- Require minimum comment counts before showing a model in the leaderboard
- Maintain a simple weight breakdown and expose it in the UI
- Add indexing and batch precomputation for leaderboard queries

## Phase 3 Handoff Notes
- Phase 3 should not alter raw comments or sentiment labels; it should add computed ranking outputs only.
- If Phase 4 UI needs extra columns, Phase 3 should produce query helpers and persistence support, not UI code.
- Phase 3 is the bridge between NLP outputs and dashboard presentation.
