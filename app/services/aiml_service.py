import httpx
import logging
from typing import Dict, Any, Tuple
from app.config import get_settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AIMLService:
    def __init__(self):
        self.settings = get_settings()

    def enhance_prompt(self, raw_prompt: str, style: str, mood: str) -> str:
        """
        Enhances user's raw prompt into a highly optimized sticker/emoji prompt for FLUX.1 Schnell.
        """
        style_descriptions = {
            "Sticker": "vibrant die-cut vinyl sticker with a distinct crisp white border contour",
            "Flat": "minimalist modern vector graphic icon, bold solid colors, clean geometric curves",
            "Doodle": "playful hand-drawn cartoon doodle illustration with charming sketchy linework",
            "Pixel": "retro 8-bit pixel art sprite, sharp vibrant color palette, arcade game aesthetic",
            "Mascot": "expressive 3D render style character mascot, glossy polished texture, lively personality"
        }

        style_context = style_descriptions.get(style, style_descriptions["Sticker"])

        enhanced = (
            f"A high quality workplace reaction emoji. {style_context}. "
            f"Subject: {raw_prompt}. Mood/Expression: {mood}. "
            f"Single centered object, perfectly isolated on a solid pristine white background, "
            f"perfectly square composition, professional workplace chat reaction icon, flawless details."
        )
        return enhanced

    async def generate_image(self, prompt: str, style: str, mood: str, width: int = 128, height: int = 128) -> Tuple[str, str]:
        """
        Calls AIMLAPI FLUX.1 Schnell model to generate the image.
        Returns (output_image_url, enhanced_prompt).
        """
        enhanced = self.enhance_prompt(prompt, style, mood)
        
        # Ensure width and height are valid multiples of 32
        w = max(64, round(width / 32) * 32)
        h = max(64, round(height / 32) * 32)

        if self.settings.aimlapi_api_key == "example_aimlapi_key" or not self.settings.aimlapi_api_key:
            logger.warning("AIMLAPI key not configured. Using high-quality SVG placeholder simulation for test mode.")
            # Fallback mock SVG matching frontend design
            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%"><circle cx="64" cy="64" r="56" fill="#f59e0b"/><text x="64" y="76" font-size="32" text-anchor="middle" font-family="sans-serif">🚀</text></svg>'
            mock_url = f"data:image/svg+xml;utf8,{svg_content}"
            return mock_url, enhanced

        headers = {
            "Authorization": f"Bearer {self.settings.aimlapi_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.settings.aimlapi_model,
            "prompt": enhanced,
            "width": w,
            "height": h
        }

        logger.info(f"Generating image via AIMLAPI with model {self.settings.aimlapi_model} at size {w}x{h}")

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                response = await client.post(
                    self.settings.aimlapi_base_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"AIMLAPI failure [{response.status_code}]: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Image generation provider returned status {response.status_code}"
                    )

                data = response.json()
                items = data.get("data", [])
                if not items or "url" not in items[0]:
                    logger.error(f"Unexpected response format from AIMLAPI: {data}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Invalid response payload from image generation provider"
                    )

                output_url = items[0]["url"]
                return output_url, enhanced

            except httpx.RequestError as exc:
                logger.error(f"HTTP request error during AIMLAPI call: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Timeout or connection error communicating with image provider"
                )
