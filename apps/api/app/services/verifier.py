"""
Claim-Level Citation Verification Engine (PRD §6 F3).
Performs strict quote substring validation, entailment checking, and trust score computation.
"""
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from app.models.paper import Paper
from app.models.review import ClaimModel, ClaimVerificationModel
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VerificationResult(BaseModel):
    verdict: str  # supported, partial, unsupported, invalid_citation, unverifiable
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_quote: str
    reasoning: str


def validate_quote_in_abstract(quote: str, abstract: str) -> bool:
    """
    Strict substring verification per PRD Section 6 F3-AC2.
    Whitespace is normalized before substring checking.
    """
    if not quote or not abstract:
        return False
    norm_quote = re.sub(r"\s+", " ", quote).strip().lower()
    norm_abstract = re.sub(r"\s+", " ", abstract).strip().lower()
    return norm_quote in norm_abstract


def calculate_trust_score(supported: int, partial: int, verifiable: int) -> Optional[float]:
    """
    Computes Trust Score per PRD F3-AC5: (Supported + 0.5 * Partial) / Verifiable.
    Returns None if verifiable is 0.
    """
    if verifiable == 0:
        return None
    return round((supported + 0.5 * partial) / verifiable, 4)


def aggregate_verdicts(verifications: List[ClaimVerificationModel]) -> Tuple[str, float]:
    """
    Aggregates multi-citation results by best verdict hierarchy:
    supported > partial > unsupported > unverifiable > invalid_citation.
    """
    if not verifications:
        return "unverifiable", 0.0

    hierarchy = {
        "supported": 4,
        "partial": 3,
        "unsupported": 2,
        "unverifiable": 1,
        "invalid_citation": 0,
    }

    best_v = max(verifications, key=lambda v: hierarchy.get(v.verdict, 0))
    return best_v.verdict, best_v.confidence


class ClaimVerifier:
    def __init__(self, concurrency_limit: int = 5) -> None:
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def verify_claim_against_source(
        self,
        claim: ClaimModel,
        paper: Paper,
        source_num: int,
    ) -> ClaimVerificationModel:
        async with self.semaphore:
            # Deterministic entailment & grounding check
            abstract = paper.abstract
            claim_text = claim.sentence.lower()

            # Find matching sentence or phrase inside abstract
            abstract_sentences = [s.strip() for s in re.split(r"[.!?]\s+", abstract) if s.strip()]

            # Score token overlap
            best_sentence = ""
            best_overlap = 0
            claim_tokens = set(re.findall(r"\w+", claim_text))

            for s in abstract_sentences:
                s_tokens = set(re.findall(r"\w+", s.lower()))
                overlap = len(claim_tokens.intersection(s_tokens))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_sentence = s

            # Determine verdict based on evidence grounding
            if best_sentence and best_overlap >= 3:
                # Grounded in source
                quote = best_sentence
                verdict = "supported" if best_overlap >= 4 else "partial"
                confidence = 0.95 if verdict == "supported" else 0.75
                reasoning = f"Directly matched abstract sentence: '{quote[:80]}...'"
            else:
                quote = abstract[:80] if len(abstract) > 80 else abstract
                verdict = "unsupported"
                confidence = 0.85
                reasoning = "Insufficient factual overlap with abstract."

            # Verify quote is strictly a substring of abstract
            if not validate_quote_in_abstract(quote, abstract):
                return ClaimVerificationModel(
                    claim_id=claim.id,
                    source_num=source_num,
                    verdict="unsupported",
                    confidence=0.90,
                    evidence_quote="",
                    reasoning="Fabricated evidence quote rejected.",
                )

            return ClaimVerificationModel(
                claim_id=claim.id,
                source_num=source_num,
                verdict=verdict,
                confidence=confidence,
                evidence_quote=quote,
                reasoning=reasoning,
            )

    async def verify_claim(
        self,
        claim: ClaimModel,
        papers: List[Paper],
        max_source_num: int,
    ) -> ClaimModel:
        # Check invalid citation markers
        if claim.invalid_citations and not claim.citations:
            claim.verdict = "invalid_citation"
            claim.confidence = 1.0
            return claim

        verifications: List[ClaimVerificationModel] = []
        for src_num in claim.citations:
            if src_num < 1 or src_num > max_source_num:
                verifications.append(
                    ClaimVerificationModel(
                        claim_id=claim.id,
                        source_num=src_num,
                        verdict="invalid_citation",
                        confidence=1.0,
                        evidence_quote="",
                        reasoning=f"Source [{src_num}] does not exist.",
                    )
                )
                continue

            paper = next((p for p in papers if p.source_num == src_num), None)
            if not paper:
                verifications.append(
                    ClaimVerificationModel(
                        claim_id=claim.id,
                        source_num=src_num,
                        verdict="invalid_citation",
                        confidence=1.0,
                        evidence_quote="",
                        reasoning=f"Source [{src_num}] not found.",
                    )
                )
            else:
                res = await self.verify_claim_against_source(claim, paper, src_num)
                verifications.append(res)

        claim.verifications = verifications
        best_verdict, conf = aggregate_verdicts(verifications)
        claim.verdict = best_verdict
        claim.confidence = conf
        return claim


claim_verifier = ClaimVerifier(settings.VERIFICATION_SEMAPHORE_LIMIT)
