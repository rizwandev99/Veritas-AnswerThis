"""
Paper Search & Discovery API (PRD §6 F1, §9 API Specification).
"""
import time
from typing import Dict, List, Optional
from fastapi import APIRouter, Query, status
from app.models.paper import Paper, PaperSearchResponse
from app.services.paper_source import OpenAlexSource
from app.services.dedup import normalize_query
from app.core.config import settings

router = APIRouter(prefix="/papers", tags=["Papers"])
paper_source = OpenAlexSource()

# 24-hour query cache: { normalized_query: (timestamp, List[Paper]) }
_query_cache: Dict[str, tuple[float, List[Paper]]] = {}
CACHE_TTL_SECONDS = 86400  # 24 hours


@router.get("/search", response_model=PaperSearchResponse)
async def search_papers(
    query: str = Query(..., min_length=2, max_length=300, description="Research query or keywords"),
    limit: int = Query(default=12, ge=1, le=20, description="Max candidate papers to retrieve"),
):
    """
    Retrieves and ranks academic papers from OpenAlex with inverted-index abstract reconstruction.
    Deduplicates by DOI and title, and caches results for 24 hours.
    """
    norm_q = normalize_query(query)
    now = time.time()

    # Check 24-hour cache
    if norm_q in _query_cache:
        cached_time, cached_papers = _query_cache[norm_q]
        if now - cached_time < CACHE_TTL_SECONDS:
            return PaperSearchResponse(
                query=query,
                count=len(cached_papers[:limit]),
                papers=cached_papers[:limit],
            )

    papers = await paper_source.search_papers(query=query, limit=limit)

    # Assign source numbers [1..N]
    for idx, p in enumerate(papers, start=1):
        p.source_num = idx

    # Update cache
    _query_cache[norm_q] = (now, papers)

    return PaperSearchResponse(
        query=query,
        count=len(papers),
        papers=papers,
    )
