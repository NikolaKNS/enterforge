"""
Application configuration using Pydantic Settings.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_ENV: str = Field(default="development", pattern=r"^(development|staging|production)$")
    DEBUG: bool = Field(default=False)
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])

    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service role key")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, description="Supabase JWT secret for token validation")

    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama server URL")
    OLLAMA_API_KEY: Optional[str] = Field(default=None, description="Ollama API key if secured")
    OLLAMA_MODEL: str = Field(default="qwen2.5:14b", description="Default model for agent")
    OLLAMA_VISION_MODEL: str = Field(default="llava:13b", description="Model for image understanding")

    # Agent Configuration
    AGENT_MAX_TURNS: int = Field(default=20, description="Maximum conversation turns")
    AGENT_TEMPERATURE: float = Field(default=0.7, ge=0, le=2)
    AGENT_TIMEOUT_SECONDS: int = Field(default=120)

    # External APIs
    AMADEUS_CLIENT_ID: Optional[str] = None
    AMADEUS_CLIENT_SECRET: Optional[str] = None
    AMADEUS_ENVIRONMENT: str = Field(default="test", pattern=r"^(test|production)$")

    # Email / Notifications
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = Field(default="noreply@tripforge.app")

    # Storage
    STORAGE_BUCKET: str = Field(default="offers")
    PDF_GENERATION_TIMEOUT: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"


# Global settings instance
settings = Settings()
