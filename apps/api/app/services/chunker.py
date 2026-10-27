"""
Deterministic Sentence-Aware Text Chunker (PRD §6 F1-AC8).
"""
import re
from typing import List
from app.models.paper import PaperChunk


def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences deterministically without destroying spacing."""
    # Split on periods/exclamations/questions followed by space and capital letter or end of string
    sentence_end = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
    raw_sentences = sentence_end.split(text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]


def chunk_abstract(
    paper_id: str,
    abstract: str,
    window_sentences: int = 3,
    overlap_sentences: int = 1,
) -> List[PaperChunk]:
    """
    Chunks an abstract into overlapping sentence windows.
    Generates deterministic chunk IDs: {paper_id}_c{chunk_index}.
    """
    sentences = split_into_sentences(abstract)
    if not sentences:
        return []

    chunks: List[PaperChunk] = []
    step = max(1, window_sentences - overlap_sentences)
    chunk_idx = 0

    for i in range(0, len(sentences), step):
        window = sentences[i : i + window_sentences]
        if not window:
            break
        chunk_text = " ".join(window)

        # Compute char offsets within abstract
        start_char = abstract.find(window[0])
        if start_char == -1:
            start_char = 0
        end_char = start_char + len(chunk_text)

        chunks.append(
            PaperChunk(
                chunk_id=f"{paper_id}_c{chunk_idx}",
                paper_id=paper_id,
                chunk_index=chunk_idx,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char,
            )
        )
        chunk_idx += 1
        if i + window_sentences >= len(sentences):
            break

    return chunks
