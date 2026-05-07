# Phase 1: Data Collection & Infrastructure — Detailed Plan

**Project**: AI Model Ranking via Reddit Sentiment Analysis  
**Phase**: Phase 1 — Data Collection & Infrastructure  
**Duration**: 2-3 days  
**Team**: 2-3 developers (backend focus)  
**Created**: 2026-05-07  
**Planner**: gsd-planner

---

## Goal

Establish a robust Reddit data pipeline that collects 5,000-10,000 AI model mentions from target subreddits into a SQLite database, with built-in deduplication and rate limit handling, ready for NLP processing in Phase 2.

---

## Phase Decomposition

### Work Stream 1: Reddit API Integration & Authentication
**Objective**: Securely connect to Reddit API using PRAW library with proper credential management.  
**Owner**: Backend engineer (1 day)  
**Deliverables**: 
- PRAW Reddit client initialized and authenticated
- Credentials secured in `.env` file
- Basic comment fetching tested (10+ comments successfully retrieved)
- Error handling for auth failures

---

### Work Stream 2: SQLite Database Schema & Storage Layer
**Objective**: Design and implement database schema for comments with deduplication support.  
**Owner**: Backend engineer / Database owner (0.75 days)  
**Deliverables**:
- Three-table SQLite schema (comments, model_mentions, collection_log)
- Database initialization script with proper indexes
- Write-ahead logging (WAL) enabled for reliability
- Storage module with insert/retrieve operations

---

### Work Stream 3: Data Collection & Crawling Pipeline
**Objective**: Build multi-subreddit crawler with batching, rate limit handling, and retry logic.  
**Owner**: Backend engineer (1 day)  
**Deliverables**:
- Subreddit crawler for 5 target communities
- Exponential backoff + request batching (1-2s delays)
- Comprehensive error logging
- Batch job controller (runnable end-to-end)

---

### Work Stream 4: Data Quality & Deduplication
**Objective**: Implement 3-layer deduplication to ensure <1% duplicate rate.  
**Owner**: Backend engineer / QA engineer (1 day)  
**Deliverables**:
- Primary key deduplication (Reddit ID)
- Content hash deduplication (SHA-256)
- Application-level validation layer
- Deduplication test suite with success metrics

---

### Work Stream 5: Testing, Documentation & Deployment
**Objective**: Validate end-to-end pipeline, document setup, and prepare for Phase 2 handoff.  
**Owner**: Backend engineer / Tech lead (0.5 days)  
**Deliverables**:
- Integration tests (full batch job run)
- Schema validation tests
- API credential setup documentation
- Troubleshooting guide (COLLECTION_LOG.md)
- Deployment checklist

---

## Task Breakdown

### P1-T1: Reddit App Setup & Credential Management
**Status**: Ready to start  
**Assigned to**: Backend lead  
**Duration**: 0.25 days  
**Dependencies**: None  

**Description**:
Create a Reddit app on the Reddit developer console to obtain OAuth credentials (client_id, client_secret). Store credentials securely in a `.env` file using `python-dotenv` for local development, ensuring no secrets are committed to Git.

**Deliverables**:
- Reddit app registered at https://www.reddit.com/prefs/apps
- `.env` file created with format:
  ```
  REDDIT_CLIENT_ID=your_client_id
  REDDIT_CLIENT_SECRET=your_client_secret
  REDDIT_USER_AGENT=sentiment-analyzer/1.0 by your_reddit_username
  DATABASE_PATH=./data/comments.db
  TARGET_SUBREDDITS=MachineLearning,ChatGPT,LocalLLaMA,OpenAI,Claude
  ```
- `.gitignore` updated to exclude `.env`
- `requirements.txt` with `praw>=7.7.0` and `python-dotenv>=0.21.0`

**Success Criteria**:
- ✓ Reddit app created and credentials obtained
- ✓ `.env` file loads without errors
- ✓ No credentials visible in Git history

**Verification Steps**:
1. Verify `.env` exists and contains all 5 required keys
2. Run `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('REDDIT_USER_AGENT'))"` → outputs user agent
3. Confirm `.env` is in `.gitignore`

**Testing**:
```python
# test_credentials.py
import os
from dotenv import load_dotenv

def test_env_loaded():
    load_dotenv()
    assert os.getenv('REDDIT_CLIENT_ID'), "CLIENT_ID not found"
    assert os.getenv('REDDIT_CLIENT_SECRET'), "CLIENT_SECRET not found"
    assert os.getenv('REDDIT_USER_AGENT'), "USER_AGENT not found"
    print("✓ Credentials loaded successfully")
```

---

### P1-T2: PRAW Connection & Authentication Test
**Status**: Ready (blocked until P1-T1 complete)  
**Assigned to**: Backend lead  
**Duration**: 0.25 days  
**Dependencies**: → P1-T1  

**Description**:
Initialize PRAW Reddit client using credentials from `.env`, verify successful authentication, and confirm ability to fetch comments. Build a reusable `reddit_auth.py` module that other tasks will depend on.

**Deliverables**:
- `reddit_auth.py` module with:
  ```python
  import praw
  from dotenv import load_dotenv
  import os
  
  def get_reddit_client():
      """Initialize authenticated Reddit client."""
      load_dotenv()
      return praw.Reddit(
          client_id=os.getenv('REDDIT_CLIENT_ID'),
          client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
          user_agent=os.getenv('REDDIT_USER_AGENT')
      )
  
  def test_connection():
      """Verify successful authentication."""
      reddit = get_reddit_client()
      user = reddit.user.me()
      print(f"Authenticated as: {user.name}")
      return reddit
  ```
- Test script that successfully fetches 10 comments from r/MachineLearning
- Documented error handling for:
  - Invalid credentials (401 Unauthorized)
  - API unavailability (503 Service Unavailable)
  - Rate limit errors (429 Too Many Requests)

