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

_mongo_uri_candidates = [
    ("MONGODB_URI", os.getenv("MONGODB_URI")),
    ("MONGO_URI", os.getenv("MONGO_URI")),
    ("MONGODB_URL", os.getenv("MONGODB_URL")),
]
MONGO_URI_SOURCE, MONGO_URI = next(
    ((name, value) for name, value in _mongo_uri_candidates if value),
    (None, None),
)
DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_project_db")

if not MONGO_URI:
    raise RuntimeError(
        "MongoDB URI not configured. Set MONGODB_URI (or MONGO_URI/MONGODB_URL) in environment variables."
    )


def create_mongo_client() -> MongoClient:
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        print(f"[OK] MongoDB Connected Successfully (source: {MONGO_URI_SOURCE})")
        return mongo_client
    except Exception as mongo_error:
        print(f"[FAIL] MongoDB connection failed (source: {MONGO_URI_SOURCE}):", mongo_error)
        raise RuntimeError(
            "Unable to connect to MongoDB using configured URI. "
            "Verify username/password and MongoDB Atlas user permissions."
        ) from mongo_error


client = create_mongo_client()
db = client[DB_NAME]
