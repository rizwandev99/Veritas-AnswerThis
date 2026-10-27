"""
Paper and Chunk Domain Models (PRD §6 F1-AC1, §8 Data Model).
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str = Field(..., description="Unique paper identifier (e.g. OpenAlex work ID)")
    title: str = Field(..., description="Full paper title")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Host venue, journal, or repository")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    url: Optional[str] = Field(None, description="Direct URL to paper or DOI landing page")
    abstract: str = Field(..., description="Reconstructed or retrieved abstract text")
    citation_count: int = Field(0, description="Reported citation count")
    referenced_work_ids: List[str] = Field(default_factory=list, description="IDs of cited works")
    similarity_score: Optional[float] = Field(None, description="Semantic similarity score to query")
    source_num: Optional[int] = Field(None, description="Numbered source index in review [1..N]")


class PaperChunk(BaseModel):
    chunk_id: str
    paper_id: str
    chunk_index: int
    text: str
    start_char: int
    end_char: int


class PaperSearchResponse(BaseModel):
    query: str
    count: int
    papers: List[Paper]
