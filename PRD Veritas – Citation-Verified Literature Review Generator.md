# PRD: Veritas – Citation-Verified Literature Review Generator

**Audience:** an AI coding agent that will build this end to end. **Purpose:** a portfolio and cold-outreach showcase for AnswerThis (AI research platform: query in, cited literature review out). **Status:** build-ready.

---

## 0. How to use this document (read first, agent)

1. This PRD is the single source of truth. Every requirement has an ID (e.g. `F2-AC3`). Tests, code reviews and commits must reference these IDs.
2. Build features in the order given in Section 14. Do not start a feature until the previous one passes its review gate.
3. Follow the **Per-Feature Workflow in Section 2** for every feature, without exception.
4. When something is ambiguous, choose the simplest option that satisfies the acceptance criteria, and record the decision in `docs/decisions.md`.
5. Never add scope that is not in this PRD. Anything in Section 13 (Non-Goals) is forbidden.

---

## 1. Product overview

### 1.1 One-line pitch

Type a research question. Get a streamed, fully cited literature review, where **every claim is automatically checked against its cited paper** and marked Supported, Partial or Unsupported, plus a citation graph of the papers used.

### 1.2 Why this exists (the showcase thesis)

AnswerThis ships literature reviews. The core trust problem in this category is hallucinated or unsupported citations. Veritas demonstrates, in one demo, the full stack named in their job description (Next.js, React, Tailwind, Python/FastAPI, Postgres, vector search and RAG, Docker, CI/CD, citation mapping, academic workflows) and adds one standout idea: **claim-level citation verification**.

### 1.3 Target viewer

A startup founder who opens the live link for 2 minutes. The first 30 seconds must show a polished UI, a streaming review, and visible verification badges. Optimize for that.

### 1.4 Success criteria

- A first-time visitor can click an example query and see a complete verified review in under 60 seconds.
- Every sentence with a citation shows a verification badge.
- The app is deployed publicly, with a green CI pipeline and a README with an architecture diagram.
- Test suite is green and was written test-first.

---

## 2. Engineering process (mandatory)

### 2.1 Per-Feature Workflow (TDD plus PRD code review)

For **each feature** (F1, F2, ...), execute these steps in order:

1. **Read** the feature section and list its acceptance criteria (AC) IDs.
2. **Write failing tests first.** Create tests that map one-to-one (or one-to-many) to the AC IDs. Name tests with the AC ID, e.g. `test_F2_AC3_unknown_citation_is_rejected`. Cover backend (unit and integration) and frontend (component) as applicable.
3. **Run the tests and confirm they fail** for the right reason (missing behavior, not syntax errors). Save the failing output summary in the review file (step 7).
4. **Implement the minimum code** to make the tests pass.
5. **Run the full test suite, linter, type checker.** All must be green.
6. **Refactor** with tests green.
7. **PRD code review gate.** Write `docs/reviews/<feature-id>.md` containing:
   - A table: every AC ID, status (Pass / Fail), evidence (file path and test name).
   - A check against Section 4 (design system) for any UI work.
   - A check against Section 12 (non-functional requirements).
   - A list of any deviation from the PRD with justification. If any AC is Fail, go back to step 2 or 4 and fix it. Repeat until all pass.
8. **Commit** with message `feat(<feature-id>): <summary> [ACs: ...]`. Only then move to the next feature.

### 2.2 Testing rules

- **No real network or LLM calls in unit/integration tests.** Mock external providers (LLM, embeddings, paper APIs) behind interfaces and use recorded fixtures in `tests/fixtures/`.
- LLM-dependent logic must be tested through its deterministic parts: prompt construction, output parsing and validation, error handling, and post-processing.
- Include a small **eval fixture set** (at least 10 hand-written claim and evidence pairs with expected verdicts) used by a non-blocking eval script (`make eval`) that runs against the real provider manually.
- Frontend: component tests for states (loading, streaming, error, empty, success) and at least a few end-to-end tests of the main flow against a mocked backend.
- Coverage target: at least 80% on backend core logic (pipeline, verification, parsing). Do not chase coverage with meaningless tests.

