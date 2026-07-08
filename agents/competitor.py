"""Competitor Analysis agent — rivals, pricing, strengths/weaknesses, gaps."""

from __future__ import annotations

from agents.base import BaseAgent
from tools import github as github_tools
from tools import search as search_tools


class CompetitorAgent(BaseAgent):
    name = "competitor"
    output_key = "competitor_analysis"
    temperature = 0.3
    live = True

    def __init__(self) -> None:
        super().__init__(tools=[
            search_tools.web_search,
            github_tools.github_repo_search,
        ])


competitor_agent = CompetitorAgent()
node = competitor_agent.node
