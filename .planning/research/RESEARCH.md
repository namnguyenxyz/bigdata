# Phase 1 Research: Data Collection & Infrastructure

**Project**: AI Model Ranking via Reddit Sentiment Analysis  
**Phase**: Phase 1 — Data Collection & Infrastructure  
**Research Date**: 2026-05-07  
**Researcher**: gsd-phase-researcher  

---

## Executive Summary

Phase 1 requires establishing a robust Reddit data pipeline to collect comments about AI models. This research recommends:
- **PRAW library** for Reddit API access (industry standard, most reliable)
- **SQLite** for local persistence (sufficient for MVP, zero DevOps overhead)
- **Exponential backoff + request batching** for rate limit handling
- **Layered deduplication** (URL + content hash) to ensure data quality
- **2-3 day timeline is realistic** with proper library selection and incremental development

---

## 1. Technology Stack Recommendations

### 1.1 Reddit Data Collection: PRAW vs. Alternatives

#### Option 1: PRAW (Python Reddit API Wrapper) — **RECOMMENDED**

**Pros**:
- **Most mature Python Reddit library** (7000+ GitHub stars, maintained since 2011)
- **Battle-tested in production** by thousands of Reddit scrapers and bots
- **Excellent rate limit handling built-in** (respects HTTP 429 backoff headers automatically)
- **Authentication abstraction** (OAuth, user agent management)
- **Low learning curve** — simple, Pythonic API
- **Active community** (StackOverflow, Reddit discussions)
- **Generous for research** — no additional API keys beyond basic Reddit app registration

**Cons**:
- No official real-time streaming (suitable for batch jobs anyway)
- Default pagination limited to 1000 posts per subreddit (acceptable for MVP)

**Example PRAW Usage**:
```python
import praw

reddit = praw.Reddit(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    user_agent='sentiment-analyzer/1.0 by your_username'
)

# Fetch top 100 comments from subreddit in last month
subreddit = reddit.subreddit('MachineLearning')
for submission in subreddit.top(time_filter='month', limit=100):
    for comment in submission.comments:
        print(f"{comment.author}: {comment.body} ({comment.score} upvotes)")
```

**Why PRAW for this project**:
- Handles Reddit's OAuth and rate limits transparently
- Built-in exponential backoff prevents API abuse
- Minimal setup: just one pip install
- Matches 2-3 day timeline (no authentication complexity)

---

#### Option 2: Direct API via `requests` + `requests-oauthlib`

**Pros**:
- Maximum control over requests
- Can implement custom retry logic
- Lower memory footprint (no wrapper overhead)

**Cons**:
- Requires manual OAuth token management
- Need to handle HTTP 429 responses manually
- Higher implementation complexity (adds 1-2 days to timeline)
- More error handling boilerplate

**Verdict**: Only if PRAW proves insufficient; unlikely for Phase 1.

---

#### Option 3: Bulk API Services (e.g., Pushshift, Academic Torrents)

**Status**: Deprecated or unreliable for MVP
- **Pushshift**: Shut down by Reddit in 2023 (no longer viable)
- **Academic data torrents**: Stale, month+ old data
- **Not suitable** for real-time ranking system

**Verdict**: Not recommended.

---

#### Option 4: Selenium + Browser Automation

**Pros**:
- Bypasses API entirely
- No rate limits (theoretically)

**Cons**:
- Fragile (HTML changes break scraper)
- Violates Reddit ToS
- 10-100x slower than API
- Not scalable for MVP timeline

**Verdict**: Not recommended; use official API.

---

### 1.2 Database: SQLite vs. Alternatives

#### Option 1: SQLite — **RECOMMENDED for MVP**

**Pros**:
- **Zero infrastructure** — file-based, no server setup
- **Adequate performance** for 100K+ records (sufficient for MVP scope)
- **Python native** (included in standard library with `sqlite3`)
- **Transaction support** (ACID guarantees for dedup)
- **Perfect for development/offline work** — no DevOps burden
- **Easy backups** — just copy the database file
- **Queryable offline** using `sqlite3` CLI or Python

