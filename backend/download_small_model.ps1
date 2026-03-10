$ErrorActionPreference = "Stop"

$BackendDir = "c:\TRUNGDUC\Do-An-TN\backend"
$ModelsDir = "$BackendDir\models"

# URL for Small Model (Better accuracy for Vietnamese)
# ggml-small.bin is ~466MB
$ModelUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
$ModelPath = "$ModelsDir\ggml-small.bin"

Write-Host "Downloading 'small' model (Better accuracy)..."
if (-not (Test-Path $ModelPath)) {
    Write-Host "   This is approx 466MB, please wait..."
    Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelPath
    Write-Host "   Done."
}
else {
    Write-Host "   Model 'small' already exists."
}

Write-Host "Model available at: $ModelPath"
Write-Host "To use this model, update config.py: WHISPER_MODEL_PATH = './models/ggml-small.bin'"