### 2.3 Tooling rules

- **Always use the latest stable versions** of every framework and library. Do not rely on remembered versions or old API patterns. At install time, check the package registry and the official current docs, and follow current best practices.
- Pin exact resolved versions through lockfiles only.
- Everything must be **free**: no paid services, no credit card required. See Section 3.

---

## 3. Tech stack and constraints

| Layer | Choice | Notes |
| --- | --- | --- |
| Frontend | Next.js (App Router) with React and TypeScript | Latest stable. Server and client components used appropriately. |
| Styling | Tailwind CSS plus CSS variable design tokens | Latest stable. Dark and light mode. |
| Backend | Python with FastAPI | Async endpoints, Pydantic models for all I/O, streaming via Server-Sent Events. |
| Database | Neon Postgres (free tier) | Integrated with Vercel. Use the `pgvector` extension for embeddings. |
| Vector search | `pgvector` in Neon behind a `VectorStore` interface | Also ship a local in-memory FAISS adapter used for local dev and benchmarks, to show familiarity with FAISS and swappability to Weaviate or Pinecone. |
| LLM | Provider abstraction `LLMClient` | Default to a **free-tier** hosted provider (e.g. Google Gemini free tier, with Groq or OpenRouter free models as fallbacks). Choose the best currently available free model at build time. Provider selected via env var. |
| Embeddings | Provider abstraction `Embedder` | Use a free-tier embeddings API. Must not require a paid plan. |
| Paper data | OpenAlex API (primary), Semantic Scholar API (secondary, optional) | Both free. Use polite-pool identification (contact email in User-Agent or params) as documented. Respect rate limits. |
| Containers | Docker and docker-compose | Local dev: frontend, backend, Postgres with pgvector. |
| CI/CD | GitHub Actions | Lint, type check, tests, build, Docker build. Deploy via Vercel's GitHub integration. |
| Hosting | Vercel (frontend and FastAPI backend) plus Neon | Verify current Vercel Python/FastAPI runtime support and function duration limits in the latest docs, and design the pipeline to fit (see Section 12). |

**Authentication: none.** No login, no accounts, no user table. All reviews are public, addressable by ID.

**Secrets:** all keys in environment variables; provide `.env.example`; never commit secrets.

---

## 4. Design system

**Goal:** modern, clean, minimal, in the spirit of linear.app. Calm, dense-but-airy, precise.

### 4.1 Principles

- Quiet UI: neutral surfaces, one accent color, color used only for meaning (status, selection).
- Tight typography, generous whitespace, subtle 1px borders instead of heavy shadows.
- Fast and responsive feeling: instant feedback, skeletons, smooth but short transitions (150-200ms), respect `prefers-reduced-motion`.
- Keyboard-first touches: `Cmd/Ctrl+K` command palette, `/` focuses search, `Esc` closes panels.

### 4.2 Tokens (implement as CSS variables, mapped into Tailwind theme)

- **Themes:** light and dark. Default to system preference, user toggle persisted in `localStorage`. No flash of wrong theme on load.
- **Colors (semantic tokens, not raw hex in components):** `background`, `surface`, `surface-elevated`, `border`, `border-strong`, `text-primary`, `text-secondary`, `text-tertiary`, `accent`, `accent-foreground`, plus status tokens `success`, `warning`, `danger`, `info`. Dark mode: near-black background with slightly lifted surfaces. Light mode: off-white background with white surfaces. Accent: a single indigo/violet-leaning hue. Verification statuses map to success (Supported), warning (Partial), danger (Unsupported), neutral (Unchecked).
- **Typography:** Inter (or the current best free system-quality sans via `next/font`) for UI, a mono font for IDs, DOIs and code. Small, consistent type scale; text-sm as the default body size; tight tracking on headings.
- **Radius and spacing:** 6-8px radius for controls, 10-12px for cards; spacing on a 4px grid.
- **Components to build in `components/ui/`:** Button, IconButton, Input, Badge, Tooltip, Card, Skeleton, Tabs, Dialog or Sheet, CommandPalette, ThemeToggle, Toast, ProgressStepper.
- **Accessibility:** WCAG AA contrast in both themes, visible focus rings, full keyboard navigation, ARIA labels on icon buttons, tooltips not required to understand status (badges also have text or icon).

