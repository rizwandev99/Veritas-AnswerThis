"""
Tier 4: Real-World Research Workload 1 - Computer Science / AI.
Scenario: 'Attention mechanisms and self-attention in Transformer architectures'
Exercises: F1 (Discovery), F2 (Generation), F3 (Verification against Vaswani et al.), F4 (Citation Graph), F5 (BibTeX).
"""

import pytest
from tests.e2e.conftest import validate_quote_in_abstract


def test_workload_transformer_attention_end_to_end(client, example_reviews):
    """
    End-to-end evaluation of CS/AI workload:
    - Discovery of foundational attention and SSM papers
    - Review generation with >=5 cited papers and Vaswani et al. as primary source
    - Claim-level verification achieving Trust Score >= 80%
    - Citation graph with Vaswani et al. as central hub
    - RFC BibTeX export containing valid @inproceedings citation
    """
    rev = example_reviews[0]
    assert rev["discipline"] == "Computer Science"

    # 1. Verify paper retrieval
    papers = rev["papers"]
    assert len(papers) >= 5
    vaswani_paper = next((p for p in papers if "Vaswani" in p["authors"][0]), None)
    assert vaswani_paper is not None
    assert vaswani_paper["source_number"] == 1

    # 2. Verify review generation text
    review_text = rev["review_text"]
    word_count = len(review_text.split())
    assert 200 <= word_count <= 800
    assert "[1]" in review_text

    # 3. Verify claim verification against abstract
    claims = rev["claims"]
    assert len(claims) >= 4
    vaswani_claim = next((c for c in claims if 1 in c["cited_numbers"]), None)
    assert vaswani_claim is not None
    assert vaswani_claim["final_verdict"] == "supported"

    # Check that evidence quote matches abstract
    verif = vaswani_claim["verifications"][0]
    assert validate_quote_in_abstract(verif["evidence_quote"], vaswani_paper["abstract"])

    # Verify overall trust score
    assert rev["trust_score"] >= 0.80

    # 4. Verify graph topology: Vaswani paper has incoming citations
    graph = rev["graph"]
    vaswani_edges = [e for e in graph["edges"] if e["target"] == vaswani_paper["id"]]
    assert len(vaswani_edges) >= 3, "Vaswani paper must act as citation hub"

    # 5. Verify BibTeX export
    resp = client.get(f"/api/reviews/{rev['id']}/bibtex")
    assert resp.status_code == 200
    bib_text = resp.text
    assert "Attention Is All You Need" in bib_text
    assert "@inproceedings" in bib_text or "@article" in bib_text
