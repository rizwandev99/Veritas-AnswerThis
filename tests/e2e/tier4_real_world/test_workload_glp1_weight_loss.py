"""
Tier 4: Real-World Research Workload 3 - Medicine & Pharmacology.
Scenario: 'Efficacy and cardiovascular outcomes of GLP-1 receptor agonists in type 2 diabetes'
Exercises: F1 (Ranking), F2 (Bounds Checking), F3 (Multi-Citation Aggregation, Trust Score), F5 (Markdown Export).
"""

import pytest
from tests.e2e.conftest import validate_quote_in_abstract, calculate_trust_score


def test_workload_glp1_cardiovascular_outcomes_end_to_end(client, example_reviews):
    """
    End-to-end evaluation of Medicine workload:
    - Analyzes SELECT and LEADER clinical trial evidence
    - Verifies multi-citation aggregation across cardiovascular endpoints
    - Mathematical verification of Trust Score formula (S + 0.5P) / V
    - Formatted Markdown export with clinical bibliography
    """
    rev = example_reviews[2]
    assert rev["discipline"] == "Medicine"

    # 1. Clinical trial papers retrieved
    papers = rev["papers"]
    assert len(papers) >= 5
    select_paper = next((p for p in papers if "SELECT" in p["abstract"] or "Lincoff" in str(p["authors"])), None)
    assert select_paper is not None

    # 2. Multi-citation claims resolution
    claims = rev["claims"]
    multi_citation_claims = [c for c in claims if len(c.get("cited_numbers", [])) > 1]
    assert len(multi_citation_claims) >= 1

    for mc in multi_citation_claims:
        verdicts = [v["verdict"] for v in mc["verifications"]]
        if "supported" in verdicts:
            assert mc["final_verdict"] == "supported"

    # 3. Trust Score formula check
    supported_cnt = sum(1 for c in claims if c.get("final_verdict") == "supported")
    partial_cnt = sum(1 for c in claims if c.get("final_verdict") == "partial")
    verifiable_cnt = len(claims)
    expected_score = calculate_trust_score(supported_cnt, partial_cnt, verifiable_cnt)
    assert abs(rev["trust_score"] - expected_score) < 0.05

    # 4. Verbatim numerical trial quote check
    mace_claim = next((c for c in claims if "20%" in c["text"] or "SELECT" in c["text"]), None)
    if mace_claim:
        verif = mace_claim["verifications"][0]
        assert "0.80" in verif["evidence_quote"]
        assert validate_quote_in_abstract(verif["evidence_quote"], select_paper["abstract"])

    # 5. Markdown export
    resp_md = client.get(f"/api/reviews/{rev['id']}/markdown")
    assert resp_md.status_code == 200
    assert "New England Journal of Medicine" in resp_md.text