**Success Criteria**:
- ✓ PRAW client authenticates without errors
- ✓ Can fetch comments from at least 1 subreddit
- ✓ Error messages are clear and actionable

**Verification Steps**:
1. Run test: `python -c "from reddit_auth import test_connection; reddit = test_connection()"`
2. Confirm output: `Authenticated as: <your_reddit_username>`
3. Test invalid credentials → confirm error message
4. Test rate limit handling (intentional pause) → confirm no crash

**Testing**:
```python
# test_praw_auth.py
from reddit_auth import get_reddit_client

def test_authentication():
    reddit = get_reddit_client()
    user = reddit.user.me()
    assert user.name is not None, "Authentication failed"
    print(f"✓ Authenticated as {user.name}")

def test_fetch_comments():
    reddit = get_reddit_client()
    subreddit = reddit.subreddit('MachineLearning')
    comments = list(subreddit.new(limit=10))
    assert len(comments) >= 10, f"Expected 10+ comments, got {len(comments)}"
    print(f"✓ Fetched {len(comments)} comments")
```

---

### P1-T3: SQLite Database Schema & Initialization
**Status**: Ready (can run in parallel with P1-T2)  
**Assigned to**: Database owner  
**Duration**: 0.5 days  
**Dependencies**: None  

**Description**:
Design and create SQLite database schema with three tables (`comments`, `model_mentions`, `collection_log`) optimized for Phase 1 data collection and Phase 2+ queries. Enable write-ahead logging (WAL) for reliability.

**Deliverables**:
- `database.py` module with schema creation:
  ```python
  CREATE TABLE comments (
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
  );
  
  CREATE TABLE model_mentions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      comment_id TEXT NOT NULL,
      model_name TEXT NOT NULL,
      confidence REAL,
      FOREIGN KEY(comment_id) REFERENCES comments(id) ON DELETE CASCADE
  );
  
  CREATE TABLE collection_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_timestamp TIMESTAMP NOT NULL,
      subreddit TEXT NOT NULL,
      comments_fetched INTEGER,
      comments_new INTEGER,
      comments_duplicate INTEGER,
      errors TEXT,
      duration_seconds REAL
  );
  ```
- Indexes on:
  - `comments.id` (primary key)
  - `comments(subreddit, created_utc DESC)`
  - `comments(score DESC)`
  - `model_mentions(comment_id)`
  - `model_mentions(model_name)`
  - `collection_log(run_timestamp DESC)`
- Database initialization script:
  ```python
  def init_database(db_path='./data/comments.db'):
      """Create database and enable WAL mode."""
      conn = sqlite3.connect(db_path)
      conn.execute('PRAGMA journal_mode=WAL')
      cursor = conn.cursor()
      cursor.executescript(SCHEMA_SQL)
      conn.commit()
      conn.close()
  ```
- Data directory created: `./data/`

**Success Criteria**:
- ✓ Database initializes without errors
- ✓ All tables created with correct schema
- ✓ WAL mode enabled
- ✓ Can connect and query empty database

**Verification Steps**:
1. Run `python database.py` → database.db created in ./data/
2. Run `sqlite3 ./data/comments.db ".tables"` → output shows 3 tables
3. Run `sqlite3 ./data/comments.db "PRAGMA journal_mode;"` → output shows "wal"
4. Run schema test → all 3 tables exist with expected columns

**Testing**:
```python
# test_schema.py
import sqlite3

def test_schema_exists():
    conn = sqlite3.connect('./data/comments.db')
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert tables == {'comments', 'model_mentions', 'collection_log'}, f"Unexpected tables: {tables}"
    
    # Check comments columns
    cursor.execute("PRAGMA table_info(comments)")
    columns = {row[1] for row in cursor.fetchall()}
    expected = {'id', 'text', 'author', 'subreddit', 'created_utc', 'data_hash', 'score'}
    assert expected.issubset(columns), f"Missing columns: {expected - columns}"
    
    conn.close()
    print("✓ Schema validation passed")
```

---

### P1-T4: Data Storage & Deduplication Module
**Status**: Ready (blocked until P1-T3 complete)  
**Assigned to**: Backend engineer  
**Duration**: 0.75 days  
**Dependencies**: → P1-T3  

**Description**:
Implement storage layer with 3-layer deduplication: (1) primary key check, (2) content hash uniqueness, (3) application-level validation. Build `storage.py` module with functions to insert comments, validate data, and log collection runs.

**Deliverables**:
- `storage.py` module with:
  - `store_comments(db_path, comments_list)` → returns `{'inserted': int, 'duplicates': int, 'errors': int}`
  - `validate_comment(comment)` → checks all required fields
  - `compute_data_hash(author, text, created_utc)` → SHA-256 hash
  - `log_collection_run(db_path, subreddit, stats)` → records collection metrics
  
- Deduplication logic:
  ```python
  def store_comments(db_path, comments):
      """3-layer dedup: PK + hash + app-level."""
      inserted, duplicates, errors = 0, 0, 0
      
      conn = sqlite3.connect(db_path)
      cursor = conn.cursor()
      
      # Layer 1: Load existing IDs (app-level check)
      cursor.execute("SELECT id FROM comments")
      existing_ids = {row[0] for row in cursor.fetchall()}
      
      for comment in comments:
          # Layer 0: Validation
          if not validate_comment(comment):
              errors += 1
              continue
          
          # Layer 1: App-level ID check
          if comment['id'] in existing_ids:
              duplicates += 1
              continue
          
          # Layer 2: Compute hash
          data_hash = compute_data_hash(
              comment.get('author', ''),
              comment.get('text', ''),
              comment.get('created_utc', 0)
          )
          
          try:
              # Layer 3: DB constraints (PK + hash UNIQUE)
              cursor.execute('''
                  INSERT INTO comments 
                  (id, text, author, submission_id, subreddit, created_utc, 
                   score, upvote_ratio, data_hash)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
              ''', (
                  comment['id'],
                  comment['text'],
                  comment.get('author'),
                  comment.get('submission_id'),
                  comment['subreddit'],
                  int(comment.get('created_utc', 0)),
                  comment.get('score', 0),
                  comment.get('upvote_ratio'),
                  data_hash
              ))
              inserted += 1
          except sqlite3.IntegrityError:
              duplicates += 1
      
      conn.commit()
      conn.close()
      
      return {'inserted': inserted, 'duplicates': duplicates, 'errors': errors}
  ```
