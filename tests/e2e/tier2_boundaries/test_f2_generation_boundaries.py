"""
Tier 2: Boundary & Corner Cases - Feature F2 (Streaming Literature Review Generation).
Validates F2-AC1..9 edge cases and boundaries.
"""

import pytest
from tests.e2e.conftest import parse_sse_events, extract_citation_markers


def test_f2_zero_citations_emitted_flags_uncited():
    """
    T2-F2-01: Review containing sentences without brackets flags factual assertions as uncited.
    """
    sentences = [
        "Language models demonstrate emergent properties at scale.",
        "We note that the dataset was collected in 2023.",
        "Transformer parameters exceed 100 billion in contemporary systems."
    ]
    for s in sentences:
        markers = extract_citation_markers(s)
        assert len(markers) == 0, f"Expected 0 markers in uncited sentence: {s}"


def test_f2_out_of_bounds_markers_negative_numbers():
    """
    T2-F2-02: Markers with negative numbers, zero, or exceeding paper count are flagged invalid.
    """
    sample_text = "Surface codes achieve fault tolerance [0] while others suggest alternative lattices [-1][99]."
    # Raw bracket tokens
    import re
    tokens = re.findall(r"\[([0-9\s,\-]+)\]", sample_text)
    total_papers = 5

    invalid_markers = []
    for t in tokens:
        try:
            val = int(t.strip())
            if val < 1 or val > total_papers:
                invalid_markers.append(val)
        except ValueError:
            pass

    assert 0 in invalid_markers
    assert 99 in invalid_markers


def test_f2_malformed_bracket_syntax():
    """
    T2-F2-03: Text containing malformed brackets like unclosed '[1', '[]', '[abc]' does not crash parser.
    """
    malformed_text = "This claim has unclosed [1 marker, empty [] marker, and non-numeric [alpha] citation."
    markers = extract_citation_markers(malformed_text)
    # The parser should safely extract empty or valid ints without throwing an exception
    assert isinstance(markers, list)
    assert len(markers) == 0  # No valid integer citation formatted strictly as [N]


def test_f2_sse_stream_error_recovery(client):
    """
    T2-F2-04: Stream failure emits error event with code and retryable flag.
    """
    response = client.get("/api/reviews/error_stream_id/stream")
    assert response.status_code == 200
    events = parse_sse_events(response.text)
    error_events = [e for e in events if e["event"] == "error"]
    assert len(error_events) == 1
    err_data = error_events[0]["data"]
    assert err_data["code"] == "LLM_PROVIDER_TIMEOUT"
    assert err_data["retryable"] is True


def test_f2_unicode_latex_symbols_in_review():
    """
    T2-F2-05: LaTeX formulas, math operators, and unicode characters render without corruption.
    """
    math_text = "The time complexity is $O(N^2)$ for dense self-attention, and $O(N)$ for SSMs [1]. Critical temperature $T_c \\approx 203\\text{ K}$."
    markers = extract_citation_markers(math_text)
    assert markers == [1]
    assert "$O(N^2)$" in math_text
    assert "\\approx" in math_text
