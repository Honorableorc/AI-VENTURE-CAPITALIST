"""Web / knowledge search tools.

Thin, swappable wrappers with graceful degradation: each tool tries a real
backend and, if the package or API key is missing (or the call fails), returns
a short informative string instead of raising — so an agent's reasoning loop
keeps going. Return values are compact text summaries meant for LLM context.

Backends:
  web_search       Tavily (if TAVILY_API_KEY) -> DuckDuckGo fallback
  wikipedia_lookup the `wikipedia` package (via tools.wikipedia)
  news_search      DuckDuckGo news
"""

from __future__ import annotations

from config import settings
from tools import wikipedia as wiki


def _format_results(results: list[dict], header: str) -> str:
    """Render [{title, url, snippet}] as a compact numbered list."""
    if not results:
        return f"{header}: no results."
    lines = [header]
    for i, r in enumerate(results, 1):
        title = (r.get("title") or "").strip() or "(untitled)"
        url = (r.get("url") or "").strip()
        snippet = " ".join((r.get("snippet") or "").split())[:300]
        lines.append(f"{i}. {title}\n   {url}\n   {snippet}")
    return "\n".join(lines)


def _tavily(query: str, max_results: int) -> list[dict] | None:
    if not settings.tavily_api_key:
        return None
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.tavily_api_key)
        resp = client.search(query, max_results=max_results)
        return [
            {"title": r.get("title"), "url": r.get("url"), "snippet": r.get("content")}
            for r in resp.get("results", [])
        ]
    except Exception as exc:
        print(f"[search] tavily failed: {exc}")
        return None


def _ddgs_client():
    """Return a DDGS class from whichever package is installed (ddgs is the
    current name; duckduckgo_search is the legacy one)."""
    try:
        from ddgs import DDGS

        return DDGS
    except Exception:
        from duckduckgo_search import DDGS  # legacy

        return DDGS


def _duckduckgo(query: str, max_results: int) -> list[dict] | None:
    try:
        DDGS = _ddgs_client()
        with DDGS() as ddgs:
            hits = ddgs.text(query, max_results=max_results) or []
        return [
            {"title": h.get("title"), "url": h.get("href"), "snippet": h.get("body")}
            for h in hits
        ]
    except Exception as exc:
        print(f"[search] duckduckgo failed: {exc}")
        return None


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return a concise summary of the top results.

    Args:
        query: What to search for.
        max_results: Maximum number of results to include.
    """
    results = _tavily(query, max_results)
    if results is None:
        results = _duckduckgo(query, max_results)
    if results is None:
        return (
            f"[web_search unavailable] '{query}': set TAVILY_API_KEY or "
            f"`pip install duckduckgo-search`."
        )
    return _format_results(results, f"Web results for '{query}':")


def wikipedia_lookup(topic: str) -> str:
    """Fetch a short Wikipedia summary for a topic.

    Args:
        topic: The subject to summarise.
    """
    return wiki.summary(topic)


def news_search(query: str, max_results: int = 5) -> str:
    """Search recent news for a query.

    Args:
        query: What to search news for.
        max_results: Maximum number of headlines to include.
    """
    try:
        DDGS = _ddgs_client()
        with DDGS() as ddgs:
            hits = ddgs.news(query, max_results=max_results) or []
    except Exception as exc:
        return f"[news_search unavailable] '{query}': {exc}"

    results = [
        {"title": h.get("title"), "url": h.get("url"),
         "snippet": f"{h.get('source', '')} — {h.get('body', '')}"}
        for h in hits
    ]
    return _format_results(results, f"News for '{query}':")
