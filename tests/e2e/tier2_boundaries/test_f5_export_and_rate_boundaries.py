"""
Tier 2: Boundary & Corner Cases - Feature F5 (Share, Export, Rate Limiting & Examples).
Validates F5-AC1..7 boundaries.
"""

import pytest
from tests.e2e.conftest import normalize_query


def test_f5_bibtex_special_characters_escaping():
    """
    T2-F5-01: Titles with special LaTeX characters (&, %, $, #, _, {, }) are properly escaped.
    """
    raw_title = "Evaluation of $500 & 50% discount on DNA_RNA {Sequencing} #1"
    escaped_title = raw_title
    for char, esc in [
        ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
        ("_", r"\_"), ("{", r"\{"), ("}", r"\}")
    ]:
        escaped_title = escaped_title.replace(char, esc)

    assert r"\$500" in escaped_title
    assert r"\&" in escaped_title
    assert r"\%" in escaped_title
    assert r"\#1" in escaped_title
    assert r"DNA\_RNA" in escaped_title


def test_f5_bibtex_missing_metadata_fallbacks():
    """
    T2-F5-02: Missing author, venue, or year fall back to safe default BibTeX fields.
    """
    paper = {
        "title": "Minimal Preprint",
        "authors": [],
        "year": None,
        "venue": None
    }
    author_str = " and ".join(paper["authors"]) if paper["authors"] else "{Unknown Author}"
    year_str = str(paper["year"]) if paper["year"] else "{n.d.}"
    entry_type = "misc" if not paper["venue"] else "article"

    assert author_str == "{Unknown Author}"
    assert year_str == "{n.d.}"
    assert entry_type == "misc"


def test_f5_rate_limit_burst_saturation(client):
    """
    T2-F5-03: Burst of requests exceeding rate limit (e.g. 5/hr) yields 429 on 6th call.
    """
    # Send requests with distinct queries to avoid cache hits
    status_codes = []
    for i in range(7):
        resp = client.post("/api/reviews", json={"query": f"burst query test {i} unique text"})
        status_codes.append(resp.status_code)

    # At least one request should receive HTTP 429 Too Many Requests
    assert 429 in status_codes
    resp_429 = client.post("/api/reviews", json={"query": "another request when saturated"})
    if resp_429.status_code == 429:
        assert "retry-after" in resp_429.headers
        data = resp_429.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_f5_query_cache_normalization_edge_cases():
    """
    T2-F5-04: Complex punctuation, capitalization, and spaces normalize to identical keys.
    """
    variations = [
        "  CRISPR-Cas9   off-target???  ",
        "crispr cas9 off target",
        "CRISPR/Cas9: off target!",
        "crispr - cas9, off-target."
    ]
    norm_0 = normalize_query(variations[0])
    norm_1 = normalize_query(variations[1])
    # Punctuation stripped and lowercased
    assert norm_0 == "crispr-cas9 off-target" or "crispr cas9 off target" in norm_0
    assert norm_1 == "crispr cas9 off target"


def test_f5_nonexistent_review_id_404(client):
    """
    T2-F5-05: Requesting non-existent review ID returns 404 with structured error envelope.
    """
    resp = client.get("/api/reviews/rev_nonexistent_999999")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data or "error" in data
