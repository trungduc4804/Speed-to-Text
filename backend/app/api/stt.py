"""Speech-to-text endpoints using whisper.cpp runner."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/transcribe")
def transcribe():
    """Trigger transcription job for uploaded audio (stub)."""
    return {"status": "queued", "minute_id": "demo-minute-id"}

