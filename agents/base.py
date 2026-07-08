"""BaseAgent: the shared contract every specialist follows.

An agent is: a name, a state key it owns, a prompt template (loaded from
`prompts/<name>.md`), an LLM, and an optional set of tools. Its public surface
is a single `run(state) -> section_text` method plus a `node(state) -> dict`
adapter that LangGraph calls.

`run()` defaults to a clearly-marked placeholder so unimplemented agents still
let the graph run. Agents that are "live" override `run()` to call
`self.reason(state)`, a reusable tool-calling loop implemented here once so
every agent adopts real reasoning by changing a single line.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Sequence

from graph.state import VentureState
from utils.llm import get_llm

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

#: Safety cap on tool-call rounds so a misbehaving model can't loop forever.
MAX_TOOL_STEPS = 6


class BaseAgent:
    #: Human-readable agent name, also used to locate prompts/<name>.md.
    name: str = "base"
    #: The single VentureState key this agent is allowed to write.
    output_key: str = ""
    #: Sampling temperature for this agent's LLM calls.
    temperature: float = 0.3
    #: When True, run() uses the live tool-calling loop; when False, a stub.
    live: bool = False

    def __init__(self, tools: Sequence[Callable[..., Any]] | None = None) -> None:
        self.tools = list(tools or [])
        self.llm = get_llm(self.temperature)

    # -- prompt handling ---------------------------------------------------
    def load_prompt(self) -> str:
        """The agent's system prompt (from prompts/<name>.md)."""
        path = PROMPTS_DIR / f"{self.name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are the {self.name} agent."

    def build_user_message(self, state: VentureState) -> str:
        """The task message: the idea plus any context this agent should see.

        Override to inject other agents' sections (e.g. the report agent).
        """
        idea = state.get("idea", "")
        context = state.get("context") or {}
        parts = [f"## Startup idea\n{idea}"]
        if context:
            details = "\n".join(f"- {k}: {v}" for k, v in context.items())
            parts.append(f"\n## Context\n{details}")
        if state.get("revision_notes"):
            parts.append(f"\n## Revision notes\n{state['revision_notes']}")
        return "\n".join(parts)

    # -- tool-calling reasoning loop --------------------------------------
    def _lc_tools(self) -> list[Any]:
        """Wrap the agent's plain callables as LangChain structured tools."""
        from langchain_core.tools import StructuredTool

        return [StructuredTool.from_function(fn) for fn in self.tools]

    def reason(self, state: VentureState, max_steps: int = MAX_TOOL_STEPS) -> str:
        """Run an LLM tool-calling loop and return the final text.

        The model may call any of this agent's tools; results are fed back and
        it is re-invoked until it answers without a tool call (or the step cap
        is hit). Degrades cleanly on the StubLLM (no tools bound, one turn).
        """
        from langchain_core.messages import (
            HumanMessage,
            SystemMessage,
            ToolMessage,
        )

        tools = self._lc_tools()
        tool_map = {t.name: t for t in tools}

        llm = self.llm
        if tools and hasattr(llm, "bind_tools"):
            llm = llm.bind_tools(tools)

        messages: list[Any] = [
            SystemMessage(content=self.load_prompt()),
            HumanMessage(content=self.build_user_message(state)),
        ]

        for _ in range(max_steps):
            ai = llm.invoke(messages)
            messages.append(ai)
            calls = getattr(ai, "tool_calls", None) or []
            if not calls:
                return ai.content if isinstance(ai.content, str) else str(ai.content)
            for call in calls:
                tool = tool_map.get(call["name"])
                try:
                    result = (
                        tool.invoke(call["args"]) if tool
                        else f"[error] unknown tool {call['name']!r}"
                    )
                except Exception as exc:  # never let a tool crash the run
                    result = f"[tool error] {exc}"
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=call["id"])
                )

        # Hit the step cap — return whatever the model last said.
        last = messages[-1]
        return getattr(last, "content", "") or "[reason: step limit reached]"

    # -- execution ---------------------------------------------------------
    def run(self, state: VentureState) -> str:
        """Produce this agent's markdown section.

        Live agents (`live = True`) run the tool-calling loop; others emit a
        clearly-marked placeholder so the graph still runs. Agents needing
        bespoke logic (e.g. report) override this directly.
        """
        if self.live:
            return self.reason(state)
        return (
            f"### {self.name.title()} (placeholder)\n"
            f"_Not yet implemented. Owns state key `{self.output_key}`._\n"
        )

    def node(self, state: VentureState) -> dict[str, Any]:
        """LangGraph node adapter: run and return a partial state update."""
        if not self.output_key:
            raise ValueError(f"{self.name}: output_key must be set")
        result = self.run(state)
        return {
            self.output_key: result,
            "log": [f"{self.name}: done"],
        }
