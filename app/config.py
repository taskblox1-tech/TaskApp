"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import List, Union


class Settings(BaseSettings):
    """Application settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Family Task Tracker"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS - can be string or list
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:8000", "http://localhost:3000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            # Handle comma-separated string from environment variable
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v, info):
        """Set DEBUG=False in production"""
        if info.data.get('ENVIRONMENT') == 'production':
            return False
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()