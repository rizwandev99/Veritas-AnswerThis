# E2E Test Infra: Project Veritas

## Test Philosophy
- **Opaque-Box & Requirement-Driven**: Tests are derived strictly from `ORIGINAL_REQUEST.md` and `PRD Veritas – Citation-Verified Literature Review Generator.md` from the perspective of an end user or external HTTP client. Tests never import internal private functions or depend on implementation internals.
- **Methodology**: Systematic 4-tier testing hierarchy combining Category-Partition, Boundary Value Analysis (BVA), Pairwise Combinatorial Testing, and Real-World Workload Testing.
- **Progressive Testability**: Each test's verification mechanism does not require features more complex than what it verifies. Tier 1 gives pass/fail signals from early milestones onwards.
- **Deterministic & Isolated**: Built to execute against local test harnesses, mock fixtures, or running docker containers with zero external network flakiness.

---

## Feature Inventory & Test Mapping

| # | Feature | PRD Source | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) |
|---|---------|------------|:-----------------:|:-----------------:|:-----------------:|
| 1 | System Health & Bootstrap | F0-AC1, §9 | 5 tests | 5 tests | ✓ |
| 2 | Design System Tokens & Theme | DS-AC1..5, §4 | 5 tests | 5 tests | ✓ |
| 3 | UI Primitives & /design Route | F0-AC2, §4.3 | 5 tests | 5 tests | ✓ |
| 4 | OpenAlex Paper Discovery & Inverted Index | F1-AC1, §6 | 5 tests | 5 tests | ✓ |
| 5 | Paper Deduplication & Quality Filter | F1-AC2, F1-AC3 | 5 tests | 5 tests | ✓ |
| 6 | Chunking & VectorStore Dual Contract | F1-AC4, F1-AC5 | 5 tests | 5 tests | ✓ |
| 7 | Semantic Ranking & Query Cache | F1-AC6, F1-AC7 | 5 tests | 5 tests | ✓ |
| 8 | Review Lifecycle & SSE Streaming | F2-AC1, F2-AC2 | 5 tests | 5 tests | ✓ |
| 9 | Sentence & Citation Parsing / Validation | F2-AC3..5 | 5 tests | 5 tests | ✓ |
| 10 | Streaming UI & Citation Chips | F2-AC7, F2-AC8 | 5 tests | 5 tests | ✓ |
| 11 | Claim Verification & Strict Quote Match | F3-AC1, F3-AC2 | 5 tests | 5 tests | ✓ |
| 12 | Out-of-Bounds Rejection & Multi-Citation | F3-AC3, F3-AC4 | 5 tests | 5 tests | ✓ |
| 13 | Mathematical Trust Score & Evidence Panel | F3-AC5..8 | 5 tests | 5 tests | ✓ |
| 14 | Ground-Truth Eval Suite & `make eval` | F3-AC10, §2.2 | 5 tests | 5 tests | ✓ |
| 15 | Citation Graph Node-Link API & Engine | F4-AC1, F4-AC2 | 5 tests | 5 tests | ✓ |
| 16 | Interactive Graph Canvas & Highlighting | F4-AC3..6 | 5 tests | 5 tests | ✓ |
| 17 | Share URLs (`/r/{id}`) & OpenGraph | F5-AC1, §12 | 5 tests | 5 tests | ✓ |
| 18 | Markdown & BibTeX Export | F5-AC2, §9 | 5 tests | 5 tests | ✓ |
| 19 | Sliding Window Rate Limiting | F5-AC3, §8 | 5 tests | 5 tests | ✓ |
| 20 | Instant Seed Example Reviews | F5-AC4, §9 | 5 tests | 5 tests | ✓ |
| 21 | Command Palette & Local History | F5-AC5, §4.1 | 5 tests | 5 tests | ✓ |
| 22 | Automated Smoke Test (`make smoke`) | F6-AC2, §14 | 5 tests | 5 tests | ✓ |

---

## Test Architecture

