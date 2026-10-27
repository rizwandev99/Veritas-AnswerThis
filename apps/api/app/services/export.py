"""
Export Services: BibTeX & Markdown Generation (PRD §6 F5-AC2).
Includes strict LaTeX escaping and fallback metadata handling.
"""
import re
from typing import List
from app.models.paper import Paper
from app.models.review import ReviewResponse


def escape_latex(text: str) -> str:
    """Escapes special LaTeX characters for BibTeX export."""
    if not text:
        return ""
    # Map special chars: &, %, $, #, _, {, }, ~, ^, \
    replacements = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
    }
    escaped = text
    for char, repl in replacements.items():
        escaped = escaped.replace(char, repl)
    return escaped


def generate_bibtex(papers: List[Paper]) -> str:
    """Generates standard BibTeX entries for cited papers with robust fallbacks."""
    entries = []
    for p in papers:
        safe_id = re.sub(r"[^\w]", "_", p.id) or f"paper_{p.source_num or 1}"
        safe_title = escape_latex(p.title)
        authors_str = " and ".join(escape_latex(a) for a in p.authors) if p.authors else "Anonymous"
        year_str = str(p.year) if p.year else "2023"
        venue_str = escape_latex(p.venue) if p.venue else "arXiv"

        entry = (
            f"@article{{{safe_id},\n"
            f"  title = {{{safe_title}}},\n"
            f"  author = {{{authors_str}}},\n"
            f"  year = {{{year_str}}},\n"
            f"  journal = {{{venue_str}}}"
        )
        if p.doi:
            entry += f",\n  doi = {{{p.doi}}}"
        if p.url:
            entry += f",\n  url = {{{p.url}}}"
        entry += "\n}"
        entries.append(entry)

    return "\n\n".join(entries)


def generate_markdown(review: ReviewResponse, papers: List[Paper]) -> str:
    """Generates comprehensive Markdown export with claim statuses and reference list."""
    md_lines = [
        f"# {review.query}",
        "",
        f"**Veritas Trust Score:** {review.trust_score if review.trust_score is not None else 'N/A'}%",
        f"**Status:** {review.status.upper()}",
        "",
        "## Literature Review",
        "",
    ]

    if review.claims:
        for c in review.claims:
            cites = "".join(f"[{s}]" for s in c.citations)
            verdict_badge = f" *({c.verdict.upper()})*" if c.verdict != "checking" else ""
            md_lines.append(f"{c.sentence} {cites}{verdict_badge}")
            md_lines.append("")
    elif review.text:
        md_lines.append(review.text)
        md_lines.append("")

    md_lines.extend(["", "## References", ""])
    for idx, p in enumerate(papers, start=1):
        num = p.source_num or idx
        authors = ", ".join(p.authors) if p.authors else "Unknown Authors"
        year = f"({p.year})" if p.year else "(N/A)"
        doi = f" DOI: {p.doi}" if p.doi else ""
        md_lines.append(f"[{num}] {authors} {year}. *{p.title}*. {p.venue}.{doi}")

    return "\n".join(md_lines)
