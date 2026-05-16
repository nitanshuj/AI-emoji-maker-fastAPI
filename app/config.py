from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Supabase configurations
    supabase_url: str = "https://example.supabase.co"
    supabase_anon_key: str = "example_anon_key"

    # AIMLAPI configurations
    aimlapi_api_key: str = "example_aimlapi_key"
    aimlapi_base_url: str = "https://api.aimlapi.com/images/generations"
    aimlapi_model: str = "flux/schnell"

    # FastAPI Server setup
    environment: str = "development"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
