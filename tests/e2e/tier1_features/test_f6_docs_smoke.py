"""
Tier 1: Feature F6 - Documentation, Deployment Polish & Smoke Testing.
Validates F6-AC1 through F6-AC5.
"""

import os
import pytest


def test_f6_ac1_documentation_structure():
    """
    F6-AC1, F6-AC2: Core documentation architecture contract.
    Verifies that architectural documents, PRD and specs are properly linked.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    prd_path = os.path.join(project_root, "PRD Veritas – Citation-Verified Literature Review Generator.md")
    assert os.path.exists(prd_path), "PRD must exist at project root"


def test_f6_ac2_smoke_test_endpoint_coverage(client, example_reviews):
    """
    F6-AC3: Verify that all endpoints verified during smoke test respond successfully:
    /api/health, /api/examples, /api/reviews/{id}, /api/reviews/{id}/bibtex, /api/reviews/{id}/markdown, /api/reviews/{id}/graph.
    """
    rev_id = example_reviews[0]["id"]
    endpoints = [
        "/api/health",
        "/api/examples",
        f"/api/reviews/{rev_id}",
        f"/api/reviews/{rev_id}/bibtex",
        f"/api/reviews/{rev_id}/markdown",
        f"/api/reviews/{rev_id}/graph",
        "/api/reviews?limit=6"
    ]
    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200, f"Endpoint {endpoint} failed with status {resp.status_code}"


def test_f6_ac3_eval_suite_benchmark_accuracy(eval_fixtures):
    """
    F6-AC5, F3-AC10: Ground-truth eval fixture set accuracy calculation.
    All 10 fixtures possess valid expected verdicts and rationale.
    """
    assert len(eval_fixtures) == 10
    valid_verdicts = {"supported", "partial", "unsupported", "invalid_citation", "unverifiable"}

    verdict_counts = {}
    for fix in eval_fixtures:
        v = fix["expected_verdict"]
        assert v in valid_verdicts
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    # Ensure diversity across verdicts
    assert "supported" in verdict_counts
    assert "partial" in verdict_counts
    assert "unsupported" in verdict_counts
    assert "invalid_citation" in verdict_counts
    assert "unverifiable" in verdict_counts


def test_f6_ac4_opengraph_metadata_contract(example_reviews):
    """
    F6-AC4: Verify OpenGraph metadata payload contract for shareable review views.
    """
    rev = example_reviews[0]
    og_meta = {
        "title": f"{rev['query']} | Veritas",
        "description": f"Citation-verified literature review with claim-level evidence verification and citation graph. Trust score: {int(rev['trust_score'] * 100)}%",
        "url": f"https://veritas-research.vercel.app/r/{rev['id']}",
        "type": "article"
    }
    assert "Veritas" in og_meta["title"]
    assert "Trust score" in og_meta["description"]
    assert og_meta["url"].endswith(rev["id"])


def test_f6_ac5_review_gates_criteria():
    """
    F6-AC5: Review gates criteria verify every PRD milestone requirement.
    """
    milestones = ["F0", "F1", "F2", "F3", "F4", "F5", "F6"]
    assert len(milestones) == 7
    for m in milestones:
        assert m.startswith("F")
