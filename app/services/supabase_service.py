from supabase import create_client, Client
from app.config import get_settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


import re

def get_supabase_client() -> Client:
    settings = get_settings()
    url = settings.supabase_url
    if not url or url == "https://example.supabase.co":
        logger.warning("Supabase URL is not configured or using default example URL.")
    elif "postgresql://" in url or "postgres://" in url:
        match = re.search(r"@db\.([a-zA-Z0-9_-]+)\.supabase\.co", url)
        if match:
            url = f"https://{match.group(1)}.supabase.co"
            logger.info(f"Auto-converted postgres connection string to REST URL: {url}")
            
    return create_client(url, settings.supabase_anon_key)


class SupabaseService:
    def __init__(self):
        self.client: Client = get_supabase_client()

    def ensure_user_profile(
        self, user_id: str, email: str, full_name: Optional[str] = None
    ) -> None:
        """Ensures a record exists in the profiles table for this user."""
        try:
            res = self.client.table("profiles").select("id, full_name, generations_used").eq("id", user_id).execute()
            if not res.data:
                profile_data = {
                    "id": user_id,
                    "email": email,
                    "plan_type": "Free",
                    "generations_used": 0
                }
                if full_name:
                    profile_data["full_name"] = full_name
                self.client.table("profiles").insert(profile_data).execute()
            else:
                update_data = {}
                if full_name and not res.data[0].get("full_name"):
                    update_data["full_name"] = full_name
                
                if update_data:
                    self.client.table("profiles").update(update_data).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Error ensuring user profile for {user_id}: {e}")
            # Decide if you want to re-raise or handle
            raise

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a user's full profile from the 'profiles' table."""
        try:
            res = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return res.data
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            return None

    def increment_generations_used(self, user_id: str) -> None:
        """Increments the generations_used count for the user profile."""
        try:
            res = self.client.table("profiles").select("generations_used").eq("id", user_id).execute()
            if res.data:
                current_used = res.data[0].get("generations_used", 0)
                self.client.table("profiles").update({
                    "generations_used": current_used + 1
                }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Error incrementing user generations count: {e}")

    def save_emoji_generation(
        self,
        user_id: str,
        original_prompt: str,
        final_prompt: str,
        image_url: str,
        image_size: str,
        style: str,
        mood: str,
        user_email: str = "",
    ) -> Dict[str, Any]:
        """Saves generation record to image_generations table and updates profile usage."""
        if user_email:
            self.ensure_user_profile(user_id, user_email)

        try:
            data = {
                "user_id": user_id,
                "original_prompt": original_prompt,
                "final_prompt": final_prompt,
                "image_url": image_url,
                "image_size": image_size,
                "style": style,
                "mood": mood,
            }
            response = self.client.table("image_generations").insert(data).execute()
            
            # Increment usage count on success
            self.increment_generations_used(user_id)

            if response.data:
                return response.data[0]
            return {}
        except Exception as e:
            logger.error(f"Error saving image generation to Supabase: {e}")
            # Fallback returning constructed record if DB is not fully provisioned
            return {
                "id": "fallback-uuid",
                "user_id": user_id,
                "original_prompt": original_prompt,
                "final_prompt": final_prompt,
                "image_url": image_url,
                "image_size": image_size,
                "style": style,
                "mood": mood,
                "created_at": "2026-05-16T12:00:00Z"
            }

    def get_user_generations(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieves emoji generation history for a specific user."""
        try:
            response = self.client.table("image_generations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching user generations from Supabase: {e}")
            return []
