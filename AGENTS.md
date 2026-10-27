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
- Milestone F1 completed: Paper discovery with OpenAlex, inverted-index abstract reconstruction, DOI/title deduplication, deterministic sentence-aware chunker, and FaissVectorStore + PgVectorStore.
- Milestone F2 completed: Streaming review generation, citation marker parsing ([1], [1][2], [1-3]), claim segmentation, and SSE streaming pipeline.
- Milestone F3 completed: Claim-level citation verification engine with strict quote substring grounding, verdict hierarchy aggregation, mathematical trust score formula, and 100% pass on 10-pair evaluation fixture benchmark.
- Milestone F4 completed: Citation network graph with log-scaled radii, claim support color mapping, and cross-highlighting.
- Milestone F5 completed: BibTeX export with LaTeX character escaping, Markdown export, 24h query cache, and 5 instant seed reviews.
- Milestone F6 completed: Comprehensive README with Mermaid architecture diagram and AnswerThis role mapping, docs/architecture.md, docs/decisions.md (ADRs), post-deploy smoke test script, and final PRD review gate.
### Technical Gotchas & Traps
- `pydantic-settings` v2 attempts `json.loads` on `List[str]` env vars; resolved by typing `Union[str, List[str]]` with comma-split fallback in validator.
- OpenAlex abstracts require inverted-index reconstruction (`abstract_inverted_index`) with word position sorting.
- Fabricated LLM quotes are strictly rejected via whitespace-normalized exact substring verification against source abstracts.
### Active Milestone & Next Steps
- Status: 100% Complete across all PRD Milestones (F0 through F6). All 90 E2E tests passing, 37 unit tests passing, Next.js production build green. Ready for showcase deployment.
