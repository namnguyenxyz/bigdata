# Requirements: AI Model Ranking System

## Functional Requirements

### FR1: Data Collection
- FR1.1 Retrieve Reddit posts and comments from target subreddits
- FR1.2 Extract AI model mentions from text (ChatGPT, Claude, Gemini, Llama, etc.)
- FR1.3 Filter and clean data for NLP processing
- FR1.4 Store collected data with metadata (upvotes, timestamp, subreddit, user)
- FR1.5 Support incremental data updates without duplication

### FR2: Sentiment Analysis
- FR2.1 Classify comments as Positive, Negative, or Neutral sentiment
- FR2.2 Extract model-specific sentiment (e.g., "Claude is fast but expensive")
- FR2.3 Handle sarcasm detection (Reddit-specific)
- FR2.4 Generate confidence scores for sentiment predictions

### FR3: Ranking Algorithm
- FR3.1 Calculate weighted sentiment score per model
- FR3.2 Apply engagement weights (upvotes/downvotes ratio)
- FR3.3 Apply source credibility weights (subreddit type, user karma)
- FR3.4 Generate final ranked leaderboard
- FR3.5 Support time-window filtering (last 30 days, all-time, etc.)

### FR4: Display & Visualization
- FR4.1 Display ranked model leaderboard with scores
- FR4.2 Show ranking trend over time
- FR4.3 Display sentiment distribution (pie chart, bar chart)
- FR4.4 Show sample comments supporting each model's ranking
- FR4.5 Interactive filtering by subreddit, date range, model

### FR5: Data Refresh
- FR5.1 Automated data collection on schedule
- FR5.2 Incremental ranking updates
- FR5.3 Data staleness monitoring and alerts

## Non-Functional Requirements

### NFR1: Performance
- NFR1.1 Render leaderboard page in <2 seconds
- NFR1.2 Process new data within 1 hour of collection
- NFR1.3 Handle 1000+ comments in batch processing

### NFR2: Scalability
- NFR2.1 Support addition of new subreddits without re-architecture
- NFR2.2 Support expansion to 20+ models
- NFR2.3 Maintain accuracy with growing dataset

### NFR3: Reliability
- NFR3.1 Handle Reddit API rate limits gracefully (retry, backoff)
- NFR3.2 Persist data across application restarts
- NFR3.3 Validate data integrity

### NFR4: Maintainability
- NFR4.1 Code documentation for NLP pipeline
- NFR4.2 Configuration file for subreddits and models (not hard-coded)
- NFR4.3 Logging for debugging and monitoring
- NFR4.4 Unit tests for core ranking logic

### NFR5: Usability
- NFR5.1 Clean, intuitive UI
- NFR5.2 Mobile-responsive design
- NFR5.3 Clear explanation of ranking methodology

## Constraints
- **Timeline**: 1-2 weeks for MVP
- **Team**: 2-3 people
- **Budget**: Minimal (free Reddit API tier)
- **Tech Stack**: Python backend + Streamlit frontend

## Out of Scope (Post-MVP)
- Real-time live updating (15+ second delay acceptable for MVP)
- Advanced NLP (multi-lingual, fine-tuned models)
- Model benchmark comparison integration
- User authentication and personalization
- API for external consumption

## Success Criteria
1. Leaderboard reflects genuine community sentiment
2. System processes Reddit data without breaking API limits
3. Ranking is explainable and reproducible
4. UI is intuitive for target users (developers)
5. MVP ships within 1-2 weeks

---
**Version**: 1.0  
**Created**: 2026-05-07
