from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.schemas.auth import UserProfile
from app.schemas.emoji import EmojiGenerateRequest, EmojiMetadata, EmojiHistoryResponse
from app.services.aiml_service import AIMLService
from app.services.supabase_service import SupabaseService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emoji", tags=["Emoji Generation"])

# Define weekly generation limits for each plan
PLAN_LIMITS = {
    "Free": 10,
    "Premium": 100,
    "Ultra": 500,
}

@router.post("/generate", response_model=EmojiMetadata, status_code=status.HTTP_200_OK)
async def generate_emoji(
    req: EmojiGenerateRequest,
    current_user: UserProfile = Depends(get_current_user),
    aiml_service: AIMLService = Depends(AIMLService),
    supabase_service: SupabaseService = Depends(SupabaseService),
):
    """
    Generates a high-quality emoji/sticker image using FLUX.1 Schnell via AIMLAPI.
    Enforces valid size constraints and saves metadata to Supabase.
    """
    logger.info(f"User [{current_user.id}] requested emoji generation for prompt: '{req.prompt}'")

    # Step 1: Fetch the user's full profile to check plan and usage
    user_profile = supabase_service.get_user_profile(user_id=current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Cannot verify generation limits."
        )

    # Step 2: Check if the user has exceeded their weekly generation limit
    plan = user_profile.get("plan_type", "Free")
    generations_used = user_profile.get("generations_used", 0)
    limit = PLAN_LIMITS.get(plan, 10)

    if generations_used >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have exceeded your weekly generation limit of {limit} for the {plan} plan. Please upgrade for more."
        )
    
    # Generate image via AIMLAPI
    output_url, enhanced_prompt = await aiml_service.generate_image(
        prompt=req.prompt,
        style=req.style,
        mood=req.mood,
        width=req.width,
        height=req.height
    )

    selected_size_str = f"{req.width}x{req.height}"

    # Save generation metadata in Supabase
    saved_record = supabase_service.save_emoji_generation(
        user_id=current_user.id,
        original_prompt=req.prompt,
        final_prompt=enhanced_prompt,
        image_url=output_url,
        image_size=selected_size_str,
        style=req.style,
        mood=req.mood,
        user_email=current_user.email,
    )

    record_id = str(saved_record.get("id", f"gen-{int(datetime.utcnow().timestamp())}"))
    created_at_val = saved_record.get("created_at")
    if isinstance(created_at_val, str):
        try:
            created_at = datetime.fromisoformat(created_at_val.replace("Z", "+00:00"))
        except ValueError:
            created_at = datetime.utcnow()
    elif isinstance(created_at_val, datetime):
        created_at = created_at_val
    else:
        created_at = datetime.utcnow()

    return EmojiMetadata(
        id=record_id,
        user_id=current_user.id,
        original_prompt=req.prompt,
        final_prompt=enhanced_prompt,
        image_url=output_url,
        image_size=selected_size_str,
        style=req.style,
        mood=req.mood,
        created_at=created_at
    )


@router.get("/history", response_model=EmojiHistoryResponse)
async def get_history(
    current_user: UserProfile = Depends(get_current_user),
    supabase_service: SupabaseService = Depends(SupabaseService),
):
    """
    Retrieves previous emoji generations for the authenticated user.
    """
    records = supabase_service.get_user_generations(user_id=current_user.id)
    
    parsed_generations = []
    for r in records:
        created_at_str = r.get("created_at", datetime.utcnow().isoformat())
        try:
            dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if isinstance(created_at_str, str) else created_at_str
        except Exception:
            dt = datetime.utcnow()

        parsed_generations.append(EmojiMetadata(
            id=str(r.get("id", "")),
            user_id=str(r.get("user_id", current_user.id)),
            original_prompt=str(r.get("original_prompt", "")),
            final_prompt=str(r.get("final_prompt", "")),
            image_url=str(r.get("image_url", "")),
            image_size=str(r.get("image_size", "128x128")),
            style=str(r.get("style", "Sticker")),
            mood=str(r.get("mood", "Happy")),
            created_at=dt
        ))

    return EmojiHistoryResponse(generations=parsed_generations)
