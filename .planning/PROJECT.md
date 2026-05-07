# AI Model Ranking via Reddit Sentiment Analysis

## Project Vision
Establish a dynamic ranking system for AI models (ChatGPT, Claude, Gemini, Llama, etc.) based on actual user experiences from Reddit discussions rather than laboratory benchmarks. This provides a "ground truth" reflection of how these models perform in real-world use by the developer and enthusiast communities.

## Problem Statement
Existing AI model rankings rely on static benchmarks that don't capture real-world user sentiment, community feedback, or emerging issues like performance degradation, hallucinations, or censoring. This project fills that gap by analyzing authentic community discussions to derive a continuous, sentiment-driven leaderboard.

## Core Value Propositions
1. **Battle-Tested Insights** — Reveals real-world model performance beyond lab scores (e.g., laziness, hallucinations, censoring)
2. **Real-Time Market Pulse** — Updated continuously as communities react to model patches and releases
3. **Transparency** — Shows which models are genuinely used and valued by developers and enthusiasts

## How It Works
Three-tier pipeline:
1. **Targeted Data Acquisition** — Focus on curated subreddits (r/MachineLearning, r/ChatGPT, r/LocalLLaMA, etc.)
2. **NLP-Driven Sentiment Analysis** — Parse comments, categorize sentiment (Positive/Negative/Neutral), extract model mentions and attributes
3. **Weighted Ranking Algorithm** — Apply engagement weights (upvotes/downvotes) and source credibility to produce realistic leaderboard

## Key Technical Challenges
- Reddit API rate limits
- Sarcasm detection (Reddit culture staple)
- Community bias (open-source vs. proprietary model favoritism)
- Maintaining fresh, accurate data

## Success Metrics
- A meaningful model leaderboard that reflects community sentiment accurately
- System can process and rank models in a sustainable way
- Results resonate with actual developer experience

## Stakeholders
- **Primary Users**: Developers, AI enthusiasts, model evaluators
- **Secondary**: Data analysts, researchers, AI selection committees

## Team
- Small team (2-3 people)

## Timeline
- Immediate (1-2 weeks) for MVP

## Technology Preferences
- **Backend**: Python
- **Frontend**: Streamlit
- **Data Source**: Reddit API

## MVP Definition
A leaderboard of AI models ranked by community sentiment from target subreddits, with transparent ranking logic.

---

## Project Status
- **Created**: 2026-05-07
- **Current Phase**: Requirements & Roadmap Generation
- **Next Step**: Execute Phase 1 planning
