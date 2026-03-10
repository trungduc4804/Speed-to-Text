"""Handle file storage and metadata (stub)."""


class FileService:
    """Manage uploads and retrieval."""

    def save_upload(self, file_bytes: bytes, filename: str) -> str:
        _ = (file_bytes, filename)
        return "stored-file-id"

    def get_path(self, file_id: str) -> str:
        _ = file_id
        return "/path/to/file"

