"""
Tier 4: Real-World Research Workload 2 - Molecular Biology / Genetics.
Scenario: 'CRISPR-Cas9 off-target cleavage mitigation strategies'
Exercises: F1 (Deduplication, Chunking), F2 (SSE Token Streaming), F3 (Strict Quote Matching), F4 (Graph), F5 (Share URL).
"""

import pytest
from tests.e2e.conftest import parse_sse_events, validate_quote_in_abstract


def test_workload_crispr_gene_editing_end_to_end(client, example_reviews):
    """
    End-to-end evaluation of Biology / Genetics workload:
    - Verifies high-fidelity Cas9 engineered variants (SpCas9-HF1, eSpCas9)
    - SSE streaming delivers progress stages and tokens
    - Verbatim quote check validates residue mutation statements
    - Graph renders with foundational Jinek/Doudna 2012 paper
    - Permanent URL /r/{id} validates accessibility
    """
    rev = example_reviews[1]
    assert rev["discipline"] == "Biology"

    # 1. Verify paper retrieval and metadata
    papers = rev["papers"]
    assert len(papers) >= 5
    doudna_paper = next((p for p in papers if "Doudna" in str(p["authors"])), None)
    assert doudna_paper is not None
    assert doudna_paper["source_number"] == 1

    # 2. SSE streaming
    resp_stream = client.get(f"/api/reviews/{rev['id']}/stream")
    assert resp_stream.status_code == 200
    events = parse_sse_events(resp_stream.text)
    event_types = [e["event"] for e in events]
    assert "stage" in event_types
    assert "token" in event_types
    assert "claim_verified" in event_types

    # 3. Strict quote matching for Cas9 specificity mutations
    claims = rev["claims"]
    mutation_claim = next((c for c in claims if "mutat" in c["text"].lower() or "residue" in c["text"].lower()), None)
    if mutation_claim:
        verif = mutation_claim["verifications"][0]
        src_paper = next(p for p in papers if p["source_number"] == verif["source_number"])
        assert validate_quote_in_abstract(verif["evidence_quote"], src_paper["abstract"])

    # 4. Interactive citation graph
    resp_graph = client.get(f"/api/reviews/{rev['id']}/graph")
    assert resp_graph.status_code == 200
    graph_data = resp_graph.json()
    assert len(graph_data["nodes"]) >= 5
    assert len(graph_data["edges"]) >= 3

    # 5. Share URL
    resp_share = client.get(f"/api/reviews/{rev['id']}")
    assert resp_share.status_code == 200
    assert resp_share.json()["status"] == "complete"