### 4.3 Design acceptance criteria

- `DS-AC1`: Light and dark themes render every screen correctly, with no hardcoded colors outside tokens.
- `DS-AC2`: Theme toggle persists and there is no flash of incorrect theme on reload.
- `DS-AC3`: All interactive elements have visible focus states and are keyboard operable.
- `DS-AC4`: Layout works at 360px, 768px and 1280px+ widths.
- `DS-AC5`: Loading, empty, error and success states exist for every data-driven view.

---

## 5. User flows

1. **Landing:** user sees a hero, a search box, and 4-6 clickable **example queries** (pre-generated and cached, so they load instantly). Below: a gallery of recent public example reviews.
2. **Generate:** user submits a query. A progress stepper shows stages: Searching papers, Ranking, Writing, Verifying. Papers appear as they are found. The review streams in. Verification badges fill in after writing completes.
3. **Read and inspect:** user reads the review with inline citation chips. Hover or click a chip to see the paper card (title, authors, year, venue, abstract excerpt, link). Click a verification badge to see the **evidence panel** (the exact passage used, verdict, explanation).
4. **Explore graph:** a tab shows the citation graph of papers used, nodes colored by how well their claims were verified.
5. **Share and export:** copy share link, copy as Markdown, export BibTeX.

---

## 6. Features

Priority: **P0** = required for the demo, **P1** = standout, build after P0 passes.

### F0 - Project scaffold, design system, CI (P0)

**Description:** monorepo, tooling, design tokens, base UI components, Docker, CI.

**Acceptance criteria:**

- `F0-AC1`: Monorepo with `apps/web` (Next.js) and `apps/api` (FastAPI), plus `docs/`, `docker-compose.yml`, `Makefile`, `.env.example`.
- `F0-AC2`: `docker compose up` starts web, api and Postgres with pgvector, and the web app loads and can call `GET /api/health` successfully.
- `F0-AC3`: GitHub Actions workflow runs lint, type check, backend tests, frontend tests, and build on every push and PR, and fails on any error.
- `F0-AC4`: All design tokens and `components/ui/*` from Section 4 exist, with a `/design` route (dev only) showing every component in light and dark.
- `F0-AC5`: Pre-commit or CI formatting check using the latest standard Python and TypeScript formatters and linters.
- `F0-AC6`: Tests exist for health endpoint, theme persistence, and at least two UI components.

### F1 - Paper discovery and ranking (P0)

**Description:** given a query, retrieve candidate papers and rank them for relevance.

**Pipeline:**

1. Normalize the query.
2. Optionally ask the LLM to expand the query into 2-4 search sub-queries (structured JSON output).
3. Fetch candidates from OpenAlex (and optionally Semantic Scholar). Deduplicate by DOI, then normalized title.
4. Filter out papers with no abstract.
5. Embed query and paper abstracts. Rank by vector similarity (and optionally a simple recency or citation-count boost). Keep the top N (default 12, max 20).
6. Persist papers, chunks and embeddings in Postgres through the `VectorStore` interface.

**Acceptance criteria:**

- `F1-AC1`: `PaperSource` interface with OpenAlex implementation; responses mapped to an internal `Paper` model (id, title, authors, year, venue, doi, url, abstract, citation\_count, referenced\_work\_ids).
- `F1-AC2`: Deduplication by DOI, then by normalized title, covered by tests.
- `F1-AC3`: Papers lacking an abstract are excluded.
- `F1-AC4`: `Embedder` and `VectorStore` interfaces with pgvector and in-memory FAISS implementations that pass the same contract test suite.
- `F1-AC5`: Ranking returns top N sorted by similarity; N is configurable and bounded (1-20).
- `F1-AC6`: Upstream failures (timeouts, 429, 5xx) trigger retry with backoff, then a typed error; never an unhandled exception.
- `F1-AC7`: Results for an identical normalized query are cached in the database for 24 hours.
- `F1-AC8`: Abstract text is chunked deterministically (sentence-aware) with chunk metadata linking to the paper.

