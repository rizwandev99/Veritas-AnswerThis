# Project: Veritas — Citation-Verified Literature Review Generator

## Architecture
Veritas is an end-to-end literature review generator with claim-level citation verification and an interactive citation graph. It is structured as a decoupled monorepo:
- **Frontend (`apps/web`)**: Next.js 14+/15 App Router, React 19, Tailwind CSS. Linear-grade design tokens (Dark/Light mode via CSS variables), responsive UI, SSE stream consumer, Evidence Panel, interactive Citation Graph canvas, `/design` component gallery, and `/r/{id}` shareable review views.
- **Backend (`apps/api`)**: Python 3.12, FastAPI, Pydantic v2 domain schemas, async lifespan, structured logging, sliding-window rate limiting.
- **Persistence & Vector Search**: PostgreSQL 16 with `pgvector` extension for production/Docker; in-memory FAISS `IndexFlatIP` fallback for offline testing. Unified under an abstract `VectorStore` base class.
- **External Providers**:
  - `PaperSource`: OpenAlex REST API (`https://api.openalex.org/works`) with polite pool headers and inverted-index abstract reconstruction.
  - `Embedder`: Sentence embeddings with cosine similarity.
  - `LLMClient`: Structured generation and claim entailment verification.
- **Infrastructure**: `docker-compose.yml` orchestrating web, api, and postgres/pgvector containers; `Makefile` for developer workflow (`make install`, `make test`, `make lint`, `make dev`, `make smoke`, `make eval`); GitHub Actions CI pipeline running linting, type checks, and tests on push/PR.

```
                      +------------------------------------+
                      |     Browser Client (Next.js 14+)    |
                      |   - App Router, React 19, Tailwind |
                      |   - Linear-Grade Design Tokens     |
                      |   - Theme Engine (Light/Dark)      |
                      |   - SSE Stream Consumer            |
                      +-----------------+------------------+
                                        |
                          REST Requests | Server-Sent Events (SSE)
                                        v
                      +------------------------------------+
                      |      FastAPI Backend (Python 3.12)  |
                      |   - Async Lifespan & Connection Pool|
                      |   - Pydantic v2 I/O Validation      |
                      |   - Structured Event Streaming     |
                      +-------+--------------------+-------+
                              |                    |
            +-----------------+                    +------------------+
            |                                                         |
            v                                                         v
+-----------------------+                                 +-----------------------+
|  Upstream Providers   |                                 |   Persistence Tier    |
| - PaperSource:        |                                 | - Postgres 16 (Neon)  |
|   OpenAlex (polite)   |                                 |   Extension: pgvector |
|   Semantic Scholar    |                                 | - In-memory Vector:   |
| - Embedder:           |                                 |   FAISS IndexFlatIP   |
|   FastEmbed / Gemini  |                                 | - 24h Query Cache     |
| - LLMClient:          |                                 | - Hashed Rate Limiter |
|   Gemini / Groq / Mock|                                 +-----------------------+
+-----------------------+
```

---

## Feature Inventory