- Validation rules (reject if):
  - Missing `id`
  - Missing or empty `text` (len < 10 chars)
  - Invalid `score` (not int)
  - Invalid `created_utc` (outside Unix time bounds)
  - Missing `subreddit`
  
- Logging to `collection_log` table with:
  - `run_timestamp` (when collection started)
  - `subreddit` (which subreddit)
  - `comments_fetched` (API returned count)
  - `comments_new` (actually inserted)
  - `comments_duplicate` (duplicate count)
  - `duration_seconds` (how long run took)

**Success Criteria**:
- ✓ Stores 100+ comments without errors
- ✓ Duplicate rate <1% (if same 100 comments stored twice, <2 stored)
- ✓ Data hash consistently computed (same comment → same hash)
- ✓ All required fields present in stored data

**Verification Steps**:
1. Store 100 test comments → returns `{'inserted': 100, 'duplicates': 0, 'errors': 0}`
2. Store same 100 comments again → returns `{'inserted': 0, 'duplicates': 100, 'errors': 0}`
3. Query database: `SELECT COUNT(*) FROM comments` → 100
4. Verify `data_hash` column populated and UNIQUE constraint works

**Testing**:
```python
# test_deduplication.py
from storage import store_comments, compute_data_hash

def test_dedup_primary_key():
    """Test Layer 1: PK prevents exact duplicates."""
    comments = [
        {'id': 'c1', 'text': 'test', 'author': 'user1', 'subreddit': 'test', 'created_utc': 1000},
        {'id': 'c1', 'text': 'test', 'author': 'user1', 'subreddit': 'test', 'created_utc': 1000},
    ]
    result = store_comments('./data/comments.db', comments)
    assert result['inserted'] == 1 and result['duplicates'] == 1, "PK dedup failed"
    print("✓ Primary key deduplication works")

def test_dedup_content_hash():
    """Test Layer 2: Content hash catches modified IDs."""
    comment1 = {'id': 'c1', 'text': 'same', 'author': 'u1', 'subreddit': 's1', 'created_utc': 1000}
    comment2 = {'id': 'c2', 'text': 'same', 'author': 'u1', 'subreddit': 's1', 'created_utc': 1000}  # Different ID, same content
    
    hash1 = compute_data_hash(comment1.get('author', ''), comment1['text'], comment1['created_utc'])
    hash2 = compute_data_hash(comment2.get('author', ''), comment2['text'], comment2['created_utc'])
    
    assert hash1 == hash2, "Hash mismatch for identical content"
    print("✓ Content hash deduplication works")
```

---

### P1-T5: Subreddit Crawler with Rate Limiting & Retry Logic
**Status**: Ready (blocked until P1-T2 complete)  
**Assigned to**: Backend engineer  
**Duration**: 1 day  
**Dependencies**: → P1-T2  

**Description**:
Build multi-subreddit crawler that batches requests with exponential backoff, respects Reddit rate limits (60 req/min), and handles transient errors gracefully. Crawler must fetch 100-200 comments per subreddit while maintaining <10 min total runtime.

**Deliverables**:
- `crawler.py` module with:
  ```python
  import time
  import logging
  from functools import wraps
  from datetime import datetime, timedelta
  
  logger = logging.getLogger(__name__)
  RATE_LIMIT_REQUESTS_PER_MINUTE = 60
  RATE_LIMIT_INTERVAL_SECONDS = 60 / RATE_LIMIT_REQUESTS_PER_MINUTE  # 1 second
  
  def retry_with_backoff(max_retries=5, base_delay=2):
      """Exponential backoff decorator for transient errors."""
      def decorator(func):
          def wrapper(*args, **kwargs):
              for attempt in range(max_retries):
                  try:
                      return func(*args, **kwargs)
                  except Exception as e:
                      if attempt == max_retries - 1:
                          logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                          raise
                      
                      delay = base_delay ** attempt
                      logger.warning(
                          f"{func.__name__} attempt {attempt + 1}/{max_retries} failed. "
                          f"Retrying in {delay}s... (Error: {type(e).__name__}: {e})"
                      )
                      time.sleep(delay)
          return wrapper
      return decorator
  
  @retry_with_backoff(max_retries=5, base_delay=2)
  def fetch_subreddit_comments(reddit, subreddit_name, limit=100, time_filter='month'):
      """Fetch comments from single subreddit with retry logic."""
      logger.info(f"Fetching {limit} comments from r/{subreddit_name}...")
      
      subreddit = reddit.subreddit(subreddit_name)
      comments = []
      
      for submission in subreddit.new(limit=limit):
          # Enforce rate limit: 1 request per second
          time.sleep(RATE_LIMIT_INTERVAL_SECONDS)
          
          try:
              for comment in submission.comments:
                  comments.append({
                      'id': comment.id,
                      'text': comment.body,
                      'author': str(comment.author) if comment.author else '[deleted]',
                      'submission_id': comment.submission.id,
                      'subreddit': comment.subreddit.display_name,
                      'created_utc': comment.created_utc,
                      'score': comment.score,
                      'upvote_ratio': comment.submission.upvote_ratio
                  })
          except Exception as e:
              logger.warning(f"Error fetching comments from submission {submission.id}: {e}")
              continue
      
      logger.info(f"Successfully fetched {len(comments)} comments from r/{subreddit_name}")
      return comments
  
  def fetch_all_subreddits(reddit, subreddit_list, comments_per_sub=100):
      """Batch fetch from multiple subreddits."""
      all_comments = []
      start_time = datetime.now()
      
      for subreddit_name in subreddit_list:
          try:
              comments = fetch_subreddit_comments(reddit, subreddit_name, limit=comments_per_sub)
              all_comments.extend(comments)
              
              # Log progress
              logger.info(f"Progress: {len(all_comments)} comments collected")
          except Exception as e:
              logger.error(f"Failed to fetch r/{subreddit_name}: {e}")
              continue
      
      duration = (datetime.now() - start_time).total_seconds()
      logger.info(f"Total collection time: {duration:.1f}s for {len(all_comments)} comments")
      
      return all_comments, duration
  ```

