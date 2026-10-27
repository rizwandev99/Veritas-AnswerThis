"""
Deduplication and Query Normalization Services (PRD §6 F1-AC2, F1-AC7).
"""
import re
from typing import Dict, List
from app.models.paper import Paper


def normalize_query(query: str) -> str:
    """Normalizes queries by lowercasing, stripping punctuation, and collapsing whitespace."""
    text = query.lower().strip()
    text = re.sub(r"[?!.,;:'\"()]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_title(title: str) -> str:
    """Normalizes paper titles for deduplication comparison."""
    text = title.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """
    Deduplicates candidate papers:
    1. Deduplicate by DOI (case-insensitive).
    2. Deduplicate by normalized title.
    Preserves paper with highest citation count on collisions.
    """
    # Phase 1: DOI deduplication
    doi_map: Dict[str, Paper] = {}
    remaining_papers: List[Paper] = []

    for p in papers:
        if p.doi:
            clean_doi = p.doi.strip().lower()
            if clean_doi in doi_map:
                if p.citation_count > doi_map[clean_doi].citation_count:
                    doi_map[clean_doi] = p
            else:
                doi_map[clean_doi] = p
        else:
            remaining_papers.append(p)

    deduped_by_doi = list(doi_map.values()) + remaining_papers

    # Phase 2: Normalized title deduplication
    title_map: Dict[str, Paper] = {}
    for p in deduped_by_doi:
        norm_t = normalize_title(p.title)
        if norm_t in title_map:
            if p.citation_count > title_map[norm_t].citation_count:
                title_map[norm_t] = p
        else:
            title_map[norm_t] = p

    return list(title_map.values())
