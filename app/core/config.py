from datetime import timedelta
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    MONGODB_DB_NAME: str = "app_db"

    # Security Policies
    MIN_PASSWORD_LENGTH: int = 12
    MIN_AGE: int = 13  # COPPA compliance

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def token_expires_delta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    def validate_secrets(self) -> None:
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY must be set in environment variables")


settings = Settings()
settings.validate_secrets()
