"""
Citation Network Graph Builder (PRD §6 F4).
Constructs node-link topology from paper referenced_work_ids and verification stats.
"""
import math
from typing import Any, Dict, List
from app.models.paper import Paper
from app.models.review import ClaimModel


def compute_node_radius(citation_count: int, min_r: int = 16, max_r: int = 48) -> int:
    """Computes bounded logarithmic radius for citation volume."""
    if citation_count <= 0:
        return min_r
    # Log scaling
    log_val = math.log10(citation_count + 1)
    # 0 to 5 on log10 scale
    norm = min(1.0, max(0.0, log_val / 5.0))
    return int(min_r + norm * (max_r - min_r))


def compute_node_color(support_rate: float) -> str:
    """Colors nodes based on claim verification support share."""
    if support_rate >= 0.8:
        return "var(--success)"
    elif support_rate >= 0.5:
        return "var(--warning)"
    elif support_rate > 0.0:
        return "var(--danger)"
    return "var(--text-tertiary)"


def build_citation_graph(papers: List[Paper], claims: List[ClaimModel]) -> Dict[str, Any]:
    """
    Constructs { nodes, edges } network topology:
    - Nodes for each paper with computed size and verification status
    - Edges where paper A's referenced_work_ids includes paper B's id
    """
    paper_ids = {p.id: p for p in papers}

    # Calculate claim support rate per paper
    paper_claim_stats: Dict[int, Dict[str, int]] = {p.source_num or idx: {"total": 0, "supported": 0} for idx, p in enumerate(papers, start=1)}

    for claim in claims:
        for src_num in claim.citations:
            if src_num in paper_claim_stats:
                paper_claim_stats[src_num]["total"] += 1
                if claim.verdict == "supported":
                    paper_claim_stats[src_num]["supported"] += 1

    nodes = []
    for idx, p in enumerate(papers, start=1):
        src_num = p.source_num or idx
        stats = paper_claim_stats.get(src_num, {"total": 0, "supported": 0})
        total = stats["total"]
        supported = stats["supported"]
        support_rate = round(supported / total, 2) if total > 0 else 1.0

        nodes.append({
            "id": p.id,
            "source_num": src_num,
            "title": p.title,
            "year": p.year,
            "citation_count": p.citation_count,
            "support_rate": support_rate,
            "radius": compute_node_radius(p.citation_count),
            "color": compute_node_color(support_rate),
        })

    # Construct edges: source -> target
    edges = []
    for p in papers:
        for ref_id in p.referenced_work_ids:
            if ref_id in paper_ids and ref_id != p.id:
                edges.append({
                    "source": p.id,
                    "target": ref_id,
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }
