"""Entry point for AI Venture Architect.

Usage:
    python app.py "an AI SaaS platform for hospitals"   # run the graph in CLI
    python app.py --ui                                   # launch the Gradio UI

Keeps orchestration thin: build the graph, feed it a fresh state, print the
report. Real UX lives in ui/gradio_ui.py.
"""

from __future__ import annotations

import sys
import uuid

# Ensure Unicode from tools/reports (Wikipedia text, em-dashes, star glyphs)
# prints safely on Windows' legacy cp1252 console instead of crashing.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from graph.state import empty_state
from graph.workflow import get_graph


def run_idea(idea: str) -> str:
    """Run the full workflow for one idea and return the final report."""
    graph = get_graph()
    # thread_id lets the checkpointer track this run (needed for interrupts).
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final = graph.invoke(empty_state(idea), config=config)
    return final.get("final_report", "(no report produced)")


# Human-friendly labels for the progress checklist, in execution order.
STEP_ORDER = ["market", "competitor", "finance", "technology", "marketing", "risk", "report"]
STEP_LABELS = {
    "market": "Market research",
    "competitor": "Competitor analysis",
    "finance": "Financial analysis",
    "technology": "Technology recommendation",
    "marketing": "Marketing strategy",
    "risk": "Risk assessment",
    "report": "Writing the report",
}


def _progress_md(done: set[str], finished: bool = False) -> str:
    """Render the step checklist as markdown for the UI status panel."""
    header = ("### ✅ Analysis complete" if finished
              else "### ⏳ Analyzing… (a few minutes on the local GPU)")
    current = next((s for s in STEP_ORDER if s not in done), None)
    lines = [header]
    for step in STEP_ORDER:
        if step in done:
            mark = "✅"
        elif step == current and not finished:
            mark = "🔄"  # currently running
        else:
            mark = "⬜"
        lines.append(f"- {mark} {STEP_LABELS[step]}")
    return "\n".join(lines)


def stream_idea(idea: str):
    """Generator for the UI: yields (status_markdown, report) as agents finish.

    Streams LangGraph node updates so the user sees the checklist tick through
    each agent instead of staring at a frozen page.
    """
    if not idea or not idea.strip():
        yield "Please enter a startup idea first.", ""
        return

    graph = get_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    done: set[str] = set()
    final = ""

    yield _progress_md(done), ""  # immediate feedback on click
    for chunk in graph.stream(empty_state(idea), config=config, stream_mode="updates"):
        for node, update in (chunk or {}).items():
            done.add(node)
            if update and update.get("final_report"):
                final = update["final_report"]
        yield _progress_md(done), final
    yield _progress_md(done, finished=True), final or "*(no report produced)*"


def main(argv: list[str]) -> int:
    if "--ui" in argv:
        from ui.gradio_ui import launch

        launch()
        return 0

    idea = " ".join(a for a in argv if not a.startswith("-")).strip()
    if not idea:
        idea = "an AI-powered platform for precision agriculture"
        print(f"[app] no idea given; using demo idea: {idea!r}\n")

    print(run_idea(idea))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
