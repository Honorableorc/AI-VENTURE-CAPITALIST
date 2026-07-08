"""Shared LangGraph state for AI Venture Architect.

Every agent reads from and writes to this single state object. Each specialized
agent updates ONLY its own section; the Report agent reads all sections and
composes the final document.

We use a TypedDict because LangGraph merges the partial dict each node returns
into the running state. As long as parallel agents write to *different* keys,
no reducer is required. Keys that could be written concurrently use an
`operator.add`-style reducer (see `tasks` / `log`).
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class VentureState(TypedDict, total=False):
    # ---- Input -----------------------------------------------------------
    idea: str                      # raw startup idea from the user
    context: dict[str, Any]        # optional user prefs, geography, budget, etc.

    # ---- Planner ---------------------------------------------------------
    # Task decomposition produced by the Planner/CEO agent. Appended to so that
    # replanning after a rejected report does not clobber history.
    tasks: Annotated[list[dict[str, Any]], operator.add]

    # ---- Specialist agent outputs (one key each, written independently) --
    market_analysis: str
    competitor_analysis: str
    finance: str
    technology: str
    marketing: str
    risk: str

    # ---- Report ----------------------------------------------------------
    final_report: str

    # ---- Human-in-the-loop -----------------------------------------------
    approved: bool                 # set by the approval node / human
    revision_notes: str            # feedback fed back to the planner on reject

    # ---- Bookkeeping -----------------------------------------------------
    # Free-form execution log; every node may append. Useful for tracing and
    # for showing progress in the UI.
    log: Annotated[list[str], operator.add]


# Keys each specialist owns. Handy for validation, the report agent, and tests.
SECTION_KEYS: tuple[str, ...] = (
    "market_analysis",
    "competitor_analysis",
    "finance",
    "technology",
    "marketing",
    "risk",
)


def empty_state(idea: str, **context: Any) -> VentureState:
    """Build a fresh state for a new run."""
    return VentureState(
        idea=idea,
        context=dict(context),
        tasks=[],
        approved=False,
        revision_notes="",
        log=[],
    )
