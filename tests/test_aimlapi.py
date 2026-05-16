import os
import sys
import asyncio
import logging
import httpx
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def test_aimlapi_connection():
    logger.info("Loading environment variables from .env...")
    load_dotenv()

    api_key = os.getenv("AIMLAPI_API_KEY")
    base_url = os.getenv("AIMLAPI_BASE_URL", "https://api.aimlapi.com/images/generations")
    model = os.getenv("AIMLAPI_MODEL", "flux/schnell")

    if not api_key or api_key == "your-aimlapi-api-key":
        logger.error("❌ AIMLAPI_API_KEY is missing or set to placeholder in .env")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Minimum valid dimensions for FLUX model (multiples of 32, min 64x64)
    payload = {
        "model": model,
        "prompt": "A minimalist flat vector icon of a golden trophy, clean solid background, square layout",
        "width": 64,
        "height": 64
    }

    logger.info(f"Connecting to AIMLAPI endpoint: {base_url}")
    logger.info(f"Model: {model} | Resolution: 64x64")

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            logger.info("Sending generation request (this may take a few seconds)...")
            response = await client.post(base_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                if items and "url" in items[0]:
                    logger.info("✅ AIMLAPI test successful!")
                    logger.info(f"Generated Image URL: {items[0]['url']}")
                    return True
                else:
                    logger.error(f"❌ Unexpected response structure: {data}")
                    return False
            else:
                logger.error(f"❌ API Request failed with status [{response.status_code}]: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Connection or request failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_aimlapi_connection())
    sys.exit(0 if success else 1)

# To Run: python -m tests.test_aimlapi