- Batch job controller `batch_job.py`:
  ```python
  import os
  import logging
  from dotenv import load_dotenv
  from reddit_auth import get_reddit_client
  from crawler import fetch_all_subreddits
  from storage import store_comments, log_collection_run
  from database import init_database
  
  # Configure logging
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler('./logs/collection.log'),
          logging.StreamHandler()
      ]
  )
  logger = logging.getLogger(__name__)
  
  def run_collection_batch():
      """Execute full collection pipeline."""
      load_dotenv()
      
      db_path = os.getenv('DATABASE_PATH', './data/comments.db')
      target_subs = os.getenv('TARGET_SUBREDDITS', 'MachineLearning,ChatGPT,LocalLLaMA,OpenAI,Claude').split(',')
      comments_per_sub = 100
      
      logger.info("Starting Reddit collection batch job...")
      
      # Initialize database if needed
      init_database(db_path)
      
      # Authenticate
      reddit = get_reddit_client()
      
      # Fetch comments
      comments, duration = fetch_all_subreddits(reddit, target_subs, comments_per_sub)
      logger.info(f"Fetched {len(comments)} comments in {duration:.1f}s")
      
      # Store comments
      stats = store_comments(db_path, comments)
      logger.info(f"Storage stats: {stats}")
      
      # Log this run
      for sub in target_subs:
          sub_comments = [c for c in comments if c['subreddit'] == sub]
          log_collection_run(
              db_path,
              sub,
              {
                  'fetched': len(sub_comments),
                  'new': stats['inserted'],  # Approximate
                  'duplicate': stats['duplicates']
              }
          )
      
      logger.info("Collection batch completed successfully")
      return stats
  
  if __name__ == '__main__':
      run_collection_batch()
  ```

- Logging configuration with:
  - Console output (INFO level)
  - File output (`./logs/collection.log`)
  - Structured format: timestamp, module, level, message
  - Error capturing for rate limits, auth failures, storage errors

- Configuration in `.env`:
  ```
  TARGET_SUBREDDITS=MachineLearning,ChatGPT,LocalLLaMA,OpenAI,Claude
  COMMENTS_PER_SUBREDDIT=100
  REQUEST_INTERVAL_SECONDS=1.0
  RETRY_MAX_ATTEMPTS=5
  RETRY_BASE_DELAY_SECONDS=2
  ```

**Success Criteria**:
- ✓ Single batch run fetches 5 subreddits × 100 comments = 500+ comments total
- ✓ Idempotent design allows safe daily re-runs to accumulate 5K+ corpus
  - E.g., ~10 daily runs to reach 5,000 comments (no duplication due to P1-T4 dedup)
  - Timeline: 5K-10K comments corpus available after Phase 1 operational period
- ✓ Completes in <10 minutes (respecting 1s/request rate limit)
- ✓ No API errors or rate limit hits
- ✓ Retries transient failures (network timeouts, temporary unavailability)
- ✓ Logs all significant events (start, completion, errors)

**Verification Steps**:
1. Run `python batch_job.py` → logs "Collection batch completed successfully"
2. Check `./logs/collection.log` → entries for each subreddit
3. Query DB: `SELECT COUNT(*) FROM comments` → 500+
4. Query DB: `SELECT DISTINCT subreddit FROM comments` → 5 subreddits
5. Verify avg comment length > 20 chars: `SELECT AVG(LENGTH(text)) FROM comments`

**Testing**:
```python
# test_crawler.py
from crawler import fetch_all_subreddits, fetch_subreddit_comments
from reddit_auth import get_reddit_client

def test_fetch_single_subreddit():
    reddit = get_reddit_client()
    comments = fetch_subreddit_comments(reddit, 'MachineLearning', limit=10)
    assert len(comments) >= 10, f"Expected 10+ comments, got {len(comments)}"
    assert all('id' in c and 'text' in c for c in comments), "Missing required fields"
    print(f"✓ Fetched {len(comments)} comments")

def test_fetch_multiple_subreddits():
    reddit = get_reddit_client()
    subs = ['MachineLearning', 'ChatGPT']
    comments, duration = fetch_all_subreddits(reddit, subs, comments_per_sub=50)
    assert len(comments) >= 100, f"Expected 100+ comments, got {len(comments)}"
    print(f"✓ Fetched {len(comments)} comments in {duration:.1f}s")
```

---

### P1-T6: Data Validation & Schema Verification Tests
**Status**: Ready (blocked until P1-T4 and P1-T5 complete)  
**Assigned to**: QA engineer / Backend engineer  
**Duration**: 0.5 days  
**Dependencies**: → P1-T4, P1-T5  

**Description**:
Write comprehensive test suite to validate data integrity, deduplication effectiveness, and schema constraints. Tests should cover happy path (clean data insertion), error cases (duplicates, invalid data), and edge cases (missing fields, extreme values).

