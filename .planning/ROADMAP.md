# Project Roadmap: AI Model Ranking System

**Project**: AI Model Ranking via Reddit Sentiment Analysis  
**Timeline**: 1-2 weeks (MVP)  
**Team**: 2-3 developers

## Phase Breakdown

### Phase 1: Data Collection & Infrastructure
**Objective**: Establish Reddit data pipeline and storage  
**Duration**: 2-3 days  
**Owner**: Backend lead  

**Deliverables**:
- Reddit API integration (PRAW library)
- Target subreddit crawler (r/MachineLearning, r/ChatGPT, r/LocalLLaMA, r/OpenAI, r/Claude)
- Data collection batch job (fetch last 1000 posts/comments per subreddit)
- SQLite database schema for comments (id, text, model_mentions, upvotes, timestamp, subreddit)
- Data deduplication logic
- Rate limit handling (exponential backoff)

**Success Criteria**:
- ✅ Can fetch 5000+ comments without API errors
- ✅ Data persists in local SQLite
- ✅ No duplicate records

**Key Risks**:
- Reddit API rate limits
- Subreddit data quality

**Dependencies**: None

---

### Phase 2: NLP Pipeline & Sentiment Analysis
**Objective**: Extract model mentions and classify sentiment  
**Duration**: 2-3 days  
**Owner**: NLP/ML engineer  

**Deliverables**:
- Model mention extractor (rule-based or regex initial, can upgrade to NER)
- Sentiment classifier (VADER or transformer-based, e.g., DistilBERT)
- Sarcasm detector (heuristic or lightweight model)
- Pipeline script to process all comments
- Sentiment cache/store (extend SQLite schema)
- Confidence score calculation

**Success Criteria**:
- ✅ Accuracy on manual test set >80%
- ✅ Processes 5000 comments in <5 minutes
- ✅ Correctly handles sarcasm samples

**Key Risks**:
- Sarcasm detection accuracy
- Sentiment model performance

**Dependencies**: Phase 1 (data availability)

---

### Phase 3: Ranking Algorithm & Metrics
**Objective**: Generate model leaderboard from sentiment data  
**Duration**: 1-2 days  
**Owner**: Data engineer  

**Deliverables**:
- Weighted scoring algorithm
  - Base sentiment score (Positive=+1, Neutral=0, Negative=-1)
  - Engagement weight (upvote ratio: upvotes/(upvotes+downvotes))
  - Source credibility (subreddit bias weight, user karma proxy)
- Leaderboard generation logic
- Historical trend tracking (daily snapshots)
- Ranking explainability (show top comments for each model)
- Config file for subreddit weights and model list

**Success Criteria**:
- ✅ Leaderboard sorts models by weighted score correctly
- ✅ Results feel accurate to human judgment
- ✅ Algorithm is reproducible and documented

**Key Risks**:
- Community bias skewing results
- Insufficient data for marginal differences

**Dependencies**: Phase 2 (sentiment data), Phase 1 (raw data)

---

### Phase 4: Frontend Dashboard & Visualization
**Objective**: Build Streamlit UI for leaderboard visualization  
**Duration**: 1-2 days  
**Owner**: Frontend/full-stack lead  

**Deliverables**:
- Streamlit app structure
- Main leaderboard view (sortable table with model, score, trend)
- Sentiment distribution charts (pie chart per model)
- Sample comments view (show top positive/negative for each model)
- Filters (subreddit, date range, sentiment)
- Methodology explanation page
- Data freshness indicator
- Deployment-ready structure (simple, no complex auth)

**Success Criteria**:
- ✅ App loads and renders in <2s
- ✅ UI is intuitive for developers
- ✅ All requirements from FR4 met

**Key Risks**:
- UX complexity
- Streamlit performance limits

**Dependencies**: Phase 3 (ranking data), Phase 1 (data access)

---

### Phase 5: Integration, Testing & Deployment
**Objective**: End-to-end testing, documentation, and launch  
**Duration**: 1 day  
**Owner**: Full team  

**Deliverables**:
- E2E testing (data → sentiment → ranking → UI)
- Manual verification of leaderboard accuracy
- README with setup instructions
- Requirements.txt for Python dependencies
- Configuration guide for subreddit/model changes
- Local deployment guide (how to run locally)
- Future roadmap (post-MVP features)
- Git repository cleanup and tagging (v1.0-mvp)

**Success Criteria**:
- ✅ Full pipeline runs end-to-end
- ✅ Results are reproducible
- ✅ Documentation is complete
- ✅ MVP ready for feedback

**Key Risks**:
- Integration issues between components

**Dependencies**: All prior phases

---

## Timeline Visualization

```
Week 1:
 Mon  │ Phase 1 (Data Collection) ████
 Tue  │ Phase 1 ████ │ Phase 2 (NLP) ████
 Wed  │ Phase 2 ████ │ Phase 3 (Algo) ████
 Thu  │ Phase 3 ████ │ Phase 4 (UI) ████
 Fri  │ Phase 4 ████ │ Phase 5 (Integration) ██

Week 2 (buffer):
 Mon  │ Phase 5 ████ / Refinement & Feedback
```

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Reddit API rate limits | High | Medium | Implement caching, batch processing, retry logic |
| Sarcasm misclassification | Medium | Medium | Use better NLP model, manual sampling |
| Community bias in results | Medium | High | Source diversity, weighting strategy, disclaimer |
| Insufficient data | Medium | Low | Expand subreddits if needed |
| Scope creep | High | Medium | Strict MVP scope, defer post-MVP features |

## Success Metrics
- [ ] Leaderboard generated successfully
- [ ] Results match developer intuition
- [ ] System runs reliably for 1 week without intervention
- [ ] Team feedback is positive
- [ ] Code is documented and maintainable

## Post-MVP Roadmap (Future)
1. **Phase 6**: Real-time updates (WebSocket, live streaming)
2. **Phase 7**: Fine-tuned NLP models for Reddit dialect
3. **Phase 8**: API for external consumption
4. **Phase 9**: Community voting and feedback loop
5. **Phase 10**: Multi-language support

---
**Created**: 2026-05-07  
**Status**: Ready for Phase 1 Planning  
**Next Command**: `/gsd-plan-phase 1`
