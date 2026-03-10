$ErrorActionPreference = "Stop"

$BackendDir = "c:\TRUNGDUC\Do-An-TN\backend"
$WhisperDir = "$BackendDir\whisper"
$ModelsDir = "$BackendDir\models"

# Create directories
New-Item -ItemType Directory -Force -Path $WhisperDir | Out-Null
New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null
New-Item -ItemType Directory -Force -Path "$BackendDir\uploads" | Out-Null

# URLs (Using specific versions for stability)
# Whisper.cpp v1.5.4 (Pre-built Windows x64 binary)
$WhisperUrl = "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.4/whisper-bin-x64.zip"
$ModelUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"

# Paths
$ZipPath = "$WhisperDir\whisper.zip"
$ExePath = "$WhisperDir\main.exe"
$ModelPath = "$ModelsDir\ggml-base.bin"

Write-Host "1. Downloading Whisper.cpp binary..."
if (-not (Test-Path $ExePath)) {
    Invoke-WebRequest -Uri $WhisperUrl -OutFile $ZipPath
    Write-Host "   Extracting..."
    Expand-Archive -Path $ZipPath -DestinationPath $WhisperDir -Force
    Remove-Item $ZipPath
    Write-Host "   Done."
}
else {
    Write-Host "   Binary already exists. Skipping."
}

Write-Host "2. Downloading Model (ggml-base.bin)..."
if (-not (Test-Path $ModelPath)) {
    Write-Host "   This may take a while..."
    Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelPath
    Write-Host "   Done."
}
else {
    Write-Host "   Model already exists. Skipping."
}

Write-Host "Setup Completed Successfully!"
Write-Host "Binary: $ExePath"
Write-Host "Model: $ModelPath"
