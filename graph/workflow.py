"""Assemble the LangGraph workflow.

Topology (v1):

    START -> planner -> {market, competitor, finance,
                         technology, marketing, risk}   (parallel fan-out)
                     -> report
                     -> approval  --accept--> END
                                  --revise--> planner   (loop)

The six specialists write to disjoint state keys, so LangGraph runs them
concurrently and merges their partial updates without a reducer. A checkpointer
(MemorySaver) is attached so the graph can pause for human approval and resume.

Business logic lives in the agents; this module only defines structure.
"""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents import (
    competitor,
    finance,
    marketing,
    market,
    planner,
    report,
    risk,
    technology,
)
from config import settings
from graph.edges import after_approval
from graph.state import VentureState

# Specialist (name -> node) roster that fans out from the planner.
SPECIALISTS = {
    "market": market.node,
    "competitor": competitor.node,
    "finance": finance.node,
    "technology": technology.node,
    "marketing": marketing.node,
    "risk": risk.node,
}


def approval_node(state: VentureState) -> dict:
    """Human-in-the-loop gate.

    When HUMAN_APPROVAL is on, the graph is compiled to interrupt *before* this
    node so a human can set `approved` / `revision_notes` on the state, then
    resume. When off, auto-approve so runs complete unattended.
    """
    if settings.human_approval:
        # A human sets state["approved"] out of band before resuming.
        return {"log": ["approval: awaiting human decision"]}
    return {"approved": True, "log": ["approval: auto-approved"]}


def build_graph():
    """Construct and compile the workflow. Returns a runnable graph."""
    g = StateGraph(VentureState)

    g.add_node("planner", planner.node)
    for name, node in SPECIALISTS.items():
        g.add_node(name, node)
    g.add_node("report", report.node)
    g.add_node("approval", approval_node)

    g.add_edge(START, "planner")

    if settings.parallel_agents:
        # Fan out to all specialists at once, then fan in to the report.
        for name in SPECIALISTS:
            g.add_edge("planner", name)
            g.add_edge(name, "report")
    else:
        # Deterministic sequential chain (easier to debug / cheaper).
        prev = "planner"
        for name in SPECIALISTS:
            g.add_edge(prev, name)
            prev = name
        g.add_edge(prev, "report")

    g.add_edge("report", "approval")
    g.add_conditional_edges(
        "approval", after_approval, {"accept": END, "revise": "planner"}
    )

    checkpointer = MemorySaver()
    interrupt_before = ["approval"] if settings.human_approval else []
    return g.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)


# Lazily built singleton so importing this module doesn't force a compile.
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