### Directory Layout
```
tests/e2e/
├── runner.py                 # Master E2E runner (CLI arguments, exit codes, junit XML)
├── conftest.py               # Shared test fixtures, mock server, client sessions
├── tier1_features/           # Tier 1: Feature coverage (isolated happy paths)
│   ├── test_f0_scaffold.py
│   ├── test_f1_discovery.py
│   ├── test_f2_generation.py
│   ├── test_f3_verification.py
│   ├── test_f4_graph.py
│   ├── test_f5_exports.py
│   └── test_f6_docs_smoke.py
├── tier2_boundaries/         # Tier 2: Boundaries, edge cases, negative tests
│   ├── test_query_boundaries.py
│   ├── test_sse_reconnection_failures.py
│   ├── test_quote_hallucination_rejection.py
│   ├── test_trust_score_edge_cases.py
│   ├── test_graph_degenerate_cases.py
│   └── test_rate_limit_saturation.py
├── tier3_pairwise/           # Tier 3: Combinatorial feature interactions
│   ├── test_discovery_and_export.py
│   ├── test_stream_and_verification.py
│   ├── test_graph_and_claim_highlight.py
│   └── test_cache_and_rate_limits.py
└── tier4_real_world/         # Tier 4: Real-world research workloads
    ├── test_workload_transformer_attention.py
    ├── test_workload_crispr_gene_editing.py
    ├── test_workload_glp1_weight_loss.py
    ├── test_workload_quantum_error_correction.py
    └── test_workload_carbon_tax_emissions.py
```

### Test Runner Invocation
- Full Test Suite: `python tests/e2e/runner.py --all`
- Per-Tier Invocations:
  - `python tests/e2e/runner.py --tier 1`
  - `python tests/e2e/runner.py --tier 2`
  - `python tests/e2e/runner.py --tier 3`
  - `python tests/e2e/runner.py --tier 4`
- Makefile Target: `make test-e2e`
- Pass/Fail Semantics:
  - Exit code `0` on 100% passing test assertions.
  - Non-zero exit code on any assertion failure or unhandled exception.
  - Colorized terminal report with summary table and execution duration.

---

## Real-World Application Scenarios (Tier 4)

| # | Scenario / Domain | Query | Features Exercised | Expected Outcome |
|---|-------------------|-------|--------------------|------------------|
| 1 | Computer Science / AI | "Attention mechanisms and self-attention in Transformer architectures" | F1 (OpenAlex discovery), F2 (400-700w review generation), F3 (claim verification against Vaswani et al.), F4 (citation graph with Vaswani as hub), F5 (BibTeX export) | Review generated with >=5 cited papers, Vaswani cited and verified supported, Trust Score >= 80%, clean BibTeX. |
| 2 | Molecular Biology | "CRISPR-Cas9 off-target cleavage mitigation strategies" | F1 (deduplication, abstract chunking), F2 (SSE token streaming), F3 (strict quote substring verification), F4 (interactive graph), F5 (shareable link) | Exact quote substrings verified in abstracts, partial/unsupported claims correctly highlighted, graph renders responsive nodes. |
| 3 | Medicine / Pharmacology | "Efficacy and cardiovascular outcomes of GLP-1 receptor agonists in type 2 diabetes" | F1 (ranking), F2 (citation bounds checking), F3 (multi-citation aggregation, trust score formula), F5 (markdown export) | Multi-citation claims resolved via priority hierarchy, trust score correctly calculated, markdown export preserves tables/references. |
| 4 | Quantum Physics | "Fault-tolerant quantum error correction using surface codes" | F1 (VectorStore FAISS & pgvector), F2 (uncited factual claim detection), F3 (unverifiable claim handling), F4 (bridge nodes) | Fast vector search, uncited sentences flagged, bridge nodes synthesized if referenced by >=3 papers, zero crashes. |
| 5 | Environmental Economics | "Empirical impacts of carbon taxation on industrial emissions and economic growth" | F1 (24h query cache), F2 (streaming review), F3 (verification filter toggle), F5 (rate limiter headers, instant seed review comparison) | Second identical query returns cached review in <50ms, rate limit headers present, verdict filter switches visible claims smoothly. |

---

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: >=5 test cases per feature across all 7 milestones (minimum 35 test cases).
- **Tier 2 (Boundary & Corner Cases)**: >=5 test cases per feature covering boundaries, empty inputs, extreme queries, malformed quotes, and error recovery (minimum 35 test cases).
- **Tier 3 (Cross-Feature Combinations)**: Pairwise interaction tests covering major cross-cutting feature pairs (minimum 15 test cases).
- **Tier 4 (Real-World Workloads)**: 5 end-to-end multi-disciplinary research scenarios.
- **Total Minimum Threshold**: >= 90 comprehensive opaque-box test cases.
- **Acceptance Criterion**: 100% test pass required for `TEST_READY.md` validation.
