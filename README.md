# AI Venture Architect

A multi-agent AI consulting platform for startup validation and business
strategy. You enter an idea; a team of specialized agents — coordinated by a
Planner/CEO agent over a LangGraph workflow with shared state — produces an
investor-ready business report.

> **Status: Phase 1 — architecture scaffold.** The graph, shared state, agent
> interfaces, tools, and UI are wired and runnable end-to-end. Business logic is
> stubbed (agents emit clearly-marked placeholders) and gets filled in per agent.

## Architecture

```
USER → Gradio UI → app → LangGraph workflow → Planner
     → {Market, Competitor, Finance, Technology, Marketing, Risk}  (parallel)
     → Report → Human approval (optional) → Final report
```

Each specialist owns exactly one key in a shared `VentureState`
([graph/state.py](graph/state.py)); they run in parallel and the Report agent
reads all sections. Topology lives in [graph/workflow.py](graph/workflow.py).

## Layout

| Path | Purpose |
|------|---------|
| `graph/` | Shared state, workflow graph, routing |
| `agents/` | Planner + 6 specialists + report (`BaseAgent` contract in `base.py`) |
| `prompts/` | One markdown system prompt per agent |
| `tools/` | Search, calculator, GitHub, Wikipedia (stubs) |
| `memory/` | Cross-session SQLite recall |
| `ui/` | Gradio front end |
| `utils/` | Provider-agnostic LLM factory |

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # optional; runs with stubs if left as-is

python app.py "an AI SaaS platform for hospitals"   # CLI
python app.py --ui                                   # Gradio
```

With no LLM provider configured, agents return placeholder sections so you can
exercise the full workflow offline. Set `LLM_PROVIDER` in `.env` (ollama /
anthropic / openai) to generate real output.

## Roadmap

Phase 2: implement agent reasoning + tool calls · Phase 3: real memory & RAG ·
Phase 4: PDF/DOCX/PPTX report export · Phase 5: FastAPI + React, auth, dashboards.
