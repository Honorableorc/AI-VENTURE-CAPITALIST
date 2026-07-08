"""Routing helpers for the workflow graph.

Keeps conditional-edge logic out of workflow.py so the graph topology reads
cleanly.
"""

from __future__ import annotations

from graph.state import VentureState


def after_approval(state: VentureState) -> str:
    """Route the final report: accepted -> finish, rejected -> replan.

    Returns a label matched in the conditional edge mapping in workflow.py.
    """
    return "accept" if state.get("approved") else "revise"