### F2 - Cited review generation with streaming (P0)

**Description:** write a structured literature review grounded only in the retrieved papers, with inline citation markers, streamed to the UI.

**Generation rules:**

- The prompt supplies numbered sources `[1]..[N]` with title, year and abstract. The model must cite only those numbers.
- Output structure: short intro, 2-4 thematic sections with headings, a brief conclusion or open questions. Target 400-700 words.
- Each factual sentence ends with one or more citation markers like `[3]` or `[2][5]`.
- The model is instructed to say so when sources are insufficient rather than invent.
- Backend streams tokens over SSE. After streaming, the full text is parsed into **sections, sentences and claims**.

**Acceptance criteria:**

- `F2-AC1`: `POST /api/reviews` with `{ query }` creates a review record (status `pending`) and returns `{ id }`. Input validated (length 3-300 chars).
- `F2-AC2`: `GET /api/reviews/{id}/stream` is an SSE endpoint emitting typed events: `stage`, `papers`, `token`, `review_complete`, `claim_verified`, `done`, `error`.
- `F2-AC3`: A citation parser extracts marker numbers from text; any marker outside `1..N` is flagged as an **invalid citation** and surfaced (never silently dropped). Covered by tests with edge cases (adjacent markers, ranges like `[1-3]` or `[1,2]` if the model emits them, no markers).
- `F2-AC4`: Sentence segmentation splits the review into claim records (text, section, cited source numbers, position).
- `F2-AC5`: Sentences with zero citations that look factual are flagged `uncited`.
- `F2-AC6`: The completed review is persisted (text, claims, paper links, status `complete`) and retrievable via `GET /api/reviews/{id}`.
- `F2-AC7`: The frontend renders streaming text smoothly, shows the progress stepper, and renders citation markers as interactive chips linking to paper cards.
- `F2-AC8`: LLM failure or rate limit shows a friendly retryable error state; partial text is preserved.
- `F2-AC9`: Prompt templates live in a dedicated module, are unit tested for correct source numbering and instructions, and contain no secrets.

### F3 - Claim-level citation verification (P0, the standout)

**Description:** after the review is written, verify each cited claim against the papers it cites and label it.

**Method:**

1. For each claim with citations, for each cited source, retrieve the top-k chunks (default 2) of that paper most similar to the claim, using `VectorStore`.
2. Ask the LLM, with structured JSON output, to judge entailment given the claim and the evidence chunks. Output schema: `verdict` (`supported` | `partial` | `unsupported`), `confidence` (0-1), `evidence_quote` (verbatim substring of provided evidence), `explanation` (one sentence).
3. Validate output: the `evidence_quote` must be an actual substring of the provided chunks (normalized whitespace). If not, mark the result as `unverifiable` and do not show the fabricated quote.
4. A claim with multiple citations takes the best verdict across its sources, but all per-source results are stored.
5. Compute a **review trust score** = (supported + 0.5 \* partial) / total verifiable claims.
6. Run verifications concurrently with a bounded concurrency limit, and emit each result as a `claim_verified` SSE event as it completes.

**Honesty rule:** the UI must state that verification is performed against abstracts (available text), not full papers, via a small info tooltip near the trust score.

**Acceptance criteria:**

