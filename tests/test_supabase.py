import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
import re

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__name__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def test_supabase_connection():
    logger.info("Loading environment variables from .env...")
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is missing from .env")
        return False

    logger.info(f"Original SUPABASE_URL from .env: {supabase_url}")
    
    # Supabase Python SDK requires the REST endpoint (https://[ref].supabase.co) rather than postgres:// string
    clean_url = supabase_url
    if "postgresql://" in supabase_url or "postgres://" in supabase_url:
        match = re.search(r"@db\.([a-zA-Z0-9_-]+)\.supabase\.co", supabase_url)
        if match:
            project_ref = match.group(1)
            clean_url = f"https://{project_ref}.supabase.co"
            logger.info(f"Auto-converted postgres connection string to REST URL: {clean_url}")
        else:
            logger.warning("SUPABASE_URL appears to be a postgres connection string but could not extract project ref.")

    try:
        logger.info("Initializing Supabase Client...")
        client: Client = create_client(clean_url, supabase_key)

        logger.info("Testing connection by querying 'profiles' table...")
        response = client.table("profiles").select("*").limit(1).execute()
        
        logger.info("✅ Connection successful!")
        logger.info(f"Profiles query returned: {response.data}")
        return True

    except Exception as e:
        logger.error(f"❌ Connection or query failed: {e}")
        return False


if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)


# To Run: python -m tests.test_supabase
