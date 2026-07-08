"""GitHub search tools for the Competitor / Technology agents.

Hits the GitHub REST search API with `requests`. A GITHUB_TOKEN (if set) raises
the rate limit but is not required. Degrades to an informative string on any
failure so it never breaks an agent's reasoning loop.
"""

from __future__ import annotations

from config import settings

_API = "https://api.github.com/search/repositories"


def github_repo_search(query: str, max_results: int = 5) -> str:
    """Search GitHub repositories relevant to a query, sorted by stars.

    Args:
        query: Repository search terms.
        max_results: Maximum number of repositories to include.
    """
    try:
        import requests
    except Exception:
        return f"[github unavailable] '{query}': `pip install requests`."

    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    try:
        resp = requests.get(
            _API,
            params={"q": query, "sort": "stars", "order": "desc",
                    "per_page": max_results},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as exc:
        return f"[github error] '{query}': {exc}"

    if not items:
        return f"GitHub repos for '{query}': no results."

    lines = [f"GitHub repos for '{query}':"]
    for i, repo in enumerate(items, 1):
        stars = repo.get("stargazers_count", 0)
        desc = " ".join((repo.get("description") or "").split())[:200]
        lines.append(
            f"{i}. {repo.get('full_name')} (★{stars})\n"
            f"   {repo.get('html_url')}\n   {desc}"
        )
    return "\n".join(lines)
