"""
Tier 4: Real-World Research Workload 4 - Quantum Physics / Materials.
Scenario: 'Fault-tolerant quantum error correction using surface codes and hydride superconductivity'
Exercises: F1 (VectorStore Search), F2 (Uncited Claim Detection), F3 (Contradiction & Retraction Handling), F4 (Graph).
"""

import pytest
from tests.e2e.conftest import validate_quote_in_abstract


def test_workload_quantum_physics_and_hydride_controversy_end_to_end(client, example_reviews):
    """
    End-to-end evaluation of Physics / Controversy workload:
    - Analyzes high-temperature hydride superconductivity claims vs replication refutations
    - Verifies handling of contradictory evidence and retracted claims
    - Graph displays opposing clusters with danger status colors on refuted claims
    - Trust Score reflects genuine scientific disagreement (~65-72%)
    """
    rev = example_reviews[3]
    assert rev["discipline"] == "Physics"

    # 1. Papers retrieved include both claim and refutation
    papers = rev["papers"]
    assert len(papers) >= 5
    retracted_paper = next((p for p in papers if "Dias" in str(p["authors"]) or "Retracted" in p["venue"]), None)
    refutation_paper = next((p for p in papers if "Absence" in p["title"] or "Ming" in str(p["authors"])), None)
    assert retracted_paper is not None
    assert refutation_paper is not None

    # 2. Refutation quote validated
    refutation_quote = "no evidence of superconductivity or zero-resistance transitions was observed"
    assert validate_quote_in_abstract(refutation_quote, refutation_paper["abstract"])

    # 3. Trust score reflects controversy
    assert 0.60 <= rev["trust_score"] <= 0.75, f"Controversial topic score should be ~69%, got {rev['trust_score']}"

    # 4. Graph visualizes danger status color on disputed node
    graph = rev["graph"]
    disputed_node = next((n for n in graph["nodes"] if n["id"] == retracted_paper["id"]), None)
    assert disputed_node is not None
    assert disputed_node["status_color"] == "danger"
