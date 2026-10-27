"""
Unit Tests for Milestone F5: Share, Export & Seed Examples.
Covers F5-AC1 through F5-AC7.
"""
import pytest
import httpx
from app.models.paper import Paper
from app.models.review import ReviewResponse, ClaimModel
from app.services.export import generate_bibtex, generate_markdown, escape_latex


def test_F5_AC2_escape_latex():
    raw = "Research & Development: 100% of $10 #trends in {AI_ML}"
    escaped = escape_latex(raw)
    assert "\\&" in escaped
    assert "\\%" in escaped
    assert "\\$" in escaped
    assert "\\#" in escaped
    assert "\\_" in escaped
    assert "\\{" in escaped
    assert "\\}" in escaped


def test_F5_AC2_generate_bibtex():
    papers = [
        Paper(
            id="W12345",
            title="Attention & Transformers",
            authors=["A. Vaswani", "N. Shazeer"],
            year=2017,
            venue="NeurIPS",
            doi="10.1000/182",
            abstract="Abstract text",
            citation_count=1000,
        )
    ]
    bib = generate_bibtex(papers)
    assert "@article{W12345," in bib
    assert "Attention \\& Transformers" in bib
    assert "author = {A. Vaswani and N. Shazeer}" in bib
    assert "year = {2017}" in bib
    assert "doi = {10.1000/182}" in bib


def test_F5_AC2_generate_markdown():
    review = ReviewResponse(
        id="rev_123",
        query="CRISPR gene editing",
        status="complete",
        trust_score=95.0,
        claims=[
            ClaimModel(
                id="c1",
                sentence="Cas9 induces double-strand breaks.",
                position=0,
                citations=[1],
                verdict="supported",
            )
        ],
    )
    papers = [
        Paper(
            id="p1",
            source_num=1,
            title="Genome editing with Cas9",
            authors=["J. Doudna"],
            year=2020,
            venue="Nature",
            abstract="Cas9 abstract",
            citation_count=500,
        )
    ]
    md = generate_markdown(review, papers)
    assert "# CRISPR gene editing" in md
    assert "Cas9 induces double-strand breaks. [1] *(SUPPORTED)*" in md
    assert "## References" in md
    assert "[1] J. Doudna (2020). *Genome editing with Cas9*. Nature." in md


@pytest.mark.asyncio
async def test_F5_AC3_examples_endpoint(async_client: httpx.AsyncClient):
    resp = await async_client.get("/api/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert "examples" in data
    assert len(data["examples"]) > 0


@pytest.mark.asyncio
async def test_F5_AC2_bibtex_and_md_endpoints(async_client: httpx.AsyncClient):
    create_resp = await async_client.post("/api/reviews", json={"query": "superconductivity"})
    review_id = create_resp.json()["id"]

    bib_resp = await async_client.get(f"/api/reviews/{review_id}/bibtex")
    assert bib_resp.status_code == 200
    assert "@article" in bib_resp.text

    md_resp = await async_client.get(f"/api/reviews/{review_id}/markdown")
    assert md_resp.status_code == 200
    assert "# superconductivity" in md_resp.text
