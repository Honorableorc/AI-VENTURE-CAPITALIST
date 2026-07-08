# Starts the local Qwen LLM server (llama-cpp-python, OpenAI-compatible) on GPU.
# Leave this running in its own terminal; the app connects to it over HTTP.
$here  = Split-Path -Parent $MyInvocation.MyCommand.Path
$py    = Join-Path $here ".venv-gpu\Scripts\python.exe"
$model = "D:\OfflineResearchAssistant\models\qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf"

Write-Host "Starting Qwen2.5-7B on GPU (16/28 layers offloaded) at http://127.0.0.1:8000 ..." -ForegroundColor Cyan
& $py -m llama_cpp.server `
    --model $model `
    --chat_format chatml-function-calling `
    --n_gpu_layers 16 `
    --n_ctx 5120 `
    --n_batch 256 `
    --host 127.0.0.1 --port 8000