Every feature discovered during the Survey Phase is assigned to an authoritative milestone below.

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Monorepo Structure & Configs | `apps/web`, `apps/api`, `Makefile`, `docker-compose.yml`, `.github/workflows/ci.yml` | M0 | PRD §1, §3 |
| 2 | Linear-Grade Design System | Semantic design tokens (light/dark CSS variables), zero raw hex, WCAG AA compliance | M0 | PRD §4, AGENTS.md |
| 3 | Theme Engine | Anti-FOUC inline `<script>`, `localStorage` persistence (`veritas-theme`), system preference fallback | M0 | PRD §4.1 |
| 4 | UI Primitive Component Library | 13 accessible UI components (Button, Input, Badge, Card, Dialog, Tooltip, Sheet, Tabs, Slider, Progress, DropdownMenu, Toast, Skeleton) | M0 | PRD §4.3 |
| 5 | Design Gallery Route (`/design`) | Visual interactive catalog showcasing all UI components in dark and light modes | M0 | PRD §4.3 |
| 6 | FastAPI Backend Scaffold | Async lifespan, CORS middleware, structured JSON logging, exception handlers | M0 | PRD §3, §10 |
| 7 | System Health Endpoint | `GET /api/health` probing API runtime, database connection, and vector extension | M0 | PRD §9 |
| 8 | Docker Compose Infrastructure | Multi-container setup (`web`, `api`, `postgres` with `pgvector`), healthchecks, volumes | M0 | PRD §3, §14 |
| 9 | GitHub Actions CI Pipeline | Automated linting (black/ruff, eslint), typechecking (mypy, tsc), and test execution | M0 | PRD §3, §14 |
| 10 | PostgreSQL Database Schemas | DDL and migrations for `papers`, `paper_chunks`, `reviews`, `review_papers`, `claims`, `claim_verifications`, `query_cache`, `rate_limits` | M1 | PRD §8 |
| 11 | OpenAlex API Client | Polite pool query integration, inverted index abstract reconstruction, retry with backoff | M1 | PRD §6 F1-AC1, §10 |
| 12 | Paper Deduplication Engine | Normalized DOI matching, title fuzzy/punctuation matching, highest-citation tie breaking | M1 | PRD §6 F1-AC2 |
| 13 | Paper Quality Filter | Rejection of papers with null/short abstracts or missing critical metadata | M1 | PRD §6 F1-AC3 |
| 14 | Abstract Chunking Service | Sentence-aware deterministic chunking (2-3 sentences window, 1 sentence overlap) | M1 | PRD §6 F1-AC4 |
| 15 | Abstract VectorStore Contract | Abstract Base Class `VectorStore` implemented by both `PgVectorStore` and `FaissVectorStore` | M1 | PRD §6 F1-AC5 |
| 16 | Semantic Ranking Pipeline | Cosine similarity scoring and top-k candidate paper selection | M1 | PRD §6 F1-AC6 |
| 17 | 24-Hour Query Cache | Query normalization, cache table lookup, 24-hour TTL expiration | M1 | PRD §6 F1-AC7 |
| 18 | Paper Search API Endpoint | `GET /api/papers/search` returning ranked candidate papers with highlights | M1 | PRD §9 |
| 19 | Review Creation API Endpoint | `POST /api/reviews` initiating pipeline, validating query length (3-300 chars) | M2 | PRD §6 F2-AC1, §9 |
| 20 | SSE Stream API Endpoint | `GET /api/reviews/{id}/stream` emitting typed SSE events (`stage`, `papers`, `token`, `review_complete`, `claim_verified`, `done`, `error`) | M2 | PRD §6 F2-AC2, §9 |
| 21 | Review Retrieval Endpoint | `GET /api/reviews/{id}` returning complete review document with papers, claims, and scores | M2 | PRD §6 F2-AC6, §9 |
| 22 | Grounded Generation Prompt | 400-700 words literature review prompt strictly constrained to retrieved abstracts `[1]..[N]` | M2 | PRD §6 F2-AC9, §10 |
| 23 | Markdown & Sentence Parser | Academic-abbreviation-safe sentence tokenizer, section hierarchy extractor | M2 | PRD §6 F2-AC4 |
| 24 | Citation Marker Extractor | Regex parser extracting `[1]`, `[1][2]`, `[1, 2]`, `[1-3]` formats | M2 | PRD §6 F2-AC3 |
| 25 | Marker Bounds & Validity Checker | Flags markers `< 1` or `> N` as `invalid_citation: true` without crashing | M2 | PRD §6 F2-AC3 |
| 26 | Uncited Factual Claim Detector | Flags substantive assertions lacking citation markers with `uncited: true` | M2 | PRD §6 F2-AC5 |
| 27 | Streaming Review UI & Stepper | Visual stepper (Searching, Ranking, Writing, Verifying), real-time token rendering | M2 | PRD §4.2, §6 F2-AC7 |
| 28 | Interactive Citation Chips | Clickable/hoverable inline chips linked to source papers | M2 | PRD §5, §6 F2-AC7 |
| 29 | Claim-Evidence Retrieval | Semantic retrieval of top-2 evidence chunks per cited paper using `VectorStore` | M3 | PRD §6 F3 |
| 30 | LLM Entailment Verifier | Structured Pydantic validation producing `verdict`, `confidence`, `evidence_quote`, `explanation` | M3 | PRD §6 F3-AC1, §10 |
| 31 | Strict Substring Quote Matcher | Exact verification that `evidence_quote` exists verbatim in source abstract; rejection of hallucinations | M3 | PRD §6 F3-AC2 |
| 32 | Out-of-Bounds Fast Rejection | Instant assignment of `invalid_citation` without LLM call for non-existent source numbers | M3 | PRD §6 F3-AC3 |
| 33 | Multi-Citation Aggregator | Prioritized resolution of multi-source claims (`supported` > `partial` > `unsupported` > `unverifiable` > `invalid_citation`) | M3 | PRD §6 F3-AC4 |
| 34 | Concurrent Verification Runner | Bounded concurrency (semaphore 5) with fault-isolated per-claim execution | M3 | PRD §6 F3-AC6 |
| 35 | Trust Score Calculator | Mathematical formula $(S + 0.5P) / V$, handling zero verifiable claims ($V=0 \implies \text{null}$) | M3 | PRD §6 F3-AC5 |
| 36 | Trust Score UI Header | Prominent score badge with abstract limitation disclaimer tooltip | M3 | PRD §4.2, §6 F3-AC7 |
| 37 | Inline Verification Badges | Color-coded status badges on each sentence with WCAG AA icons and accessible labels | M3 | PRD §4.2, §6 F3-AC7 |
| 38 | Interactive Evidence Panel | Context-sensitive side drawer / bottom sheet showing claim audit details and paper info | M3 | PRD §4, §6 F3-AC8 |
| 39 | Verbatim Quote Highlighting | `<mark>` highlight of exact evidence quote within full source abstract | M3 | PRD §6 F3-AC8 |
| 40 | Claim Verdict Filter | UI toggle allowing filtering review text by verdict (All, Unsupported, Partial, Supported) | M3 | PRD §6 F3-AC9 |
| 41 | Verification Evaluation Suite | 10 ground-truth claim-evidence pairs in `tests/fixtures/eval_fixtures.json` | M3 | PRD §2.2, §6 F3-AC10 |
| 42 | Evaluation Runner CLI | `make eval` running verification engine and outputting accuracy & confusion matrix | M3 | PRD §2.2, §6 F3-AC10 |
| 43 | Citation Graph API Endpoint | `GET /api/reviews/{id}/graph` returning node-link JSON schema | M4 | PRD §6 F4-AC1, §9 |
| 44 | In-Memory Graph Builder | Internal edge construction from `referenced_work_ids` without additional web crawling | M4 | PRD §6 F4-AC2 |
| 45 | Bridge Node Synthesizer | Up to 10 bridge nodes for external papers cited by $\ge 3$ review papers | M4 | PRD §6 F4 |
| 46 | Interactive Graph Canvas | Modern node-link canvas (pan, zoom, fit-to-view, responsive resizing) | M4 | PRD §4, §6 F4-AC3 |
| 47 | Graph Node Sizing & Coloring | Logarithmic radius scaling (16-48px) by citations, color mapping by verification support ratio | M4 | PRD §6 F4-AC4 |
| 48 | Graph Node Tooltips | Hover tooltips displaying paper title, authors, year, citation count, and verification stats | M4 | PRD §4, §6 F4-AC5 |
| 49 | Bidirectional Cross-Highlighting | Synchronized selection between graph nodes/edges and review sentences/chips | M4 | PRD §6 F4-AC5 |
| 50 | Shareable Review URLs (`/r/{id}`) | Public read-only SSR routes with OpenGraph metadata tags | M5 | PRD §6 F5-AC1, §12 |
| 51 | Markdown Export | Downloadable formatted markdown with References and verification notices (`GET /api/reviews/{id}/markdown`) | M5 | PRD §6 F5-AC2, §9 |
| 52 | BibTeX Export | RFC/BibTeX standard citations with LaTeX character escaping (`GET /api/reviews/{id}/bibtex`) | M5 | PRD §6 F5-AC2, §9 |
| 53 | IP-Based Sliding Window Limiter | Zero-cost rate limiter in Postgres with hashed IPs (`X-RateLimit-*` headers, 429 on limit) | M5 | PRD §6 F5-AC3, §8 |
| 54 | Cached Instant Example Reviews | `GET /api/examples` serving 5 pre-computed multidisciplinary seed reviews | M5 | PRD §6 F5-AC4, §9 |
| 55 | Command Palette (`Cmd/Ctrl+K`) | Keyboard shortcut navigation for search, examples, theme toggle, and recent reviews | M5 | PRD §6 F5-AC5 |
| 56 | Recent Review History | `localStorage` review history list on home page with quick reload | M5 | PRD §4.1, §6 F5-AC5 |
| 57 | Automated Smoke Test Script | Python standard-library script (`scripts/smoke_test.py` / `make smoke`) verifying live endpoints | M5 | PRD §6 F6-AC2 |
| 58 | Comprehensive Documentation | `README.md`, `docs/architecture.md`, `docs/decisions.md` (6 ADRs), `docs/reviews/final.md` | M5 | PRD §6 F6-AC1 |
| 59 | 4-Tier E2E Test Suite | Requirement-driven opaque-box test suite (Tier 1-4) published via `TEST_READY.md` | E2E | PRD §14, ORIGINAL_REQUEST |
| 60 | 100% E2E Pass & Tier 5 Hardening | Final verification passing 100% E2E tests followed by white-box adversarial stress tests | M_final | ORIGINAL_REQUEST |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Project Scaffold, Design System, Docker & CI | Features 1–9: Monorepo layout (`apps/web`, `apps/api`), Linear design tokens (dark/light), 13 UI primitives, `/design` gallery, FastAPI lifespan, CORS, `GET /api/health`, `docker-compose.yml`, `Makefile`, `.github/workflows/ci.yml` | none | IN_PROGRESS (worker: 6bb87073-3698-498e-80cc-dfec509bb9bd) |
| M1 | Paper Discovery, Deduplication & Semantic Ranking | Features 10–18: PostgreSQL DDLs & migrations, OpenAlex client with inverted-index abstract reconstruction, deduplication, chunking, `VectorStore` ABC (`PgVectorStore` & `FaissVectorStore`), 24h query cache, `GET /api/papers/search` | M0 | PLANNED |
| M2 | Streaming Review Generation & SSE Protocol | Features 19–28: `POST /api/reviews`, `GET /api/reviews/{id}`, `GET /api/reviews/{id}/stream` (7 typed SSE events), grounded prompt (400-700 words), sentence & citation parsing, marker bounds validation, uncited detection, streaming UI | M1 | PLANNED |
| M3 | Claim-Level Verification & Trust Score | Features 29–42: Chunk retrieval, LLM entailment verification, strict quote substring match in abstract, multi-citation aggregation, trust score $(S + 0.5P)/V$, evidence panel with quote highlight, badges, filter, 10 eval fixtures, `make eval` | M2 | PLANNED |
| M4 | Interactive Citation Graph | Features 43–49: `GET /api/reviews/{id}/graph`, in-memory edge construction from `referenced_work_ids`, bridge paper synthesis, node-link canvas, log sizing (16-48px), color mapping, hover tooltips, bidirectional cross-highlighting | M2, M3 | PLANNED |
| M5 | Share, Export, Rate Limiting, Examples & Docs | Features 50–58: `/r/{id}` public SSR routes & OpenGraph, Markdown export, BibTeX export with LaTeX escaping, sliding-window rate limiter, 5 instant seed reviews, `Cmd/Ctrl+K` command palette, `make smoke` script, `README.md` & docs | M3, M4 | PLANNED |
| E2E | Opaque-Box E2E Testing Track | Feature 59: 4-Tier requirement-driven E2E test suite (Tier 1 Feature coverage, Tier 2 Boundary/Corner, Tier 3 Pairwise combinations, Tier 4 Real-world workloads), publishes `TEST_READY.md` | none (independent) | IN_PROGRESS (test_writer: 7939e987-387d-4d86-851f-1602ac474557) |
| M_final | Final Milestone: 100% E2E Pass & Tier 5 Hardening | Feature 60: Phase 1: 100% pass of Tiers 1-4 E2E tests; Phase 2: Tier 5 adversarial coverage hardening | M0-M5, E2E | PLANNED |

