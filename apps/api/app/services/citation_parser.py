"""
Citation Parser & Sentence Segmentation Engine (PRD §6 F2-AC3, F2-AC4, F2-AC5).
Extracts citation markers ([1], [1, 2], [1-3]), validates bounds, segments into claims.
"""
import re
from typing import List, Tuple
from app.models.review import ClaimModel


def extract_citation_markers(text: str) -> List[int]:
    """
    Extract citation marker integers from text supporting [1], [1][2], [1, 2], [1-3].
    PRD Section 6 F2-AC3.
    """
    markers = set()
    bracket_matches = re.findall(r"\[([0-9\s,\-]+)\]", text)
    for match in bracket_matches:
        range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", match.strip())
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            if start <= end:
                for n in range(start, end + 1):
                    markers.add(n)
            continue
        tokens = re.split(r"[,\s]+", match.strip())
        for token in tokens:
            if token.isdigit():
                markers.add(int(token))
    return sorted(list(markers))


def segment_into_sentences(text: str) -> List[str]:
    """Splits body text into sentences preserving citations."""
    sentence_end = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
    raw_sentences = sentence_end.split(text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]


def segment_into_claims(text: str, max_source_num: int) -> List[ClaimModel]:
    """
    Segments full review text into claims, validating citation numbers against 1..max_source_num.
    Flags uncited factual statements and out-of-bounds markers.
    """
    sentences = segment_into_sentences(text)
    claims: List[ClaimModel] = []

    for idx, sentence in enumerate(sentences):
        # Extract markers
        raw_markers = extract_citation_markers(sentence)

        valid_citations: List[int] = []
        invalid_citations: List[int] = []

        for m in raw_markers:
            if 1 <= m <= max_source_num:
                valid_citations.append(m)
            else:
                invalid_citations.append(m)

        # Remove bracket markers to clean sentence text for evaluation
        clean_text = re.sub(r"\[[0-9\s,\-]+\]", "", sentence).strip()

        # Factual uncited check (PRD F2-AC5): sentence > 25 chars, no citations, factual structure
        is_uncited = False
        if not raw_markers:
            is_factual = len(clean_text) > 25 and not clean_text.endswith("?")
            if is_factual:
                is_uncited = True

        claims.append(
            ClaimModel(
                id=f"claim_{idx + 1}",
                sentence=clean_text,
                position=idx,
                citations=valid_citations,
                invalid_citations=invalid_citations,
                is_uncited=is_uncited,
                verdict="invalid_citation" if invalid_citations and not valid_citations else "checking",
            )
        )

    return claims
