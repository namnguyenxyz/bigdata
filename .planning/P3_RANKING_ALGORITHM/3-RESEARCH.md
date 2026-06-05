# Phase 3 Research: Ranking Algorithm & Metrics

## Objective
Research ranking approaches that turn sentiment and engagement data into an explainable model leaderboard. The goal is to identify a small number of robust, reproducible scoring strategies that are appropriate for the current SQLite + Python MVP stack.

## Key Research Questions
1. How should we aggregate sentiment across comments for each model?
2. Which engagement signals should influence model score without overpowering sentiment?
3. How should subreddit credibility be modeled to compensate for community bias?
4. What time windows and trend metrics are most useful for an MVP leaderboard?
5. How can we keep ranking logic explainable while still producing meaningful ordering?

## Findings

### Sentiment aggregation
- **Weighted average sentiment** is the most interpretable approach: model_score = sum(weight * sentiment_value) / sum(weights).
- Use sentiment values: positive=+1, neutral=0, negative=-1, then multiply by confidence.
- Confidence should modulate contribution: `sentiment_value * confidence` preserves Phase 2 output semantics.
- Aggregating per comment and then per model prevents a small number of highly engaged comments from dominating raw mention counts.

### Engagement weight options
- `upvote_ratio` is a strong proxy for community agreement and is already present in Phase 1 data.
- `score` (upvotes minus downvotes) is useful but may be sparse or zero for many comments.
- A combined engagement factor can be computed as:
  - `engagement = 1 + alpha * upvote_ratio + beta * log(1 + abs(score))`
- For MVP, keep weights simple and bounded: `engagement_score = 1 + 0.5*upvote_ratio + 0.2*log1p(abs(score))`.
- Engagement should not flip sentiment polarity; it should only scale the contribution magnitude.

### Source credibility weights
- Different subreddits have distinct biases; r/ChatGPT may be positively skewed while r/MachineLearning may be more critical.
- Use a configurable `subreddit_weight` table or dictionary with default weight `1.0`.
- For MVP, implement a `subreddit_bias` factor and document it as part of the ranking methodology.
- User karma is not available in the Phase 1 schema, so use subreddit-level credibility rather than per-user weight.

### Time-window filtering and trend tracking
- Phase 3 should support at least two windows: `last 30 days` and `all-time`.
- Implement a `processed_at` filter on the comments table for windowing.
- Maintain a daily snapshot table for leaderboard history if the query performance is slow:
  - `leaderboard_snapshot(date, model_name, score, rank)`
- For MVP, windowed leaderboard queries can be computed on demand if data volume is moderate.

### Explainability
- Provide the final score as a sum of components:
  - sentiment_score component
  - engagement multiplier
  - subreddit credibility multiplier
- Return top supporting comments for each model, sorted by `abs(sentiment_confidence) * engagement`.
- Expose a `rank_reason` payload with numeric contributions for each model.
- Keep formula documentation in `ACCURACY_VALIDATION.md` or a Phase 3 summary doc.

### Implementation patterns
- A `ranking.py` module is a good MVP home for algorithm utilities.
- Create `get_model_scores`, `get_leaderboard`, `get_supporting_comments`, and `get_trend_snapshots` functions.
- Write unit tests around the scoring formula, window filters, and explainability output.
- Use SQLite indexes on `model_mentions.comment_id`, `comments.processed_at`, and `comments.subreddit` if needed.

## Candidate algorithms

### Algorithm A: Weighted sentiment average

```
comment_score = sentiment_value * sentiment_confidence
contribution = comment_score * engagement_factor * subreddit_weight
model_score = sum(contribution) / sum(engagement_factor * subreddit_weight)
```

- Pros: interpretable, stable, easy to explain.
- Cons: may underweight low-confidence but high-volume models.

### Algorithm B: Score with minimum support threshold

- Compute Algorithm A, but only rank models with at least `N` comments or `M` mentions.
- Pros: avoids ranking on weak evidence.
- Cons: needs threshold tuning.

### Algorithm C: Trend-aware score

- `final_score = current_window_score + lambda * trend_score`
- Use daily snapshots to compute trend over time.
- Pros: surfaces momentum.
- Cons: more complex for MVP; can be added later.

## Recommendation
- Use Algorithm A as the Phase 3 MVP ranking function.
- Add a simple `min_support` threshold to avoid sparse models.
- Include time-window filtering for `30-day` and `all-time` views.
- Add a `subreddit_weights` config object and document bias assumptions.
- Expose supporting comment extraction for explainability.

## Validation criteria
- Rankings should be reproducible from the same data inputs.
- Explanation data must show at least 3 supporting comments per ranked model.
- Leaderboard queries should return in <2 seconds for 5,000 comments.
- Score formula is documented and unit-tested.

## Open questions
- Should the leaderboard hide models with fewer than 5 supporting comments? (Recommend yes for MVP.)
- Should engagement use `upvote_ratio` only, or also `score`? (Recommend both with bounded scaling.)
- How should neutral sentiment be represented in the UI? (Keep it as a separate distribution bucket.)
