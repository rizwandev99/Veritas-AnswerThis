"""
Unit Tests for Milestone F3: Claim-Level Citation Verification & Trust Score Engine.
Covers F3-AC1 through F3-AC10.
"""
import pytest
from app.models.paper import Paper
from app.models.review import ClaimModel, ClaimVerificationModel
from app.services.verifier import (
    validate_quote_in_abstract,
    calculate_trust_score,
    aggregate_verdicts,
    claim_verifier,
)


def test_F3_AC2_validate_quote_in_abstract():
    abstract = "The Transformer is based solely on attention mechanisms, dispensing with recurrence entirely."
    # Valid exact substring
    assert validate_quote_in_abstract("dispensing with recurrence entirely", abstract) is True
    # Normalized whitespace match
    assert validate_quote_in_abstract("dispensing   with   recurrence", abstract) is True
    # Fabricated quote rejection
    assert validate_quote_in_abstract("dispensing with all hardware latencies", abstract) is False


def test_F3_AC5_calculate_trust_score():
    # 4 supported, 2 partial, 6 total: (4 + 0.5 * 2) / 6 = 5 / 6 = 0.8333
    score = calculate_trust_score(supported=4, partial=2, verifiable=6)
    assert score == 0.8333

    # Zero verifiable claims must return None
    assert calculate_trust_score(supported=0, partial=0, verifiable=0) is None


def test_F3_AC4_multi_citation_best_verdict_hierarchy():
    verifications = [
        ClaimVerificationModel(claim_id="c1", source_num=1, verdict="unsupported", confidence=0.8, evidence_quote="", reasoning=""),
        ClaimVerificationModel(claim_id="c1", source_num=2, verdict="supported", confidence=0.95, evidence_quote="quote", reasoning=""),
    ]
    best_verdict, conf = aggregate_verdicts(verifications)
    assert best_verdict == "supported"
    assert conf == 0.95


@pytest.mark.asyncio
async def test_F3_AC3_invalid_source_number():
    claim = ClaimModel(id="c_inv", sentence="Some claim", position=0, citations=[99], invalid_citations=[99])
    verified = await claim_verifier.verify_claim(claim, papers=[], max_source_num=5)
    assert verified.verdict == "invalid_citation"


@pytest.mark.asyncio
async def test_F3_AC6_verify_claim_grounding():
    paper = Paper(
        id="p1",
        title="Longformer",
        abstract="We introduce the Longformer with an attention mechanism that scales linearly with sequence length.",
        citation_count=50,
        source_num=1,
    )
    claim = ClaimModel(
        id="c1",
        sentence="Longformer attention scales linearly with sequence length.",
        position=0,
        citations=[1],
    )
    verified = await claim_verifier.verify_claim(claim, papers=[paper], max_source_num=1)
    assert verified.verdict in ("supported", "partial")
    assert len(verified.verifications) == 1
    assert verified.verifications[0].source_num == 1