- `F3-AC1`: Verification output is parsed with a strict Pydantic schema; malformed LLM JSON triggers one repair retry, then marks the claim `unverifiable`.
- `F3-AC2`: Evidence-quote substring validation implemented and tested (valid quote passes, fabricated quote is rejected).
- `F3-AC3`: A citation to a source number that does not exist yields verdict `invalid_citation` without calling the LLM.
- `F3-AC4`: Multi-citation claims aggregate by best verdict; per-source results stored.
- `F3-AC5`: Trust score computed per the formula, unit tested with fixtures including edge cases (zero verifiable claims returns `null`).
- `F3-AC6`: Concurrency is bounded and configurable; one failing claim never aborts the others.
- `F3-AC7`: UI shows a verification badge (Supported, Partial, Unsupported, Invalid, Unverifiable, Checking) after each cited sentence, and a trust score summary at the top of the review.
- `F3-AC8`: Clicking a badge opens an **evidence panel** with verdict, confidence, the verbatim evidence quote highlighted inside its source abstract, the explanation, and a link to the paper.
- `F3-AC9`: A filter control lets users show only Unsupported or Partial claims.
- `F3-AC10`: `make eval` runs the fixture eval set against the real provider and prints accuracy and a confusion matrix.

### F4 - Citation graph (P1, second standout)

**Description:** an interactive graph of the papers used in the review, showing how they cite each other and how well they were verified.

**Data:** nodes are the review's papers. Edges exist where one paper's `referenced_work_ids` includes another included paper. Optionally add up to 10 "bridge" papers that are referenced by at least 3 included papers, drawn as dimmer nodes (use only data already fetched; no extra heavy crawling).

**Acceptance criteria:**

- `F4-AC1`: `GET /api/reviews/{id}/graph` returns `{ nodes, edges }` with node fields (id, title, year, citation\_count, verification summary) and edges (source, target).
- `F4-AC2`: Edge construction logic is unit tested, including papers with no references and no internal edges.
- `F4-AC3`: Graph renders in a Graph tab using a latest-stable free graph/visualization library, with pan, zoom, and a force or layered layout.
- `F4-AC4`: Node size reflects citation count (bounded scale); node color reflects the share of supported claims for that paper (success, warning, danger, neutral if no claims).
- `F4-AC5`: Hover shows a tooltip; click selects the node and highlights its related review sentences in the review view (and vice versa: selecting a citation chip highlights the node).
- `F4-AC6`: Graph is legible in both themes, handles 1 to 25 nodes, and shows a helpful empty state when there are no edges.

### F5 - Share, export, examples and history (P0)

**Acceptance criteria:**

- `F5-AC1`: Every review has a permanent public URL `/r/{id}`, server-rendered metadata (title, description) for link previews.
- `F5-AC2`: Copy as Markdown (with citations and a references list) and export BibTeX (`GET /api/reviews/{id}/bibtex`) work. BibTeX generation is unit tested for escaping and missing fields.
- `F5-AC3`: A seed script generates and stores 5 example reviews, exposed through `GET /api/examples`; landing page example chips open them instantly without LLM calls.
- `F5-AC4`: Landing page shows recent public reviews (latest 6), excluding failed ones.
- `F5-AC5`: Anonymous rate limiting on `POST /api/reviews` (e.g. 5 per hour per IP, configurable) returns a clear 429 with retry information, and the UI explains it kindly.
- `F5-AC6`: Identical normalized queries within 24 hours return the existing review rather than generating a new one, with a "regenerate" option that respects the rate limit.
- `F5-AC7`: Command palette (`Cmd/Ctrl+K`) supports: new review, jump to examples, toggle theme, copy link.

### F6 - Documentation and polish (P0)

**Acceptance criteria:**

- `F6-AC1`: README with: pitch, live demo link, GIF or screenshots of the main flow, architecture diagram (Mermaid), pipeline explanation, how verification works and its limits, local setup with Docker, test and eval instructions, and a section mapping features to the AnswerThis role requirements.
- `F6-AC2`: `docs/architecture.md` and `docs/decisions.md` exist and are accurate.
- `F6-AC3`: Deployed to Vercel with Neon; migrations applied; seed examples loaded; a post-deploy smoke test (script) passes.
- `F6-AC4`: Open Graph image or metadata set so the shared link looks good.
- `F6-AC5`: A final full review file `docs/reviews/final.md` verifying every AC in this PRD, with evidence.

---

## 7. Architecture

