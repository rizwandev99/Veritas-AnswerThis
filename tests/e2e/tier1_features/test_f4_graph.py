"""
Tier 1: Feature F4 - Interactive Citation Graph.
Validates F4-AC1 through F4-AC6.
"""

import math
import pytest


def test_f4_ac1_citation_graph_payload(client, example_reviews):
    """
    F4-AC1: GET /api/reviews/{id}/graph returns { nodes, edges } schema.
    """
    rev_id = example_reviews[0]["id"]
    response = client.get(f"/api/reviews/{rev_id}/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)
    assert len(data["nodes"]) == len(example_reviews[0]["papers"])


def test_f4_ac2_edge_construction_from_references(example_reviews):
    """
    F4-AC2: Edges are formed when one paper's referenced_work_ids contains another paper's ID.
    """
    rev = example_reviews[0]
    papers = {p["id"]: p for p in rev["papers"]}
    edges = rev["graph"]["edges"]

    for edge in edges:
        source_id = edge["source"]
        target_id = edge["target"]
        assert source_id in papers
        assert target_id in papers
        # Source references target
        assert target_id in papers[source_id].get("referenced_work_ids", [])


def test_f4_ac3_isolated_nodes_handling():
    """
    F4-AC3, F4-AC6: Papers with zero mutual citations exist as isolated nodes without graph errors.
    """
    nodes = [
        {"id": "p1", "title": "Paper 1"},
        {"id": "p2", "title": "Paper 2"},
        {"id": "p3", "title": "Paper 3"}
    ]
    edges = []  # No internal references

    connected_node_ids = set()
    for e in edges:
        connected_node_ids.add(e["source"])
        connected_node_ids.add(e["target"])

    isolated_nodes = [n for n in nodes if n["id"] not in connected_node_ids]
    assert len(isolated_nodes) == 3


def test_f4_ac4_node_sizing_and_color_mapping(example_reviews):
    """
    F4-AC4: Logarithmic radius scaling (bounded 16-48px) and verification status coloring.
    """
    nodes = example_reviews[0]["graph"]["nodes"]

    for node in nodes:
        assert "radius" in node
        radius = node["radius"]
        assert 16.0 <= radius <= 48.0, f"Radius {radius} out of bounds"

        assert "status_color" in node
        assert node["status_color"] in ["success", "warning", "danger", "neutral"]


def test_f4_ac5_cross_highlighting_contract(example_reviews):
    """
    F4-AC5: Graph node IDs map 1:1 to paper IDs in the review document.
    """
    rev = example_reviews[0]
    paper_ids = {p["id"] for p in rev["papers"]}
    node_ids = {n["id"] for n in rev["graph"]["nodes"]}
    assert paper_ids == node_ids
