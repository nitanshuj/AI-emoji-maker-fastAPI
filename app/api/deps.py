from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client
from app.services.supabase_service import get_supabase_client, SupabaseService
from app.schemas.auth import UserProfile
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase_client)
) -> UserProfile:
    """
    Dependency to verify JWT token and retrieve current authenticated user from Supabase.
    """
    try:
        # Supabase Python SDK validates the JWT token against Supabase Auth service
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = user_resp.user
        meta = user_data.user_metadata or {}

        # Build full_name from metadata fields
        fn = meta.get("first_name") or (meta.get("name", "").split(" ")[0] if meta.get("name") else None)
        ln = meta.get("last_name") or (meta.get("name", "").split(" ")[1] if meta.get("name") and " " in meta.get("name") else None)
        full_name_parts = [p for p in [fn, ln] if p]
        full_name = meta.get("full_name") or (" ".join(full_name_parts) if full_name_parts else None)

        profile = UserProfile(
            id=str(user_data.id),
            email=str(user_data.email),
            full_name=full_name,
        )

        # Ensure user profile row exists in the database
        display_name = full_name or profile.email.split("@")[0]
        SupabaseService().ensure_user_profile(profile.id, profile.email, display_name)

        return profile

    except HTTPException:
        # Re-raise HTTPExceptions without wrapping them in the generic auth error
        raise
    except Exception as e:
        logger.error(f"Authentication validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please verify your token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
