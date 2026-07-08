"""Wikipedia tool.

Hits Wikipedia's REST API directly with `requests` and a proper User-Agent
(the old `wikipedia` PyPI package is unmaintained and gets blocked). On a
missing page it falls back to the search API and summarises the top hit.
Degrades to an informative string on any failure so it never breaks a run.
"""

from __future__ import annotations

_UA = "AI-Venture-Architect/0.1 (https://example.com; contact@example.com)"
_REST = "https://en.wikipedia.org/api/rest_v1/page/summary/"
_SEARCH = "https://en.wikipedia.org/w/api.php"


def _get_summary(title: str) -> dict | None:
    import requests
    from urllib.parse import quote

    resp = requests.get(_REST + quote(title, safe=""),
                        headers={"User-Agent": _UA}, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def _search_title(topic: str) -> str | None:
    import requests

    resp = requests.get(
        _SEARCH,
        params={"action": "query", "list": "search", "srsearch": topic,
                "format": "json", "srlimit": 1},
        headers={"User-Agent": _UA}, timeout=15,
    )
    resp.raise_for_status()
    hits = resp.json().get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


def summary(topic: str, sentences: int = 3) -> str:
    """Return a short Wikipedia summary for a topic.

    Args:
        topic: The subject to summarise.
        sentences: Approximate number of sentences to return.
    """
    try:
        import requests  # noqa: F401
    except Exception:
        return f"[wikipedia unavailable] '{topic}': `pip install requests`."

    try:
        data = _get_summary(topic)
        if data is None:  # no direct page — search then summarise
            title = _search_title(topic)
            data = _get_summary(title) if title else None
        if not data:
            return f"[wikipedia] no page for '{topic}'."
        if data.get("type") == "disambiguation":
            return f"[wikipedia] '{topic}' is ambiguous; be more specific."
        extract = (data.get("extract") or "").strip()
        if not extract:
            return f"[wikipedia] no summary text for '{topic}'."
        trimmed = ". ".join(extract.split(". ")[:sentences]).strip()
        return f"{data.get('title', topic)}: {trimmed}"
    except Exception as exc:
        return f"[wikipedia error] '{topic}': {exc}"
