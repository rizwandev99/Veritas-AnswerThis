# Project Memory & Guidelines

<!-- === ZONE 1: USER-OWNED (DO NOT MODIFY BY AGENT) === -->
## Project Overview & Directives
- **Project**: Veritas - Citation-Verified Literature Review Generator
- **Purpose**: Portfolio & cold-outreach showcase for AnswerThis. End-to-end citation-verified literature review generator (Next.js, React, Tailwind, Python/FastAPI, Postgres, vector search/RAG, Docker, CI/CD).
- **Core Value**: Standout claim-level citation verification (Supported, Partial, Unsupported) + interactive citation graph.
- **Specification**: Governed strictly by `PRD Veritas - Citation-Verified Literature Review Generator.md`.
- **Engineering Rules**:
  - Test-Driven Development (TDD) mandatory: failing tests first per acceptance criterion (AC).
  - PRD Code Review Gate per feature in `docs/reviews/<feature-id>.md`.
  - Atomic micro-commits adhering to PRD milestones.
  - Zero cost / 100% free tier tools & services only.
  - Strict compliance with Section 13 Non-Goals.

<!-- === ZONE 2: AGENT-MAINTAINED (UPDATED BY AGENT) === -->
## Architecture & Active Context
### Key Architectural Decisions
- Initialized project memory following repository setup and PRD inspection.
- Milestone F0 completed: Decoupled monorepo scaffold (apps/web + apps/api), Linear-grade design system, anti-FOUC theme engine, Docker Compose with pgvector, GitHub Actions CI workflow, and passing test suites.
### Technical Gotchas & Traps
- `pydantic-settings` v2 attempts `json.loads` on `List[str]` env vars; resolved by typing `Union[str, List[str]]` with comma-split fallback in validator.
### Active Milestone & Next Steps
- Status: Milestone F0 committed. Proceeding to Milestone F1 (Paper Discovery & Ranking with OpenAlex, FAISS/pgvector VectorStore).
