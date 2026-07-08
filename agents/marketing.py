"""Marketing agent — audience, GTM, personas, channels, launch timeline."""

from __future__ import annotations

from agents.base import BaseAgent
from tools import search as search_tools


class MarketingAgent(BaseAgent):
    name = "marketing"
    output_key = "marketing"
    temperature = 0.4  # a little creativity for GTM ideas
    live = True

    def __init__(self) -> None:
        super().__init__(tools=[search_tools.web_search])


marketing_agent = MarketingAgent()
node = marketing_agent.node