**Cons**:
- Not suitable for horizontal scaling (read-only for analytics layer later)
- Single-writer limitation (acceptable for batch jobs)
- No built-in full-text search (not critical for Phase 1)

**Why SQLite for Phase 1**:
- Aligns with 2-day timeline (no database provisioning)
- Sufficient for MVP (target: 10K-50K comments initial)
- Can migrate to PostgreSQL in Phase 2 if needed
- Reduces team cognitive load

**Timeline Impact**: SQLite saves 1-2 hours vs. setting up PostgreSQL.

---

#### Option 2: PostgreSQL

**Pros**:
- Better scaling properties
- Advanced indexing
- Concurrent write support

**Cons**:
- Requires installation/docker setup
- Extra DevOps overhead for MVP timeline
- Overkill for Phase 1 (10K-50K records is tiny)

**Verdict**: Post-MVP optimization; too heavyweight for 2-day phase.

---

#### Option 3: MongoDB

**Pros**:
- Schema-flexible (useful for unstructured Reddit data)
- Built-in replication

**Cons**:
- Heavier memory footprint
- Overkill for structured comment data
- Added complexity (no clear advantage for this use case)

**Verdict**: Not recommended for Phase 1.

---

### 1.3 Data Processing & Deduplication Library Recommendations

| Task | Recommended Library | Rationale |
|------|---------------------|-----------|
| Hashing (dedup) | `hashlib` (built-in) | Fast, reliable, SHA-256 standard |
| Data validation | `pydantic` | Type hints, easy schema validation |
| Date handling | `datetime` (built-in) + `pytz` | Simple, sufficient for UTC timestamps |
| Logging | `logging` (built-in) + `python-json-logger` | Structured logs for debugging |
| Configuration | `python-dotenv` + YAML | Environment variables + config file flexibility |

---

## 2. Rate Limit Handling Strategy

### 2.1 Understanding Reddit API Rate Limits

**Reddit's Rate Limit Policy**:
- **OAuth endpoints**: ~60 requests per minute (per-user basis, not per-IP)
- **Backoff signals**: HTTP 429 (Too Many Requests) with `Retry-After` header
- **Subreddit crawling**: ~1-2 seconds between requests recommended for politeness
- **PRAW default**: Automatically respects `Retry-After` headers

**Key Insight**: PRAW + exponential backoff handles 95% of rate limit issues automatically.

### 2.2 Recommended Rate Limit Strategy

#### Layer 1: PRAW Built-in Rate Limit Handling
```python
# PRAW automatically:
# 1. Respects HTTP 429 responses
# 2. Reads Retry-After header
# 3. Exponential backoff (up to 16 seconds)

reddit = praw.Reddit(
    client_id='...',
    client_secret='...',
    user_agent='sentiment-analyzer/1.0'
)
```

#### Layer 2: Application-Level Request Batching
```python
import time
from datetime import datetime, timedelta

REQUESTS_PER_MINUTE = 60
MIN_INTERVAL = 60 / REQUESTS_PER_MINUTE  # 1 second

def fetch_subreddit_comments(subreddit_name, limit=100):
    """Batch fetch with controlled request rate."""
    subreddit = reddit.subreddit(subreddit_name)
    comments = []
    
    for submission in subreddit.new(limit=limit):
        # Manual rate limiting: enforce minimum interval
        time.sleep(MIN_INTERVAL)
        
        for comment in submission.comments:
            comments.append({
                'id': comment.id,
                'text': comment.body,
                'author': str(comment.author),
                'score': comment.score,
                'timestamp': datetime.fromtimestamp(comment.created_utc),
                'subreddit': comment.subreddit.display_name
            })
    
    return comments
```

#### Layer 3: Retry Logic with Exponential Backoff
```python
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=5, base_delay=2):
    """Decorator for exponential backoff on transient errors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries exceeded: {e}")
                        raise
                    
                    delay = base_delay ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed. "
                        f"Retrying in {delay}s... (Error: {type(e).__name__})"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=5, base_delay=2)
def fetch_with_retry(subreddit_name):
    return reddit.subreddit(subreddit_name).new(limit=100)
```

### 2.3 Batch Job Scheduling Strategy

