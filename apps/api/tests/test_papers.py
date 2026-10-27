"""
Unit and Integration Tests for Milestone F1: Paper Discovery, Deduplication & VectorStore.
Covers F1-AC1 through F1-AC8.
"""
import pytest
import httpx
from app.models.paper import Paper
from app.services.dedup import deduplicate_papers, normalize_query, normalize_title
from app.services.chunker import chunk_abstract, split_into_sentences
from app.services.paper_source import reconstruct_abstract_from_inverted_index
from app.services.vector_store import DeterministicEmbedder, FaissVectorStore, PaperChunk


def test_F1_AC2_deduplicate_by_doi():
    papers = [
        Paper(
            id="p1",
            title="Transformer Scaling Laws",
            abstract="Abstract 1",
            doi="10.1000/182",
            citation_count=50,
        ),
        Paper(
            id="p2",
            title="Transformer Scaling Laws Variant",
            abstract="Abstract 2",
            doi="10.1000/182",
            citation_count=200,
        ),
    ]
    deduped = deduplicate_papers(papers)
    assert len(deduped) == 1
    # Preserves highest citation count
    assert deduped[0].id == "p2"
    assert deduped[0].citation_count == 200


def test_F1_AC2_deduplicate_by_normalized_title():
    papers = [
        Paper(
            id="p1",
            title="FlashAttention: Fast Attention",
            abstract="Abstract 1",
            citation_count=100,
        ),
        Paper(
            id="p2",
            title="flashattention: fast attention!",
            abstract="Abstract 2",
            citation_count=150,
        ),
    ]
    deduped = deduplicate_papers(papers)
    assert len(deduped) == 1
    assert deduped[0].id == "p2"


def test_F1_AC8_deterministic_chunking():
    abstract = "This is sentence one. This is sentence two. This is sentence three! Here is sentence four."
    chunks = chunk_abstract("paper_123", abstract, window_sentences=2, overlap_sentences=1)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.paper_id == "paper_123"
        assert c.chunk_id.startswith("paper_123_c")
        assert len(c.text) > 0
        assert c.start_char >= 0
        assert c.end_char > c.start_char


def test_reconstruct_abstract_inverted_index():
    inverted_index = {
        "Attention": [0],
        "is": [1],
        "all": [2],
        "you": [3],
        "need.": [4],
    }
    reconstructed = reconstruct_abstract_from_inverted_index(inverted_index)
    assert reconstructed == "Attention is all you need."


@pytest.mark.asyncio
async def test_F1_AC4_vector_store_contract():
    embedder = DeterministicEmbedder()
    store = FaissVectorStore(embedder)

    chunks = [
        PaperChunk(chunk_id="c1", paper_id="p1", chunk_index=0, text="Quantum computing and qubits", start_char=0, end_char=28),
        PaperChunk(chunk_id="c2", paper_id="p2", chunk_index=0, text="CRISPR gene editing and Cas9 enzymes", start_char=0, end_char=37),
    ]
    await store.add_chunks(chunks)

    results = await store.search("quantum mechanics algorithms", top_k=1)
    assert len(results) == 1
    matched_chunk, score = results[0]
    assert matched_chunk.paper_id == "p1"
    assert score > 0.0


@pytest.mark.asyncio
async def test_F1_AC1_search_papers_endpoint(async_client: httpx.AsyncClient):
    resp = await async_client.get("/api/papers/search", params={"query": "transformer attention", "limit": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert "papers" in data
    assert len(data["papers"]) > 0
    paper = data["papers"][0]
    assert "title" in paper
    assert "abstract" in paper
    assert "source_num" in paper
    assert paper["source_num"] == 1
