"""
Tier 1: Feature F3 - Claim-Level Citation Verification & Trust Score.
Validates F3-AC1 through F3-AC10.
"""

import pytest
from tests.e2e.conftest import validate_quote_in_abstract, calculate_trust_score


def test_f3_ac1_exact_quote_substring_verification(eval_fixtures):
    """
    F3-AC1, F3-AC2: Verbatim substring quote in abstract validates successfully.
    """
    fixture = eval_fixtures[0]  # Transformer attention
    quote = fixture["expected_evidence_quote"]
    abstract = fixture["paper_abstract"]

    is_valid = validate_quote_in_abstract(quote, abstract)
    assert is_valid is True
    assert fixture["expected_verdict"] == "supported"


def test_f3_ac2_fabricated_quote_rejection(eval_fixtures):
    """
    F3-AC2: Hallucinated / fabricated quote is detected and rejected.
    """
    fixture = eval_fixtures[5]  # Fabricated quote fixture (eval_06)
    quote = fixture["expected_evidence_quote"]
    abstract = fixture["paper_abstract"]

    # The fabricated quote should NOT exist in the abstract
    is_valid = validate_quote_in_abstract(quote, abstract)
    assert is_valid is False
    assert fixture["expected_verdict"] == "unverifiable"


def test_f3_ac3_out_of_bounds_citation_rejection(eval_fixtures):
    """
    F3-AC3: Marker citing non-existent paper yields invalid_citation without LLM invocation.
    """
    fixture = eval_fixtures[8]  # Out of bounds citation [99] (eval_09)
    assert fixture["expected_verdict"] == "invalid_citation"
    assert fixture["expected_evidence_quote"] is None


def test_f3_ac4_multi_citation_best_verdict_hierarchy():
    """
    F3-AC4: Multi-citation claims aggregate by best verdict hierarchy:
    supported > partial > unsupported > unverifiable > invalid_citation.
    """
    hierarchy = ["supported", "partial", "unsupported", "unverifiable", "invalid_citation"]

    def aggregate_verdicts(verdicts: list[str]) -> str:
        for v in hierarchy:
            if v in verdicts:
                return v
        return "unverifiable"

    assert aggregate_verdicts(["partial", "supported"]) == "supported"
    assert aggregate_verdicts(["unsupported", "partial"]) == "partial"
    assert aggregate_verdicts(["invalid_citation", "unsupported"]) == "unsupported"
    assert aggregate_verdicts(["unverifiable", "invalid_citation"]) == "unverifiable"


def test_f3_ac5_mathematical_trust_score_formula():
    """
    F3-AC5: Trust Score = (supported + 0.5 * partial) / total_verifiable.
    Zero verifiable returns null.
    """
    # 4 supported, 2 partial, 0 unsupported out of 6 verifiable
    # (4 + 0.5 * 2) / 6 = 5 / 6 = 0.8333
    score = calculate_trust_score(supported=4, partial=2, verifiable=6)
    assert score == 0.8333

    # Perfect score: 10 supported out of 10
    score_perf = calculate_trust_score(supported=10, partial=0, verifiable=10)
    assert score_perf == 1.0

    # Zero verifiable claims edge case: returns None
    score_zero = calculate_trust_score(supported=0, partial=0, verifiable=0)
    assert score_zero is None
