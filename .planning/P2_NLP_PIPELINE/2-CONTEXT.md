---
phase: P2_NLP_PIPELINE
phase_number: 2
phase_name: NLP Pipeline & Sentiment Analysis
created: 2026-05-07
created_by: gsd-progress --next
decision_status: locked
---

# Phase 2 Context: NLP Pipeline & Sentiment Analysis

**Phase Goal**: Extract model mentions and classify sentiment from the 5,000+ comments collected in Phase 1, with confidence scores and sarcasm handling. Prepare data for Phase 3 leaderboard ranking.

**Success Criteria** (from ROADMAP.md):
- ✅ Accuracy on manual test set >80%
- ✅ Processes 5000 comments in <5 minutes
- ✅ Correctly handles sarcasm samples

---

## Locked Decisions

### 1. Model Mention Extraction Strategy
**Decision**: Rule-based/regex approach for MVP  
**Rationale**: Fast implementation, no training required, good enough for initial phase. Can upgrade to NER later if accuracy insufficient.

**Implementation Details**:
- Maintain a configurable list of AI model names (e.g., GPT-4, Claude, Llama, etc.)
- Use regex patterns to find mentions in comment text
- Extract context window around each mention (e.g., surrounding sentence)
- Store raw mention text + detected model name + confidence score (1.0 for exact match, <1.0 for fuzzy)

**Future Extension**: In post-MVP phases, can replace with a pre-trained NER model (e.g., spaCy NER or transformer-based) for higher accuracy on ambiguous mentions.

---

### 2. Sentiment Classification Approach
**Decision**: VADER (Valence Aware Dictionary and sEntiment Reasoner)  
**Rationale**: Lightweight, Reddit-optimized lexicon. No GPU required. Proven effective for social media text (sarcasm heuristics built-in).

