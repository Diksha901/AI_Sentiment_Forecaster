# from fastapi import APIRouter, HTTPException
# from schemas import UserLogin,UserRegister
# from hashing import verify_password
# from services import user_service
# from oauth2 import create_access_token
# from server import generate_otp
# from datetime import datetime,timedelta
# router = APIRouter(
#     prefix="/api/auth",
#     tags=["Authentication"]
# )

# @router.post("/login")
# async def login(payload: dict):
#     user = user_service.get_user_by_email(user.email) 
#     if not user or not verify_password(payload.get("password"), user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # Check if 2FA is enabled in user settings
#     if user.get("twoFactorEnabled"):
#         otp = generate_otp()
#         otp_collection.update_one(
#             {"email": user["email"]},
#             {"$set": {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=5)}},
#             upsert=True
#         )
#         return {"status": "2fa_required", "email": user["email"]}

#     # Normal login logic returns access_token
#     token = create_access_token(data={"user_id": str(user["_id"])})
#     return {"access_token": token, "token_type": "bearer"}
# # def login(user: UserLogin):

# #     db_user = user_service.get_user_by_email(user.email)

# #     if not db_user:
# #         raise HTTPException(status_code=404, detail="User not found")

# #     if not verify_password(user.password, db_user["password"]):
# #         raise HTTPException(status_code=401, detail="Invalid password")

# #     # CREATE TOKEN
# #     access_token = create_access_token(
# #         data={"user_id": str(db_user["_id"])}
# #     )

# #     return {
# #         "access_token": access_token,
# #         "token_type": "bearer"
# #     }

# @router.post("/register")
# def register(user: UserRegister):
#     try:
#         print("Incoming user:", user)

#         if user_service.get_user_by_email(user.email):
#             raise HTTPException(status_code=400, detail="Email already registered")

#         result = user_service.create_user(
#             user.firstname,
#             user.lastname,
#             user.email,
#             user.password
#         )

#         print("User created with ID:", result)

#         return {"message": "User created successfully"}

#     except Exception as e:
#         print("REGISTER ERROR:", str(e))
#         raise e
from fastapi import APIRouter, HTTPException, Depends
from schemas import UserLogin, UserRegister
from hashing import verify_password, hash_password, is_bcrypt_hash
from services import user_service
from services.email_service import send_otp_email, send_password_reset_email, is_email_configured
from oauth2 import create_access_token
from datetime import datetime, timedelta
import random
from database import db
import secrets
import asyncio
import logging
import os

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# Move OTP generation here to avoid circular imports with server.py
def generate_otp():
    return str(random.randint(100000, 999999))

otp_collection = db["otps"]
user_service.ensure_admin_user()
logger = logging.getLogger(__name__)


async def _send_otp_email_in_background(recipient_email: str, otp: str):
    """Send OTP asynchronously so login response is never blocked by SMTP latency."""
    try:
        sent = await asyncio.to_thread(send_otp_email, recipient_email, otp)
        if sent:
            otp_collection.update_one(
                {"email": recipient_email},
                {"$set": {"delivery_status": "sent", "delivery_error": None}},
                upsert=True,
            )
        else:
            otp_collection.update_one(
                {"email": recipient_email},
                {"$set": {"delivery_status": "failed", "delivery_error": "smtp_send_failed"}},
                upsert=True,
            )
    except Exception as exc:
        otp_collection.update_one(
            {"email": recipient_email},
            {"$set": {"delivery_status": "failed", "delivery_error": str(exc)}},
            upsert=True,
        )
        logger.warning("OTP email background send failed for %s: %s", recipient_email, exc)


