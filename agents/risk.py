"""Risk Analysis agent — business/legal/technical/financial/AI-ethics risks."""

from __future__ import annotations

from agents.base import BaseAgent
from tools import search as search_tools


class RiskAgent(BaseAgent):
    name = "risk"
    output_key = "risk"
    temperature = 0.2
    live = True

    def __init__(self) -> None:
        super().__init__(tools=[search_tools.web_search])


risk_agent = RiskAgent()
node = risk_agent.node
