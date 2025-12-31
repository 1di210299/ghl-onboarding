"""
Configuration settings for the application.
Loads environment variables and provides centralized config management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "GHL Healthcare Onboarding System"
    environment: str = "development"
    log_level: str = "INFO"
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    database_url: str
    
    # n8n
    n8n_webhook_url: str
    
    # GoHighLevel Integration
    ghl_api_key: Optional[str] = None
    ghl_location_id: Optional[str] = None
    ghl_workflow_id: Optional[str] = None
    ghl_api_url: str = "https://rest.gohighlevel.com/v1"
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        # Find .env file relative to this config file
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export for convenience
settings = get_settings()
