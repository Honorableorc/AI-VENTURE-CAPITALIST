"""Gradio front end. One idea in, one report out — with live progress.

Kept dependency-light: imports gradio lazily inside launch() so the rest of the
app runs without it installed.
"""

from __future__ import annotations

from app import stream_idea


def launch(share: bool = False) -> None:
    import gradio as gr

    with gr.Blocks(title="AI Venture Architect") as demo:
        gr.Markdown(
            "# AI Venture Architect\n"
            "Multi-agent startup validation & business strategy."
        )
        idea = gr.Textbox(label="Your startup idea", lines=2,
                          placeholder="e.g. an AI SaaS platform for hospitals")
        go = gr.Button("Analyze", variant="primary")

        # Progress checklist (ticks through agents) + the final report.
        status = gr.Markdown(value="_Enter an idea and click Analyze._")
        report = gr.Markdown(label="Business report")

        # Generator -> Gradio streams each yield into (status, report), so the
        # user sees immediate feedback and per-agent progress.
        go.click(fn=stream_idea, inputs=idea, outputs=[status, report])

    demo.launch(share=share)


if __name__ == "__main__":
    launch()