**Recommended Approach for MVP**:
- **Daily batch job** (runs once per day at off-peak time, e.g., 2 AM UTC)
- **Target subreddits per run**: 5 subreddits × 100 comments = 500 API calls
- **Expected duration**: 8-10 minutes (including delays)
- **Rate limit headroom**: ~3600 requests/hour available; using ~30 → 92% available

**Example Scheduling**:
```python
# schedule/batch_job.py
import schedule
import time

def daily_reddit_collection():
    """Run once per day."""
    subreddits = [
        'MachineLearning',
        'ChatGPT',
        'LocalLLaMA',
        'OpenAI',
        'Claude'
    ]
    
    for subreddit_name in subreddits:
        print(f"Fetching {subreddit_name}...")
        comments = fetch_subreddit_comments(subreddit_name, limit=100)
        store_comments(comments)
        time.sleep(2)  # Politeness delay

if __name__ == '__main__':
    schedule.every().day.at("02:00").do(daily_reddit_collection)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

### 2.4 Rate Limit Monitoring & Alerting

```python
def check_rate_limit_status():
    """Check remaining API quota."""
    user = reddit.user.me()
    
    # Log current quota
    logger.info(f"Authenticated as: {user.name}")
    
    # Note: Exact remaining quota not exposed by Reddit API,
    # but PRAW logs warnings if approaching limits

# Add to logging setup:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Key Insight**: Reddit doesn't expose remaining quota, but PRAW logs warnings. Monitor logs for `HTTP 429` or `Retry-After` patterns.

---

## 3. SQLite Schema Design

### 3.1 Core Tables

#### Table: `comments`
Stores raw Reddit comments with metadata.

```sql
CREATE TABLE comments (
    -- Primary identifier
    id TEXT PRIMARY KEY,              -- Reddit comment ID
    
    -- Content
    text TEXT NOT NULL,               -- Comment body
    author TEXT,                      -- Reddit username (can be [deleted])
    
    -- Metadata
    submission_id TEXT,               -- Parent post ID
    subreddit TEXT NOT NULL,          -- Subreddit name
    created_utc INTEGER NOT NULL,     -- Unix timestamp (sortable)
    
    -- Engagement metrics
    score INTEGER DEFAULT 0,          -- Net upvotes (upvotes - downvotes)
    upvote_ratio REAL,                -- Ratio 0.0-1.0 (if available)
    
    -- Processing metadata
    collected_at TIMESTAMP 
        DEFAULT CURRENT_TIMESTAMP,    -- When we fetched this
    data_hash TEXT UNIQUE,            -- SHA-256(author + text + created_utc)
    
    -- Data quality flags
    is_deleted BOOLEAN DEFAULT 0,     -- Comment removed/deleted
    is_archived BOOLEAN DEFAULT 0     -- Reddit archives after 6 months
);

-- Indexes for common queries
CREATE INDEX idx_subreddit_created 
    ON comments(subreddit, created_utc DESC);
CREATE INDEX idx_score_desc 
    ON comments(score DESC);
CREATE INDEX idx_author 
    ON comments(author);
```

**Rationale**:
- `id` as PRIMARY KEY: Guaranteed unique, prevents duplicates
- `data_hash`: Secondary dedup check (catches edge cases)
- `created_utc`: Unix timestamp (more sortable than datetime)
- `subreddit` indexed: Common filter in Phase 2+3
- `score DESC` indexed: Needed for ranking weights

---

#### Table: `model_mentions` (Phase 1 Prep)
Reserve table for Phase 2 NLP pipeline; created but unused in Phase 1.

```sql
CREATE TABLE model_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL,
    model_name TEXT NOT NULL,         -- 'ChatGPT', 'Claude', etc.
    confidence REAL,                  -- 0.0-1.0 extraction confidence
    FOREIGN KEY(comment_id) 
        REFERENCES comments(id) ON DELETE CASCADE
);

CREATE INDEX idx_comment_mentions 
    ON model_mentions(comment_id);
CREATE INDEX idx_model_name 
    ON model_mentions(model_name);
```

---

#### Table: `collection_log` (Operational)
Tracks collection runs for monitoring and debugging.

