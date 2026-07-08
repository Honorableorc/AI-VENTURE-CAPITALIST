"""Technology agent — stack recommendation and technical complexity."""

from __future__ import annotations

from agents.base import BaseAgent
from tools import github as github_tools
from tools import search as search_tools


class TechnologyAgent(BaseAgent):
    name = "technology"
    output_key = "technology"
    temperature = 0.2
    live = True

    def __init__(self) -> None:
        super().__init__(tools=[
            github_tools.github_repo_search,
            search_tools.web_search,
        ])


technology_agent = TechnologyAgent()
node = technology_agent.node
