# How to run AI Venture Architect (local Qwen on GPU)

The app is **two processes**: a local LLM **server** (your Qwen model on the GPU)
and the **app** that talks to it. Both use the same environment: `.venv-gpu`.

## One-time: pick the interpreter in VS Code
1. `Ctrl+Shift+P` → **Python: Select Interpreter**
2. Choose **`.\.venv-gpu\Scripts\python.exe`**

## Every time: two terminals

Open two integrated terminals in VS Code (the `+` in the terminal panel).

### Terminal 1 — start the LLM server (leave it running)
```powershell
.\run_server.ps1
```
Wait until it prints **`Uvicorn running on http://127.0.0.1:8000`**. The model
loads into GPU/RAM here (takes ~20–40s). Keep this terminal open.

### Terminal 2 — run the app
```powershell
.\run_app.ps1 "an AI startup that detects crop diseases"   # one-shot report in the terminal
.\run_app.ps1                                               # or: open the Gradio web UI
```
The Gradio UI prints a local URL (e.g. http://127.0.0.1:7860) — open it in a browser.

## If the .ps1 scripts are blocked by execution policy
Run them via bypass, or use the raw commands:
```powershell
# bypass just for this command:
powershell -ExecutionPolicy Bypass -File .\run_server.ps1

# --- or the raw commands (equivalent) ---
# server:
.\.venv-gpu\Scripts\python.exe -m llama_cpp.server `
  --model "D:\OfflineResearchAssistant\models\qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf" `
  --chat_format chatml-function-calling --n_gpu_layers 16 --n_ctx 5120 --n_batch 256 `
  --host 127.0.0.1 --port 8000
# app:
.\.venv-gpu\Scripts\python.exe app.py "your idea here"
```

## Notes
- **Port already in use?** A server is already running from a previous session.
  Either reuse it (skip Terminal 1) or stop it:
  `Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`
- **Speed:** 7B partly on a 4 GB GPU is deliberate; a full report takes several
  minutes. For faster runs, use a 3B model (change `--model`) or offload more
  layers (`--n_gpu_layers`) if you free VRAM.
- **Config:** provider/model/URL live in `.env` (already set to the local server).