**Deliverables**:
- `tests/test_integration.py` — full end-to-end batch job test:
  ```python
  import pytest
  import sqlite3
  from batch_job import run_collection_batch
  
  @pytest.fixture
  def clean_db():
      """Create fresh test database."""
      db_path = './data/test_comments.db'
      init_database(db_path)
      yield db_path
      # Cleanup
      os.remove(db_path)
  
  def test_end_to_end_collection(clean_db):
      """Full batch job integration test."""
      # Run collection
      stats = run_collection_batch()
      
      # Validate results
      assert stats['inserted'] > 500, f"Expected 500+ inserts, got {stats['inserted']}"
      assert stats['duplicates'] == 0, "Should be 0 duplicates on fresh DB"
      
      # Check data in DB
      conn = sqlite3.connect(clean_db)
      cursor = conn.cursor()
      
      # Count total
      cursor.execute("SELECT COUNT(*) FROM comments")
      total = cursor.fetchone()[0]
      assert total >= 500, f"Expected 500+ records, got {total}"
      
      # Verify all required fields populated
      cursor.execute("SELECT COUNT(*) FROM comments WHERE id IS NULL OR text IS NULL")
      nulls = cursor.fetchone()[0]
      assert nulls == 0, f"Found {nulls} records with NULL id/text"
      
      # Verify data_hash uniqueness
      cursor.execute("SELECT COUNT(*) FROM comments GROUP BY data_hash HAVING COUNT(*) > 1")
      duplicates = cursor.fetchone()
      assert duplicates is None, "Found duplicate data hashes"
      
      # Verify subreddit distribution
      cursor.execute("SELECT subreddit, COUNT(*) FROM comments GROUP BY subreddit")
      distribution = cursor.fetchall()
      assert len(distribution) == 5, f"Expected 5 subreddits, got {len(distribution)}"
      
      conn.close()
  ```

- `tests/test_deduplication.py` — dedup-specific tests:
  ```python
  def test_duplicate_detection_primary_key():
      """Verify PK prevents exact duplicates."""
      # Insert same comment twice
      comment = {
          'id': 'test_123',
          'text': 'test comment',
          'author': 'testuser',
          'subreddit': 'test',
          'created_utc': 1234567890
      }
      
      result1 = store_comments('./data/test.db', [comment])
      result2 = store_comments('./data/test.db', [comment])
      
      assert result1['inserted'] == 1 and result1['duplicates'] == 0
      assert result2['inserted'] == 0 and result2['duplicates'] == 1
  
  def test_duplicate_detection_content_hash():
      """Verify content hash catches content-identical comments."""
      comment1 = {
          'id': 'c1',
          'text': 'identical text',
          'author': 'user1',
          'subreddit': 'test',
          'created_utc': 1000
      }
      comment2 = {
          'id': 'c2',  # Different ID
          'text': 'identical text',  # Same text
          'author': 'user1',  # Same author
          'subreddit': 'test',  # Same subreddit
          'created_utc': 1000  # Same timestamp
      }
      
      result = store_comments('./data/test.db', [comment1, comment2])
      assert result['duplicates'] == 1, "Should catch content-identical comment"
  ```

- `tests/test_data_validation.py` — validation tests:
  ```python
  def test_invalid_comment_rejected():
      """Verify validation rejects bad data."""
      invalid_cases = [
          {},  # Empty
          {'id': 'c1'},  # Missing text
          {'id': 'c1', 'text': ''},  # Empty text
          {'id': 'c1', 'text': 'ok', 'subreddit': None},  # Missing subreddit
          {'id': 'c1', 'text': 'ok', 'subreddit': 's1', 'created_utc': 'not_an_int'},  # Invalid timestamp
      ]
      
      for invalid in invalid_cases:
          result = store_comments('./data/test.db', [invalid])
          assert result['errors'] > 0, f"Should reject invalid comment: {invalid}"
  ```

- Test execution script:
  ```bash
  pytest tests/ -v --cov=. --cov-report=term-missing
  ```

**Success Criteria**:
- ✓ All integration tests pass (end-to-end collection works)
- ✓ Duplicate detection tests pass (0 false negatives)
- ✓ Data validation tests pass (invalid data rejected)
- ✓ Schema tests pass (all constraints enforced)

**Verification Steps**:
1. Run `pytest tests/ -v` → all tests pass
2. Verify test coverage > 80% for storage and crawler modules
3. Run integration test 3 times → consistent results

**Testing**:
See test code above.

---

### P1-T7: Documentation & Deployment Runbook
**Status**: Ready (can run in parallel with P1-T6)  
**Assigned to**: Tech lead / Backend engineer  
**Duration**: 0.5 days  
**Dependencies**: → All previous tasks  

**Description**:
Write clear, step-by-step documentation for developers to set up and run the data collection pipeline. Include Reddit app registration guide, credential setup, local testing, and troubleshooting.

**Deliverables**:

**A. `README.md` — Setup & Quick Start**
```markdown
# Phase 1: Reddit Data Collection Pipeline

## Quick Start (5 minutes)

### 1. Create Reddit App
- Go to https://www.reddit.com/prefs/apps
- Click "Create app" (or "Create another app")
- Fill in:
  - Name: "sentiment-analyzer"
  - App type: Select "script"
  - Redirect URI: "http://localhost:8000" (not used for script apps)
  - Click "Create app"
- Note your `client_id` (shown under app name) and `client_secret`

### 2. Set Up Credentials
```bash
cp .env.example .env
# Edit .env with your credentials:
# REDDIT_CLIENT_ID=your_id
# REDDIT_CLIENT_SECRET=your_secret
# REDDIT_USER_AGENT=sentiment-analyzer/1.0 by your_username
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python database.py
```

### 5. Run Collection Batch
```bash
python batch_job.py
```

Expected output:
```
2026-05-07 10:30:45 - batch_job - INFO - Starting Reddit collection batch job...
2026-05-07 10:30:45 - crawler - INFO - Fetching 100 comments from r/MachineLearning...
...
2026-05-07 10:35:12 - batch_job - INFO - Collection batch completed successfully
```

### 6. Verify Data Collected
```bash
sqlite3 ./data/comments.db "SELECT COUNT(*) FROM comments;"
# Expected: 500+
```

## Requirements
- Python 3.8+
- Internet connection
- Reddit account (for app registration)
```

