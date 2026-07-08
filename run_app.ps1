# Runs AI Venture Architect. The LLM server (run_server.ps1) must be running first.
#   .\run_app.ps1                       -> Gradio web UI
#   .\run_app.ps1 "your startup idea"   -> one-shot CLI report
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py   = Join-Path $here ".venv-gpu\Scripts\python.exe"

if ($args.Count -gt 0) {
    & $py app.py ($args -join " ")
} else {
    Write-Host "Launching Gradio UI (Ctrl+C to stop)..." -ForegroundColor Cyan
    & $py app.py --ui
}