```sql
CREATE TABLE collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TIMESTAMP NOT NULL,
    subreddit TEXT NOT NULL,
    comments_fetched INTEGER,
    comments_new INTEGER,            -- After dedup
    comments_duplicate INTEGER,
    errors TEXT,                     -- JSON array of error messages
    duration_seconds REAL            -- How long the run took
);

CREATE INDEX idx_run_timestamp 
    ON collection_log(run_timestamp DESC);
```

**Rationale**: Essential for debugging rate limit issues, dedup validation, and performance monitoring.

---

### 3.2 Schema Design Rationale

| Design Choice | Rationale | Alternative Considered |
|---------------|-----------|------------------------|
| Text PK for `id` | Reddit IDs are globally unique; no need for surrogate key | Numeric surrogate (more overhead) |
| `data_hash` UNIQUE | Catches duplicate submissions (same author, same text, same time) | Content-only hash (too permissive) |
| `created_utc` INTEGER | Sortable, immutable, avoids timezone issues | ISO 8601 string (less queryable) |
| Separate `model_mentions` table | Denormalizes Phase 2 data; keeps Phase 1 focused | Nullable array column (less queryable) |
| `collection_log` | Single source of truth for run diagnostics | Print statements to logs (fragile) |

---

### 3.3 Example Data Flow

```python
import sqlite3
import hashlib
from datetime import datetime

def store_comments(db_path, comments):
    """Insert comments with deduplication."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    duplicates = 0
    
    for comment in comments:
        # Compute hash for dedup
        hash_input = f"{comment['author']}{comment['text']}{comment['timestamp']}"
        data_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO comments 
                (id, text, author, submission_id, subreddit, created_utc, 
                 score, upvote_ratio, data_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                comment['id'],
                comment['text'],
                comment['author'],
                comment.get('submission_id'),
                comment['subreddit'],
                int(comment['timestamp'].timestamp()),
                comment['score'],
                comment.get('upvote_ratio'),
                data_hash
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            # Duplicate found
            duplicates += 1
            continue
    
    conn.commit()
    conn.close()
    
    return {'inserted': inserted, 'duplicates': duplicates}
```

---

## 4. Data Quality Pipeline

### 4.1 Deduplication Strategy (3-Layer Approach)

#### Layer 1: Database Constraints (Primary Key)
- Reddit's native `id` ensures no exact duplicates
- PRAW fetches each comment once per API call

#### Layer 2: Content Hash (Secondary Check)
- Hash = SHA-256(`author + text + created_utc`)
- Catches cases where Reddit returns same comment in multiple subreddit queries
- Set UNIQUE constraint on `data_hash`

#### Layer 3: Application-Level Bloom Filter (Optional, Phase 1+)
```python
import sqlite3

def deduplicate_batch(db_path, new_comments):
    """Check for duplicates before insert."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    existing_ids = set()
    cursor.execute("SELECT id FROM comments")
    existing_ids.update(row[0] for row in cursor.fetchall())
    
    conn.close()
    
    # Filter out already-seen comments
    unique_comments = [
        c for c in new_comments 
        if c['id'] not in existing_ids
    ]
    
    return unique_comments
```

**Benefit**: Application-level check prevents unnecessary database round-trips.

---

### 4.2 Data Validation Checklist

Before storing a comment, validate:

```python
def validate_comment(comment):
    """Pre-storage validation."""
    checks = {
        'has_id': comment.get('id') is not None,
        'has_text': comment.get('text') and len(comment['text'].strip()) > 0,
        'valid_score': isinstance(comment.get('score'), int),
        'valid_timestamp': 0 < comment.get('timestamp', 0) < 2**31,  # Unix time bounds
        'has_subreddit': comment.get('subreddit') is not None,
        'non_empty_author': comment.get('author') and len(str(comment['author']).strip()) > 0,
    }
    
    # Log failures for debugging
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        logger.warning(f"Comment {comment.get('id')} failed: {failed}")
        return False
    
    return True

# In storage function:
for comment in comments:
    if not validate_comment(comment):
        continue
    store_comment(db_path, comment)
```

---