---

## Interface Contracts

### 1. `apps/api` ↔ `apps/web` REST & SSE APIs

#### Health Probe
- `GET /api/health`
- Response `200 OK`:
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "vector_store": "pgvector",
    "version": "1.0.0"
  }
  ```

#### Review Creation
- `POST /api/reviews`
- Request body: `{"query": str, "regenerate": bool}` (3 <= len(query) <= 300)
- Response `201 Created` or `200 OK` (if cached):
  ```json
  {
    "id": "rev_k8s9d7f2",
    "query": "Impact of LLMs on code synthesis",
    "status": "pending",
    "cached": false
  }
  ```

#### Review Retrieval
- `GET /api/reviews/{id}`
- Response `200 OK`: Review object including `id`, `query`, `status`, `review_text`, `trust_score`, `papers`: list[Paper], `claims`: list[ClaimWithVerification].

#### SSE Streaming Protocol
- `GET /api/reviews/{id}/stream` (Accept: `text/event-stream`)
- Emits events formatted as `event: <event_type>\ndata: <json_payload>\n\n`:
  - `event: stage` -> `{"stage": "searching" | "ranking" | "writing" | "verifying"}`
  - `event: papers` -> `{"papers": [{"id": str, "source_number": int, "title": str, "authors": [...], "year": int, "citation_count": int, "doi": str, "url": str}]}`
  - `event: token` -> `{"token": str}`
  - `event: review_complete` -> `{"review_id": str, "text": str, "total_claims": int}`
  - `event: claim_verified` -> `{"claim_id": str, "sentence_index": int, "verdict": "supported"|"partial"|"unsupported"|"invalid_citation"|"unverifiable", "confidence": float, "source_numbers": [int], "evidence_quote": str | null, "explanation": str}`
  - `event: done` -> `{"review_id": str, "trust_score": float | null, "status": "complete"}`
  - `event: error` -> `{"code": str, "message": str, "retryable": bool}`

#### Citation Graph
- `GET /api/reviews/{id}/graph`
- Response `200 OK`:
  ```json
  {
    "nodes": [
      {
        "id": "paper_1",
        "source_number": 1,
        "title": "...",
        "year": 2023,
        "citation_count": 1420,
        "radius": 34.2,
        "status_color": "success",
        "verification_stats": {"supported": 3, "partial": 1, "unsupported": 0},
        "is_bridge": false
      }
    ],
    "edges": [
      {"source": "paper_1", "target": "paper_2"}
    ]
  }
  ```

#### Export Endpoints
- `GET /api/reviews/{id}/markdown` -> `Content-Type: text/markdown`, attachment filename `veritas-{id}.md`.
- `GET /api/reviews/{id}/bibtex` -> `Content-Type: application/x-bibtex`, attachment filename `veritas-{id}.bib`.
- `GET /api/examples` -> `200 OK` returning 5 instant pre-computed reviews.

---

### 2. Internal Domain Contracts (`apps/api`)

#### `VectorStore` Abstract Base Class
```python
class VectorStore(ABC):
    @abstractmethod
    async def add_chunks(self, chunks: list[PaperChunk]) -> None:
        pass

    @abstractmethod
    async def search(self, query_embedding: list[float], top_k: int, paper_id: str | None = None) -> list[tuple[PaperChunk, float]]:
        pass

    @abstractmethod
    async def delete_paper_chunks(self, paper_id: str) -> None:
        pass
