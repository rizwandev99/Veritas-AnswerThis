"""
Tier 1: Feature F5 - Share, Export, Examples, History & Polish.
Validates F5-AC1 through F5-AC7.
"""

import pytest


def test_f5_ac1_permanent_review_retrieval(client, example_reviews):
    """
    F5-AC1: Review is retrievable by permanent ID via GET /api/reviews/{id}.
    """
    rev_id = example_reviews[0]["id"]
    response = client.get(f"/api/reviews/{rev_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rev_id
    assert "query" in data
    assert "review_text" in data
    assert data["status"] == "complete"


def test_f5_ac2_markdown_export(client, example_reviews):
    """
    F5-AC2: GET /api/reviews/{id}/markdown returns clean markdown with references.
    """
    rev_id = example_reviews[0]["id"]
    response = client.get(f"/api/reviews/{rev_id}/markdown")
    assert response.status_code == 200
    assert "text/markdown" in response.headers.get("content-type", "")
    assert f'filename="veritas-{rev_id}.md"' in response.headers.get("content-disposition", "")

    content = response.text
    assert content.startswith("# ")
    assert "## References" in content
    assert "Trust Score" in content


def test_f5_ac2_bibtex_export(client, example_reviews):
    """
    F5-AC2: GET /api/reviews/{id}/bibtex returns valid BibTeX entries with escaped characters.
    """
    rev_id = example_reviews[0]["id"]
    response = client.get(f"/api/reviews/{rev_id}/bibtex")
    assert response.status_code == 200
    assert "application/x-bibtex" in response.headers.get("content-type", "")
    assert f'filename="veritas-{rev_id}.bib"' in response.headers.get("content-disposition", "")

    content = response.text
    assert "@" in content
    assert "title = {" in content
    assert "author = {" in content


def test_f5_ac3_instant_seed_examples(client):
    """
    F5-AC3: GET /api/examples returns 5 multidisciplinary pre-computed reviews.
    """
    response = client.get("/api/examples")
    assert response.status_code == 200
    examples = response.json()
    assert len(examples) == 5

    disciplines = {ex["discipline"] for ex in examples}
    assert "Computer Science" in disciplines
    assert "Biology" in disciplines
    assert "Medicine" in disciplines
    assert "Physics" in disciplines
    assert "Economics" in disciplines


def test_f5_ac4_rate_limit_headers(client):
    """
    F5-AC5: Responses include X-RateLimit-Limit and X-RateLimit-Remaining headers.
    """
    response = client.get("/api/health")
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert int(response.headers["x-ratelimit-limit"]) >= 1