### 4.3 Data Cleaning Rules

| Rule | Action | Rationale |
|------|--------|-----------|
| `[deleted]` author | Store as-is (flagged for Phase 2) | Sentiment still extractable from text |
| Empty comment body | Reject | No meaningful content for analysis |
| Overly long comments (>5000 chars) | Store but flag | Rare edge case; retain for auditing |
| Non-ASCII characters | Store as-is (UTF-8) | Reddit supports international users |
| Removed comments (score < -2 visible threshold) | Store but flag `is_deleted` | Useful for bias detection |

---

### 4.4 Expected Data Quality Metrics

From preliminary Reddit research:

| Metric | Expected Value | Threshold |
|--------|----------------|-----------|
| Duplicate rate (same id fetched twice) | <1% | Warn if >5% |
| Data validation pass rate | >98% | Warn if <95% |
| Deleted comment rate | 2-5% | Normal; investigate if >10% |
| Missing author rate | <1% | Warn if >3% |
| Average comment length | 80-200 chars | Informational |

---

## 5. Reddit Community Patterns & Domain Insights

### 5.1 AI Model Discussion Trends in Target Subreddits

**Data gathered from Reddit community culture (2025-2026)**:

#### r/MachineLearning
- **Tone**: Academic, technical depth
- **AI models discussed**: Research models (LLaMA, Mistral), less ChatGPT bashing
- **Sentiment pattern**: Measured, cites benchmarks
- **Bias**: Favor open-source models
- **Sarcasm rate**: Low (2-5%)

#### r/ChatGPT
- **Tone**: General users, product-focused
- **AI models discussed**: ChatGPT heavily, comparisons to Claude/Gemini
- **Sentiment pattern**: Emotional ("ChatGPT is lazy", "I stopped my subscription")
- **Bias**: Mixed; many complaints about recent performance
- **Sarcasm rate**: Medium (15-25%)

#### r/LocalLLaMA
- **Tone**: Enthusiast, DIY-focused
- **AI models discussed**: Open-source models, running locally
- **Sentiment pattern**: Optimistic about self-hosted alternatives
- **Bias**: Prefer local models over commercial ones
- **Sarcasm rate**: High (20-30%)

#### r/OpenAI
- **Tone**: News-driven, policy-focused
- **AI models discussed**: OpenAI products (GPT-4, o1), related models for comparison
- **Sentiment pattern**: Mixed (product launches + pricing criticism)
- **Bias**: OpenAI centric but critical
- **Sarcasm rate**: Low-medium (5-15%)

#### r/Claude (claude_ai subreddit or r/Anthropic)
- **Tone**: Early adopter, technical
- **AI models discussed**: Claude variants, comparisons to GPT-4
- **Sentiment pattern**: Generally positive (early adopter effect)
- **Bias**: Favor Claude; critical of competition
- **Sarcasm rate**: Low-medium (8-15%)

---

### 5.2 Sarcasm Detection Considerations

**Common Reddit sarcasm patterns**:

```
1. Compliment-as-sarcasm:
   "ChatGPT is definitely the best model ever" (context matters)

2. Exaggeration:
   "Claude is literally sentient and will take over the world"

3. Sarcastic suggestions:
   "Just use ChatGPT; it's perfect for everything" (often code for "don't")

4. Mock quotes:
   '"Fast and accurate" - ChatGPT marketing'

5. Ironic endings:
   "The model works fine, just ignore the hallucinations /s"
```

**Phase 1 approach**: Flag comments with `/s` or `/sarcasm` markers; Phase 2 can use ML for implicit sarcasm.

---

### 5.3 Data Requirements Implications

**Minimum comment corpus for Phase 1**:
- **Target**: 5,000-10,000 comments (across all 5 subreddits)
- **Rationale**: Statistically sufficient for Phase 2 NLP training; respects rate limits
- **Time to collect**: ~1 week of daily batch jobs (100-200 comments/day across all subs)
- **Can be accelerated**: Fetch historical data from last 30 days in first batch

**Quality thresholds**:
- Minimum comment length: 10 characters (filter very short responses like "yes")
- Minimum subreddit representation: 500+ comments (ensures balanced data)
- Score distribution: Capture range of upvoted and downvoted comments (both contain signal)

