from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Supabase configurations
    supabase_url: str = "https://example.supabase.co"
    supabase_anon_key: str = "example_anon_key"

    # AIMLAPI configurations
    aimlapi_api_key: str = "example_aimlapi_key"
    aimlapi_base_url: str = "https://api.aimlapi.com/v1/images/generations"
    aimlapi_model: str = "flux/schnell"

    # FastAPI Server setup
    environment: str = "development"
    port: int = 8000

    # CORS — comma-separated list of allowed frontend origins.
    # Example: "https://your-app.netlify.app,https://www.yourdomain.com"
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_allowed_origins(self) -> List[str]:
        """Parse the ALLOWED_ORIGINS env var into a list."""
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()

