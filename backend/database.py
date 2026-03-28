"""
Shared MongoDB connection for all backend modules.
Keeps auth and analytics endpoints on the same database target.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

# Must be set BEFORE importing pymongo/cryptography
warnings.simplefilter("ignore", DeprecationWarning)

from pymongo import MongoClient

# Load .env from backend/ first, then project root as fallback.
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env", override=False)
load_dotenv(PROJECT_ROOT / ".env", override=False)

MONGO_URI = (
    os.getenv("MONGO_URI")
    or os.getenv("MONGODB_URI")
    or os.getenv("MONGODB_URL")
)
DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_project_db")

if not MONGO_URI:
    raise RuntimeError(
        "MongoDB URI not configured. Set MONGO_URI (or MONGODB_URI/MONGODB_URL) in .env."
    )


def create_mongo_client() -> MongoClient:
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        print("[OK] MongoDB Connected Successfully")
        return mongo_client
    except Exception as mongo_error:
        print("[FAIL] MongoDB connection failed:", mongo_error)
        raise RuntimeError("Unable to connect to MongoDB using configured URI.") from mongo_error


client = create_mongo_client()
db = client[DB_NAME]