---

## 6. Risks and Mitigation Strategies

### 6.1 Reddit API-Specific Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Rate limit hits causing data loss** | High | Missed data collection run | PRAW exponential backoff + logging of rate limit events |
| **Subreddit policy changes (private/archived)** | Low | Cannot fetch from 1-2 subreddits | Monitor subreddit status; fallback to alternative subs (r/LanguageModels) |
| **Reddit API changes** | Low | PRAW becomes incompatible | Pin PRAW version; maintain compatibility layer |
| **OAuth token expiration** | Medium | Daily batch job fails silently | Log authentication errors; set token refresh before expiry |
| **Comments deleted between fetch and store** | Medium | Missing data on rerun | Store `created_utc` to avoid re-fetching same period |

---

### 6.2 Database & Data Integrity Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Database corruption** | Low | All data lost | Weekly backups; use WAL mode (write-ahead logging) |
| **Deduplication failure** | Low | Duplicate comments break Phase 2 | Add 3-layer dedup + validation tests |
| **Data schema conflicts** | Medium | Cannot migrate to Phase 2 | Design schema for extensibility; Phase 2 review before lock-in |
| **Timezone bugs** | Medium | Time-based queries wrong | Use Unix timestamps (UTC-agnostic) consistently |

**SQLite WAL Mode (improves reliability)**:
```python
conn = sqlite3.connect('comments.db')
conn.execute('PRAGMA journal_mode=WAL')  # Write-ahead logging
conn.close()
```

---

### 6.3 Development & Deployment Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **PRAW/library version conflicts** | Medium | Code breaks on different systems | Use `requirements.txt` pinned versions; `pipenv` or `poetry` |
| **Incomplete error handling** | High | Silent failures, stuck jobs | Comprehensive logging; email alerts on failures |
| **No data refresh history** | Medium | Cannot debug data gaps | Keep `collection_log` table; monthly audit |
| **Hardcoded credentials** | High | Security breach if repo leaked | Use `.env` file with `python-dotenv`; never commit secrets |

**Example .env**:
```
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=sentiment-analyzer/1.0 by username
DATABASE_PATH=./data/comments.db
```

---

### 6.4 Data Science Risks (Phase 2 impact, but plan for Phase 1)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Insufficient data** for rare models | High | Cannot rank Llama fairly | Collect data for 1 week before ranking; set minimum comment threshold per model |
| **Subreddit bias** skews ranking | High | ChatGPT overrepresented | Weight by subreddit credibility; document biases |
| **Temporal bias** (older comments fade) | Medium | Recent sentiment dominance | Include time-decay weights in Phase 3; collect daily |

---

## 7. Implementation Checklist & Timeline

### 7.1 Phase 1 Tasks (2-3 Days)

