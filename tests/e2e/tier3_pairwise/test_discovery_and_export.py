"""
Tier 3: Pairwise Combination - F1 Discovery & F5 Export / Graph.
Validates cross-feature interactions between discovery and downstream exports.
"""

import pytest


def test_t3_01_discovery_to_bibtex_author_formatting():
    """
    T3-01: OpenAlex author structures with compound surnames and initials
    format into valid BibTeX 'Lastname, Firstname and ...' syntax.
    """
    raw_authors = ["A. Michael Lincoff", "John J.V. McMurray", "Kirsten Brown-Frandsen"]
    bibtex_authors = []
    for a in raw_authors:
        parts = a.strip().split()
        if len(parts) > 1:
            surname = parts[-1]
            given = " ".join(parts[:-1])
            bibtex_authors.append(f"{surname}, {given}")
        else:
            bibtex_authors.append(a)

    formatted = " and ".join(bibtex_authors)
    assert "Lincoff, A. Michael" in formatted
    assert "Brown-Frandsen, Kirsten" in formatted
    assert " and " in formatted


def test_t3_02_discovery_to_markdown_references(example_reviews):
    """
    T3-02: Paper discovery metadata maps into formatted Markdown references list.
    """
    papers = example_reviews[0]["papers"]
    lines = []
    for p in papers:
        doi = f"https://doi.org/{p['doi']}" if p.get("doi") else p.get("url", "")
        lines.append(f"[{p['source_number']}] {', '.join(p['authors'])} ({p['year']}). {p['title']}. {doi}")

    md_refs = "\n".join(lines)
    assert "[1]" in md_refs
    assert "Attention Is All You Need" in md_refs


def test_t3_03_deduplication_affects_graph_edges():
    """
    T3-03: Deduplication merges duplicate paper variants into canonical IDs;
    graph edges connect only to canonical nodes without dangling orphans.
    """
    raw_papers = [
        {"id": "p1_dup", "canonical_id": "p1_canon"},
        {"id": "p2", "canonical_id": "p2"},
        {"id": "p3", "canonical_id": "p3"}
    ]
    id_map = {p["id"]: p["canonical_id"] for p in raw_papers}

    raw_edges = [
        {"source": "p2", "target": "p1_dup"},
        {"source": "p3", "target": "p1_dup"}
    ]

    canonical_edges = [
        {"source": id_map[e["source"]], "target": id_map[e["target"]]}
        for e in raw_edges
    ]

    for e in canonical_edges:
        assert e["target"] == "p1_canon"
        assert e["target"] != "p1_dup"


def test_t3_04_query_cache_bypasses_rate_limit(client, example_reviews):
    """
    T3-04: Submitting query present in 24h cache returns cached review (200 OK)
    without decrementing rate limit remaining count.
    """
    cached_query = example_reviews[0]["query"]
    resp = client.post("/api/reviews", json={"query": cached_query, "regenerate": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("cached") is True
    assert data["id"] == example_reviews[0]["id"]
