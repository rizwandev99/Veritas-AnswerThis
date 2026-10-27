import os
import sys
import json
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, HTTPException, Request, Response, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.testclient import TestClient
import httpx

# Paths to fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures")
EVAL_FIXTURES_PATH = os.path.join(FIXTURES_DIR, "eval_fixtures.json")
EXAMPLE_REVIEWS_PATH = os.path.join(FIXTURES_DIR, "example_reviews.json")


def load_json_fixture(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Helper Domain Functions strictly matching PRD ---

def normalize_query(query: str) -> str:
    """Normalize query according to PRD Section 2.4.1."""
    text = query.lower().strip()
    text = re.sub(r"[?!.,;:'\"()]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_trust_score(supported: int, partial: int, verifiable: int) -> Optional[float]:
    """Calculate trust score per PRD Section 6 F3-AC5: (S + 0.5 * P) / V, null if V=0."""
    if verifiable == 0:
        return None
    return round((supported + 0.5 * partial) / verifiable, 4)


def extract_citation_markers(text: str) -> List[int]:
    """
    Extract citation marker integers from text supporting [1], [1][2], [1, 2], [1-3].
    PRD Section 6 F2-AC3.
    """
    markers = set()
    # Matches patterns inside brackets like [1], [1, 2, 3], [1-3]
    bracket_matches = re.findall(r"\[([0-9\s,\-]+)\]", text)
    for match in bracket_matches:
        # Check for range: e.g. 1-3
        range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", match.strip())
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            if start <= end:
                for n in range(start, end + 1):
                    markers.add(n)
            continue
        # Check for comma-separated or space-separated: e.g. 1, 2 or 1 2
        tokens = re.split(r"[,\s]+", match.strip())
        for token in tokens:
            if token.isdigit():
                markers.add(int(token))
    return sorted(list(markers))


def validate_quote_in_abstract(quote: str, abstract: str) -> bool:
    """
    Strict substring verification per PRD Section 6 F3-AC2.
    Whitespace is normalized to single spaces before substring check.
    """
    if not quote or not abstract:
        return False
    norm_quote = re.sub(r"\s+", " ", quote).strip().lower()
    norm_abstract = re.sub(r"\s+", " ", abstract).strip().lower()
    return norm_quote in norm_abstract


def parse_sse_events(sse_text: str) -> List[Dict[str, Any]]:
    """Parse raw SSE text into structured events."""
    events = []
    blocks = sse_text.strip().split("\n\n")
    for block in blocks:
        if not block.strip():
            continue
        event_type = "message"
        data_str = ""
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("event:"):
                event_type = line[len("event:"):].strip()
            elif line.startswith("data:"):
                data_str = line[len("data:"):].strip()
        if data_str:
            try:
                parsed_data = json.loads(data_str)
            except Exception:
                parsed_data = data_str
            events.append({"event": event_type, "data": parsed_data})
    return events


# --- In-Memory Mock Server implementing 100% PRD API Contracts ---

def create_mock_veritas_app() -> FastAPI:
    app = FastAPI(title="Veritas Mock Backend", version="1.0.0")

    # In-memory stores
    eval_fixtures = load_json_fixture(EVAL_FIXTURES_PATH)
    example_reviews = load_json_fixture(EXAMPLE_REVIEWS_PATH)

    reviews_db: Dict[str, Dict[str, Any]] = {rev["id"]: rev for rev in example_reviews}
    query_cache_db: Dict[str, Dict[str, Any]] = {
        normalize_query(rev["query"]): {"review_id": rev["id"], "created_at": time.time()}
        for rev in example_reviews
    }
    rate_limits_db: Dict[str, List[float]] = {}
    RATE_LIMIT_PER_HOUR = 5
    RATE_LIMIT_WINDOW = 3600

    def check_rate_limit(request: Request) -> Dict[str, int]:
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = hashlib.sha256(f"{client_ip}_salt_veritas".encode()).hexdigest()
        now = time.time()
        timestamps = rate_limits_db.get(key, [])
        # Evict old timestamps
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        rate_limits_db[key] = timestamps
        limit = RATE_LIMIT_PER_HOUR
        remaining = max(0, limit - len(timestamps))
        reset_time = int(timestamps[0] + RATE_LIMIT_WINDOW) if timestamps else int(now + RATE_LIMIT_WINDOW)
        return {
            "key": key,
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "count": len(timestamps)
        }

    @app.middleware("http")
    async def add_rate_limit_and_cors_headers(request: Request, call_next):
        info = check_rate_limit(request)
        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response

    @app.get("/api/health")
    def health_check():
        """PRD Section 9: GET /api/health."""
        return {
            "status": "healthy",
            "database": "connected",
            "vector_store": "pgvector",
            "version": "1.0.0"
        }

    @app.get("/api/papers/search")
    def search_papers(query: str = Query(..., min_length=1), limit: int = 15):
        """PRD Section 6 F1 & Section 9: Paper search endpoint."""
        stripped = query.strip()
        if not stripped:
            raise HTTPException(status_code=422, detail="Query cannot be empty or pure whitespace.")
        if len(query) > 300:
            raise HTTPException(status_code=422, detail="Query exceeds maximum 300 characters.")

        if "zero_results_marker" in stripped:
            return {"papers": [], "total": 0}
        if "null_abstracts_marker" in stripped:
            # Simulate papers that all lack abstracts
            return {
                "papers": [
                    {"id": "p_null_1", "title": "Paper Without Abstract", "abstract": None, "authors": ["A"]},
                    {"id": "p_null_2", "title": "Paper With Empty Abstract", "abstract": "", "authors": ["B"]}
                ],
                "total": 2
            }

        # Return mock papers from first seed review
        sample_papers = example_reviews[0]["papers"][:limit]
        return {
            "papers": sample_papers,
            "total": len(sample_papers)
        }

    @app.post("/api/reviews", status_code=201)
    def create_review(payload: Dict[str, Any], request: Request, response: Response):
        """PRD Section 6 F2-AC1, F5-AC3, F5-AC6: Review creation."""
        query = payload.get("query", "")
        if not query or len(query.strip()) < 3:
            raise HTTPException(status_code=422, detail="Query must be at least 3 characters.")
        if len(query) > 300:
            raise HTTPException(status_code=422, detail="Query cannot exceed 300 characters.")

        regenerate = payload.get("regenerate", False)
        norm_q = normalize_query(query)

        # Check 24-hour cache
        if not regenerate and norm_q in query_cache_db:
            cache_entry = query_cache_db[norm_q]
            if time.time() - cache_entry["created_at"] < 86400:
                response.status_code = 200
                return {
                    "id": cache_entry["review_id"],
                    "query": query,
                    "status": "complete",
                    "cached": True
                }

        # Rate limiting check
        info = check_rate_limit(request)
        if info["count"] >= RATE_LIMIT_PER_HOUR:
            retry_after = max(1, info["reset"] - int(time.time()))
            return JSONResponse(
                status_code=429,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(RATE_LIMIT_PER_HOUR),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"])
                },
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"You have reached the limit of {RATE_LIMIT_PER_HOUR} literature reviews per hour. Please try again in {retry_after // 60} minutes, or browse our pre-computed example reviews.",
                        "retry_after": retry_after
                    }
                }
            )

        # Register request in rate limit store
        rate_limits_db[info["key"]].append(time.time())

        # Create review
        new_id = f"rev_{hashlib.md5(norm_q.encode()).hexdigest()[:8]}"
        base_review = example_reviews[0]
        new_review = {
            **base_review,
            "id": new_id,
            "query": query,
            "normalized_query": norm_q,
            "status": "pending",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        reviews_db[new_id] = new_review
        query_cache_db[norm_q] = {"review_id": new_id, "created_at": time.time()}

        return {
            "id": new_id,
            "query": query,
            "status": "pending",
            "cached": False
        }

    @app.get("/api/reviews/{id}")
    def get_review(id: str):
        """PRD Section 6 F2-AC6 & Section 9: Review retrieval."""
        if id not in reviews_db:
            raise HTTPException(status_code=404, detail="Review not found")
        return reviews_db[id]

    @app.get("/api/reviews/{id}/stream")
    def stream_review(id: str):
        """PRD Section 6 F2-AC2 & Section 9: SSE event stream."""
        if id not in reviews_db and id != "stream_test_id" and id != "error_stream_id":
            raise HTTPException(status_code=404, detail="Review not found")

        def event_generator():
            if id == "error_stream_id":
                yield 'event: stage\ndata: {"stage": "searching", "message": "Querying literature database"}\n\n'
                yield 'event: error\ndata: {"code": "LLM_PROVIDER_TIMEOUT", "message": "Upstream provider timed out after 3 retries", "retryable": true}\n\n'
                return

            rev = reviews_db.get(id, example_reviews[0])
            yield 'event: stage\ndata: {"stage": "searching", "message": "Retrieving candidate papers from OpenAlex"}\n\n'
            yield 'event: stage\ndata: {"stage": "ranking", "message": "Ranking abstracts by vector similarity"}\n\n'
            yield f'event: papers\ndata: {json.dumps({"papers": rev["papers"]})}\n\n'
            yield 'event: stage\ndata: {"stage": "writing", "message": "Generating structured literature review"}\n\n'

            # Stream sample tokens
            tokens = ["Recent ", "advancements ", "in ", "deep ", "learning ", "architectures ", "[1].\n\n"]
            for token in tokens:
                yield f'event: token\ndata: {json.dumps({"token": token})}\n\n'

            yield f'event: review_complete\ndata: {json.dumps({"review_id": id, "text": rev["review_text"], "total_claims": len(rev["claims"])})}\n\n'
            yield 'event: stage\ndata: {"stage": "verifying", "message": "Verifying claims against cited abstracts"}\n\n'

            for claim in rev["claims"]:
                yield f'event: claim_verified\ndata: {json.dumps(claim)}\n\n'

            yield f'event: done\ndata: {json.dumps({"review_id": id, "trust_score": rev["trust_score"], "status": "complete"})}\n\n'

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.get("/api/reviews/{id}/graph")
    def get_review_graph(id: str):
        """PRD Section 6 F4 & Section 9: Graph nodes and edges."""
        if id not in reviews_db:
            raise HTTPException(status_code=404, detail="Review not found")
        return reviews_db[id]["graph"]

    @app.get("/api/reviews/{id}/markdown")
    def export_markdown(id: str):
        """PRD Section 6 F5-AC2: Downloadable formatted Markdown."""
        if id not in reviews_db:
            raise HTTPException(status_code=404, detail="Review not found")
        rev = reviews_db[id]
        trust_pct = int(rev["trust_score"] * 100) if rev["trust_score"] is not None else "N/A"
        supported_cnt = sum(1 for c in rev["claims"] if c.get("final_verdict") == "supported")
        total_claims = len(rev["claims"])

        md_content = f"# {rev['query']}\n\n"
        md_content += f"*Generated by [Veritas](https://veritas-research.vercel.app) on {rev['created_at']}.*\n"
        md_content += f"**Trust Score**: {trust_pct}% | **Verified Claims**: {supported_cnt}/{total_claims} Supported.\n\n"
        md_content += "---\n\n"
        md_content += rev["review_text"] + "\n\n"
        md_content += "---\n\n## References\n\n"
        for p in rev["papers"]:
            authors = ", ".join(p["authors"])
            doi_link = f"https://doi.org/{p['doi']}" if p.get("doi") else p.get("url", "")
            md_content += f"[{p['source_number']}] {authors} ({p['year']}). {p['title']}. *{p.get('venue', 'Preprint')}*. {doi_link}\n"
        md_content += "\n---\n*Citation Verification Notice: Claims verified against peer-reviewed publication abstracts via exact substring entailment checking.*\n"

        return Response(
            content=md_content,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="veritas-{id}.md"'}
        )

    @app.get("/api/reviews/{id}/bibtex")
    def export_bibtex(id: str):
        """PRD Section 6 F5-AC2: BibTeX export with LaTeX escaping."""
        if id not in reviews_db:
            raise HTTPException(status_code=404, detail="Review not found")
        rev = reviews_db[id]
        entries = []
        for p in rev["papers"]:
            first_author = p["authors"][0].split()[-1].lower() if p["authors"] else "unknown"
            key = f"source{p['source_number']}_{first_author}{p['year']}"
            venue = p.get("venue") or ""
            is_proc = any(kw in venue.lower() for kw in ["proceedings", "conference", "neurips", "iclr", "icml", "acl", "cvpr"])
            entry_type = "inproceedings" if is_proc else ("article" if venue else "misc")

            # LaTeX escaping
            title = p["title"]
            for char, esc in [
                ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                ("_", r"\_"), ("{", r"\{"), ("}", r"\}")
            ]:
                title = title.replace(char, esc)

            authors_str = " and ".join(p["authors"]) if p["authors"] else "{Unknown Author}"
            year_val = p.get("year", "{n.d.}")

            lines = [f"@{entry_type}{{{key},"]
            lines.append(f"  title = {{{title}}},")
            lines.append(f"  author = {{{authors_str}}},")
            if is_proc:
                lines.append(f"  booktitle = {{{venue}}},")
            elif venue:
                lines.append(f"  journal = {{{venue}}},")
            lines.append(f"  year = {{{year_val}}},")
            if p.get("doi"):
                lines.append(f"  doi = {{{p['doi']}}},")
            if p.get("url"):
                lines.append(f"  url = {{{p['url']}}}")
            lines.append("}")
            entries.append("\n".join(lines))

        bib_content = "\n\n".join(entries) + "\n"
        return Response(
            content=bib_content,
            media_type="application/x-bibtex; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="veritas-{id}.bib"'}
        )

    @app.get("/api/examples")
    def get_examples():
        """PRD Section 6 F5-AC3: 5 Instant seed example reviews."""
        results = []
        for rev in example_reviews:
            results.append({
                "id": rev["id"],
                "discipline": rev.get("discipline", "Multidisciplinary"),
                "query": rev["query"],
                "summary": rev.get("summary", ""),
                "paper_count": len(rev["papers"]),
                "trust_score": rev["trust_score"],
                "created_at": rev["created_at"]
            })
        return results

    @app.get("/api/reviews")
    def get_recent_reviews(limit: int = 6):
        """PRD Section 6 F5-AC4: Recent completed reviews."""
        completed = [
            {
                "id": rev["id"],
                "query": rev["query"],
                "trust_score": rev["trust_score"],
                "paper_count": len(rev["papers"]),
                "created_at": rev["created_at"]
            }
            for rev in reviews_db.values()
            if rev.get("status") == "complete"
        ]
        return completed[:limit]

    return app


# --- Pytest Fixtures ---

@pytest.fixture(scope="session")
def eval_fixtures():
    return load_json_fixture(EVAL_FIXTURES_PATH)


@pytest.fixture(scope="session")
def example_reviews():
    return load_json_fixture(EXAMPLE_REVIEWS_PATH)


@pytest.fixture(scope="session")
def client():
    """
    Opaque HTTP client fixture.
    If VERITAS_API_URL is specified (e.g. against live docker container),
    uses httpx.Client to point to it.
    Otherwise uses FastAPI TestClient against mock server for 100% deterministic local/offline execution.
    """
    live_url = os.environ.get("VERITAS_API_URL")
    if live_url:
        with httpx.Client(base_url=live_url, timeout=30.0) as http_client:
            yield http_client
    else:
        app = create_mock_veritas_app()
        with TestClient(app) as test_client:
            yield test_client
