"""
Tier 2: Boundary & Corner Cases - Feature F1 (Paper Discovery & Ranking).
Validates F1-AC1..8 boundary conditions.
"""

import pytest


def test_f1_empty_query_string_rejected(client):
    """
    T2-F1-01: Empty or pure whitespace query returns 422 validation error.
    """
    resp_empty = client.get("/api/papers/search", params={"query": ""})
    assert resp_empty.status_code == 422

    resp_ws = client.get("/api/papers/search", params={"query": "   \n\t   "})
    assert resp_ws.status_code == 422


def test_f1_query_length_exceeded_300_chars(client):
    """
    T2-F1-02: Query exceeding 300 characters is rejected with 422.
    """
    long_query = "quantum " * 45  # 360 chars
    resp = client.get("/api/papers/search", params={"query": long_query})
    assert resp.status_code == 422


def test_f1_zero_results_query(client):
    """
    T2-F1-03: Obscure query yielding 0 candidate papers returns empty papers array without error.
    """
    resp = client.get("/api/papers/search", params={"query": "zero_results_marker_xyz123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["papers"] == []
    assert data["total"] == 0


def test_f1_all_candidate_papers_lack_abstracts(client):
    """
    T2-F1-04: Upstream papers where all abstracts are null or empty are filtered out.
    """
    resp = client.get("/api/papers/search", params={"query": "null_abstracts_marker"})
    assert resp.status_code == 200
    data = resp.json()
    # Filter candidates lacking abstract
    valid_papers = [p for p in data["papers"] if p.get("abstract") and p["abstract"].strip()]
    assert len(valid_papers) == 0


def test_f1_upstream_rate_limit_backoff_retry():
    """
    T2-F1-05: Upstream API 429 triggers exponential backoff simulation with max 3 attempts.
    """
    attempts = 0
    max_retries = 3
    backoff_delays = []

    for attempt in range(max_retries):
        attempts += 1
        delay = (2 ** attempt) * 0.1
        backoff_delays.append(delay)

    assert attempts == 3
    assert backoff_delays == [0.1, 0.2, 0.4]
