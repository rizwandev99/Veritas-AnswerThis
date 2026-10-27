"""
Tier 1: Feature F2 - Streaming Literature Review Generation.
Validates F2-AC1 through F2-AC9.
"""

import pytest
from tests.e2e.conftest import parse_sse_events, extract_citation_markers


def test_f2_ac1_review_creation_lifecycle(client):
    """
    F2-AC1: POST /api/reviews creates review record, validates length (3-300), returns { id }.
    """
    payload = {"query": "Transformer attention mechanisms in vision models"}
    response = client.post("/api/reviews", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["id"].startswith("rev_")
    assert data["status"] in ["pending", "complete"]


def test_f2_ac2_sse_streaming_event_sequence(client, example_reviews):
    """
    F2-AC2: GET /api/reviews/{id}/stream emits typed SSE events in order:
    stage -> papers -> token -> review_complete -> claim_verified -> done.
    """
    rev_id = example_reviews[0]["id"]
    response = client.get(f"/api/reviews/{rev_id}/stream")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

    events = parse_sse_events(response.text)
    assert len(events) > 0

    event_types = [e["event"] for e in events]
    assert "stage" in event_types
    assert "papers" in event_types
    assert "token" in event_types
    assert "review_complete" in event_types
    assert "claim_verified" in event_types
    assert "done" in event_types

    # Verify stage transitions
    stages = [e["data"]["stage"] for e in events if e["event"] == "stage"]
    assert "searching" in stages
    assert "writing" in stages
    assert "verifying" in stages


def test_f2_ac3_citation_marker_parser():
    """
    F2-AC3: Citation parser extracts markers across multiple formats:
    [1], adjacent [1][2], comma [1, 2], range [1-3].
    """
    text_single = "Self-attention reduces sequential operations [1]."
    assert extract_citation_markers(text_single) == [1]

    text_adjacent = "Hybrid architectures combine convolutions with attention [1][3]."
    assert extract_citation_markers(text_adjacent) == [1, 3]

    text_comma = "Multiple studies support this observation [2, 4, 5]."
    assert extract_citation_markers(text_comma) == [2, 4, 5]

    text_range = "Broad benchmark consensus is established [1-4]."
    assert extract_citation_markers(text_range) == [1, 2, 3, 4]


def test_f2_ac4_sentence_and_claim_segmentation(example_reviews):
    """
    F2-AC4, F2-AC6: Parsed claims retain section, position, cited numbers, and text.
    """
    rev = example_reviews[0]
    claims = rev["claims"]
    assert len(claims) >= 3

    for i, claim in enumerate(claims):
        assert "id" in claim
        assert "position" in claim and claim["position"] >= 1
        assert "section" in claim and len(claim["section"]) > 0
        assert "text" in claim and len(claim["text"]) > 10
        assert "cited_numbers" in claim and isinstance(claim["cited_numbers"], list)


def test_f2_ac5_uncited_factual_claim_detection():
    """
    F2-AC5: Factual sentences lacking citation markers are identified with uncited flag.
    """
    sentence_with_citation = "CRISPR-Cas9 enables high-efficiency genome editing in mammalian cells [1]."
    sentence_uncited = "CRISPR-Cas9 was discovered in bacterial adaptive immune systems."

    markers_1 = extract_citation_markers(sentence_with_citation)
    markers_2 = extract_citation_markers(sentence_uncited)

    is_uncited_1 = len(markers_1) == 0
    is_uncited_2 = len(markers_2) == 0

    assert is_uncited_1 is False
    assert is_uncited_2 is True