```
Browser (Next.js)
  |  REST + SSE
FastAPI
  |-- PaperSource (OpenAlex)        -> external, free
  |-- Embedder (free-tier API)      -> external, free
  |-- LLMClient (free-tier API)     -> external, free
  |-- VectorStore (pgvector | FAISS)
  |-- Repository layer              -> Neon Postgres
```

**Backend module layout (`apps/api/app/`):**

- `api/` routers (reviews, examples, graph, health)
- `core/` config, logging, errors, rate limiting
- `domain/` Pydantic models (Paper, Chunk, Review, Claim, Verification)
- `services/` discovery, generation, citation\_parser, verification, graph, bibtex, trust\_score
- `providers/` llm, embedder, paper\_source (interfaces plus implementations plus fakes for tests)
- `storage/` vector\_store, repositories, migrations
- `prompts/` all prompt templates

**Frontend layout (`apps/web/`):** App Router with routes `/`, `/r/[id]`, `/design` (dev only). Feature folders for review, graph, evidence; shared `components/ui/`; a typed API client; an SSE hook with reconnection and state machine.

**Principle:** all external dependencies sit behind interfaces so tests use fakes and providers can be swapped.

---

## 8. Data model (Postgres)

- `papers`: id (internal), external\_id (unique), doi, title, authors (jsonb), year, venue, url, abstract, citation\_count, referenced\_work\_ids (text\[\]), created\_at.
- `paper_chunks`: id, paper\_id (fk), chunk\_index, text, embedding (vector, dimension set from the chosen embedder via config).
- `reviews`: id (short URL-safe id), query, normalized\_query, status (`pending` | `running` | `complete` | `failed`), text, trust\_score (nullable), error (nullable), created\_at, completed\_at.
- `review_papers`: review\_id, paper\_id, source\_number (1..N), relevance\_score.
- `claims`: id, review\_id, position, section, text, cited\_numbers (int\[\]), flags (jsonb: uncited, invalid\_citation), final\_verdict (nullable), final\_confidence (nullable).
- `claim_verifications`: id, claim\_id, source\_number, verdict, confidence, evidence\_quote, evidence\_chunk\_id, explanation.
- `query_cache`: normalized\_query, review\_id, created\_at.
- `rate_limits`: key (hashed IP), window\_start, count.

Use migrations (latest standard Python migration tool). Add indexes: vector index on embeddings (HNSW or IVFFlat as supported on Neon), unique on `papers.external_id`, index on `reviews.normalized_query` and `reviews.created_at`.

---

## 9. API specification

All responses are JSON unless SSE. Errors use `{ error: { code, message, retry_after? } }`.

| Method and path | Purpose |
| --- | --- |
| `GET /api/health` | Liveness and dependency status. |
| `POST /api/reviews` | Body `{ query, regenerate? }`. Returns `{ id, cached }`. |
| `GET /api/reviews/{id}` | Full review: text, papers, claims with verifications, trust score, status. |
| `GET /api/reviews/{id}/stream` | SSE stream of pipeline events (see below). Replays state if the review is already complete. |
| `GET /api/reviews/{id}/graph` | Graph nodes and edges. |
| `GET /api/reviews/{id}/bibtex` | BibTeX text. |
| `GET /api/examples` | Cached example reviews. |
| `GET /api/reviews?limit=6` | Recent public complete reviews. |

**SSE event types and payloads:**

- `stage`: `{ stage: searching | ranking | writing | verifying, message }`
- `papers`: `{ papers: [...] }` (ranked list with source numbers)
- `token`: `{ text }`
- `review_complete`: `{ claims: [...] }` (parsed claims before verification)
- `claim_verified`: `{ claim_id, verifications, final_verdict }`
- `done`: `{ trust_score }`
- `error`: `{ code, message, retryable }`

---

## 10. LLM usage guidelines

