# Architecture Decision Records (ADRs)

## ADR-001: Linear-Grade Design Tokens with Semantic CSS Variables
- **Status:** Accepted
- **Context:** The project requires a clean, minimal UI inspired by `linear.app` supporting Dark and Light themes with zero flash of unstyled theme (anti-FOUC).
- **Decision:** Implement design tokens as CSS variables (`--background`, `--surface`, `--accent`, `--success`, `--warning`, `--danger`) mapped into Tailwind CSS colors. An inline script in `apps/web/app/layout.tsx` inspects `localStorage` and `prefers-color-scheme` before HTML render.

## ADR-002: Dual VectorStore Implementation (pgvector and FAISS)
- **Status:** Accepted
- **Context:** PRD requires pgvector in production and a fast, local in-memory FAISS adapter for offline testing and Dockerless workflows.
- **Decision:** Standardized an abstract `VectorStore` base class with `add_chunks` and `search` methods. `FaissVectorStore` uses deterministic cosine similarity; `PgVectorStore` uses PostgreSQL `<=>` vector distance operator.

## ADR-003: Strict Evidence Substring Validation for Claim Grounding
- **Status:** Accepted
- **Context:** LLMs frequently hallucinate or paraphrase quotes when performing fact verification.
- **Decision:** All extracted evidence quotes must pass an exact normalized substring check against the source abstract. Fabricated quotes are rejected and marked unverifiable, protecting the trust score from hallucinated grounding.

## ADR-004: In-Memory 24-Hour Query Cache & Seed Examples
- **Status:** Accepted
- **Context:** PRD requires instant response for example queries and 24h caching of identical normalized queries without consuming LLM quotas.
- **Decision:** Implemented a normalized query cache with 24-hour TTL and seeded 5 gold standard reviews exposed via `GET /api/examples`.
