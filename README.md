# 🏛️ AI Venture Architect

**A multi-agent AI consulting platform that validates startup ideas and drafts investor-ready business reports — running entirely on a local LLM.**

You type one idea. A team of specialized AI agents — coordinated by a Planner/CEO
agent over a [LangGraph](https://langchain-ai.github.io/langgraph/) workflow —
researches the market, sizes up competitors, models the finances, designs the
tech stack, plans the go-to-market, scores the risks, and synthesizes it all
into a structured business report.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-green)
![LLM](https://img.shields.io/badge/LLM-Qwen2.5--7B%20(local)-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ✨ Why this project is interesting

- **Multi-agent orchestration**, not a single prompt — a Planner delegates to seven specialists that share state.
- **Tool-calling reasoning loop** — each agent decides when to call a tool (web search, GitHub, calculator, Wikipedia); the LLM reasons, the tools fetch facts.
- **Graph-based workflow** with LangGraph — parallel/sequential execution, shared state, checkpoints, and an optional human-in-the-loop approval gate.
- **Local-first & private** — all reasoning runs on a local **Qwen2.5-7B** model via an OpenAI-compatible `llama-cpp` server (partial GPU offload). No data leaves your machine except optional web searches.
- **Clean, extensible architecture** — adding a new agent (e.g. Legal, Investor persona) is a small, self-contained change.

## 🧠 Architecture

```
                          USER  →  Gradio UI  →  LangGraph workflow
                                                       │
                                              Planner / CEO agent
                                                       │
        ┌───────────┬───────────┬───────────┬───────────┬───────────┐
        ▼           ▼           ▼           ▼           ▼           ▼
     Market    Competitor    Finance    Technology   Marketing    Risk
      agent       agent       agent       agent        agent      agent
        │           │           │           │           │           │
     web +       web +       calc       GitHub +      web        web
     wiki        GitHub      (local)      web
        └───────────┴───────────┴─── shared state ───┴───────────┘
                                                       │
                                          Report Generator agent
                                                       │
                                        (optional human approval)
                                                       │
                                             Final business report
```

**One model, many roles.** Every agent calls the *same* local LLM — only the
system prompt (and lightly, temperature/tools) changes. Reasoning (LLM), data
acquisition (tools), and orchestration (LangGraph) are cleanly separated.

## 🤖 The agents

| Agent | Role | Tools |
|-------|------|-------|
| **Planner / CEO** | Decomposes the idea into tasks; never answers directly | — |
| **Market Research** | Market size (TAM/SAM/SOM), CAGR, trends, demand | web search, Wikipedia |
| **Competitor** | Rivals, pricing, strengths/weaknesses, market gap | web search, GitHub |
| **Finance** | Costs, pricing, revenue, break-even, ROI | calculator |
| **Technology** | Recommended stack + complexity rating | GitHub, web search |
| **Marketing** | Audience, personas, GTM, channels, timeline | web search |
| **Risk** | Business/legal/technical/etc. risks, each scored 1–10 | web search |
| **Report Generator** | Synthesizes everything into the final document | — |

## 📄 What's in the generated report

Executive Summary · Business Plan · SWOT · Lean Canvas · Business Model Canvas ·
Technology Stack · Revenue Model · Risk Report · Implementation Roadmap ·
Investor Pitch — grounded in the specialists' concrete numbers, competitor
names, and risk scores.

## 🛠️ Tech stack

**Python** · **LangGraph** / **LangChain** (orchestration + tool-calling) ·
**llama-cpp-python** (OpenAI-compatible local server, CUDA) ·
**Qwen2.5-7B-Instruct** (GGUF) · **Gradio** (UI) · **DuckDuckGo / Wikipedia /
GitHub** APIs for retrieval.

## 🚀 Running it

Full setup and troubleshooting are in **[RUN.md](RUN.md)**. In short — two terminals:

```powershell
# Terminal 1 — start the local LLM server (Qwen2.5 on GPU)
.\run_server.ps1

# Terminal 2 — launch the web UI (http://127.0.0.1:7860)
.\run_app.ps1
```

The app is **provider-agnostic**: it talks to any OpenAI-compatible endpoint via
`.env` (`LLM_PROVIDER` = `openai` / `ollama` / `anthropic`). With no provider
configured it falls back to a stub so the whole graph still runs offline.

> **Note:** the model weights (multi-GB GGUF) are **not** in this repo — point
> `run_server.ps1` at your own local model. See [`.env.example`](.env.example).

## 📁 Project structure

```
graph/     shared state (VentureState), workflow graph, routing
agents/    BaseAgent contract + planner, 6 specialists, report
prompts/   one system prompt per agent
tools/     web search, calculator, GitHub, Wikipedia
utils/     provider-agnostic LLM factory
ui/        Gradio front end (live per-agent progress)
memory/    cross-session SQLite recall
```

## 🗺️ Roadmap

- LLM-powered Planner (dynamic task selection)
- Report export to PDF / DOCX / PPTX
- Real long-term memory & RAG over past ideas
- FastAPI backend + React front end, auth, dashboards

## 📜 License

MIT — see [LICENSE](LICENSE).

---

<sub>Built with LangGraph · runs 100% locally on your own GPU.</sub>
