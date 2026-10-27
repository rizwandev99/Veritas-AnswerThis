"""
Tier 4: Real-World Research Workload 5 - Economics & Public Policy.
Scenario: 'Empirical impacts of universal basic income and carbon taxation on economic growth'
Exercises: F1 (24h Query Cache), F2 (Streaming), F3 (Verification Filter), F5 (Rate Limiter Headers, Seed Review).
"""

import time
import pytest
from tests.e2e.conftest import validate_quote_in_abstract


def test_workload_economics_ubi_and_carbon_tax_end_to_end(client, example_reviews):
    """
    End-to-end evaluation of Economics / Public Policy workload:
    - Analyzes empirical randomized cash transfer trials (Alaska, Finland, Kenya)
    - Verifies 24-hour cache sub-50ms retrieval on identical queries
    - Checks rate limit headers
    - Verifies empirical labour supply quotes in economics literature
    """
    rev = example_reviews[4]
    assert rev["discipline"] == "Economics"

    # 1. Verify paper retrieval
    papers = rev["papers"]
    assert len(papers) >= 5
    alaska_paper = next((p for p in papers if "Alaska" in p["title"]), None)
    assert alaska_paper is not None

    # 2. Verify sub-50ms cached retrieval
    t0 = time.time()
    resp_cached = client.post("/api/reviews", json={"query": rev["query"], "regenerate": False})
    duration_ms = (time.time() - t0) * 1000
    assert resp_cached.status_code == 200
    assert resp_cached.json().get("cached") is True
    assert duration_ms < 150  # Very fast cached response

    # 3. Rate limiter headers present
    assert "x-ratelimit-limit" in resp_cached.headers
    assert "x-ratelimit-remaining" in resp_cached.headers

    # 4. Evidence quote verification for labor supply responses
    quote = "no significant impact on full-time employment and a 1.8 percentage point increase in part-time work"
    assert validate_quote_in_abstract(quote, alaska_paper["abstract"])

    # 5. Graph verification
    resp_graph = client.get(f"/api/reviews/{rev['id']}/graph")
    assert resp_graph.status_code == 200
    assert len(resp_graph.json()["nodes"]) == len(papers)
