# RESEARCH QUICK REFERENCE

**Phase 1 Researcher**: gsd-phase-researcher  
**Document**: Quick reference for Phase 1 planners  
**Full Research**: See [RESEARCH.md](RESEARCH.md)

---

## One-Page Summary

### Technology Decisions (Why This Stack?)

| Component | Choice | Why | Alternatives |
|-----------|--------|-----|--------------|
| Reddit API | **PRAW** | Built-in rate limiting, 7K GitHub stars, mature | Direct API, Selenium |
| Database | **SQLite** | Zero DevOps, perfect for MVP, file-based | PostgreSQL, MongoDB |
| Rate Limiting | **PRAW + batching** | Handles 95% auto, exponential backoff built-in | Custom retry logic |
| Deduplication | **3-layer** (PK + hash + app) | Catches all edge cases | PK-only or hash-only |
| Deployment | **Local daily batch job** | Respects rate limits, 10 min runtime | Real-time streaming |

### Critical Numbers

```
Reddit Rate Limits:  60 requests/minute (OAuth)
Batch Size:          500 API calls (5 subs × 100 comments)
Run Duration:        ~10 minutes per batch
Min Comment Count:   5,000-10,000 (for Phase 2)
Collection Schedule: Daily (off-peak)
Expected Duplicates: <1% (flag >5%)
```

### Minimal Viable Architecture

```
┌─────────────────────┐
│  Daily Batch Job    │
│  (runs @ 2 AM UTC)  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐       ┌──────────────────┐
│   PRAW Library      │ ──→ │   SQLite DB      │
│  (Auth + API Call)  │       │  (Persist Data) │
└─────────────────────┘       └──────────────────┘
           │
           ↓
┌─────────────────────┐       ┌──────────────────┐
│   Rate Limiter      │ ──→ │  collection_log  │
│  (Exponential BO)   │       │  (Run History)   │
└─────────────────────┘       └──────────────────┘
```

---

## Implementation Roadmap (2.5 days)

### Day 1: Foundation
**Morning (2 hours)**
- Get Reddit API credentials (https://reddit.com/prefs/apps)
- Set up .env with secrets
- Install PRAW: `pip install praw`
- Write and test `reddit_auth.py`
- ✅ **Test**: Fetch 10 comments from r/MachineLearning

**Afternoon (2.5 hours)**
- Design SQLite schema (3 tables: comments, model_mentions, collection_log)
- Write `database.py` with init, store, query functions
- Implement 3-layer dedup logic
- ✅ **Test**: Store 100 comments, no duplicates

### Day 2: Pipeline
**Morning (3 hours)**
- Write `subreddit_crawler.py` batch fetcher
- Implement rate limiting (1-2 sec delays)
- Add exponential backoff decorator
- Add comprehensive logging
- ✅ **Test**: Fetch 5000+ comments without errors

**Afternoon (2 hours)**
- End-to-end batch job test (1 full run)
- Verify collection_log entries
- Write README with setup instructions
- ✅ **Test**: Run batch job 3x, check for duplicates

### Day 3: Polish & Docs
**Morning (1 hour)**
- Unit tests: `test_dedup.py`, `test_schema.py`
- Data quality report (duplication rate, validation pass rate)

**Afternoon (1 hour)**
- Create deployment guide
- Document troubleshooting (rate limits, auth failures)
- **DONE**: Ready for Phase 2

---

## Key Decisions (Ask Questions During Planning)

1. **When to start collecting?** 
   - Rec: Start batch job today → gives Phase 2 data to work with
   
2. **How many comments?** 
   - Rec: 10K before Phase 2 starts (1 week of daily batches)
   
3. **Which subreddits?** 
   - Rec: r/MachineLearning, r/ChatGPT, r/LocalLLaMA, r/OpenAI, r/Claude (5 total)
   
4. **How to handle schema changes?** 
   - Rec: Add model_mentions table in Phase 1 (prep for Phase 2, not used yet)
   
5. **Monitoring/alerting?** 
   - Rec: Basic logging first; Phase 1+ can add email alerts on rate limit hits

---

## Risks Mitigated

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Rate limit hits | PRAW built-in backoff + request batching | PRAW library |
| Duplicate data | 3-layer validation + uniqueness tests | Batch job |
| Silent failures | Structured logging + collection_log table | Batch job |
| DB corruption | SQLite WAL mode + weekly backups | DB config |
| Schema conflicts | Extensible design (Phase 2 can add columns) | DB design |

---

## Code Examples

### Simplest Viable Batch Job (20 lines)

```python
import praw
import sqlite3

reddit = praw.Reddit(client_id='...', client_secret='...', 
                    user_agent='bot/1.0')

for sub_name in ['MachineLearning', 'ChatGPT', 'LocalLLaMA']:
    comments = reddit.subreddit(sub_name).new(limit=100)
    for comment in comments:
        # Store to SQLite
        conn = sqlite3.connect('comments.db')
        conn.execute('INSERT INTO comments VALUES (...)')
        conn.commit()
```

### Full Example

See [RESEARCH.md Section 8.1](RESEARCH.md#81-full-example-minimal-batch-job) for production-ready code.

---

## Validation Checklist

Before Phase 1 is done:

- [ ] Can authenticate to Reddit API
- [ ] Database schema created with 3 tables
- [ ] Can fetch 5000+ comments without errors
- [ ] Deduplication verified (run batch job twice, check for duplicates)
- [ ] Logging shows collection_log entries
- [ ] Batch job completes in <15 min
- [ ] README explains setup and deployment
- [ ] Unit tests pass

---

## Questions for Phase 1 Planner

1. **Timeline pressure**: Is 2.5 days realistic or should we spike a day for extra testing?
2. **Team composition**: Who will own database vs. crawler code?
3. **Deployment**: Should batch job run locally on laptop or on a server?
4. **Monitoring**: Do we want Slack/email alerts if batch job fails?
5. **Data cleanup**: Any sensitive data we should filter out (PII, spam)?

---

**Full Research Document**: [RESEARCH.md](RESEARCH.md)  
**For Detailed Rationales**: See sections 1-11 in RESEARCH.md
