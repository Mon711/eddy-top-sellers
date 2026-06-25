import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_ADMIN_ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-04")