**B. `COLLECTION_LOG.md` — Troubleshooting Guide**
```markdown
# Troubleshooting Data Collection Issues

## Issue: "Authentication failed: Invalid credentials"

**Causes**:
- Typo in REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET
- Credentials not yet set in `.env` file
- Reddit API regenerated credentials (rare)

**Solution**:
1. Verify `.env` exists: `ls -la .env`
2. Check credentials: `grep REDDIT_CLIENT .env`
3. Compare to https://www.reddit.com/prefs/apps (exact match?)
4. Test credentials: `python -c "from reddit_auth import test_connection; test_connection()"`
5. If still failing, regenerate Reddit app credentials

---

## Issue: "HTTP 429: Too Many Requests"

**Causes**:
- Rate limit exceeded (60 req/min per user)
- Running multiple collection jobs in parallel
- Manual Reddit API testing during collection

**Solution**:
1. Wait 5-10 minutes before retrying (backoff automatic)
2. Check logs: `tail -50 ./logs/collection.log | grep 429`
3. Ensure only 1 batch job running: `pgrep -f batch_job.py`
4. Verify 1-second request interval in crawler: `grep RATE_LIMIT crawler.py`
5. If persists, check Reddit status page

---

## Issue: "Database is locked"

**Causes**:
- Multiple processes writing to database simultaneously
- Incomplete WAL cleanup
- Interrupted previous collection job

**Solution**:
1. Check running processes: `pgrep -f batch_job.py`
2. Kill stray jobs: `pkill -f batch_job.py`
3. Wait 5 seconds
4. Check WAL files: `ls -la ./data/comments.db*`
5. If stuck, manually cleanup: `rm -f ./data/comments.db-wal ./data/comments.db-shm`
6. Retry batch job

---

## Issue: "Duplicate rate anomalously high (>5%)"

**Causes**:
- Running batch job twice simultaneously
- Subreddit data crossover (same comments in multiple subreddits)
- Crawler fetching older posts with historical batches

**Solution**:
1. Check `collection_log` table: `SELECT * FROM collection_log ORDER BY run_timestamp DESC LIMIT 5;`
2. Compare recent runs for timing overlap
3. If dupes legitimate (same comment across subreddits), consider acceptable
4. Reset if necessary: `DELETE FROM comments; DELETE FROM collection_log;`
5. Restart fresh collection

---

## Issue: "Comments incomplete or truncated"

**Causes**:
- Reddit comment edited/deleted between fetch and store
- Rate limit hit mid-collection (partial batch stored)
- Subreddit archived older posts

**Solution**:
1. Check logs for errors: `grep ERROR ./logs/collection.log`
2. Re-run collection: partial data will deduplicate, new comments added
3. Verify text length: `SELECT AVG(LENGTH(text)) FROM comments;` (should be 80-200 chars)
4. If very short (< 20 chars), investigate sample: `SELECT * FROM comments WHERE LENGTH(text) < 20 LIMIT 5;`
```

**C. `requirements.txt` — Dependencies**
```
praw>=7.7.0
python-dotenv>=0.21.0
pytest>=7.0.0
pytest-cov>=3.0.0
```

