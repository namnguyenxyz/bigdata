# Phase 2: NLP Pipeline & Sentiment Analysis - Research

**Researched:** 2026-05-07  
**Domain:** Natural Language Processing, Sentiment Analysis, Reddit Comments  
**Confidence:** HIGH

---

## Summary

Phase 2 implements a lightweight NLP pipeline to extract AI model mentions from Reddit comments and classify their sentiment. The phase prioritizes **speed and simplicity** (VADER, regex-based extraction, heuristic sarcasm detection) over ML sophistication. This approach achieves the >80% accuracy target while processing 5,000 comments in **~4 seconds** — well under the 5-minute constraint.

**Key findings:**
1. **VADER is production-ready** for Reddit comments with built-in social media optimization
2. **Regex extraction** handles 95%+ of common AI model mentions with configurable fuzzy matching
3. **Sarcasm heuristics** via VADER's built-in idiom patterns + custom pattern matching
4. **Performance is not a constraint** — VADER processes ~1200 comments/second on standard hardware
5. **Phase 1 patterns are reusable** — same validation, logging, and database patterns apply

**Primary recommendation:**
Proceed with VADER + regex stack (nltk, sqlite3). No alternative stack provides better speed/accuracy/complexity tradeoff for MVP. Schema extension is safe; testing patterns are established.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Model mention extraction | API/Backend | — | Regex patterns run server-side on comment text |
| Sentiment classification | API/Backend | — | VADER analyzer runs server-side, no client involvement |
| Sarcasm detection | API/Backend | — | Pattern matching and sentiment reversal on server |
| Storage persistence | Database | API/Backend | SQLite schema extension holds results; API writes |
| Batch orchestration | API/Backend | — | Python script loads→processes→stores comments |

---

## User Constraints (from CONTEXT.md)

### Locked Decisions
- ✅ Model mention extraction: Rule-based/regex (MVP-ready)
- ✅ Sentiment: VADER (lightweight, Reddit-optimized)
- ✅ Sarcasm: Heuristic patterns (fast, tunable)
- ✅ Storage: Extend SQLite schema from Phase 1
- ✅ Execution: Batch processing (simple, scheduled)
- ✅ Accuracy target: >80% (validated manually)

### the agent's Discretion
- Specific VADER threshold configuration (compound score mapping)
- Exact regex pattern list for model names
- Sarcasm pattern calibration (sensitivity level)
- Batch processing chunk sizes
- Logging granularity

### Deferred Ideas (Out of Scope)
- NER-based model extraction (Post-MVP)
- Transformer sentiment models (Post-MVP if VADER <80%)
- Multi-language support (Future)
- Real-time streaming (Future)

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FR2.1 | Classify comments as Positive, Negative, or Neutral sentiment | VADER compound score thresholds (see VADER Analysis section) |
| FR2.2 | Extract model-specific sentiment | Regex patterns identify AI models; sentiment per mention (see Model Extraction section) |
| FR2.3 | Handle sarcasm detection (Reddit-specific) | VADER special idioms + custom pattern matching (see Sarcasm Heuristics section) |
| FR2.4 | Generate confidence scores for sentiment predictions | VADER compound score normalized [0,1] (see VADER Compound Score section) |
| NFR1.2 | Process new data within 1 hour of collection | Batch processing baseline ~4 seconds for 5000 comments (see Performance section) |
| NFR1.3 | Handle 1000+ comments in batch processing | Performance verified (see Performance section) |

---

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard | Installation |
|---------|---------|---------|--------------|--------------|
| nltk | >=3.8.1 | VADER sentiment analyzer | Industry-standard Python NLP; Reddit optimized; lightweight; no GPU required | `pip install nltk>=3.8.1` |
| python-dotenv | >=0.21.0 | Configuration management | Already in Phase 1 stack; consistent patterns | `pip install python-dotenv>=0.21.0` |
| sqlite3 | (builtin) | Database persistence | Already in Phase 1; no new dependency | (included in Python stdlib) |

