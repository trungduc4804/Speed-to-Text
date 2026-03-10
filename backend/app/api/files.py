"""File upload/download endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
def upload_file():
    """Receive audio file, store metadata (stub)."""
    return {"status": "ok", "file_id": "demo-file-id"}


@router.get("/{file_id}")
def get_file(file_id: str):
    """Return file metadata or download link (stub)."""
    return {"status": "ok", "file_id": file_id}

