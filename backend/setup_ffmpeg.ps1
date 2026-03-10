$ErrorActionPreference = "Stop"

$BackendDir = "c:\TRUNGDUC\Do-An-TN\backend"
$FfmpegDir = "$BackendDir\ffmpeg"

# Create directory
New-Item -ItemType Directory -Force -Path $FfmpegDir | Out-Null

# URL for FFmpeg (Gyan.dev build - essential for stability)
$FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ZipPath = "$FfmpegDir\ffmpeg.zip"
$ExePath = "$FfmpegDir\bin\ffmpeg.exe"

Write-Host "1. Downloading FFmpeg..."
if (-not (Test-Path "$FfmpegDir\bin\ffmpeg.exe")) {
    Invoke-WebRequest -Uri $FfmpegUrl -OutFile $ZipPath
    Write-Host "   Extracting..."
    
    # Extract to temp
    Expand-Archive -Path $ZipPath -DestinationPath "$FfmpegDir\temp" -Force
    
    # Move bin/ffmpeg.exe to $FfmpegDir/bin
    $ExtractedRoot = Get-ChildItem -Path "$FfmpegDir\temp" -Directory | Select-Object -First 1
    $BinSource = "$($ExtractedRoot.FullName)\bin"
    
    New-Item -ItemType Directory -Force -Path "$FfmpegDir\bin" | Out-Null
    Move-Item -Path "$BinSource\ffmpeg.exe" -Destination "$FfmpegDir\bin\ffmpeg.exe" -Force
    Move-Item -Path "$BinSource\ffprobe.exe" -Destination "$FfmpegDir\bin\ffprobe.exe" -Force
    
    # Cleanup
    Remove-Item -Path "$FfmpegDir\temp" -Recurse -Force
    Remove-Item -Path $ZipPath -Force
    Write-Host "   Done."
}
else {
    Write-Host "   FFmpeg already exists. Skipping."
}

Write-Host "Setup Completed!"
Write-Host "FFmpeg: $FfmpegDir\bin\ffmpeg.exe"