- All LLM calls go through `LLMClient` with methods for streaming text and for structured (JSON-schema constrained) output.
- Use the provider's native structured-output or JSON mode where available, and always validate with Pydantic.
- Temperature low for verification (deterministic), moderate for writing.
- Prompts must treat paper text as **untrusted data**: wrap it in clear delimiters and instruct the model to ignore any instructions found inside source text (prompt-injection hygiene).
- Track and log token usage per review to stay inside free-tier limits. Keep prompts compact: send abstracts only, not extra metadata.
- Handle free-tier rate limits with backoff, a configurable fallback provider, and graceful user-facing messages.
- Cache aggressively (query cache, embeddings per paper) so free quotas last.

---

## 11. Frontend screens

**Landing (`/`):** hero headline and subline, search input with submit, example query chips, recent reviews grid, theme toggle, command palette hint.

**Review page (`/r/[id]`):** two-column desktop layout.

- Left (main): title (the query), trust score summary with info tooltip, progress stepper while running, the review text with citation chips and verification badges, a Papers list at the bottom, and a references list.
- Right (sticky panel): context-sensitive. Default shows a paper list with source numbers. When a badge is clicked, shows the evidence panel. Tabs at the top of the page: **Review | Graph | Sources**.
- Mobile: panels become bottom sheets.

**States:** every screen has skeleton loading, empty, error and success states (DS-AC5).

---

## 12. Non-functional requirements

- `NFR1` Performance: landing page loads fast (good Lighthouse performance and accessibility scores, aim 90+). Cached example reviews render with no LLM call.
- `NFR2` Pipeline latency: first streamed token appears within roughly 8 seconds of submission under normal conditions. The full pipeline fits within the current maximum function duration of the chosen Vercel plan. If it cannot, split work across steps (for example: generation request, then verification as a separate resumable request triggered by the client) while keeping the same SSE contract to the UI. Record the decision in `docs/decisions.md`.
- `NFR3` Reliability: no unhandled exceptions in the pipeline; every failure maps to a typed error and a UI state.
- `NFR4` Security: input validation, rate limiting, CORS restricted to the deployed origin, secrets only in env, no user data stored beyond public reviews and hashed IP rate-limit keys, outbound requests only to configured provider hosts.
- `NFR5` Observability: structured JSON logs with a request id; log pipeline stage timings and token usage.
- `NFR6` Accessibility and responsiveness per Section 4.3.
- `NFR7` Code quality: strict typing (TypeScript strict mode, Python type hints checked in CI), no dead code, small functions, meaningful names.

---

## 13. Non-goals (do not build)

- Authentication, accounts, payments, teams, or per-user libraries.
- PDF upload or full-text ingestion.
- Any paid service or paid API tier.
- Admin dashboards, analytics products, email, notifications.
- Multi-language support.
- Fine-tuning or training models.
- Crawling beyond the already-fetched metadata for the graph.

---

## 14. Build order and milestones

1. **F0** Scaffold, design system, Docker, CI.
2. **F1** Discovery and ranking.
3. **F2** Generation with streaming and UI.
4. **F3** Verification (the standout; do this before polish).
5. **F5** Share, export, examples, rate limiting, command palette.
6. **F4** Citation graph.
7. **F6** Docs, deploy, smoke test, final review.

Each milestone ends with its review file in `docs/reviews/` and a commit.

---

## 15. Definition of done (global)

A feature is done only when all are true:

- Failing tests were written first and later pass (evidence in the review file).
- Every AC of the feature is marked Pass with evidence.
- Lint, type check, tests and build are green locally and in CI.
- UI passes the design acceptance criteria in both themes.
- NFRs relevant to the feature are checked.
- No TODOs, commented-out code, or console noise left behind.
- `docs/reviews/<feature-id>.md` is committed.

---

## 16. Demo script (for the outreach video)

1. Open the live site in dark mode and click an example query.
2. Watch the review stream and the stepper advance.
3. Point to the trust score and hover the info tooltip (abstract-based verification).
4. Click an Unsupported badge, show the evidence panel.
5. Open the Graph tab, click a node, and show the linked sentences highlight.
6. Toggle light mode, press `Cmd+K`, copy BibTeX.
7. Close on the README's section mapping the project to the job description.