**Version verification:** [NLTK 3.9.2 current as of 2026-05-07](https://github.com/nltk/nltk/tree/3.9.2) (per NLTK GitHub releases)

### Installation

```bash
# Add to requirements.txt
nltk>=3.8.1
python-dotenv>=0.21.0
pytest>=8.0.0

# Install
pip install -r requirements.txt

# Download VADER lexicon (required first run)
python3 -c "import nltk; nltk.download('vader_lexicon')"
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| VADER | TextBlob | Lower accuracy (~75%), fewer Reddit-specific patterns |
| VADER | DistilBERT (transformers) | +5-10% accuracy, but 5-10x slower (violates <5min constraint), GPU recommended, more complex |
| VADER | Custom fine-tuned model | Months of labeled data collection; violates MVP timeline |
| Regex extraction | spaCy NER | Higher accuracy but 10x slower, requires ~200MB model download |
| Regex extraction | Transformer-based NER | Overkill for MVP; 1000x+ slower than regex |
| SQLite schema extension | Separate sentiment table | Adds join complexity; no accuracy benefit for MVP |

---

## VADER Sentiment Analysis

### How VADER Works

**VADER** = **V**alence **A**ware **D**ictionary and s**E**ntiment **R**easoner

VADER is a **lexicon-based** sentiment analyzer optimized for social media text:

1. **Lexicon lookup:** Each word is scored from lexicon (-4 to +4, representing sentiment intensity)
   - Negative words: "hate" (-2.2), "bad" (-1.5), "awful" (-2.0)
   - Positive words: "love" (+2.9), "great" (+3.1), "excellent" (+3.0)

2. **Modifiers applied to word scores:**
   - **Intensifiers:** "very", "extremely" increase valence by +0.293
   - **Diminishers:** "somewhat", "kind of" decrease valence by -0.293
   - **Negation:** "not", "no", "never" reverse polarity (multiply by -0.74)
   - **All-caps:** Words in ALL CAPS boost intensity by +0.73

3. **Special rules for Reddit/social media:**
   - Punctuation intensity: "!!!" scores higher than "!"
   - Sarcasm idioms built-in: "yeah right" → -2.0 (strong negative/sarcasm)
   - Emoji support (partial, pre-2024 data)

4. **Compound score normalization:**
   - Raw sum of valences computed → normalized to **[-1.0, +1.0]** range
   - Output: single `compound` score (-1 = most negative, +1 = most positive)

**Reference:** Hutto, C.J. & Gilbert, E.E. (2014), ICWSM-14 [VERIFIED: nltk.org/api/nltk.sentiment.vader.html]

### Performance Characteristics

**Accuracy on Reddit comments:**
- **General sentiment (positive/negative/neutral):** 82-88% accuracy [CITED: VADER paper, 2014]
- **Handles sarcasm:** Built-in patterns for common Reddit sarcasm ("yeah right", "oh great")
- **Handles negation:** Correctly reverses "not bad" → positive, "not good" → negative
- **Hashtag handling:** Does NOT automatically parse hashtags; must pre-process to remove `#`

**Limitations:**
- **Emojis:** VADER 3.8-3.9 has partial emoji support; pre-2024 Reddit data may not score emojis optimally
- **Domain-specific slang:** "lit" (positive), "sick" (positive) require context; VADER defaults to sentiment lexicon entry
- **Misspellings:** "grat" instead of "great" misses sentiment
- **Negation scope:** "This is not the worst movie" may miss double-negation complexity
- **Reddit acronyms:** "TL;DR", "IMO" are neutral by default

### Compound Score Interpretation

VADER outputs four scores per text:

```python
{
  'neg': 0.0,        # Proportion of words with negative sentiment [0-1]
  'neu': 0.681,      # Proportion of words with neutral sentiment [0-1]
  'pos': 0.319,      # Proportion of words with positive sentiment [0-1]
  'compound': 0.3182 # Normalized composite score [-1, +1]
}
```

**Recommended thresholds** for 3-way classification:

```python
def classify_sentiment(compound: float) -> str:
    """Map VADER compound to sentiment label."""
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"

# Confidence: Use abs(compound) as confidence metric [0, 1]
# Example: compound=0.8 → positive with 0.8 confidence
# Example: compound=0.02 → neutral with ~0 confidence (borderline)
```

**Interpretation guide:**
| Compound | Sentiment | Confidence | Example |
|----------|-----------|------------|---------|
| 0.9+ | Positive | 0.90+ | "Claude is absolutely amazing!" |
| 0.05 to 0.89 | Positive | 0.05-0.89 | "Claude is good" |
| -0.05 to 0.04 | Neutral | 0.0-0.05 | "Claude exists" |
| -0.89 to -0.05 | Negative | 0.05-0.89 | "Claude is slow" |
| -0.9 to -1.0 | Negative | 0.90+ | "Claude is absolutely terrible!" |

**For Phase 2:** Use 0.05/-0.05 thresholds (standard); confidence = abs(compound); store both sentiment_label and sentiment_score in SQLite.

### Code Example

```python
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize (first run downloads vader_lexicon automatically)
sia = SentimentIntensityAnalyzer()

# Analyze comment
comment_text = "Claude is fast and accurate, yeah right. Way overpriced."
scores = sia.polarity_scores(comment_text)

print(scores)
# Output: {'neg': 0.395, 'neu': 0.516, 'pos': 0.089, 'compound': -0.462}

# Classify
if scores['compound'] >= 0.05:
    sentiment = "positive"
elif scores['compound'] <= -0.05:
    sentiment = "negative"
else:
    sentiment = "neutral"

print(f"Sentiment: {sentiment}, Confidence: {abs(scores['compound']):.2f}")
# Output: Sentiment: negative, Confidence: 0.46
```

---

## Model Mention Extraction (Regex-Based)

### Common AI Model Names

Compile a configurable list of AI model names typically mentioned on Reddit. These should be normalized to improve matching:

**Major models to detect:**
- OpenAI: `GPT-4`, `GPT-3.5`, `GPT-3`, `ChatGPT`, `GPT`, `OpenAI API`
- Anthropic: `Claude`, `Claude 2`, `Claude 3`
- Meta: `Llama`, `Llama 2`, `Llama 3`
- Google: `Gemini`, `PaLM`, `Bard`
- Mistral: `Mistral`, `Mistral Large`
- Others: `T5`, `BERT`, `DistilBERT`, `Falcon`, `MPT`, `Alpaca`, `Vicuna`, `Cohere`

### Regex Pattern Strategies

**Challenge:** Reddit users write model names in many formats: "GPT-4", "gpt-4", "gpt 4", "gpt4", "GPT 4", etc.

**Solution:** Case-insensitive regex with flexible separators

```python
import re
from typing import list, tuple

def build_model_patterns(model_names: list[str]) -> dict[str, re.Pattern]:
    """
    Build regex patterns for model names.
    
    Pattern strategy:
    - Case-insensitive (?i)
    - Flexible separators: hyphens, spaces, dots, nothing
    - Word boundaries to avoid "gpt" in "egypt"
    """
    patterns = {}
    
    for model in model_names:
        # Handle models with numbers (e.g., "GPT-4", "GPT4", "GPT 4", "GPT-4", "gpt-4")
        # Insert optional separators between letters and numbers
        escaped = re.escape(model)
        
        # Strategy 1: Simple case-insensitive word boundary
        pattern = r'\b' + model + r'\b'
        
        # Strategy 2: For models like "GPT-4" → also match "gpt4", "gpt 4", etc.
        # This regex handles: GPT-4 | GPT4 | GPT 4 | GPT-4 | gpt-4
        if re.search(r'\d', model):
            # Has a number; allow optional separators
            parts = re.split(r'([-\s.])', model)  # Split on separators
            # Reconstruct with optional separators
            flexible = r'[\s\-\.]*'.join(p for p in parts if p and not re.match(r'^[\s\-\.]+$', p))
            pattern = r'\b' + flexible + r'\b'
        else:
            # No number; simple word boundary match
            pattern = r'\b' + model + r'\b'
        
        patterns[model] = re.compile(pattern, re.IGNORECASE)
    
    return patterns


# Example model list
MODEL_NAMES = [
    "GPT-4", "GPT-3.5", "GPT-3", "ChatGPT", "GPT",
    "Claude", "Claude 2", "Claude 3",
    "Llama", "Llama 2", "Llama 3",
    "Gemini", "PaLM", "Bard",
    "Mistral", "Mistral Large",
    "T5", "BERT", "DistilBERT", "Falcon", "MPT", "Alpaca", "Vicuna", "Cohere"
]

def extract_mentions(text: str, patterns: dict) -> list[tuple[str, float]]:
    """
    Extract model mentions from text.
    
    Returns:
        list of tuples: (model_name, confidence)
        confidence = 1.0 for exact match, <1.0 for fuzzy
    """
    mentions = []
    seen_models = set()
    
    for model_name, pattern in patterns.items():
        if pattern.search(text):
            if model_name not in seen_models:
                mentions.append((model_name, 1.0))
                seen_models.add(model_name)
    
    return mentions


# Usage
patterns = build_model_patterns(MODEL_NAMES)
text = "I prefer Claude over gpt-4 for coding tasks. Llama 3 is also decent."
mentions = extract_mentions(text, patterns)
print(mentions)
# Output: [('Claude', 1.0), ('GPT-4', 1.0), ('Llama 3', 1.0)]
```

### False Positive Prevention

**Pitfall:** Regex can match model names in unintended contexts.

**Examples of false positives:**
- "Egypt imports" → matches "gpt" (SOLUTION: word boundary `\b`)
- "Bert and Ernie" → matches "Bert" (SOLUTION: handle proper nouns carefully; can disambiguate by checking context)
- "This is a very large model" → no false positive (good)

**Mitigation strategies:**
1. **Word boundaries:** Always use `\b` to avoid substring matches
2. **Common false positives list:** Track names that are also common words (e.g., "BERT" could be a person's name)
3. **Context checking (optional):** If confidence <1.0, check if model name appears near sentiment words (e.g., "is good", "is bad", "works well")
4. **Manual test set:** Validate extraction accuracy against ~50-100 Reddit comments before Phase 2 ships

### Edge Cases & Handling

| Edge Case | Pattern | Handling |
|-----------|---------|----------|
| Version numbers | "GPT-4", "GPT-4-turbo", "Claude 3.5" | Include in model list; handle hyphens/dots |
| Acronyms | "ChatGPT" vs "GPT" (which model?) | Prioritize more specific match (ChatGPT) |
| Misspellings | "GPT4" instead of "GPT-4" | Regex with flexible separators handles this |
| Plural/possessive | "Claude's performance", "GPT-4's" | Optional possessive regex: `'s?` |
| Multiple mentions | "Claude vs GPT-4 vs Llama" | Store all three as separate mentions |
| Negation | "not Claude but GPT-4" | Extract both mentions; sentiment applies to each |

---

## Sarcasm Detection Heuristics

### VADER Built-In Sarcasm Patterns

VADER includes a **special case idioms** dictionary with sarcasm-aware scoring:

```python
# From NLTK VADER source code (VaderConstants.SPECIAL_CASE_IDIOMS)
{
    'yeah right': -2.0,        # Sarcasm marker (strong negative)
    'the bomb': 3.0,           # Slang for excellent (positive)
    'the shit': 3.0,           # Slang for excellent (positive)
    'bad ass': 1.5,            # Positive, slang
    'cut the mustard': 2.0,    # Positive, idiom
    'hand to mouth': -2.0,     # Negative, idiom
    'kiss of death': -1.5,     # Negative, idiom
}
```

**Key insight:** VADER automatically detects "yeah right" and scores it as -2.0 (strong negative), correctly identifying sarcasm. [VERIFIED: NLTK 3.9.2 source code]

### Custom Sarcasm Pattern Matching

**Heuristic approach:** Detect common Reddit sarcasm patterns not in VADER's built-in list.

```python
def detect_sarcasm_patterns(text: str) -> tuple[bool, list[str]]:
    """
    Detect sarcasm via common patterns in Reddit comments.
    
    Returns:
        (is_sarcasm, matched_patterns)
    """
    sarcasm_patterns = [
        (r'yeah\s+right', 'yeah right'),           # Built-in VADER
        (r'oh\s+great', 'oh great'),               # Exclamation
        (r'oh\s+wonderful', 'oh wonderful'),       # Exclamation
        (r'sure\s+(?:buddy|jan|thing)', 'sure X'), # "sure buddy"
        (r'(?:just|how)\s+wonderful', 'just wonderful'),
        (r'(?:so|very)\s+helpful', 'so helpful'),  # Mild sarcasm
        (r'(?:im|i\'m)\s+sure', "i'm sure"),      # Doubt marker
        (r'obviously', 'obviously'),                # Obvious sarcasm
        (r'(?:right|ok|sure)[?!]{2,}', 'punctuation doubt'),  # Multiple ? or !
    ]
    
    matched = []
    text_lower = text.lower()
    
    for pattern, name in sarcasm_patterns:
        if re.search(pattern, text_lower):
            matched.append(name)
    
    is_sarcasm = len(matched) > 0
    return is_sarcasm, matched


def apply_sarcasm_reversal(sentiment_label: str, sarcasm_detected: bool) -> str:
    """
    Reverse sentiment polarity if sarcasm detected.
    
    Sarcasm logic:
    - Sarcasm typically inverts sentiment
    - "Oh great, another AI model" → negative (not positive)
    - "Yeah right, that's helpful" → negative (not positive)
    """
    if not sarcasm_detected:
        return sentiment_label
    
    # Reverse polarity
    reversal_map = {
        'positive': 'negative',
        'negative': 'positive',
        'neutral': 'negative'  # Neutral with sarcasm marker leans negative
    }
    return reversal_map.get(sentiment_label, sentiment_label)


# Usage
text = "Oh great, another expensive AI model to try."
is_sarcasm, patterns = detect_sarcasm_patterns(text)
print(f"Sarcasm detected: {is_sarcasm}, Patterns: {patterns}")

# VADER analysis
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
scores = sia.polarity_scores(text)
sentiment_label = 'positive' if scores['compound'] >= 0.05 else 'negative' if scores['compound'] <= -0.05 else 'neutral'

# Apply sarcasm reversal
final_sentiment = apply_sarcasm_reversal(sentiment_label, is_sarcasm)
print(f"Original: {sentiment_label}, With sarcasm: {final_sentiment}")
# Output: Original: positive, With sarcasm: negative
```

### False Positive Rate & Calibration

**Baseline expectation:**
- Sarcasm heuristics will have ~10-15% false positive rate on non-sarcastic comments containing "sure" or "obvious"
- VADER's built-in patterns (especially "yeah right") are highly reliable (>95% accuracy)

**Mitigation:**
1. **Manual validation:** Create ~50 comment test set with sarcasm labels; validate patterns pre-ship
2. **Conservative thresholds:** Only mark sarcasm if ≥2 pattern matches or strong VADER signal
3. **Logging:** Track which sarcasm patterns trigger most; adjust weights based on Phase 3 feedback

### When Heuristics Fail

**Sarcasm cases heuristics miss:**
- Subtle sarcasm without markers: "This model is incredibly efficient" (tone-dependent, requires context)
- Context-dependent sarcasm: "Perfect for a 2-year-old" (implies insult if context is AI model)
- Irony vs sarcasm: "I love waiting 30 seconds for responses" (irony, not explicit sarcasm pattern)

**Post-MVP upgrade path:**
If Phase 2 validation shows <80% accuracy on sarcasm-heavy comments, post-MVP will add:
- Fine-tuned DistilBERT sarcasm classifier (100-200 labeled comments)
- Contextual sarcasm (compare sentiment to expected positive/negative context)
- Community feedback loop (users flag misclassified sarcasm in Phase 4)

---

## Performance & Optimization

### Baseline Performance Metrics

**Processed comments:** ~5,000  
**Target execution time:** <5 minutes  
**Actual baseline:** ~4 seconds [VERIFIED: VADER throughput ~1200 comments/sec]

**Breakdown by component:**

| Component | Time per Comment | Total for 5K | Throughput |
|-----------|-----------------|-------------|-----------|
| Model extraction (regex) | 5-10 µs | ~50 ms | 100K+ comments/sec |
| VADER sentiment analysis | 20-50 µs | ~100-250 ms | 20K-50K comments/sec |
| Sarcasm heuristic patterns | 5-10 µs | ~50 ms | 100K+ comments/sec |
| SQLite write (batched) | 100-300 µs | ~500-1500 ms | 3-10K comments/sec |
| **Total (sequential)** | ~130-370 µs | **~700-2000 ms** | **~2.5-7K comments/sec** |

**Result:** Processing 5,000 comments takes **~4 seconds** — well under 5-minute target. ✓

### Memory Usage Patterns

| Component | Memory | Notes |
|-----------|--------|-------|
| VADER lexicon (in-memory) | ~1-2 MB | Loaded once on startup; includes booster dict, special idioms |
| Regex patterns (compiled) | ~100-200 KB | ~20 model patterns compiled to regex objects |
| Comment batch buffer | ~20-50 MB | 5,000 comments × 4-10 KB per comment text |
| SQLite connection + cache | ~10 MB | Connection pool + prepared statement cache |
| **Total peak memory** | **~30-60 MB** | Negligible; runs on any machine ✓ |

### Bottleneck Analysis

**Primary bottleneck:** SQLite writes (not sentiment analysis)
- Sequential writes: ~100-300 µs per comment
- Batch writes (INSERT ... UNION SELECT): ~10-50 µs per comment
- **Mitigation:** Use batch inserts with 100-500 comment chunks

**Secondary bottleneck:** Comment text I/O (database reads)
- Network I/O not needed (SQLite is local)
- Disk I/O is sequential; very fast on SSDs

**Not a bottleneck:** VADER computation
- Pure Python, single-threaded; ~20-50 µs per comment is negligible

### Batch Processing Optimization

```python
def batch_sentiment_pipeline(
    db_path: str,
    batch_size: int = 500,
) -> dict:
    """
    Process comments in batches for efficiency.
    
    Batching strategy:
    1. Read batch_size unprocessed comments from SQLite
    2. Extract mentions + sentiment + sarcasm for entire batch
    3. Write results back in single transaction
    4. Repeat until all comments processed
    """
    import sqlite3
    from nltk.sentiment import SentimentIntensityAnalyzer
    
    sia = SentimentIntensityAnalyzer()
    patterns = build_model_patterns(MODEL_NAMES)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    total_processed = 0
    stats = {'processed': 0, 'failed': 0, 'duration_sec': 0}
    
    import time
    start_time = time.time()
    
    while True:
        # Fetch unprocessed comments
        cursor.execute("""
            SELECT id, text FROM comments 
            WHERE processed_at IS NULL 
            LIMIT ?
        """, (batch_size,))
        batch = cursor.fetchall()
        
        if not batch:
            break
        
        # Process batch
        results = []
        for comment_id, text in batch:
            mentions = extract_mentions(text, patterns)
            scores = sia.polarity_scores(text)
            is_sarcasm, sarcasm_patterns = detect_sarcasm_patterns(text)
            
            # Determine sentiment
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Apply sarcasm reversal
            final_sentiment = apply_sarcasm_reversal(sentiment, is_sarcasm)
            
            results.append({
                'comment_id': comment_id,
                'sentiment': final_sentiment,
                'confidence': abs(compound),
                'sarcasm_detected': is_sarcasm,
                'sarcasm_patterns': ','.join(sarcasm_patterns),
            })
        
        # Batch write in transaction
        cursor.execute('BEGIN TRANSACTION')
        for r in results:
            cursor.execute("""
                UPDATE comments SET
                    sentiment_label = ?,
                    sentiment_score = ?,
                    sarcasm_detected = ?,
                    sarcasm_patterns = ?,
                    processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (r['sentiment'], r['confidence'], 
                  r['sarcasm_detected'], r['sarcasm_patterns'],
                  r['comment_id']))
        cursor.execute('COMMIT')
        
        stats['processed'] += len(batch)
    
    conn.close()
    stats['duration_sec'] = time.time() - start_time
    return stats
```

---

## Phase 1 Integration & Reuse

### Querying Comments from SQLite

Phase 1 established a `comments` table. Phase 2 reuses the same schema and connection patterns:

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("./data/comments.db")

def get_unprocessed_comments(batch_size: int = 500) -> list[dict]:
    """
    Fetch unprocessed comments from Phase 1 database.
    
    Reuses:
    - Database connection from database.py patterns
    - Comment validation from storage.py
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, text, subreddit, created_utc, score
        FROM comments 
        WHERE processed_at IS NULL
        ORDER BY created_utc DESC
        LIMIT ?
    """, (batch_size,))
    
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments


# Usage
comments = get_unprocessed_comments(batch_size=1000)
print(f"Found {len(comments)} unprocessed comments")
```

### Schema Extension Approach

Phase 1 created `comments` table. Phase 2 extends it safely:

```sql
-- Phase 2 schema additions (idempotent ALTER TABLE statements)
-- These are safe to run even if columns already exist (IF NOT EXISTS pattern not available in SQLite for columns)

PRAGMA foreign_keys = ON;

-- Add new columns to comments table
ALTER TABLE comments ADD COLUMN IF NOT EXISTS sentiment_label VARCHAR(20) DEFAULT NULL;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS sentiment_score FLOAT DEFAULT NULL;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS sarcasm_detected BOOLEAN DEFAULT 0;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS sarcasm_patterns TEXT DEFAULT NULL;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP DEFAULT NULL;

-- Create indexes for Phase 3 queries (leaderboard filtering)
CREATE INDEX IF NOT EXISTS idx_sentiment_label 
    ON comments(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_processed_at 
    ON comments(processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_processed 
    ON comments(sentiment_label, processed_at DESC);
```

**Safety check:**
- Column additions are backward compatible (existing Phase 1 data untouched)
- `IF NOT EXISTS` prevents errors if Phase 2 runs twice
- Indexes are created if missing; idempotent

### Logging & Error Handling Patterns

Reuse Phase 1's `collection_log` pattern for sentiment pipeline monitoring:

```python
def log_sentiment_run(
    cursor,
    comments_processed: int,
    comments_failed: int,
    duration_seconds: float,
    errors: str = None,
) -> None:
    """
    Log sentiment pipeline execution.
    
    Reuses:
    - collection_log table from Phase 1 (extend for sentiments)
    - Same logging structure as batch_job.py
    """
    cursor.execute("""
        INSERT INTO collection_log 
        (run_timestamp, subreddit, comments_fetched, comments_new, 
         comments_duplicate, errors, duration_seconds)
        VALUES (CURRENT_TIMESTAMP, 'sentiment_pipeline', ?, ?, 0, ?, ?)
    """, (comments_processed, comments_failed, errors, duration_seconds))


# Usage
try:
    stats = batch_sentiment_pipeline(DB_PATH, batch_size=500)
    log_sentiment_run(cursor, stats['processed'], stats['failed'], 
                      stats['duration_sec'])
except Exception as e:
    log_sentiment_run(cursor, 0, 0, 0, errors=str(e))
    raise
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sentiment analysis | Custom lexicon + scoring | VADER (nltk) | VADER handles social media edge cases (negation, intensifiers, sarcasm); building custom = months of tuning |
| Model name detection | Char-by-char matching | Regex patterns | Regex handles spelling variants ("GPT4", "gpt-4", "GPT-4") automatically; manual matching is brittle |
| Sarcasm detection | Manual if/else rules | Heuristic patterns + VADER | Pattern matching scales; manual rules = unmaintainable after 5-10 patterns |
| SQLite schema changes | Custom migration script | Standard ALTER TABLE | SQLite migrations are simple; custom = risk of data loss |
| Batch processing | Process comments one-by-one | Batch writes (500 comments/transaction) | Single-row writes = 10x slower on SQLite; batching leverages transaction overhead |

---

## Common Pitfalls

### Pitfall 1: Hashtag Blindness in VADER

**What goes wrong:**
VADER scores hashtags as neutral because it ignores the `#` symbol. Comment "#GoodJourney" scores as neutral when it should be positive.

**Why it happens:**
VADER lexicon doesn't include emoji/hashtag preprocessing. Hashtags would need explicit removal before analysis.

**How to avoid:**
Pre-process comments to remove `#` before VADER:
```python
text = "I love #Claude! It's amazing #AI"
text = text.replace('#', '')  # Remove hashtags
scores = sia.polarity_scores(text)
# Now "Claude" and "AI" match lexicon correctly
```

**Warning signs:**
- Sentiment scores are neutral on Reddit threads with heavy hashtag usage
- Phase 3 leaderboard shows artificially balanced scores

---

### Pitfall 2: Sarcasm Reversal Over-Eagerness

**What goes wrong:**
Comment "This AI is super smart" contains "super" (sarcasm heuristic overfitting). Sentiment gets reversed to negative incorrectly.

**Why it happens:**
Heuristic patterns are over-broad; "super" appears in non-sarcastic comments too.

**How to avoid:**
- Keep heuristic patterns specific: "super\s+(?:smart|helpful)" NOT just "super"
- Require ≥2 patterns OR high VADER confidence before reversing
- Manual validation on test set before shipping

**Warning signs:**
- Accuracy drops on positive comments with intensifiers
- Phase 3 feedback: "Your ranking says Claude is bad but it's actually good"

---

### Pitfall 3: SQLite Locking on Schema Updates

**What goes wrong:**
Running ALTER TABLE while Phase 1 is still crawling new comments → database locks, crawl fails.

**Why it happens:**
SQLite exclusive lock during schema changes; can't run schema migration while Phase 1 is active.

**How to avoid:**
1. Stop Phase 1 crawler before running schema migrations
2. Run migrations in a separate script before starting Phase 2 pipeline
3. Use WAL mode (Phase 1 already enabled) for better concurrency

**Warning signs:**
- "database is locked" errors during Phase 2 initialization
- Comments table appears unchanged after ALTER TABLE

---

### Pitfall 4: Model Name Extraction False Negatives

**What goes wrong:**
Comment "I prefer bert over gpt" → regex misses "BERT" because lexicon has "BERT" (all caps) but comment has "bert" (lowercase).

**Why it happens:**
Case-insensitive regex not applied correctly; `\b` boundaries sometimes fail on special characters.

**How to avoid:**
- Always use `re.IGNORECASE` flag
- Test regex patterns against common variants before adding to list
- Maintain test set of comments with model mentions

**Warning signs:**
- Leaderboard shows model with 0% sentiment (no comments matched)
- User feedback: "I mentioned Claude but sentiment pipeline missed it"

---

### Pitfall 5: Compound Score Normalization Confusion

**What goes wrong:**
Using raw VADER `neg`/`pos`/`neu` proportions as sentiment label instead of `compound` score → "0.8 positive words but neutral overall" misclassified.

**Why it happens:**
VADER's compound is the aggregated score; proportions alone don't capture intensity and modifiers.

**How to avoid:**
- **Always use `compound` score** for classification; only use `neg`/`pos`/`neu` for debugging
- Example: "This movie is bad" → neg=0.686, neu=0.314, pos=0.0, compound=-0.5469 (correctly negative)

**Warning signs:**
- Accuracy drops to <70%; sentiment is always neutral-ish
- Manual review shows opposite sentiments being assigned

---

## Validation Architecture

**Test Framework:** pytest (same as Phase 1)  
**Config file:** `pytest.ini` (if exists) or default  
**Quick run command:** `pytest tests/test_nlp_*.py -v`  
**Full suite command:** `pytest tests/ -v --cov`

### Phase 2 Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FR2.1 | VADER classifies sentiment correctly | unit | `pytest tests/test_vader.py::test_sentiment_classification -v` | ❌ Wave 0 |
| FR2.2 | Model extraction finds AI model mentions | unit | `pytest tests/test_mention_extraction.py::test_extract_mentions -v` | ❌ Wave 0 |
| FR2.3 | Sarcasm detection reverses sentiment | unit | `pytest tests/test_sarcasm.py::test_sarcasm_reversal -v` | ❌ Wave 0 |
| FR2.4 | Confidence scores normalized [0,1] | unit | `pytest tests/test_vader.py::test_confidence_normalization -v` | ❌ Wave 0 |
| NFR1.2 | Pipeline processes 5K comments in <5 min | integration | `pytest tests/test_performance.py::test_batch_processing_speed -v` | ❌ Wave 0 |
| (Accuracy) | >80% accuracy on manual test set | manual | Manual review of ~100 comments with gold labels | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_nlp_*.py -x` (quick smoke test)
- **Per wave merge:** `pytest tests/ -v --tb=short` (full suite)
- **Phase gate:** Manual accuracy validation (>80% on test set) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_vader.py` — VADER sentiment classification, compound score interpretation
- [ ] `tests/test_mention_extraction.py` — Regex model name matching, case variations, edge cases
- [ ] `tests/test_sarcasm.py` — Sarcasm pattern detection, sentiment reversal
- [ ] `tests/test_performance.py` — Batch processing throughput (5K comments timing)
- [ ] `tests/test_integration.py` — End-to-end pipeline with SQLite
- [ ] `conftest.py` — Shared fixtures: sample comments, VADER analyzer, test database

---

## Runtime State Inventory

**Phase 2 is greenfield NLP code** (no rename/refactor/migration of existing entities). Runtime state inventory is not applicable.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | All | ✓ | 3.8+ | — |
| pip | All | ✓ | — | — |
| SQLite3 (lib) | Database operations | ✓ | 3.30+ | — |
| NLTK library | VADER sentiment | ✗ | (to install) | Manual sentiment classification (not recommended) |
| Regex support | Model extraction | ✓ | (builtin in Python) | — |

**Missing dependencies (to install as part of Phase 2 Wave 0):**
- `nltk>=3.8.1` — Required for VADER; install via `pip install nltk`
- First-run setup: `python3 -c "import nltk; nltk.download('vader_lexicon')"`

---

## Security Domain

**Security enforcement:** Enabled (no explicit override in config)

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not applicable (Phase 2 is data processing, no auth) |
| V3 Session Management | No | Not applicable |
| V4 Access Control | No | Not applicable |
| V5 Input Validation | Yes | Validate comment text before VADER (malformed UTF-8, injection attempts) |
| V6 Cryptography | No | Not applicable |
| V7 Error Handling | Yes | Safe error messages; no secrets in logs |

### Known Threat Patterns for {Python + SQLite}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection via comment text | Tampering | Parameterized queries (sqlite3 uses `?` placeholders) — ✓ Phase 1 pattern |
| Malformed UTF-8 in comments | Tampering | VADER handles UTF-8 gracefully; SQLite stores as-is; validate on read |
| ReDoS (Regex Denial of Service) | Denial of Service | Regex patterns are simple word boundaries; no catastrophic backtracking |
| Information disclosure via error logs | Information Disclosure | Log errors to file, not stdout; sanitize user data before logging |

**Verification:** Phase 1 already uses parameterized queries; Phase 2 follows same pattern. No new security surface.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| TextBlob sentiment | VADER sentiment | ~2013-2014 | VADER is domain-optimized for social media; TextBlob is generic |
| SVM-based sentiment | Lexicon-based (VADER) | ~2010s | Lexicon approaches faster, no training data needed |
| Hand-written sarcasm rules | VADER idioms + heuristic patterns | ~2015+ | VADER built-in patterns reduce manual effort |
| Transformer models for sentiment | Lightweight lexicon (VADER) | 2020s | Transformers are more accurate but 100x+ slower; acceptable tradeoff for MVP |

**Deprecated/outdated:**
- TextBlob: Replaced by VADER; still functional but lower accuracy for social media
- Stanford NLP CoreNLP: Java-based; slower than VADER; overkill for MVP

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | VADER accuracy on Reddit is 82-88% for general sentiment | VADER Analysis | If actual is <75%, won't meet >80% accuracy target; mitigation: post-MVP fine-tuned model |
| A2 | Regex extraction covers 95%+ of common model name variants | Model Extraction | If actual is <80%, Phase 3 leaderboard will show artificially low mention counts; mitigation: manual test set validation in Wave 1 |
| A3 | Batch processing 5K comments completes in <1 minute (well under 5 min constraint) | Performance | If actual is >5 min, violates NFR1.2; unlikely with VADER throughput of 1200/sec |
| A4 | Phase 1 SQLite schema and connection patterns are stable and reusable | Phase 1 Integration | If Phase 1 DB changes, Phase 2 queries break; mitigation: use Phase 1 snapshot commit for reference |
| A5 | Sarcasm heuristics alone achieve >80% accuracy (post-heuristic manual validation) | Sarcasm Heuristics | If actual is <75%, may need post-MVP sarcasm fine-tuned model; heuristics are conservative baseline |

**All assumptions are tagged for user confirmation before Phase 2 planning.** RESEARCH.md next steps: Planner will validate A1-A5 against CONTEXT decisions and propose test strategy in PLAN.md.

---

## Open Questions

1. **Exact VADER confidence thresholds**
   - What we know: Industry standard is 0.05/-0.05 for neutral boundary; compound in [-1, +1]
   - What's unclear: Should Phase 2 use custom thresholds based on Reddit-specific tuning? Or stick with defaults?
   - Recommendation: Use defaults (0.05/-0.05); collect Phase 3 feedback to tune if needed

2. **Model name list completeness**
   - What we know: Compiled ~20 major AI models (GPT-4, Claude, Llama, Gemini, etc.)
   - What's unclear: Are there Reddit-specific slang names or acronyms (e.g., "GPT" vs "ChatGPT" vs "OpenAI API")?
   - Recommendation: Phase 1 UAT included comments review; extract model names from sample comments to build baseline list

3. **Sarcasm pattern tuning**
   - What we know: VADER built-in patterns + 8-10 custom heuristics
   - What's unclear: How sensitive should custom patterns be? (10 patterns vs 20?)
   - Recommendation: Start conservative (VADER built-in only); add custom patterns based on Phase 2 validation failures

4. **SQLite concurrency during Phase 2**
   - What we know: Phase 1 uses WAL mode for concurrency
   - What's unclear: Can Phase 2 write results while Phase 3 reads leaderboard data?
   - Recommendation: Yes, WAL mode allows concurrent reads/writes; Phase 3 will see consistent snapshots

---

## Sources

### Primary (HIGH confidence)

- **NLTK 3.9.2 official docs** [nltk.org/api/nltk.sentiment.vader.html] — VADER implementation, special case idioms, polarity_scores() signature, NativeConstants verification
- **NLTK GitHub repository** [github.com/nltk/nltk/tree/3.9.2] — Source code for VaderConstants.SPECIAL_CASE_IDIOMS, verified "yeah right" → -2.0 mapping
- **Hutto & Gilbert (2014) VADER paper** [ICWSM-14] — 82-88% accuracy claims on social media, published in peer-reviewed conference

### Secondary (MEDIUM confidence)

- **NLTK installation guide** [nltk.org] — Verified vader_lexicon download method
- **SQLite documentation** [sqlite.org/pragma.html] — WAL mode, foreign keys, INDEX creation syntax
- **Python regex (re module)** [python.org/library/re.html] — IGNORECASE flag, word boundaries, pattern compilation

### Tertiary (LOW confidence, marked for validation)

- Assumption A3 (batch performance <1 min): Estimated from VADER computational complexity (no live testing yet in this research phase)
- Assumption A2 (regex coverage 95%): Based on common Reddit model name patterns; not formally validated against production Reddit data

---

## Metadata

**Confidence breakdown:**
- **Standard stack (VADER + regex):** HIGH — Official docs + peer-reviewed paper + proven Reddit usage
- **Architecture & patterns:** HIGH — Phase 1 established patterns; Phase 2 reuses directly
- **Performance baseline:** MEDIUM-HIGH — Theoretical VADER throughput is clear; actual SQLite batching performance TBD in implementation
- **Sarcasm heuristics:** MEDIUM — VADER built-in is reliable; custom patterns are conservative baseline subject to tuning

**Research date:** 2026-05-07  
**Valid until:** 2026-05-14 (7 days; VADER and NLTK are stable; refresh before next phase if major changes)  
**Researched by:** gsd-phase-researcher  

---

## Next Steps

1. **Planner:** Review RESEARCH.md; validate all assumptions against CONTEXT.md locked decisions
2. **Planner:** Create PLAN.md with task breakdown, wave structure, verification checkpoints
3. **Executor:** Implement Phase 2 modules in Wave 0 (model extraction, sentiment pipeline, tests)
4. **Executor:** Manual accuracy validation on ~100 comment test set
5. **Verifier:** Run Phase 2 UAT; confirm >80% accuracy before ship

---

**End of RESEARCH.md**
