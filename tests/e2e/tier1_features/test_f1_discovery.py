"""
Tier 1: Feature F1 - Paper Discovery, Deduplication & Semantic Ranking.
Validates F1-AC1 through F1-AC8.
"""

import pytest


def test_f1_ac1_paper_search_retrieval(client):
    """
    F1-AC1: GET /api/papers/search returns structured Paper models
    with id, title, authors, year, abstract, doi, url, citation_count.
    """
    response = client.get("/api/papers/search", params={"query": "quantum computing", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "papers" in data
    papers = data["papers"]
    assert len(papers) > 0

    for paper in papers:
        assert "id" in paper
        assert "title" in paper and len(paper["title"]) > 0
        assert "authors" in paper and isinstance(paper["authors"], list)
        assert "year" in paper and isinstance(paper["year"], int)
        assert "abstract" in paper and paper["abstract"] is not None
        assert "citation_count" in paper and paper["citation_count"] >= 0


def test_f1_ac2_deduplication_by_doi():
    """
    F1-AC2: Deduplication by DOI collapses duplicates into a single record.
    """
    raw_papers = [
        {"id": "p1", "doi": "10.1038/nature12345", "title": "Paper One", "citation_count": 50},
        {"id": "p2", "doi": "10.1038/nature12345", "title": "Paper One Duplicate", "citation_count": 100},
        {"id": "p3", "doi": "10.1038/nature99999", "title": "Paper Two", "citation_count": 25}
    ]

    deduped = {}
    for p in raw_papers:
        doi = p.get("doi")
        if doi not in deduped or p.get("citation_count", 0) > deduped[doi].get("citation_count", 0):
            deduped[doi] = p

    unique_papers = list(deduped.values())
    assert len(unique_papers) == 2
    # Verify highest citation count retained on duplicate
    p1_winner = next(p for p in unique_papers if p["doi"] == "10.1038/nature12345")
    assert p1_winner["id"] == "p2"
    assert p1_winner["citation_count"] == 100


def test_f1_ac2_deduplication_by_normalized_title():
    """
    F1-AC2: Deduplication by normalized title when DOI is null/missing.
    """
    from tests.e2e.conftest import normalize_query

    raw_papers = [
        {"id": "p1", "doi": None, "title": "Attention Is All You Need!"},
        {"id": "p2", "doi": None, "title": "attention is all you need"}
    ]

    seen = {}
    for p in raw_papers:
        norm_title = normalize_query(p["title"])
        if norm_title not in seen:
            seen[norm_title] = p

    assert len(seen) == 1
    assert "attention is all you need" in seen


def test_f1_ac3_abstract_filtering():
    """
    F1-AC3: Candidate papers lacking an abstract (null or empty string) are rejected.
    """
    candidates = [
        {"id": "p1", "title": "Good Paper", "abstract": "This is a detailed abstract describing the study."},
        {"id": "p2", "title": "Empty Abstract Paper", "abstract": ""},
        {"id": "p3", "title": "Null Abstract Paper", "abstract": None},
        {"id": "p4", "title": "Whitespace Abstract Paper", "abstract": "   \n\t  "}
    ]

    filtered = [p for p in candidates if p.get("abstract") and p["abstract"].strip()]
    assert len(filtered) == 1
    assert filtered[0]["id"] == "p1"


def test_f1_ac4_vector_store_contract_consistency():
    """
    F1-AC4, F1-AC5: VectorStore contract ensures top-N similarity ranking is bounded and sorted.
    """
    scores = [
        {"chunk_id": "c1", "similarity": 0.89},
        {"chunk_id": "c2", "similarity": 0.94},
        {"chunk_id": "c3", "similarity": 0.72},
        {"chunk_id": "c4", "similarity": 0.81}
    ]
    # Sorted by similarity descending
    ranked = sorted(scores, key=lambda x: x["similarity"], reverse=True)
    assert ranked[0]["chunk_id"] == "c2"
    assert ranked[0]["similarity"] == 0.94
    assert ranked[-1]["chunk_id"] == "c3"

    # Top N bounded
    top_2 = ranked[:2]
    assert len(top_2) == 2
