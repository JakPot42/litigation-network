"""
CourtListener API client for searching securities class action cases.

Free tier (no key): search endpoint only → returns docket metadata.
With COURTLISTENER_API_KEY: full access to individual dockets and RECAP document text.

For live ingestion, Claude extracts from whatever text is available — full document
text when the API key is provided, or structured metadata (caseName, cause, firms)
when working from search results alone.
"""
import httpx
from config import COURTLISTENER_API, COURTLISTENER_API_KEY, COURTLISTENER_TIMEOUT


class CourtListenerError(Exception):
    pass


def search_securities_cases(query: str = "securities class action", page_size: int = 10) -> list[dict]:
    """
    Search CourtListener RECAP for securities class action dockets.
    Returns list of normalized case dicts. Free — no API key required.
    """
    try:
        params = {
            "type": "r",
            "q": query,
            "order_by": "score desc",
            "page_size": page_size,
        }
        headers = _auth_headers()
        r = httpx.get(
            f"{COURTLISTENER_API}/search/",
            params=params,
            headers=headers,
            timeout=COURTLISTENER_TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        return [_normalize_search_result(item) for item in results]
    except httpx.HTTPError as exc:
        raise CourtListenerError(f"CourtListener search failed: {exc}") from exc


def fetch_docket(docket_id: int) -> dict | None:
    """
    Fetch full docket details. Requires API key; returns None if unavailable.
    """
    if not COURTLISTENER_API_KEY:
        return None
    try:
        r = httpx.get(
            f"{COURTLISTENER_API}/dockets/{docket_id}/",
            headers=_auth_headers(),
            timeout=COURTLISTENER_TIMEOUT,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise CourtListenerError(f"Docket fetch failed: {exc}") from exc


def fetch_recap_document_text(document_id: int) -> str | None:
    """
    Attempt to retrieve plain text from a RECAP document.
    Returns None if document not found or text not yet OCR'd.
    Requires API key.
    """
    if not COURTLISTENER_API_KEY:
        return None
    try:
        r = httpx.get(
            f"{COURTLISTENER_API}/recap-documents/{document_id}/",
            headers=_auth_headers(),
            timeout=COURTLISTENER_TIMEOUT,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("plain_text") or ""
        return text[:8000] if text.strip() else None
    except httpx.HTTPError:
        return None


def build_courtlistener_url(docket_absolute_url: str) -> str:
    return f"https://www.courtlistener.com{docket_absolute_url}"


def _normalize_search_result(item: dict) -> dict:
    firms = item.get("firm") or []
    return {
        "case_name": item.get("caseName") or item.get("case_name_full") or "",
        "docket_number": item.get("docketNumber") or "",
        "court": item.get("court_citation_string") or item.get("court") or "",
        "date_filed": item.get("dateFiled") or "",
        "judge_name": item.get("assignedTo") or "",
        "cause": item.get("cause") or "",
        "docket_id": item.get("docket_id"),
        "docket_absolute_url": item.get("docket_absolute_url") or "",
        "firms": firms,
        "attorneys": item.get("attorney") or [],
        "parties": item.get("party") or [],
    }


def _auth_headers() -> dict:
    if COURTLISTENER_API_KEY:
        return {"Authorization": f"Token {COURTLISTENER_API_KEY}"}
    return {}
