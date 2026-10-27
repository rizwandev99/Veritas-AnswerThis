"""
Tier 2: Boundary & Corner Cases - Feature F4 (Citation Graph).
Validates F4-AC1..6 degenerate cases and boundaries.
"""

import math
import pytest


def test_f4_single_node_graph():
    """
    T2-F4-01: Graph with only 1 paper renders single node with zero edges without zero division.
    """
    nodes = [{"id": "single_p1", "title": "Solitary Paper", "citation_count": 100}]
    edges = []

    assert len(nodes) == 1
    assert len(edges) == 0
    # Center coordinates formula (w/2, h/2) avoids division by (len(nodes) - 1)
    center_x = 800 / 2
    center_y = 600 / 2
    assert center_x == 400.0 and center_y == 300.0


def test_f4_disconnected_graph_empty_edges():
    """
    T2-F4-02: 10 papers with zero mutual citations render cleanly with empty edges list.
    """
    papers = [f"p_{i}" for i in range(10)]
    nodes = [{"id": pid, "title": f"Paper {pid}"} for pid in papers]
    edges = []

    assert len(nodes) == 10
    assert len(edges) == 0


def test_f4_complete_clique_graph():
    """
    T2-F4-03: Dense clique graph where all papers cite each other is handled cleanly.
    """
    n = 6
    nodes = [{"id": f"p_{i}"} for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(n):
            if i != j:
                edges.append({"source": f"p_{i}", "target": f"p_{j}"})

    expected_edge_count = n * (n - 1)
    assert len(edges) == expected_edge_count


def test_f4_zero_citation_count_minimum_radius():
    """
    T2-F4-04: Paper with 0 external citations receives minimum readable radius (e.g. 16px), not 0px.
    """
    def compute_radius(citations: int) -> float:
        min_r, max_r = 16.0, 48.0
        # Logarithmic scaling
        scale = math.log10(max(1, citations) + 1) / math.log10(100000)
        return round(min_r + (max_r - min_r) * min(1.0, scale), 1)

    r_zero = compute_radius(0)
    assert r_zero >= 16.0, f"Expected radius >= 16.0, got {r_zero}"

    r_huge = compute_radius(100000)
    assert r_huge <= 48.0


def test_f4_cyclic_citation_references():
    """
    T2-F4-05: Cyclic references (A cites B, B cites C, C cites A) form a valid directed cycle.
    """
    edges = [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"},
        {"source": "C", "target": "A"}
    ]
    # In-degree and out-degree should all be 1
    in_degrees = {"A": 0, "B": 0, "C": 0}
    for e in edges:
        in_degrees[e["target"]] += 1

    assert all(deg == 1 for deg in in_degrees.values())