**Implementation Details**:
- Use `nltk.sentiment.vader.SentimentIntensityAnalyzer`
- Output: `negative` | `neutral` | `positive` (mapped from VADER's compound score)
- Confidence: Use VADER's compound score (0-1) as confidence metric
- Normalize: Compound in [-1, 1] → map to [0, 1] confidence range
- Store: `sentiment_label` (negative/neutral/positive) + `sentiment_score` (0-1)

**Trade-off**: Lower accuracy than transformer models, but much faster and lower resource cost. Acceptable for MVP with >80% target on manual validation.

---

### 3. Sarcasm Detection Strategy
**Decision**: Heuristic/rule-based approach  
**Rationale**: Fast and simple for MVP. Pattern-matching for common sarcasm indicators.

**Implementation Details**:
- Pattern list: `["yeah right", "sure buddy", "oh great", "how wonderful", "perfect", "brilliant"]` (configurable)
- Detection: If pattern found in comment → flag as `sarcasm_heuristic: true`
- Sarcasm handling: If sarcasm detected, reverse sentiment polarity (e.g., positive → negative)
- Store: `sarcasm_detected` (bool) + `sarcasm_patterns` (list of matched patterns)

**Validation**: Manual review of sarcasm samples to calibrate patterns before Phase 2 completion.

**Future Enhancement**: Post-MVP can add fine-tuned sarcasm classification model if heuristic accuracy <80%.

---

### 4. Data Storage Strategy
**Decision**: Extend SQLite schema with sentiment columns  
**Rationale**: Single source of truth. Simpler data model for downstream phases. Easier joins for leaderboard generation in Phase 3.

**Schema Extension** (add to `comments` table):
```sql
ALTER TABLE comments ADD COLUMN sentiment_label VARCHAR(20) DEFAULT NULL;
ALTER TABLE comments ADD COLUMN sentiment_score FLOAT DEFAULT NULL;
ALTER TABLE comments ADD COLUMN sarcasm_detected BOOLEAN DEFAULT 0;
ALTER TABLE comments ADD COLUMN sarcasm_patterns TEXT DEFAULT NULL;  -- JSON array
ALTER TABLE comments ADD COLUMN processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

**Indexes**: Add index on `(processed_at, sentiment_label)` for efficient queries in Phase 3.

**Alternative considered but rejected**: Separate `sentiments` table — adds join complexity without benefit for MVP.

---

### 5. Pipeline Execution Strategy
**Decision**: Batch processing (scheduled, process-all-at-once)  
**Rationale**: Simpler architecture. Good for MVP. Can run nightly or on-demand.

**Implementation Details**:
- Entry point: Python script `sentiment_pipeline.py` (or similar)
- Process: Load all unprocessed comments → run sentiment analysis → update SQLite
- Idempotency: Check `processed_at` timestamp; skip already-processed comments
- Output: Summary stats (comments processed, sentiment distribution, runtime)
- Scheduling: Can be wrapped in cron job or manual trigger

**Alternative considered but rejected**:
- Incremental (only new comments) — adds state management complexity
- Real-time streaming — requires Kafka/message queue; too heavy for MVP

---

### 6. Accuracy Target
**Decision**: >80% accuracy (strict, high quality)  
**Rationale**: Matches ROADMAP success criteria. Ensures Phase 3 leaderboard is reliable.

**Validation Approach**:
- Manual test set: Create ~100 comments with gold-standard sentiment/sarcasm labels
- Evaluate: Test pipeline against manual labels; calculate precision/recall/F1
- Threshold: Must achieve ≥80% accuracy before shipping Phase 2
- If <80%: Review failure cases and adjust patterns/tuning before production

---

## Required Artifacts (Phase 2 Deliverables)

1. **NLP Pipeline Module** (`nlp_pipeline.py` or similar)
   - Model mention extraction (regex-based)
   - Sentiment analysis (VADER)
   - Sarcasm detection (heuristic)
   - Error handling and logging

2. **Storage Integration** (`sentiment_storage.py` or similar)
   - SQLite connection and schema extension
   - Insert/update operations for sentiment results
   - Query helpers for Phase 3 (e.g., get comments by sentiment)

3. **Batch Job Orchestrator** (`run_sentiment_pipeline.py` or similar)
   - Load comments from database
   - Call NLP pipeline for each comment
   - Batch write results back to SQLite
   - Summary output and error reporting

4. **Test Suite** (offline validation)
   - Test model mention extraction (various formats, edge cases)
   - Test sentiment classification (positive/negative/neutral)
   - Test sarcasm detection (sarcasm patterns vs normal text)
   - Integration test: end-to-end batch job with sample comments
   - Accuracy validation against manual test set

5. **Configuration** (`.env`, defaults, patterns)
   - Model names list (AI models to detect)
   - Sarcasm patterns list
   - VADER tuning parameters (if needed)
   - Batch size and processing options

6. **Documentation**
   - NLP Pipeline README (setup, usage, adding new models/patterns)
   - Manual test set template (for validation before ship)
   - Troubleshooting guide (common issues, debugging)

---

## Canonical References
- `.planning/ROADMAP.md` — Phase 2 specification and success criteria
- `.planning/REQUIREMENTS.md` — NFR requirements (performance, accuracy)
- `reddit_auth.py` — Credential loading pattern (reuse for consistency)
- `database.py` — SQLite schema patterns and WAL mode setup
- `storage.py` — Data validation and error handling patterns

---

## Code Context (Reusable from Phase 1)

**Available patterns:**
- Credential/config loading: `reddit_auth.py` has clean env var + error handling pattern
- Database operations: `database.py` has connection pooling, schema management, indexes
- Storage layer: `storage.py` has validation, error recovery, logging patterns
- Testing: `tests/test_*.py` files show offline-first approach with fake object injection

**Recommended reuse:**
- Use same Python environment (3.14.4+)
- Use same SQLite database and connection patterns
- Follow same error handling and logging conventions
- Continue offline testing pattern (no live Reddit API needed)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| VADER accuracy <80% on sarcasm-heavy comments | Medium | Manual tuning of patterns; fallback: post-MVP fine-tuned model |
| Regex mention extraction misses variant spellings | Medium | Build configurable model name list with common aliases; gather feedback from Phase 3 |
| Batch processing too slow (>5 min for 5K comments) | Medium | Profile performance; consider batching in chunks; skip transformer overhead with VADER |
| Schema alteration breaks existing data | Low | Phase 1 data already committed; use migration script to add columns safely |
| Sarcasm heuristics too simplistic | Low | Monitor false positives during validation; upgrade to ML model post-MVP if needed |

---

## Deferred Ideas (Not in Phase 2 Scope)

These are valuable but belong in future phases or as post-MVP enhancements:
- **Fine-tuned NER for model mentions**: Post-MVP after gathering feedback on regex accuracy
- **Transformer-based sentiment (DistilBERT)**: Phase 2 extension if VADER accuracy insufficient
- **Multi-language support**: Future phase (currently Reddit = English-heavy)
- **Real-time streaming architecture**: Future enhancement when volume grows
- **Sarcasm fine-tuned model**: Post-MVP, only if heuristic accuracy <80%

---

## Next Steps (After Context)

1. **Researcher phase**: Validate VADER performance on Reddit comments; gather model names list and sarcasm patterns
2. **Planner phase**: Create detailed PLAN.md with 3-5 work streams, task breakdown, dependencies
3. **Execution phase**: Implement NLP pipeline modules, tests, batch orchestrator
4. **Verification phase**: Validate >80% accuracy, performance <5 min on 5K comments, ship PR #2

---

**Session**: Phase 2 context captured via `/gsd-progress --next`  
**Status**: Ready for research → planning → execution  
**Next Command**: `/gsd-plan-phase 2`
