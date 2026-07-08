"""Finance agent — cost, revenue, pricing, break-even, runway, ROI.

First fully-live agent and the reference other specialists copy: it overrides
`run()` to use the shared tool-calling loop (`BaseAgent.reason`) with a
deterministic calculator tool, so every figure is computed rather than guessed.
Mostly offline — no web/keys required.
"""

from __future__ import annotations

from agents.base import BaseAgent
from tools import calculator as calc_tools


class FinanceAgent(BaseAgent):
    name = "finance"
    output_key = "finance"
    temperature = 0.1  # numbers want low variance
    live = True        # LLM reasons and offloads arithmetic to the calculator

    def __init__(self) -> None:
        super().__init__(tools=[calc_tools.calculator])


finance_agent = FinanceAgent()
node = finance_agent.node
