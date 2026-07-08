"""Planner / CEO agent — coordinates the team; never answers directly.

Its job is to turn a raw idea into a task list for the specialists and to
decide (on a rejected report) what should be revised. It does not write any
specialist section; it writes `tasks` (and reads `revision_notes`).
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from graph.state import VentureState

# The fixed roster of specialties the planner delegates to. In a later phase
# the planner can prune/prioritise these dynamically from the idea.
DEFAULT_TASKS: list[dict[str, str]] = [
    {"agent": "market", "goal": "Assess market size, growth, trends, demand."},
    {"agent": "competitor", "goal": "Map competitors, pricing, and market gaps."},
    {"agent": "finance", "goal": "Estimate costs, revenue, break-even, runway."},
    {"agent": "technology", "goal": "Recommend a stack and gauge complexity."},
    {"agent": "marketing", "goal": "Define audience, GTM, channels, timeline."},
    {"agent": "risk", "goal": "Identify and score key risks."},
]


class PlannerAgent(BaseAgent):
    name = "planner"
    output_key = "tasks"
    temperature = 0.2

    def run(self, state: VentureState) -> Any:  # returns a task list, not text
        # TODO: use the LLM to tailor/prioritise tasks from state["idea"] and
        # state["revision_notes"]. For now, emit the default roster.
        return list(DEFAULT_TASKS)

    def node(self, state: VentureState) -> dict[str, Any]:
        tasks = self.run(state)
        return {"tasks": tasks, "log": [f"planner: created {len(tasks)} tasks"]}


planner_agent = PlannerAgent()
node = planner_agent.node
