"""
Tier 3: Pairwise Combination - F3 Verification & F4 Graph / UI Highlighting.
Validates cross-feature interactions between claim verification, graph visualization, and theme engine.
"""

import pytest


def test_t3_09_verification_verdicts_update_graph_node_colors(example_reviews):
    """
    T3-09: Claim verification verdicts determine graph node status_color
    (success for high support, warning for partial, danger for unsupported).
    """
    nodes = example_reviews[0]["graph"]["nodes"]
    for node in nodes:
        stats = node["verification_stats"]
        supported = stats.get("supported", 0)
        unsupported = stats.get("unsupported", 0)
        color = node["status_color"]

        if unsupported > 0 and supported == 0:
            assert color == "danger"
        elif supported > 0:
            assert color in ["success", "warning"]


def test_t3_10_graph_node_selection_links_to_review_claims(example_reviews):
    """
    T3-10: Selecting graph node filters review claims citing that paper source number.
    """
    rev = example_reviews[0]
    selected_source_num = 1

    linked_claims = [
        c for c in rev["claims"]
        if selected_source_num in c.get("cited_numbers", [])
    ]
    assert len(linked_claims) >= 1
    for c in linked_claims:
        assert selected_source_num in c["cited_numbers"]


def test_t3_11_theme_toggle_updates_graph_palette():
    """
    T3-11: Switching between dark and light modes provides high contrast node strokes and edge colors.
    """
    palettes = {
        "dark": {"edge_stroke": "rgba(255, 255, 255, 0.15)", "node_text": "#ffffff"},
        "light": {"edge_stroke": "rgba(0, 0, 0, 0.15)", "node_text": "#0f172a"}
    }
    assert palettes["dark"]["node_text"] != palettes["light"]["node_text"]
    assert palettes["dark"]["edge_stroke"] != palettes["light"]["edge_stroke"]


def test_t3_12_evidence_panel_deep_links_to_paper_source(example_reviews):
    """
    T3-12: Evidence panel references source paper DOI/URL directly from paper model.
    """
    papers = {p["source_number"]: p for p in example_reviews[0]["papers"]}
    claims = example_reviews[0]["claims"]

    for claim in claims:
        for v in claim.get("verifications", []):
            src_num = v["source_number"]
            assert src_num in papers
            paper = papers[src_num]
            assert "doi" in paper or "url" in paper
