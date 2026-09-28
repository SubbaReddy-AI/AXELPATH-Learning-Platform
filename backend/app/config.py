from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # ============================================================
    # App
    # ============================================================
    APP_NAME: str = "AXELPATH Learning Platform"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str

    # ============================================================
    # Database
    # ============================================================
    DATABASE_URL: str

    # ============================================================
    # JWT
    # ============================================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============================================================
    # Admin
    # ============================================================
    ADMIN_EMAIL: str = "admin@axelpath.com"
    ADMIN_DEFAULT_PASSWORD: str

    # ============================================================
    # CORS
    # ============================================================
    # CORS
    ALLOWED_ORIGINS: str = (
        "https://axelpath-learning-platform.vercel.app,"
        "http://localhost:5173,"
        "http://localhost:3000"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Frontend URL
    FRONTEND_URL: str = "https://axelpath-learning-platform.vercel.app"


    # ============================================================
    # Cloudflare R2 / S3-compatible object storage
    # ============================================================
    R2_ENABLED: bool = False
    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_REGION: str = "auto"
    R2_SIGNED_URL_EXPIRE_SECONDS: int = 900

    # ============================================================
    # Media
    # ============================================================
    MEDIA_ROOT: str = "../media"
    MAX_UPLOAD_SIZE_MB: int = 1000

    # ============================================================
    # Email
    # ============================================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@axelpath.com"
    SMTP_FROM_NAME: str = "AXELPATH Platform"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # ============================================================
    # Rate Limiting
    # ============================================================
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_PERIOD_SECONDS: int = 900

    # ============================================================
    # Cleanup
    # ============================================================
    CLEANUP_JOB_HOUR: int = 2
    CLEANUP_JOB_MINUTE: int = 0

    # ============================================================
    # Deadline Reminder Email
    # ============================================================
    REMINDER_JOB_HOUR: int = 9
    REMINDER_JOB_MINUTE: int = 0
    REMINDER_HOURS_BEFORE: int = 12

    # ============================================================
    # Google Sheets — Student Details
    # ============================================================
    GOOGLE_SPREADSHEET_ID: str = ""
    GOOGLE_SHEET_WORKSHEET: str = "Sheet1"
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "./google-service-account.json"

    # ============================================================
    # Media Paths
    # ============================================================

    @property
    def media_recordings_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "recordings")

    @property
    def media_thumbnails_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "thumbnails")

    @property
    def media_assignments_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "assignments")

    @property
    def media_projects_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "projects")

    @property
    def media_quizzes_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "quizzes")

    @property
    def media_resources_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "resources")

    @property
    def media_profiles_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "profiles")

    @property
    def media_domains_path(self) -> str:
        return os.path.join(self.MEDIA_ROOT, "domains")

    # ============================================================
    # Pydantic Settings Configuration
    # ============================================================
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()