import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from app.config import settings
from app.services.r2_storage import r2_storage
from app.services.storage_keys import media_key

# Allowed MIME types per category
ALLOWED_VIDEO_MIMES = {
    "video/mp4", "video/webm", "video/x-matroska",
    "video/x-msvideo", "video/quicktime"
}
ALLOWED_IMAGE_MIMES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"
}
ALLOWED_DOCUMENT_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "application/zip",
    "application/x-zip-compressed",
}
ALLOWED_CODE_MIMES = {
    "text/x-python", "text/x-java", "text/x-c", "text/x-c++",
    "application/javascript", "text/javascript", "application/sql",
    "text/html", "text/css", "text/plain",
    "application/zip", "application/x-zip-compressed",
}

# Dangerous extensions to block
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".php", ".jsp", ".asp", ".aspx",
    ".ps1", ".vbs", ".wsf", ".jar", ".msi", ".dll", ".so"
}


def safe_filename(original_filename: str) -> str:
    """Generate a UUID-based safe filename preserving extension."""
    ext = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def ensure_media_dirs():
    """Ensure all media subdirectories exist."""
    dirs = [
        settings.media_recordings_path,
        settings.media_thumbnails_path,
        settings.media_assignments_path,
        settings.media_projects_path,
        settings.media_quizzes_path,
        settings.media_resources_path,
        settings.media_profiles_path,
        settings.media_domains_path,
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def validate_file_extension(filename: str, allowed_extensions: Optional[list] = None) -> str:
    """Validate and return the lowercase extension, raise on dangerous/disallowed."""
    ext = Path(filename).suffix.lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed",
        )
    if allowed_extensions and ext.lstrip(".") not in [e.lstrip(".") for e in allowed_extensions]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}",
        )
    return ext


def validate_file_size(file_size: int, max_size_mb: int = None) -> None:
    """Raise if file exceeds maximum allowed size."""
    max_mb = max_size_mb or settings.MAX_UPLOAD_SIZE_MB
    max_bytes = max_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_mb}MB",
        )


async def save_upload_file(
    file: UploadFile,
    destination_dir: str,
    allowed_extensions: Optional[list] = None,
    max_size_mb: Optional[int] = None,
) -> Tuple[str, str, int, str]:
    """Store an upload in R2 when enabled, otherwise preserve local storage."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    validate_file_extension(file.filename, allowed_extensions)
    safe_name = safe_filename(file.filename)
    mime = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    # Starlette's UploadFile uses a spooled temporary file. Determine size without
    # loading a multi-GB video into RAM.
    try:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
    except Exception:
        content = await file.read()
        file_size = len(content)
        from io import BytesIO
        file.file = BytesIO(content)
        file.file.seek(0)

    validate_file_size(file_size, max_size_mb)

    if r2_storage.enabled:
        category = Path(destination_dir).name or "media"
        key = media_key(category, safe_name)
        r2_storage.upload_fileobj(file.file, key, mime)
        return f"r2://{key}", safe_name, file_size, mime

    dest_dir = Path(destination_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / safe_name
    with open(file_path, "wb") as output:
        file.file.seek(0)
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    return str(file_path), safe_name, file_size, mime


def delete_file_safe(file_path: str) -> bool:
    """Delete either a local file or an R2 object reference."""
    try:
        if not file_path:
            return False
        if file_path.startswith("r2://"):
            key = file_path[5:]
            if not r2_storage.enabled:
                return False
            r2_storage.delete(key)
            return True
        p = Path(file_path)
        if p.exists() and p.is_file():
            p.unlink()
            return True
    except Exception:
        return False
    return False


def stored_file_response(file_path: str, filename: str, media_type: str = "application/octet-stream"):
    """Return a local FileResponse or a short-lived R2 redirect after auth."""
    if file_path.startswith("r2://"):
        if not r2_storage.enabled:
            raise HTTPException(status_code=503, detail="R2 storage is not configured")
        url = r2_storage.signed_url(file_path[5:], response_content_type=media_type)
        return RedirectResponse(url=url, status_code=307)

    path = Path(file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")
    return FileResponse(path=str(path), filename=filename, media_type=media_type)