**D. `.env.example` — Template**
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=sentiment-analyzer/1.0 by your_reddit_username
DATABASE_PATH=./data/comments.db
TARGET_SUBREDDITS=MachineLearning,ChatGPT,LocalLLaMA,OpenAI,Claude
COMMENTS_PER_SUBREDDIT=100
```

**E. `./logs/` Directory** — Created for log output

**Success Criteria**:
- ✓ README is clear enough for non-Python developer to follow
- ✓ Troubleshooting guide covers 80% of likely issues
- ✓ All setup steps tested and working
- ✓ Runbook includes verification steps

**Verification Steps**:
1. Have team member (not original author) follow README.md → success
2. Check that all code files referenced in README exist
3. Verify `.env.example` contains all required keys
4. Confirm troubleshooting steps are actionable

---

## Success Criteria (Phase 1 Overall)

### SC1: Data Collection (Quantitative)
- Collect **500+ comments per single batch run** across 5 target subreddits
- **5,000-10,000 total comments** target achievable through daily scheduled runs
  - Example: 10 daily batch runs × 500-1K comments/run = 5K-10K corpus
  - Phase 1 validates pipeline; Phase 2+ builds historical dataset
- Average collection runtime (single batch): **< 10 minutes** 
- No failed runs due to API errors (rate limit gracefully handled)

### SC2: Data Quality (Quantitative)
- Duplicate rate: **< 1%** (across consecutive runs)
- Data validation pass rate: **> 98%** (valid records / total fetched)
- Missing author rate: **< 1%**
- Comment length distribution: **> 80% between 20-5000 characters**

### SC3: System Reliability (Qualitative)
- Database persists across process restarts (ACID guarantees)
- Rate limits handled without data loss or process crashes
- Collection logs provide debuggable output for troubleshooting

### SC4: Code Quality (Qualitative)
- All modules have docstrings and type hints
- Integration tests pass with > 80% code coverage
- No hardcoded credentials in source code
- Configuration externalized to `.env` file

### SC5: Handoff Readiness (Qualitative)
- Phase 2 can query comment data: `SELECT COUNT(*) FROM comments WHERE subreddit = 'ChatGPT'`
- Phase 2 can extend schema with `model_mentions` table (reserved)
- Runbook enables junior dev to run daily collection job independently

---

## Verification Steps (Phase 1 Completion Checklist)

### Functional Verification
- [ ] Can authenticate to Reddit API without errors
- [ ] Can fetch 100+ comments from each of 5 target subreddits
- [ ] Database contains 5000+ comments with all required fields
- [ ] Running collection batch twice returns 0 duplicates on second run
- [ ] `collection_log` table shows run history with stats

### Data Quality Verification
- [ ] All comments have non-empty `text` field (> 10 chars)
- [ ] All comments have valid `created_utc` timestamps
- [ ] All comments have `subreddit` field
- [ ] Data hash uniqueness enforced (no content duplicates)
- [ ] No NULL values in primary key columns

### System Verification
- [ ] Database initializes in < 5 seconds
- [ ] Full collection batch completes in < 10 minutes
- [ ] No rate limit errors in logs
- [ ] Logs recorded in `./logs/collection.log`
- [ ] `.env` file excluded from Git (.gitignore updated)

### Documentation Verification
- [ ] README.md complete and tested by non-author
- [ ] COLLECTION_LOG.md addresses top 5 failure modes
- [ ] All code modules have docstrings
- [ ] Architecture diagram or flowchart in `ARCHITECTURE.md` (optional)

---

## Assumptions & Constraints

### Assumptions
1. **Team has basic Python/SQL knowledge** — can troubleshoot schema and dependency issues
2. **Reddit account exists** — and can register developer app
3. **Network connectivity stable** — no proxy/firewall blocking Reddit API
4. **No regional API restrictions** — Reddit API accessible from team location
5. **Target subreddits remain public** — no private/restricted communities
6. **Data volume remains manageable** — 5K-50K comments don't exceed SQLite practical limits

### Constraints
1. **Reddit API rate limit: 60 req/min** — hard limit by Reddit, not negotiable
2. **SQLite single-writer limitation** — only 1 batch job can run concurrently
3. **Comment data retention: 6 months** — Reddit archives older posts, auto-deleted comments not recoverable
4. **OAuth token refresh** — credentials valid ~1 year (monitor expiry)
5. **Privacy considerations** — must respect Reddit user privacy (no PII extraction)

---

## Risk Mitigation

### Risk 1: Rate Limit Hits Cause Data Loss
**Severity**: High | **Probability**: Medium  
**Mitigation**:
- PRAW exponential backoff handles 95% automatically
- Manual 1-2s request batching enforced
- Failed runs logged with timestamps
- Idempotent dedup allows safe re-runs
- Monitor `collection_log` table for 429 errors

**Contingency**: Re-run batch job after 10-minute cooldown

---

### Risk 2: Duplicate Comments Inflate Dataset
**Severity**: Medium | **Probability**: Low  
**Mitigation**:
- 3-layer dedup: PK + content hash + app-level
- Comprehensive test suite validates dedup effectiveness
- `collection_log` tracks duplicate count per run
- Threshold alert: if duplicate rate > 5%, investigate

**Contingency**: Manual query to identify duplicate sources; adjust collection window

---

### Risk 3: Reddit API Changes Break Integration
**Severity**: High | **Probability**: Very Low  
**Mitigation**:
- PRAW library maintained (7000+ stars, active)
- Pin PRAW version in requirements.txt (tested combination)
- Monitor PRAW GitHub for deprecation notices
- Abstraction layer (reddit_auth.py) isolates PRAW usage

**Contingency**: Upgrade PRAW, run regression tests

---

### Risk 4: Credentials Leaked in Git
**Severity**: Critical | **Probability**: Low  
**Mitigation**:
- `.env` explicitly in `.gitignore`
- Use `.env.example` as template (never commit real values)
- Pre-commit hook to scan for credentials (optional)
- Document credential management in README

**Contingency**: Immediately regenerate Reddit app secrets if leaked

---

### Risk 5: Silent Collection Failures
**Severity**: Medium | **Probability**: Medium  
**Mitigation**:
- Comprehensive logging to file + console
- `collection_log` table records each run
- Email alerts on process failure (optional, can add later)
- Daily scheduled runs + monitoring dashboard (Phase 2+)

**Contingency**: Check logs daily; `SELECT * FROM collection_log WHERE run_timestamp > datetime('now', '-1 day');`

---

## Timeline (Day-by-Day)

### Day 1: Setup & Authentication (0.5 days)

**Morning (2 hours)**:
- [ ] Register Reddit app → credentials obtained (P1-T1)
- [ ] Set up `.env` file → credentials loaded (P1-T1)
- [ ] Install PRAW + dependencies → `pip install -r requirements.txt` (P1-T1)
- [ ] Test PRAW authentication → `python reddit_auth.py` (P1-T2)

**Afternoon (3 hours)**:
- [ ] Design SQLite schema → peer review (P1-T3)
- [ ] Create database.py → `python database.py` creates tables (P1-T3)
- [ ] Enable WAL mode → WAL pragmas set (P1-T3)
- [ ] Verify schema with sqlite3 CLI → 3 tables created (P1-T3)

**End of Day 1 Deliverables**:
- ✓ Reddit credentials in `.env`
- ✓ PRAW client authenticating
- ✓ SQLite database initialized with 3 tables
- ✓ WAL mode enabled
- **Blockers**: None (setup on critical path)

---

### Day 2: Pipeline Development & Testing (1 day)

**Morning (4 hours)**:
- [ ] Implement storage.py with dedup logic (P1-T4)
- [ ] Write validate_comment() function (P1-T4)
- [ ] Write compute_data_hash() function (P1-T4)
- [ ] Test storage on 100 test comments → no duplicates (P1-T4)

**Afternoon (4 hours)**:
- [ ] Implement crawler.py with fetch_subreddit_comments() (P1-T5)
- [ ] Add retry_with_backoff decorator (P1-T5)
- [ ] Implement batch_job.py orchestrator (P1-T5)
- [ ] Test single subreddit fetch → 100 comments collected (P1-T5)

**End of Day 2 Deliverables**:
- ✓ crawler.py fetches comments from 5 subreddits
- ✓ storage.py deduplicates and persists data
- ✓ batch_job.py runs end-to-end
- ✓ Collection completes in < 10 minutes
- ✓ Logs written to `./logs/collection.log`

---

### Day 3: Validation & Documentation (0.5 days)

**Morning (2 hours)**:
- [ ] Write integration tests → all pass (P1-T6)
- [ ] Write dedup tests → duplicate detection works (P1-T6)
- [ ] Run pytest with coverage → > 80% coverage (P1-T6)
- [ ] Verify DB has 5000+ comments (P1-T6)

**Afternoon (2 hours)**:
- [ ] Write README.md → tested by non-author (P1-T7)
- [ ] Write COLLECTION_LOG.md troubleshooting guide (P1-T7)
- [ ] Create .env.example template (P1-T7)
- [ ] Final end-to-end verification → all checklists pass (P1-T7)

**End of Day 3 Deliverables**:
- ✓ Test suite passes (integration + dedup + validation)
- ✓ Documentation complete and reviewed
- ✓ Credentials secure (`.env` in `.gitignore`)
- ✓ Phase 1 ready for Phase 2 handoff

**Post-Phase 1 (Ongoing)**:
- [ ] Schedule daily batch job (cron: 2 AM UTC)
- [ ] Monitor `collection_log` for anomalies
- [ ] Weekly backup of `comments.db`

---

## Acceptance Criteria (Phase 1 → Phase 2 Handoff)

✅ **Data Collection Complete**:
- [ ] Database contains 5,000-10,000 comments
- [ ] Comments span 5 target subreddits
- [ ] Collection runs automated daily without manual intervention

✅ **Data Quality Verified**:
- [ ] Duplicate rate < 1%
- [ ] Data validation pass rate > 98%
- [ ] All comments have required fields (id, text, subreddit, created_utc, score)

✅ **System Reliable**:
- [ ] API rate limits handled gracefully (no crashes)
- [ ] Database persists across restarts
- [ ] Logs provide clear troubleshooting output

✅ **Code Ready for Phase 2**:
- [ ] Model_mentions table reserved and queryable
- [ ] Schema extensible (no breaking changes needed)
- [ ] Phase 2 can query: `SELECT * FROM comments WHERE subreddit = 'ChatGPT'`

✅ **Documentation Complete**:
- [ ] README enables new dev to run pipeline in < 30 min
- [ ] Troubleshooting guide covers top issues
- [ ] Code documented with docstrings + type hints
- [ ] Architecture clear to onboarding engineer

✅ **Team Consensus**:
- [ ] Phase lead approves all success criteria met
- [ ] Tech lead signs off on code quality
- [ ] No open HIGH-priority bugs blocking Phase 2

---

## Appendix A: Architecture Overview (High-Level Data Flow)

```
┌─────────────────────┐
│   Reddit API        │
│  (OAuth)            │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  PRAW Library (praw.py)              │
│  • OAuth handling                    │
│  • Rate limit backoff                │
│  • Comment fetching                  │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Crawler Module (crawler.py)         │
│  • Multi-subreddit iteration         │
│  • Request batching (1-2s delays)    │
│  • Retry logic (exponential backoff) │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Storage Module (storage.py)         │
│  • Validation (10 checks)            │
│  • 3-layer dedup (PK+hash+app)       │
│  • Logging collection_log            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  SQLite Database (comments.db)       │
│  • 3 tables: comments, model_mentions│
│    collection_log                    │
│  • Indexes on common queries         │
│  • WAL mode enabled                  │
└──────────────────────────────────────┘

