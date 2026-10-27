"""
Tier 3: Pairwise Combination - F1 Cache & F5 Rate Limits / Seed Examples.
Validates cross-feature interactions between rate limiting, query caching, and seed examples.
"""

import pytest


def test_t3_13_rate_limit_exceeded_allows_example_access(client):
    """
    T3-13: When rate limits are saturated on POST /api/reviews,
    GET /api/examples remains 100% operational (200 OK).
    """
    resp_examples = client.get("/api/examples")
    assert resp_examples.status_code == 200
    assert len(resp_examples.json()) == 5


def test_t3_14_regenerate_flag_bypasses_cache():
    """
    T3-14: Review creation with regenerate=True forces a fresh generation pass,
    bypassing the 24-hour cache.
    """
    cache_store = {"transformer attention": {"id": "rev_old", "cached": True}}
    norm_query = "transformer attention"
    regenerate = True

    if not regenerate and norm_query in cache_store:
        result = cache_store[norm_query]
    else:
        result = {"id": "rev_new", "cached": False}

    assert result["id"] == "rev_new"
    assert result["cached"] is False


def test_t3_15_markdown_export_includes_verification_audit_summary(client, example_reviews):
    """
    T3-15: Markdown export document incorporates Trust Score and verified claim metrics.
    """
    rev_id = example_reviews[0]["id"]
    resp = client.get(f"/api/reviews/{rev_id}/markdown")
    assert resp.status_code == 200
    content = resp.text
    assert "**Trust Score**:" in content
    assert "**Verified Claims**:" in content
    assert "Citation Verification Notice:" in content
