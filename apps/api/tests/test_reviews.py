"""
Unit and Integration Tests for Milestone F2: Literature Review Generation & SSE Streaming.
Covers F2-AC1 through F2-AC9.
"""
import pytest
import httpx
from app.models.paper import Paper
from app.services.citation_parser import extract_citation_markers, segment_into_claims
from app.services.llm_client import build_review_prompt


def test_F2_AC3_citation_parser():
    # Test standard single citation
    assert extract_citation_markers("This is a fact [1].") == [1]
    # Test adjacent citations
    assert extract_citation_markers("Fact with adjacent [1][3].") == [1, 3]
    # Test comma separated
    assert extract_citation_markers("Fact with comma [2, 4].") == [2, 4]
    # Test ranges
    assert extract_citation_markers("Fact with range [1-3].") == [1, 2, 3]


def test_F2_AC4_AC5_segment_into_claims():
    text = (
        "This is an ungrounded general statement without citations. "
        "Self-attention achieves quadratic complexity [1]. "
        "Out of bounds marker emitted here [99]."
    )
    claims = segment_into_claims(text, max_source_num=5)
    assert len(claims) == 3

    # First claim is uncited factual statement
    assert claims[0].is_uncited is True
    assert claims[0].citations == []

    # Second claim has valid citation
    assert claims[1].citations == [1]
    assert claims[1].invalid_citations == []

    # Third claim has out-of-bounds marker
    assert 99 in claims[2].invalid_citations
    assert claims[2].verdict == "invalid_citation"


def test_F2_AC9_prompt_construction():
    papers = [
        Paper(id="p1", title="Transformer Attention", abstract="Self-attention is key.", citation_count=100),
        Paper(id="p2", title="FlashAttention", abstract="Tiling improves IO.", citation_count=50),
    ]
    prompt = build_review_prompt("Attention efficiency", papers)
    assert "--- SOURCE [1] ---" in prompt
    assert "--- SOURCE [2] ---" in prompt
    assert "<SOURCES>" in prompt
    assert "You may ONLY cite numbers between [1] and [2]" in prompt


@pytest.mark.asyncio
async def test_F2_AC1_create_review_endpoint(async_client: httpx.AsyncClient):
    # Valid creation
    resp = await async_client.post("/api/reviews", json={"query": "quantum error correction"})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["id"].startswith("rev_")

    # Invalid creation (< 3 chars)
    resp_bad = await async_client.post("/api/reviews", json={"query": "q"})
    assert resp_bad.status_code in (400, 422)


@pytest.mark.asyncio
async def test_F2_AC2_stream_review_endpoint(async_client: httpx.AsyncClient):
    # Create review first
    create_resp = await async_client.post("/api/reviews", json={"query": "CRISPR CAS9"})
    review_id = create_resp.json()["id"]

    # Stream
    async with async_client.stream("GET", f"/api/reviews/{review_id}/stream") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        events = []
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                events.append(line.split(":")[1].strip())

        assert "stage" in events
        assert "papers" in events
        assert "token" in events
        assert "review_complete" in events
        assert "done" in events