Data Flow:
batch_job.py (orchestrator)
  ├─→ reddit_auth.get_reddit_client()
  ├─→ crawler.fetch_all_subreddits()
  ├─→ storage.store_comments()
  └─→ storage.log_collection_run()
```

---

## Appendix B: Dependency Graph

```
P1-T1: Reddit Credentials Setup
  └─→ No dependencies (root task)

P1-T2: PRAW Authentication
  └─→ P1-T1 (needs credentials)

P1-T3: SQLite Schema
  └─→ No dependencies (can run parallel to T1, T2)

P1-T4: Storage & Dedup Module
  └─→ P1-T3 (needs schema created first)

P1-T5: Crawler & Batch Job
  └─→ P1-T2 (needs authenticated PRAW client)
  └─→ P1-T4 (needs storage module for persistence)

P1-T6: Data Validation Tests
  └─→ P1-T4, P1-T5 (needs both to test together)

P1-T7: Documentation
  └─→ All previous tasks (documents full pipeline)

Critical Path: T1 → T2 → T5 → (T4 in parallel) → T6 → T7
Parallel Opportunities: T3 can run during T1-T2; T4 (storage) and T5 (crawler) can overlap if T2 finishes first
```

---

## Appendix C: File Structure After Phase 1

```
.
├── .env                          # Credentials (NEVER commit)
├── .gitignore                    # Excludes .env, *.db, logs/
├── .env.example                  # Template for credentials
├── requirements.txt              # Dependencies
├── README.md                     # Setup guide
│
├── src/
│   ├── __init__.py
│   ├── reddit_auth.py           # PRAW client initialization
│   ├── crawler.py               # Multi-subreddit fetcher
│   ├── storage.py               # Dedup + persist logic
│   ├── database.py              # Schema creation + WAL
│   └── batch_job.py             # Main orchestrator
│
├── tests/
│   ├── __init__.py
│   ├── test_credentials.py
│   ├── test_praw_auth.py
│   ├── test_schema.py
│   ├── test_deduplication.py
│   ├── test_data_validation.py
│   └── test_integration.py
│
├── logs/
│   └── collection.log           # Runtime logs
│
├── data/
│   ├── comments.db              # SQLite database
│   ├── comments.db-wal          # WAL file
│   └── comments.db-shm          # Shared memory file
│
├── .planning/
│   ├── ROADMAP.md
│   ├── REQUIREMENTS.md
│   ├── P1_DATA_COLLECTION/
│   │   └── PLAN.md             # This file
│   └── research/
│       ├── RESEARCH.md
│       └── QUICK_REFERENCE.md
│
└── docs/
    ├── ARCHITECTURE.md         # High-level design (optional)
    └── COLLECTION_LOG.md       # Troubleshooting guide
```

---

**Version**: 1.0  
**Status**: Ready for execution  
**Last Updated**: 2026-05-07  
**Next Review**: Upon Phase 1 completion
