from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.schemas.auth import UserProfile
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/users", tags=["Users"])

# Plan generation limits — must match emoji.py PLAN_LIMITS
PLAN_LIMITS = {
    "Free": 10,
    "Premium": 100,
    "Ultra": 500,
}


@router.get("/me", response_model=UserProfile)
async def read_users_me(
    current_user: UserProfile = Depends(get_current_user),
    supabase_service: SupabaseService = Depends(SupabaseService),
):
    """
    Fetch the full profile for the currently authenticated user.
    Injects max_generations based on the user's plan_type since it is
    a computed field (not stored in the database).
    """
    user_profile = supabase_service.get_user_profile(user_id=current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # Inject the computed max_generations based on the user's current plan
    plan_type = user_profile.get("plan_type", "Free")
    user_profile["max_generations"] = PLAN_LIMITS.get(plan_type, 10)

    return user_profile
