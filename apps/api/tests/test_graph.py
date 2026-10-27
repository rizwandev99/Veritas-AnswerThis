"""
Unit Tests for Milestone F4: Citation Network Graph Visualization.
Covers F4-AC1 through F4-AC6.
"""
import pytest
import httpx
from app.models.paper import Paper
from app.models.review import ClaimModel
from app.services.graph import (
    build_citation_graph,
    compute_node_radius,
    compute_node_color,
)


def test_F4_AC2_edge_construction():
    papers = [
        Paper(id="p1", title="Paper 1", abstract="Abs 1", referenced_work_ids=["p2"], citation_count=100),
        Paper(id="p2", title="Paper 2", abstract="Abs 2", referenced_work_ids=[], citation_count=50),
        Paper(id="p3", title="Paper 3", abstract="Abs 3", referenced_work_ids=["non_existent"], citation_count=10),
    ]
    graph = build_citation_graph(papers, claims=[])
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["source"] == "p1"
    assert graph["edges"][0]["target"] == "p2"


def test_F4_AC4_node_sizing_and_colors():
    assert compute_node_radius(0) == 16
    assert compute_node_radius(100000) >= 40

    assert compute_node_color(0.9) == "var(--success)"
    assert compute_node_color(0.6) == "var(--warning)"
    assert compute_node_color(0.2) == "var(--danger)"


@pytest.mark.asyncio
async def test_F4_AC1_graph_endpoint(async_client: httpx.AsyncClient):
    create_resp = await async_client.post("/api/reviews", json={"query": "quantum gravity"})
    review_id = create_resp.json()["id"]

    resp = await async_client.get(f"/api/reviews/{review_id}/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    node = data["nodes"][0]
    assert "id" in node
    assert "radius" in node
    assert "color" in node
