"""
Review and Claim Data Models (PRD §6 F2, §8 Data Model).
"""
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=300, description="Research topic query")


class ClaimVerificationModel(BaseModel):
    claim_id: str
    source_num: int
    verdict: str  # supported, partial, unsupported, invalid_citation, unverifiable
    confidence: float
    evidence_quote: str
    reasoning: str


class ClaimModel(BaseModel):
    id: str
    sentence: str
    section: str = "Main"
    position: int
    citations: List[int] = Field(default_factory=list)
    invalid_citations: List[int] = Field(default_factory=list)
    is_uncited: bool = False
    verdict: str = "checking"  # checking, supported, partial, unsupported, invalid_citation, unverifiable
    confidence: float = 0.0
    verifications: List[ClaimVerificationModel] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    id: str
    query: str
    status: str  # pending, generating, verifying, complete, error
    text: Optional[str] = None
    claims: List[ClaimModel] = Field(default_factory=list)
    paper_ids: List[str] = Field(default_factory=list)
    trust_score: Optional[float] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    error_message: Optional[str] = None
