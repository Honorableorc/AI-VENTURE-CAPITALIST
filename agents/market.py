"""Market Research agent — market size, CAGR, trends, demand/opportunity."""

from __future__ import annotations

from agents.base import BaseAgent
from tools import search as search_tools


class MarketAgent(BaseAgent):
    name = "market"
    output_key = "market_analysis"
    temperature = 0.3
    live = True

    def __init__(self) -> None:
        # Web + knowledge tools for demand and trend evidence.
        super().__init__(tools=[
            search_tools.web_search,
            search_tools.wikipedia_lookup,
        ])


market_agent = MarketAgent()
node = market_agent.node