def _otp_debug_enabled() -> bool:
    return os.getenv("OTP_DEBUG_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}

@router.post("/login")
async def login(payload: UserLogin): # Use your Pydantic schema for validation
    user_service.ensure_admin_user()

    # 1. Fetch user
    user = user_service.get_user_by_email(payload.email) 
    
    # 2. Verify existence and password
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Migrate any legacy plaintext password to bcrypt on successful login.
    if not is_bcrypt_hash(user.get("password", "")):
        upgraded_hash = hash_password(payload.password)
        db["users"].update_one({"_id": user["_id"]}, {"$set": {"password": upgraded_hash}})
        user["password"] = upgraded_hash

    is_admin = bool(user.get("is_admin", False))

    # 3. Check if 2FA is enabled (check 'settings' or 'users' collection)
    # Usually, 2FA status is stored in the settings collection or user doc
    user_settings = db["settings"].find_one({"user_id": str(user["_id"])})
    is_2fa_enabled = user_settings.get("twoFactorEnabled", False) if user_settings else False

    if is_2fa_enabled:
        otp = generate_otp()
        email_configured = is_email_configured()
        # Store OTP with a 5-minute expiry
        otp_collection.update_one(
            {"email": user["email"]},
            {"$set": {
                "otp": otp,
                "expires_at": datetime.utcnow() + timedelta(minutes=5),
                "delivery_status": "pending",
                "delivery_error": None,
            }},
            upsert=True
        )

        if email_configured:
            # Send OTP in background to avoid blocking login response.
            asyncio.create_task(_send_otp_email_in_background(user["email"], otp))
        else:
            otp_collection.update_one(
                {"email": user["email"]},
                {"$set": {"delivery_status": "failed", "delivery_error": "email_not_configured"}},
                upsert=True,
            )
            logger.warning("2FA email not configured for user %s", user["email"])

        response = {
            "status": "2fa_required",
            "email": user["email"],
            "message": "Please enter the OTP sent to your email",
            "is_admin": is_admin,
            "delivery_status": "queued" if email_configured else "failed",
            "delivery_error": None if email_configured else "email_not_configured",
        }

        if _otp_debug_enabled():
            response["otp_debug"] = otp

        return response

    # 4. Normal login logic (No 2FA)
    token = create_access_token(data={"user_id": str(user["_id"]), "is_admin": is_admin})
    return {"access_token": token, "token_type": "bearer", "is_admin": is_admin}

@router.post("/verify-2fa")
async def verify_2fa(payload: dict):
    email = payload.get("email")
    user_code = payload.get("code")
    if not email or not user_code:
        raise HTTPException(status_code=400, detail="Email and Code required")

    # Find the OTP entry
    entry = otp_collection.find_one({"email": email, "otp": user_code})
    
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    if entry["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")

    # OTP is valid! Get the user to issue the final token
    user = user_service.get_user_by_email(email)
    is_admin = bool(user.get("is_admin", False)) if user else False
    token = create_access_token(data={"user_id": str(user["_id"]), "is_admin": is_admin})
    
    # Clean up: Delete OTP after successful use
    otp_collection.delete_one({"email": email})

    return {"access_token": token, "token_type": "bearer", "is_admin": is_admin}


@router.post("/resend-2fa")
async def resend_2fa(payload: dict):
    """Resend OTP for an ongoing 2FA login attempt."""
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    otp_collection.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "expires_at": datetime.utcnow() + timedelta(minutes=5),
                "delivery_status": "pending",
                "delivery_error": None,
            }
        },
        upsert=True,
    )

    email_configured = is_email_configured()
    if email_configured:
        asyncio.create_task(_send_otp_email_in_background(email, otp))
        response = {
            "status": "resent",
            "email": email,
            "message": "A new OTP has been sent to your email",
            "delivery_status": "queued",
            "delivery_error": None,
        }
    else:
        otp_collection.update_one(
            {"email": email},
            {"$set": {"delivery_status": "failed", "delivery_error": "email_not_configured"}},
            upsert=True,
        )
        response = {
            "status": "failed",
            "email": email,
            "message": "Email service is not configured on the server",
            "delivery_status": "failed",
            "delivery_error": "email_not_configured",
        }

    if _otp_debug_enabled():
        response["otp_debug"] = otp

    return response

@router.post("/register")
def register(user: UserRegister):
    try:
        print("Incoming user:", user)
        if user_service.get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        result = user_service.create_user(
            user.firstname,
            user.lastname,
            user.email,
            user.password
        )
        print("User created with ID:", result)
        return {"message": "User created successfully"}
    except Exception as e:
        print("REGISTER ERROR:", str(e))
        raise e

@router.post("/forgot-password")
async def forgot_password(payload: dict):
    """Request password reset email"""
    email = payload.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        user = user_service.get_user_by_email(email)

        if not user:
            # Don't reveal if user exists for security
            return {"message": "If email exists, password reset link has been sent"}

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # Store reset token with 30-minute expiry
        reset_collection = db["password_resets"]
        reset_collection.update_one(
            {"email": email},
            {"$set": {
                "token": reset_token,
                "expires_at": datetime.utcnow() + timedelta(minutes=30)
            }},
            upsert=True
        )

        # Create reset link (frontend will handle this URL)
        reset_link = f"https://ai-sentiment-forecaster.onrender.com/reset-password?token={reset_token}&email={email}"

        # Send email
        email_sent = send_password_reset_email(email, reset_token, reset_link)

        if not email_sent:
            print(f"[WARN] Failed to send password reset email to {email}")

        return {"message": "If email exists, password reset link has been sent"}

    except Exception as e:
        print(f"[FAIL] Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")

@router.post("/reset-password")
async def reset_password(payload: dict):
    """Reset password with token"""
    token = payload.get("token")
    email = payload.get("email")
    new_password = payload.get("new_password")

    if not token or not email or not new_password:
        raise HTTPException(status_code=400, detail="Token, email, and new_password are required")

    try:
        reset_collection = db["password_resets"]

        # Find reset entry
        reset_entry = reset_collection.find_one({"email": email, "token": token})

        if not reset_entry:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        if reset_entry["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Reset token has expired")

        # Update user password
        hashed_password = hash_password(new_password)
        db["users"].update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )

        # Delete used token
        reset_collection.delete_one({"email": email})

        return {"message": "Password reset successful. You can now login with your new password."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[FAIL] Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset password")