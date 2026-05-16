from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime


class EmojiGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Raw text prompt from user describing the emoji/reaction")
    style: Literal["Flat", "Sticker", "Doodle", "Pixel", "Mascot"] = Field(
        "Sticker", description="Visual art style desired for the emoji"
    )
    mood: Literal["Happy", "Tired", "Confused", "Celebrate"] = Field(
        "Happy", description="Mood emotional undertone"
    )
    # AIMLAPI constraint: width and height must be multiples of 32, minimum 64x64.
    width: int = Field(128, ge=64, le=512, description="Image output width in pixels (must be multiple of 32)")
    height: int = Field(128, ge=64, le=512, description="Image output height in pixels (must be multiple of 32)")

    @field_validator("width", "height")
    @classmethod
    def validate_multiples_of_32(cls, v: int) -> int:
        # Enforce or snap to nearest multiple of 32
        if v % 32 != 0:
            snapped = max(64, round(v / 32) * 32)
            return snapped
        return v


class EmojiMetadata(BaseModel):
    id: str
    user_id: str
    original_prompt: str
    final_prompt: str
    image_url: str
    image_size: str
    style: str
    mood: str
    created_at: datetime


class EmojiHistoryResponse(BaseModel):
    generations: List[EmojiMetadata]
