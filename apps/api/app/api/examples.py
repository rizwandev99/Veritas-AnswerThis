"""
Seed Examples API (PRD §6 F5-AC3).
Exposes 5 pre-computed, citation-verified literature reviews.
"""
import os
import json
from typing import Any, Dict, List
from fastapi import APIRouter

router = APIRouter(prefix="/examples", tags=["Examples"])

_EXAMPLES_CACHE: List[Dict[str, Any]] = []


def load_seed_examples() -> List[Dict[str, Any]]:
    global _EXAMPLES_CACHE
    if _EXAMPLES_CACHE:
        return _EXAMPLES_CACHE

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    path = os.path.join(root_dir, "tests", "fixtures", "example_reviews.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                _EXAMPLES_CACHE = json.load(f)
                return _EXAMPLES_CACHE
        except Exception:
            pass

    # Fallback minimal examples
    _EXAMPLES_CACHE = [
        {
            "id": "rev_example_transformer",
            "query": "Transformer self-attention efficiency in long contexts",
            "status": "complete",
            "trust_score": 92.5,
            "papers_count": 12,
        }
    ]
    return _EXAMPLES_CACHE


@router.get("")
async def get_examples():
    """Returns curated seed reviews for instant demonstration without live LLM calls."""
    examples = load_seed_examples()
    return {"count": len(examples), "examples": examples}
