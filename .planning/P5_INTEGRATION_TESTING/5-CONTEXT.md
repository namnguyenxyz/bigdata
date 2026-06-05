# Phase 5 Context: Integration, Testing & Deployment

## Phase
P5_INTEGRATION_TESTING

## Phase Name
Integration, Testing & Deployment

## Phase Goal
Ship a reliable end-to-end MVP by validating that data collection, sentiment analysis, ranking, and the dashboard work together as a cohesive system. Add deployment-ready documentation and local launch instructions so the project can be run and reviewed by others.

## What this phase consumes
- Phase 1 Reddit data collection pipeline and SQLite schema
- Phase 2 NLP sentiment extraction and sarcasm handling
- Phase 3 ranking algorithm and scored model leaderboard
- Phase 4 Streamlit dashboard and visualization components
- Existing tests, verification artifacts, and documentation

## What this phase produces
- End-to-end integration tests for the full pipeline
- Deployment/run instructions for local MVP execution
- Release checklist for data refresh, dashboard launch, and verification
- Bug fixes for integration gaps and end-to-end data flow issues
- Final verification artifact for MVP readiness

## Locked Decisions
- D-01: The MVP is a local Python/Streamlit deployment; no cloud hosting is required now.
- D-02: End-to-end testing will focus on the existing SQLite pipeline and dashboard path.
- D-03: The deployment guide should target developer setup, not production operations.
- D-04: All phases must remain compatible with the same database schema and local dependencies.

## Success Criteria
- ✅ The full pipeline runs end-to-end locally and produces the dashboard leaderboard
- ✅ Integration tests cover data collection, sentiment processing, ranking, and dashboard import
- ✅ Deployment docs let a reviewer run `python database.py`, collect data, run the sentiment pipeline, and launch the dashboard
- ✅ Any integration gaps are identified and fixed before handoff
- ✅ The project is ready for a code review or demo without manual setup guessing

## Constraints
- Must use the existing SQLite-backed architecture and local Python environment
- Must not add complex infrastructure or deployment platforms for MVP
- Must not alter Phase 1-4 deliverables beyond fixes needed for integration
- Must preserve reproducibility and simplicity for reviewers

## Risks
- R-01: The dashboard data path may diverge from the ranking engine or database schema
- R-02: Local environment setup may be incomplete or missing dependency declarations
- R-03: End-to-end smoke testing may reveal performance or data consistency issues
- R-04: Tests may be too shallow and miss important cross-component failures

## Mitigations
- Use integration tests that exercise the live SQLite database and dashboard import path
- Document exact commands for setup, pipeline execution, and dashboard launch
- Keep the integration scope narrow and focused on MVP flows
- Add a final verification checklist covering both runtime and documentation
