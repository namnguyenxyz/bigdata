# Phase 3 Plan: Ranking Algorithm & Metrics

## Phase Objective
Implement a leaderboard ranking engine that orders AI models by Reddit sentiment signal, engagement, and source credibility. Deliver query helpers, explainability payloads, and supporting tests for the MVP ranking pipeline.

## Plan Overview
- Build ranking utilities in a dedicated module
- Add filtering, time-window support, and explainability
- Define score components and weights in a configurable, documented way
- Validate with unit tests and sample leaderboard outputs

## Success criteria
1. `get_leaderboard(window="30d"/"all", subreddit=None)` returns a ranked model list
2. Each ranked entry includes a score breakdown and top supporting comments
3. Ranking logic is unit-tested and reproducible
4. Documentation explains the formula, weights, and bias assumptions
5. Leaderboard queries are efficient enough for MVP data volume

## Tasks

### T1: Design ranking data model and scoreboard helpers
- T1.1 Define ranking calculation formula in `ranking.py`
- T1.2 Implement `compute_comment_contribution(comment, subreddit_weights)`
- T1.3 Implement `aggregate_model_scores(comment_contributions)`
- T1.4 Add `min_support` or `min_mentions` guard for MVP leaderboard inclusion
- T1.5 Create a `RankingConfig` structure for engagement and subreddit weights

### T2: Implement windowed leaderboard generation
- T2.1 Add `windowed_comments(window)` filter for `30-day` and `all-time`
- T2.2 Add optional `subreddit` filter and default `all subreddits`
- T2.3 Implement `get_leaderboard(db, window, subreddit, limit)` helper
- T2.4 Add optional sorting by rank, score, and comment count

### T3: Add explainability and supporting comment extraction
- T3.1 Implement `get_supporting_comments_for_model(model, top_n)`
- T3.2 Include `score_components` in each leaderboard row:
  - raw sentiment score
  - engagement multiplier
  - subreddit weight
  - final contribution sum
- T3.3 Ensure `top_supporting_comments` includes comment text, subreddit, sentiment_label, and score breakdown

### T4: Add metrics and trend support for MVP
- T4.1 Add `ranking_trend` helper to compare `last 30 days` vs `all-time`
- T4.2 Implement optional daily snapshots if on-demand queries are too slow
- T4.3 Add `sentiment_distribution` helper for leaderboard view charts
- T4.4 Add count of positive/negative/neutral mentions per model

### T5: Add tests and verification
- T5.1 Create unit tests for ranking formula and engagement scaling
- T5.2 Add tests for time-window filtering and `subreddit` filter behavior
- T5.3 Add tests for explainability payload structure
- T5.4 Add tests for minimum support threshold and sparse model exclusion
- T5.5 Add sample data fixture for ranking integration tests

### T6: Document ranking methodology
- T6.1 Add Phase 3 summary content to `3-SUMMARY.md` after implementation
- T6.2 Document formula, weights, and bias assumptions in the Phase 3 summary
- T6.3 Add verification checklist to `3-VERIFICATION.md`

## Implementation notes
- Use existing comment-level sentiment outputs from Phase 2; do not reclassify sentiment in Phase 3.
- Keep ranking logic in Python and query the SQLite backend via existing DB helpers.
- Use default `subreddit_weights` that can be overridden in config for future tuning.
- If performance becomes an issue, add an SQLite `model_score_snapshot` materialized table later.
- Maintain `all-time` and `30-day` windows in the MVP API surface.

## Work breakdown

### Sprint 1: Core scoring and ranking
- T1, T2, T3
- Deliver a working leaderboard with support comments and windowed filters

### Sprint 2: trend metrics and UX helpers
- T4, T5
- Deliver distribution summaries, rank trend helpers, and robust tests

### Sprint 3: documentation and verification
- T6
- Deliver Phase 3 docs and acceptance criteria for execution handoff

## Verification plan
- Verify leaderboard output against a synthetic dataset with known signal
- Validate all windows and subreddit filters in tests
- Confirm support comments reflect the highest weighted contributions
- Confirm ranking formula remains stable when sentiment confidence changes
- Confirm final scores are explainable and documented

## Risks and contingencies
- If `subreddit_weights` is uncertain, default to `1.0` for all subreddits and tune later.
- If on-demand leaderboard performance is poor, switch to snapshot persistence after the MVP rank algorithm is correct.
- If model mention coverage is sparse, add a fallback that ranks by total weighted sentiment instead of raw counts.
