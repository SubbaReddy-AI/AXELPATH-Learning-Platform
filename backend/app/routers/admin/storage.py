from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.auth.dependencies import get_current_admin
from app.models.user import User
from app.services.r2_storage import r2_storage

router = APIRouter(prefix="/admin/storage", tags=["Admin - Storage"])

class SignedUrlRequest(BaseModel):
    key: str = Field(min_length=1, max_length=1024)
    expires_seconds: int = Field(default=900, ge=60, le=3600)
    response_content_type: str | None = None

@router.get("/status")
async def storage_status(admin: User = Depends(get_current_admin)):
    return {"enabled": r2_storage.enabled, "bucket_configured": bool(getattr(__import__("app.config", fromlist=["settings"]), "settings").R2_BUCKET_NAME)}

@router.post("/signed-url")
async def signed_url(payload: SignedUrlRequest, admin: User = Depends(get_current_admin)):
    key = payload.key.strip().lstrip("/")
    if not key.startswith("axelpath/"):
        raise HTTPException(status_code=400, detail="Invalid storage key")
    if not r2_storage.enabled:
        raise HTTPException(status_code=503, detail="R2 storage is not configured")
    return {"key": key, "url": r2_storage.signed_url(key, payload.expires_seconds, payload.response_content_type), "expires_seconds": payload.expires_seconds}
