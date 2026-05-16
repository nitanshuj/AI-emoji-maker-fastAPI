from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, emoji, user
from app.config import get_settings
import logging

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="AI Emoji Maker Backend",
    description="Production-ready FastAPI backend for generating sticker and emoji style reactions powered by FLUX.1 Schnell and Supabase.",
    version="1.0.0",
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(emoji.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/", tags=["System Health"], status_code=status.HTTP_200_OK)
async def root_health_check():
    """
    Root status health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "AI Emoji Maker API",
        "environment": settings.environment,
        "aimlapi_model": settings.aimlapi_model,
        "supabase_connected": bool(settings.supabase_url and settings.supabase_url != "https://example.supabase.co")
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {settings.port} in {settings.environment} mode.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))


# uvicorn app.main:app --reload --port 8000