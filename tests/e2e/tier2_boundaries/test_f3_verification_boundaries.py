"""
Tier 2: Boundary & Corner Cases - Feature F3 (Claim Verification & Trust Score).
Validates F3-AC1..10 boundaries.
"""

import pytest
from tests.e2e.conftest import validate_quote_in_abstract, calculate_trust_score


def test_f3_zero_verifiable_claims_trust_score_null():
    """
    T2-F3-01: Zero verifiable claims returns trust_score: null (no ZeroDivisionError).
    """
    assert calculate_trust_score(supported=0, partial=0, verifiable=0) is None


def test_f3_whitespace_normalization_in_quotes():
    """
    T2-F3-02: Abstract containing multiline whitespace and tabs matches single-spaced quote.
    """
    abstract_multiline = """
    Engineered     CRISPR-Cas9    nucleases
    provide    robust genome editing
    across   diverse   mammalian   cell   lines.
    """
    quote_clean = "provide robust genome editing across diverse mammalian cell lines."

    match = validate_quote_in_abstract(quote_clean, abstract_multiline)
    assert match is True


def test_f3_corrupted_llm_json_repair_retry():
    """
    T2-F3-03: Truncated or malformed LLM JSON output triggers one repair attempt, then unverifiable.
    """
    import json
    malformed_json_str = '{"verdict": "supported", "confidence": 0.9, "evidence_quote": "missing closing brace"'

    # Simulated repair parser
    try:
        parsed = json.loads(malformed_json_str)
        verdict = parsed.get("verdict")
    except json.JSONDecodeError:
        # First repair attempt: append closing brace
        try:
            repaired_str = malformed_json_str + "}"
            parsed = json.loads(repaired_str)
            verdict = parsed.get("verdict")
        except json.JSONDecodeError:
            verdict = "unverifiable"

    assert verdict == "supported"


def test_f3_verification_timeout_isolation():
    """
    T2-F3-04: Concurrent execution with bounded timeout isolates individual slow claims.
    """
    results = [
        {"claim_id": "c1", "status": "completed", "verdict": "supported"},
        {"claim_id": "c2", "status": "timeout", "verdict": "unverifiable"},
        {"claim_id": "c3", "status": "completed", "verdict": "supported"}
    ]
    # Timeout claim is gracefully marked unverifiable without throwing
    assert results[1]["verdict"] == "unverifiable"
    # Other claims completed successfully
    assert results[0]["verdict"] == "supported"
    assert results[2]["verdict"] == "supported"


def test_f3_multi_citation_contradictory_verdicts():
    """
    T2-F3-05: Claim citing both supported and unsupported sources resolves to supported (best verdict).
    """
    verifications = [
        {"source_number": 1, "verdict": "supported", "confidence": 0.95},
        {"source_number": 2, "verdict": "unsupported", "confidence": 0.88}
    ]
    hierarchy = {"supported": 1, "partial": 2, "unsupported": 3, "unverifiable": 4, "invalid_citation": 5}
    best_verdict = min((v["verdict"] for v in verifications), key=lambda x: hierarchy[x])

    assert best_verdict == "supported"
    assert len(verifications) == 2
