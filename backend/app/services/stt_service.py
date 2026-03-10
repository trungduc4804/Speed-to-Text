import subprocess
import os
import shutil
from app.core.config import settings

def save_upload_file(upload_file, destination):
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using Whisper.cpp binary.
    """
    binary_path = settings.WHISPER_BINARY_PATH
    model_path = settings.WHISPER_MODEL_PATH

    abs_binary_path = os.path.abspath(binary_path)
    abs_model_path = os.path.abspath(model_path)
    abs_audio_path = os.path.abspath(audio_path)
    # FFmpeg path
    abs_ffmpeg_path = os.path.abspath(settings.FFMPEG_BINARY_PATH)

    print(f"DEBUG: STT Start")
    print(f"DEBUG: Binary: {abs_binary_path}")
    print(f"DEBUG: Model: {abs_model_path}")
    print(f"DEBUG: Audio: {abs_audio_path}")
    print(f"DEBUG: FFmpeg: {abs_ffmpeg_path}")

    if not os.path.exists(abs_binary_path):
        return "[ERROR] Whisper binary not found"
    
    # Check FFmpeg
    if os.path.exists(abs_ffmpeg_path):
        # Convert to 16kHz WAV
        wav_path = abs_audio_path + ".wav"
        print(f"DEBUG: Converting to WAV 16kHz: {wav_path}")
        try:
            # ffmpeg -i input -ar 16000 -ac 1 -c:a pcm_s16le output.wav
            ffmpeg_cmd = [
                abs_ffmpeg_path,
                "-y", # Overwrite
                "-i", abs_audio_path,
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                wav_path
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            # Use the converted file for transcription
            abs_audio_path = wav_path
            print(f"DEBUG: Conversion successful. Using: {abs_audio_path}")
        except Exception as e:
            print(f"DEBUG: FFmpeg conversion failed: {e}")
            return f"[ERROR] Audio conversion failed."
    else:
        print("DEBUG: FFmpeg not found, trying raw file (may fail if not WAV)")

    try:
        # Command: ./main -m models/ggml-base.bin -f audio.wav -otxt --no-timestamps -l vi
        cmd = [
            abs_binary_path,
            "-m", abs_model_path,
            "-f", abs_audio_path,
            "--output-txt",
            "--no-timestamps",
            "-l", "vi" # Force Vietnamese
        ]
        
        print(f"DEBUG: Running command: {' '.join(cmd)}")
        
        # Run subprocess
        # Added encoding='utf-8' and errors='ignore' to handle non-cp1252 output gracefully on Windows
        result = subprocess.run(
            cmd, 
            check=False, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        
        print(f"DEBUG: Return Code: {result.returncode}")
        if result.returncode != 0:
            print(f"DEBUG: STDOUT: {result.stdout}")
            print(f"DEBUG: STDERR: {result.stderr}")
            return f"[ERROR] Whisper process failed with code {result.returncode}"

        # Read the generated txt file
        # Whisper.cpp typically appends .txt. e.g. input.wav -> input.wav.txt
        txt_path = abs_audio_path + ".txt"
        print(f"DEBUG: Looking for output file at: {txt_path}")
        
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"DEBUG: Found content ({len(content)} chars)")
            
            # Cleanup temp wav if created
            if abs_audio_path.endswith(".wav") and abs_audio_path != os.path.abspath(audio_path):
                try:
                    os.remove(abs_audio_path)
                    print(f"DEBUG: Removed temp file {abs_audio_path}")
                except:
                    pass
            
            return content.strip()
        else:
            print(f"DEBUG: Output file not found. STDOUT: {result.stdout}")
            return "[Error] Transcription completed but output file not found."
            
    except subprocess.CalledProcessError as e:
        print(f"Whisper Error: {e}")
        return f"[Error] Whisper process failed: {e}"
    except Exception as e:
        print(f"Error: {e}")
        return f"[Error] Unexpected error: {e}"
