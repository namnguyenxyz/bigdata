# Project State & Memory

## Questioning Phase (Complete)
- ✅ Project name, type, and description captured
- ✅ User and stakeholder context identified
- ✅ Team size and tech stack preferences documented
- ✅ Key risks and MVP scope defined
- ✅ Workflow preferences set to automatic with research phase

## Current Milestone
- Milestone 1: MVP Delivery (Week 1-2)

## Key Decisions
1. **Focus subreddits**: r/MachineLearning, r/ChatGPT, r/LocalLLaMA (more to be determined)
2. **MVP target**: Working leaderboard with at least 5 models ranked by sentiment
3. **Stack**: Python backend + Streamlit frontend
4. **Ranking algorithm**: Engagement-weighted sentiment scores

## Open Questions for Planning
- [ ] Which exact subreddits to target (expand beyond initial 3)
- [ ] NLP library choice (VADER, transformer-based, or hybrid)
- [ ] Data refresh frequency (daily, weekly, monthly)
- [ ] Model list scope (top 5, top 10, dynamic)
- [ ] Storage strategy (CSV, SQLite, PostgreSQL)
- [ ] Deployment target (local, cloud, web)

## Risks Tracked
- **Rate Limiting**: Reddit API free tier limits
  - Mitigation: Implement caching, batch processing
- **Sarcasm Detection**: May misclassify sentiments
  - Mitigation: Use advanced NLP model, manual validation sample
- **Community Bias**: Some subreddits favor certain model types
  - Mitigation: Source diversity, bias scoring in algo
- **Data Staleness**: May miss emerging trends quickly
  - Mitigation: Real-time monitoring of top posts/comments

## Assumptions
- Reddit data is representative of AI user sentiment
- Community discussions contain actionable ranking signals
- Team can handle data collection + analysis + visualization in 1-2 weeks
- Streamlit is sufficient for MVP UI needs

## Dependencies
- Reddit API access (free tier may require throttling)
- Python environment (3.8+)
- NLP libraries (PRAW, nltk, transformers, etc.)

---
**Last Updated**: 2026-05-07
