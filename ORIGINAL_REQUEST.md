# Original User Request

## 2026-10-27T10:18:33Z

Use a very large team of agents, invoking multiple parallel subagents to complete it quickly.

Build Veritas: an end-to-end citation-verified literature review generator (Next.js, React, Tailwind, Python/FastAPI, Postgres/pgvector, RAG, Docker, CI/CD) with claim-level citation verification and interactive citation graph, strictly adhering to `PRD Veritas - Citation-Verified Literature Review Generator.md`.

Working directory: C:\Users\rizwan\Desktop\projects\Veritas
Integrity mode: demo

Reference material: `C:\Users\rizwan\Desktop\projects\Veritas\PRD Veritas - Citation-Verified Literature Review Generator.md`

## Requirements

### R1. Project Scaffold, Design System, Docker & CI (Milestone F0)
Monorepo layout (`apps/web` with Next.js/Tailwind, `apps/api` with FastAPI, Postgres + pgvector in `docker-compose.yml`, Makefile, GitHub Actions CI workflow running lint, type checks, and tests on push/PR). Full Linear-grade design tokens and UI components with a `/design` gallery route.

### R2. Paper Discovery, Deduplication & Semantic Ranking (Milestone F1)
Retrieve research papers via OpenAlex API (and optional Semantic Scholar) given user query. Deduplicate by DOI and normalized title; filter papers lacking abstracts; chunk abstracts deterministically; embed and rank candidates using pgvector and FAISS implementations under a common contract. Cache results for identical queries for 24 hours.

### R3. Streaming Literature Review Generation (Milestone F2)
Generate a 400-700 word structured literature review strictly grounded in the retrieved sources `[1]..[N]` with inline citation markers. Stream tokens via Server-Sent Events (`GET /api/reviews/{id}/stream`). Parse output into sections, sentences, and claims; validate citations against source list; flag uncited factual sentences and invalid markers.

### R4. Claim-Level Citation Verification & Trust Score (Milestone F3)
Verify every cited claim against its referenced abstract(s) concurrently using structured LLM output with Pydantic validation and strict quote substring matching. Produce verdicts (`supported`, `partial`, `unsupported`, `invalid_citation`, `unverifiable`) and calculate aggregate Trust Score. Surface verification badges, interactive evidence panel with quote highlighting, and verification filters. Include a 10-pair evaluation fixture suite (`make eval`).

### R5. Interactive Citation Graph (Milestone F4)
Build an interactive node-link graph visualization of the papers cited in the review. Construct edges from paper reference works; size nodes by citation count; color nodes by claim support ratio; enable pan, zoom, and cross-highlighting between graph nodes and review claims/citations.

### R6. Share, Export, Examples, History & Polish (Milestones F5 & F6)
Permanent public review URLs (`/r/{id}`), Markdown export, BibTeX generation (`GET /api/reviews/{id}/bibtex`), rate limiting (configurable IP-based), cached example reviews (`GET /api/examples`), command palette (`Cmd/Ctrl+K`), comprehensive documentation (`README.md`, `docs/architecture.md`, `docs/decisions.md`, `docs/reviews/final.md`), and automated smoke testing script.

## Acceptance Criteria

### Scaffold & Pipeline Quality (F0, F1, F2)
- [ ] `docker compose up` starts web, api, and postgres/pgvector, with healthy status on `GET /api/health`.
- [ ] CI pipeline runs formatting, linting, TypeScript/Python type checks, and test suites with zero errors.
- [ ] OpenAlex integration fetches papers, deduplicates by DOI/title, and rejects papers without abstracts.
- [ ] VectorStore passes identical contract test suite across pgvector and in-memory FAISS.
- [ ] Review generation streams typed SSE events (`stage`, `papers`, `token`, `review_complete`, `claim_verified`, `done`, `error`) with graceful error recovery.
- [ ] Citation parser extracts markers and flags any out-of-bounds marker as invalid.

### Verification & Trust Score (F3)
- [ ] Claim verification validates evidence quotes against source abstracts via exact substring checking.
- [ ] Fabricated evidence quotes are rejected; malformed responses trigger retry then mark unverifiable.
- [ ] Trust score calculates deterministic percentage per PRD formula with null handling for zero verifiable claims.
- [ ] Evidence panel displays verbatim quote highlighted within source abstract, confidence, and verdict.
- [ ] Non-blocking evaluation fixture set runs via `make eval` and reports accuracy/confusion matrix.

### Visual Polish, Graph & Delivery (F4, F5, F6)
- [ ] Graph renders responsive interactive network visualization with pan, zoom, and bidirectional node-review highlighting.
- [ ] Export features (Markdown and BibTeX) produce clean, validated citations.
- [ ] Seed script populates 5 instant cached example reviews.
- [ ] Dark/Light mode supported seamlessly across all components and pages.
- [ ] All feature review gates in `docs/reviews/<feature-id>.md` completed with passing test evidence.
