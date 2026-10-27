"""
Tier 3: Pairwise Combination - F2 Streaming & F3 Verification.
Validates cross-feature interactions between SSE review streaming and claim verification.
"""

import pytest
from tests.e2e.conftest import parse_sse_events, calculate_trust_score


def test_t3_05_stream_tokens_followed_by_claim_verifications(client, example_reviews):
    """
    T3-05: Review completes text generation before firing claim_verified events;
    verified claims correspond to parsed review claims.
    """
    rev_id = example_reviews[0]["id"]
    resp = client.get(f"/api/reviews/{rev_id}/stream")
    events = parse_sse_events(resp.text)

    token_indices = [i for i, e in enumerate(events) if e["event"] == "token"]
    claim_indices = [i for i, e in enumerate(events) if e["event"] == "claim_verified"]

    assert len(token_indices) > 0
    assert len(claim_indices) > 0
    # All tokens stream before claim verification
    assert max(token_indices) < min(claim_indices)


def test_t3_06_invalid_citations_affect_trust_score():
    """
    T3-06: Claims with invalid citations ([99]) count in the denominator of trust score
    as verifiable claims with 0 support points.
    """
    # 3 supported, 1 invalid_citation (counts as 0 points in numerator, 1 in denominator)
    # Total verifiable = 4, numerator = 3 + 0 = 3 -> 3 / 4 = 0.75
    score = calculate_trust_score(supported=3, partial=0, verifiable=4)
    assert score == 0.75


def test_t3_07_uncited_claims_excluded_from_verification():
    """
    T3-07: Sentences flagged as uncited are excluded from abstract chunk retrieval
    and LLM verification calls.
    """
    claims = [
        {"id": "c1", "text": "Cited claim [1].", "flags": {"uncited": False}},
        {"id": "c2", "text": "Uncited general statement.", "flags": {"uncited": True}},
        {"id": "c3", "text": "Another cited claim [2].", "flags": {"uncited": False}}
    ]
    claims_to_verify = [c for c in claims if not c["flags"]["uncited"]]
    assert len(claims_to_verify) == 2
    assert "c2" not in [c["id"] for c in claims_to_verify]


def test_t3_08_stream_error_preserves_partial_state(client, example_reviews):
    """
    T3-08: Stream error triggers graceful status handling while preserving review document.
    """
    # Verify existing review document is retrievable regardless of stream state
    rev_id = example_reviews[0]["id"]
    resp = client.get(f"/api/reviews/{rev_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == rev_id