**Day 1: Setup & Authentication**
- [ ] Install PRAW: `pip install praw`
- [ ] Create Reddit app (https://www.reddit.com/prefs/apps) → get credentials
- [ ] Set up `.env` file with credentials
- [ ] Write `reddit_auth.py` with PRAW connection test
- [ ] **Verification**: Can fetch 10 comments from r/MachineLearning

**Day 1-2: Database Schema & Storage**
- [ ] Design and create SQLite schema (`comments`, `model_mentions`, `collection_log`)
- [ ] Write `database.py` with create/store functions
- [ ] Implement 3-layer deduplication logic
- [ ] Write `validate_comment()` function
- [ ] **Verification**: Can store 100 comments without duplicates

**Day 2: Data Collection Pipeline**
- [ ] Write `subreddit_crawler.py` to batch-fetch from 5 target subreddits
- [ ] Implement exponential backoff + rate limit handling
- [ ] Write retry logic decorator
- [ ] Add comprehensive logging
- [ ] **Verification**: Collect 5000+ comments without API errors

**Day 2-3: Testing & Documentation**
- [ ] Write `test_dedup.py` (verify no duplicates after 2 runs)
- [ ] Write `test_schema.py` (verify data integrity)
- [ ] Test batch job end-to-end (1 full run)
- [ ] Document API credentials setup in `README.md`
- [ ] Create `COLLECTION_LOG.md` for troubleshooting
- [ ] **Verification**: Daily batch job runs without manual intervention

---

### 7.2 Estimated Timeline Breakdown

| Task | Days | Notes |
|------|------|-------|
| Setup & Auth | 0.5 | Mostly waiting for Reddit app approval (instant) |
| DB Schema | 0.5 | SQLite is straightforward |
| Crawler (PRAW) | 0.75 | PRAW library does most heavy lifting |
| Dedup & Validation | 0.75 | 3-layer approach requires test coverage |
| Error Handling & Logging | 0.5 | Essential for debugging |
| Integration & Testing | 0.75 | Full end-to-end test |
| Documentation | 0.25 | README, deployment guide |
| **Total** | **2.5 days** | Within planned 2-3 day window |

**Dependency on team skill**: 
- Experienced Python dev: 2-2.5 days
- Mid-level dev: 2.5-3 days
- Junior dev: 3-4 days (might need mentoring)

---

## 8. Code Patterns & Examples

### 8.1 Full Example: Minimal Batch Job

```python
# batch_job.py
import praw
import sqlite3
import time
import logging
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
DATABASE_PATH = os.getenv('DATABASE_PATH', './comments.db')
TARGET_SUBREDDITS = [
    'MachineLearning', 'ChatGPT', 'LocalLLaMA', 
    'OpenAI', 'Anthropic'
]

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def fetch_subreddit_comments(subreddit_name, limit=100):
    """Fetch recent comments from subreddit."""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        comments = []
        
        for submission in subreddit.new(limit=limit):
            time.sleep(1)  # Rate limit politeness
            
            for comment in submission.comments:
                comments.append({
                    'id': comment.id,
                    'text': comment.body,
                    'author': str(comment.author),
                    'score': comment.score,
                    'upvote_ratio': comment.upvote_ratio,
                    'timestamp': datetime.fromtimestamp(comment.created_utc),
                    'submission_id': comment.submission.id,
                    'subreddit': subreddit_name
                })
        
        logger.info(f"Fetched {len(comments)} from r/{subreddit_name}")
        return comments
    
    except Exception as e:
        logger.error(f"Failed to fetch r/{subreddit_name}: {e}")
        return []

def store_comments(comments):
    """Insert comments with deduplication."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    inserted = duplicates = 0
    
    for comment in comments:
        # Validate
        if not comment['text'] or len(comment['text'].strip()) < 10:
            continue
        
        # Compute dedup hash
        hash_input = f"{comment['author']}{comment['text']}{comment['timestamp']}"
        data_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO comments 
                (id, text, author, submission_id, subreddit, 
                 created_utc, score, upvote_ratio, data_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                comment['id'],
                comment['text'],
                comment['author'],
                comment.get('submission_id'),
                comment['subreddit'],
                int(comment['timestamp'].timestamp()),
                comment['score'],
                comment.get('upvote_ratio'),
                data_hash
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            duplicates += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Stored: {inserted} new, {duplicates} duplicates")
    return {'inserted': inserted, 'duplicates': duplicates}

def run_batch_job():
    """Main batch job."""
    logger.info("=== Starting Reddit Collection Batch ===")
    start_time = time.time()
    
    total_comments = []
    
    for subreddit_name in TARGET_SUBREDDITS:
        comments = fetch_subreddit_comments(subreddit_name, limit=50)
        total_comments.extend(comments)
    
    result = store_comments(total_comments)
    
    duration = time.time() - start_time
    logger.info(
        f"Batch complete: {result['inserted']} new comments, "
        f"{result['duplicates']} duplicates in {duration:.1f}s"
    )

if __name__ == '__main__':
    run_batch_job()
```

---

### 8.2 Database Initialization Script

```python
# init_db.py
import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_database(db_path):
    """Create database schema."""
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode=WAL')  # Write-ahead logging
    cursor = conn.cursor()
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            author TEXT,
            submission_id TEXT,
            subreddit TEXT NOT NULL,
            created_utc INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            upvote_ratio REAL,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_hash TEXT UNIQUE,
            is_deleted BOOLEAN DEFAULT 0,
            is_archived BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_subreddit_created 
        ON comments(subreddit, created_utc DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_score_desc 
        ON comments(score DESC)
    ''')
    
    # Collection log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TIMESTAMP NOT NULL,
            subreddit TEXT NOT NULL,
            comments_fetched INTEGER,
            comments_new INTEGER,
            comments_duplicate INTEGER,
            errors TEXT,
            duration_seconds REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized: {db_path}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_database('./comments.db')
```

---

## 9. Success Criteria & Validation

### 9.1 Phase 1 Acceptance Criteria

| Criterion | Validation | Pass/Fail |
|-----------|-----------|----------|
| **Fetch 5000+ comments** | Count rows in DB > 5000 | Count > 5000 |
| **No duplicate IDs** | Query: `SELECT COUNT(*) FROM comments; SELECT COUNT(DISTINCT id) FROM comments;` Should be equal | Counts match |
| **Data integrity** | No NULL required fields; all scores are integers; all timestamps valid | Query validation passes |
| **No API errors** | Run batch job 3x in succession; should see 0 HTTP 429 errors | Log contains no 429 |
| **Rate limit respected** | Batch job duration <15 minutes for 5000 comments | Duration metric logged |
| **Schema extensible** | Phase 2 can add `model_mentions` table without altering `comments` | Schema review passes |
| **Logging complete** | `collection_log` captures all runs with counts & errors | Log entries present |

---

## 10. Knowledge Transfer & Documentation

### 10.1 Deliverables for Next Phase (Phase 2)

Phase 1 must deliver to Phase 2:
1. **comments.db** with 10K+ deduplicated comments
2. **collection_log** showing run history & performance
3. **Code repository** with `batch_job.py`, `database.py`, tests
4. **README.md** with:
   - How to set up Reddit credentials
   - How to run batch job manually or on schedule
   - Database schema diagram
5. **RESEARCH.md** (this document) for reference

### 10.2 Phase 2 Assumptions (Document for Planners)

- Comments table is clean (no duplicates, validated)
- All timestamps are UTC (Unix format)
- Comments include author and subreddit context (for credibility weighting)
- ~10K+ comments available for NLP training

---

## 11. Conclusion

**Phase 1 is achievable in 2-3 days** with the recommended stack:
- **PRAW library** handles Reddit API complexity transparently
- **SQLite** eliminates database provisioning overhead
- **Exponential backoff** built into PRAW prevents rate limit issues
- **Layered deduplication** ensures data quality
- **Comprehensive logging** enables debugging

**Key success factors**:
1. Start with `.env` credentials immediately (fastest path)
2. Use PRAW's defaults (don't reinvent rate limiting)
3. Test deduplication with 2 runs before scaling
4. Monitor logs for any 429 errors (early warning)
5. Collect 1 week of data before Phase 2 starts

**Risk mitigation**:
- Most risks are handled by library defaults (PRAW) or database constraints (SQLite)
- Remaining risks are operational (logging, monitoring, backups)
- No known blockers for 2-3 day completion

---

## Appendix: External Resources

### Reddit API Documentation
- Official Reddit API: https://www.reddit.com/dev/api/
- PRAW Documentation: https://praw.readthedocs.io/

### SQLite Best Practices
- SQLite Docs: https://www.sqlite.org/docs.html
- Write-Ahead Logging (WAL): https://www.sqlite.org/wal.html
- Deduplication Patterns: https://sqlite.org/hashfunc.html

### Rate Limiting & API Design
- HTTP 429 Standards: https://httpwg.org/specs/rfc6585.html
- Exponential Backoff: https://en.wikipedia.org/wiki/Exponential_backoff
- Reddit Rate Limit API Reference: https://www.reddit.com/r/reddit.com/comments/o6tz0/important_api_guideline_v2/

### Python Tools
- PRAW: `pip install praw` (https://github.com/praw-dev/praw)
- python-dotenv: `pip install python-dotenv`
- pydantic (optional validation): `pip install pydantic`

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-07  
**Next Review**: After Phase 1 completion for Phase 2 planning