```
Implemented identically by:
- `PgVectorStore`: uses pgvector `<=>` cosine distance with HNSW index.
- `FaissVectorStore`: uses FAISS `IndexFlatIP` with L2-normalized vectors.

#### `PaperSource` Abstract Base Class
```python
class PaperSource(ABC):
    @abstractmethod
    async def search_papers(self, query: str, limit: int = 15) -> list[Paper]:
        pass
```
Implemented by:
- `OpenAlexPaperSource`: queries OpenAlex API with inverted index reconstruction and polite pool header.
- `MockPaperSource`: returns deterministic fixtures for offline testing.

#### `LLMClient` Abstract Base Class
```python
class LLMClient(ABC):
    @abstractmethod
    async def stream_review(self, query: str, papers: list[Paper]) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def verify_claim(self, claim: str, source_text: str) -> VerificationResult:
        pass
```
Implemented by:
- `GeminiLLMClient`: live Gemini / Groq free tier integration.
- `MockLLMClient`: deterministic responses and evaluation fixture oracle.

---

## Code Layout

```
Veritas/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI matrix
├── Makefile                     # Root developer orchestration
├── docker-compose.yml           # Local multi-service infrastructure
├── README.md                    # System documentation & showcase
├── docs/
│   ├── architecture.md          # Technical architecture & data flows
│   ├── decisions.md             # Architecture Decision Records (ADRs)
│   └── reviews/                 # PRD Review Gates (<feature-id>.md)
├── scripts/
│   ├── smoke_test.py            # Automated end-to-end smoke test script
│   └── seed_examples.py         # Seed data generator for 5 example reviews
├── tests/
│   ├── e2e/                     # Opaque-box E2E test suite (Tiers 1-4)
│   │   ├── runner.py            # E2E test runner
│   │   ├── tier1_features/      # >=5 cases per feature (F0-F6)
│   │   ├── tier2_boundaries/    # Boundary, corner, error cases
│   │   ├── tier3_pairwise/      # Cross-feature combinations
│   │   └── tier4_real_world/    # Realistic research workloads
│   └── fixtures/
│       ├── eval_fixtures.json   # 10 ground-truth claim verification pairs
│       └── example_reviews.json # 5 pre-computed seed reviews
├── apps/
│   ├── web/                     # Next.js Application
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── tailwind.config.ts
│   │   ├── public/
│   │   └── src/
│   │       ├── app/
│   │       │   ├── layout.tsx
│   │       │   ├── globals.css  # Linear design tokens
│   │       │   ├── page.tsx     # Landing page
│   │       │   ├── design/page.tsx # Component gallery
│   │       │   └── r/[id]/page.tsx # Public review view
│   │       ├── components/
│   │       │   ├── ui/          # 13 accessible UI primitives
│   │       │   └── review/      # ReviewReader, EvidencePanel, CitationGraph
│   │       ├── hooks/           # useSSE, useTheme, useCommandPalette
│   │       ├── lib/             # API client, cn, formatters
│   │       └── types/           # TypeScript definitions
│   └── api/                     # FastAPI Application
│       ├── Dockerfile
│       ├── pyproject.toml
│       ├── requirements.txt
│       ├── app/
│       │   ├── main.py          # FastAPI entry point, lifespan, CORS
│       │   ├── api/             # Routers (health, reviews, graph, examples)
│       │   ├── core/            # Config, logging, errors, rate limiter
│       │   ├── db/              # Postgres connection, migrations, DDL
│       │   ├── domain/          # Pydantic models (Paper, Review, Claim, etc.)
│       │   └── services/        # Business logic:
│       │       ├── paper_source.py  # OpenAlex client
│       │       ├── deduplicator.py  # DOI & title normalization
│       │       ├── chunker.py       # Deterministic chunking
│       │       ├── vector_store.py  # PgVector & FAISS
│       │       ├── review_generator.py # Grounded generation
│       │       ├── parser.py        # Sentence & citation extraction
│       │       ├── verifier.py      # Claim verification & quote matching
│       │       ├── trust_score.py   # Mathematical scoring
│       │       ├── graph_builder.py # Node-link graph constructor
│       │       └── exporter.py      # Markdown & BibTeX export
│       └── tests/               # Unit and integration test suites
```
