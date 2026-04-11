"""File upload/download endpoints."""

import os
import mimetypes
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/stream")
def stream_audio(request: Request, path: str):
    """Stream audio files với HTTP Range support, giúp cho HTML5 <audio> tua được mà không phải tải toàn bộ file."""
    # BASE_DIR: backend/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Path thường có dạng "uploads/audio/xxx.wav"
    # Chuẩn hóa path để tương thích trên môi trường Windows và Linux
    file_path = os.path.join(BASE_DIR, path.replace("/", os.sep))
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    file_size = os.path.getsize(file_path)
    
    # Lấy Header Range
    range_header = request.headers.get("Range")
    
    if not range_header:
        # Nếu trình duyệt không gửi Range request (ít xảy ra với <audio> tag)
        def file_iterator(file_path, chunk_size=8192*4):
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        media_type, _ = mimetypes.guess_type(file_path)
        return StreamingResponse(
            file_iterator(file_path),
            headers={"Accept-Ranges": "bytes"},
            media_type=media_type or "application/octet-stream"
        )
        
    try:
        # Lược bỏ chữ "bytes=" và tách lấy [start, end]
        range_str = range_header.strip().lower().replace("bytes=", "")
        start_str, end_str = range_str.split("-")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="Invalid Range header format"
        )
        
    # Tính Bytes cần gửi
    start = int(start_str) if start_str else 0
    end = int(end_str) if end_str else file_size - 1
    
    if start < 0 or start >= file_size or end < start or end >= file_size:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="Requested Range not satisfiable"
        )
        
    chunk_size = end - start + 1
    
    def ranged_file_iterator(file_path, start, chunk_size, buffer_size=8192*4):
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = chunk_size
            while remaining > 0:
                bytes_to_read = min(buffer_size, remaining)
                data = f.read(bytes_to_read)
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
    }

    media_type, _ = mimetypes.guess_type(file_path)

    return StreamingResponse(
        ranged_file_iterator(file_path, start, chunk_size),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers,
        media_type=media_type or "audio/wav"
    )

