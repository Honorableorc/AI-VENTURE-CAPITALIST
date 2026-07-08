"""Report Generator agent — composes the final document.

Never uses tools. Reads every specialist section from state and either
synthesises them with the LLM into an investor-ready report (Executive
Summary, SWOT, Lean Canvas, roadmap, pitch, ...) or, when no real LLM is
configured, falls back to a clean concatenation so demos still produce output.
"""

from __future__ import annotations

from agents.base import BaseAgent
from graph.state import SECTION_KEYS, VentureState
from utils.llm import StubLLM

SECTION_TITLES = {
    "market_analysis": "Market Research",
    "competitor_analysis": "Competitor Analysis",
    "finance": "Financial Analysis",
    "technology": "Technology Recommendation",
    "marketing": "Marketing Strategy",
    "risk": "Risk Assessment",
}


class ReportAgent(BaseAgent):
    name = "report"
    output_key = "final_report"
    temperature = 0.3

    def _sections_block(self, state: VentureState, max_chars: int | None = None) -> str:
        """The labelled specialist sections. `max_chars` caps each section so
        the synthesis prompt can't overflow a small local context window; the
        concatenation fallback passes None to keep full text."""
        blocks = []
        for key in SECTION_KEYS:
            title = SECTION_TITLES.get(key, key)
            body = state.get(key) or "_(section missing)_"
            if max_chars and len(body) > max_chars:
                body = body[:max_chars].rstrip() + " …[trimmed]"
            blocks.append(f"## {title}\n\n{body}")
        return "\n\n".join(blocks)

    def build_user_message(self, state: VentureState) -> str:
        idea = state.get("idea", "")
        # Cap each section (~400 tokens). Kept modest so most of the ~5k context
        # window is free for the OUTPUT (the report expands from these facts).
        # This is what prevents mid-report truncation on limited local context.
        sections = self._sections_block(state, max_chars=1600)
        return (
            f"Startup idea: {idea}\n\n"
            f"Here are the specialist findings. Write the full, detailed report "
            f"described in your instructions, preserving the specifics (numbers, "
            f"names, scores) from each section.\n\n{sections}"
        )

    def _concatenate(self, state: VentureState) -> str:
        idea = state.get("idea", "(no idea provided)")
        return f"# Business Report\n\n**Idea:** {idea}\n\n{self._sections_block(state)}\n"

    def run(self, state: VentureState) -> str:
        # No real LLM -> deterministic concatenation (keeps demos useful).
        if isinstance(self.llm, StubLLM):
            return self._concatenate(state)
        return self.reason(state)


report_agent = ReportAgent()
node = report_agent.node
