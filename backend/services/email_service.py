import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def _clean_env(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return _clean_env(value).lower() in {"1", "true", "yes", "on"}


GMAIL_EMAIL = _clean_env(getenv("GMAIL_EMAIL"))
_RAW_GMAIL_APP_PASSWORD = _clean_env(getenv("GMAIL_APP_PASSWORD"))
GMAIL_APP_PASSWORD = _RAW_GMAIL_APP_PASSWORD.replace(" ", "")

SMTP_SERVER = _clean_env(getenv("SMTP_HOST")) or "smtp.gmail.com"
SMTP_PORT = int(_clean_env(getenv("SMTP_PORT")) or 587)
SMTP_USERNAME = _clean_env(getenv("SMTP_USERNAME")) or GMAIL_EMAIL
SMTP_PASSWORD = _clean_env(getenv("SMTP_PASSWORD")) or GMAIL_APP_PASSWORD
SMTP_USE_TLS = _as_bool(getenv("SMTP_USE_TLS"), default=True)
SMTP_USE_SSL = _as_bool(getenv("SMTP_USE_SSL"), default=False)
SMTP_FROM_EMAIL = _clean_env(getenv("SMTP_FROM_EMAIL")) or GMAIL_EMAIL
SMTP_TIMEOUT_SECONDS = 10

RESEND_API_KEY = _clean_env(getenv("RESEND_API_KEY"))
RESEND_FROM_EMAIL = _clean_env(getenv("RESEND_FROM_EMAIL")) or SMTP_FROM_EMAIL
RESEND_API_URL = _clean_env(getenv("RESEND_API_URL")) or "https://api.resend.com/emails"

EMAIL_PROVIDER = (_clean_env(getenv("EMAIL_PROVIDER")) or "auto").lower()


def is_email_configured() -> bool:
    """Return True when SMTP credentials are available."""
    smtp_ready = bool(SMTP_SERVER and SMTP_PORT and SMTP_USERNAME and SMTP_PASSWORD and SMTP_FROM_EMAIL)
    resend_ready = bool(RESEND_API_KEY and RESEND_FROM_EMAIL)
    return smtp_ready or resend_ready

# Validate configuration
if not is_email_configured():
    print("[WARN] Email configuration incomplete. Set SMTP_* or GMAIL_EMAIL/GMAIL_APP_PASSWORD in environment")


def _smtp_configured() -> bool:
    return bool(SMTP_SERVER and SMTP_PORT and SMTP_USERNAME and SMTP_PASSWORD and SMTP_FROM_EMAIL)


def _resend_configured() -> bool:
    return bool(RESEND_API_KEY and RESEND_FROM_EMAIL)


def _provider_order() -> list[str]:
    if EMAIL_PROVIDER == "smtp":
        return ["smtp"]
    if EMAIL_PROVIDER == "resend":
        return ["resend"]

    # auto mode: prefer Resend over SMTP on cloud deployments for better deliverability.
    order = []
    if _resend_configured():
        order.append("resend")
    if _smtp_configured():
        order.append("smtp")
    return order

def send_otp_email(recipient_email: str, otp: str):
    """Send OTP via Gmail"""
    if not is_email_configured():
        print("[FAIL] OTP email skipped: missing SMTP credentials")
        return False

    try:
        subject = "Your 2FA OTP - AI Sentiment Forecaster"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #0dcbf2; text-align: center;">Two-Factor Authentication</h2>
                    <p style="color: #333; font-size: 16px;">Hi,</p>
                    <p style="color: #666;">Your One-Time Password (OTP) for login is:</p>
                    <div style="background-color: #0dcbf2; color: white; padding: 20px; text-align: center; border-radius: 8px; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #999; font-size: 14px;">This OTP will expire in 5 minutes.</p>
                    <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">© 2026 AI Sentiment Forecaster. All rights reserved.</p>
                </div>
            </body>
        </html>
        """

        return _send_email(recipient_email, subject, html_body)
    except Exception as e:
        print(f"[FAIL] Failed to send OTP email: {str(e)}")
        return False

def send_password_reset_email(recipient_email: str, reset_token: str, reset_link: str):
    """Send password reset link via Gmail"""
    if not is_email_configured():
        print("[FAIL] Password reset email skipped: missing SMTP credentials")
        return False

    try:
        subject = "Password Reset - AI Sentiment Forecaster"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #0dcbf2; text-align: center;">Password Reset Request</h2>
                    <p style="color: #333; font-size: 16px;">Hi,</p>
                    <p style="color: #666;">We received a request to reset your password. Click the button below to reset it:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #0dcbf2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset Password</a>
                    </div>
                    <p style="color: #666;">Or copy this link: <br><span style="color: #0dcbf2; word-break: break-all;">{reset_link}</span></p>
                    <p style="color: #999; font-size: 14px;">This link will expire in 30 minutes.</p>
                    <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">© 2026 AI Sentiment Forecaster. All rights reserved.</p>
                </div>
            </body>
        </html>
        """

        return _send_email(recipient_email, subject, html_body)
    except Exception as e:
        print(f"[FAIL] Failed to send password reset email: {str(e)}")
        return False

def _send_email_via_smtp(recipient_email: str, subject: str, html_body: str) -> bool:
    """Send email using SMTP transport."""
    server = None
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient_email

        # Attach HTML body
        part = MIMEText(html_body, "html")
        message.attach(part)

        # Send via configurable SMTP transport.
        if SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS)

        server.ehlo()
        if SMTP_USE_TLS and not SMTP_USE_SSL:
            server.starttls()
            server.ehlo()

        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, recipient_email, message.as_string())

        print(f"[OK] Email sent via SMTP to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[FAIL] SMTP authentication failed: {str(e)}")
        return False
    except Exception as e:
        print(f"[FAIL] SMTP Error: {str(e)}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


def _send_email_via_resend(recipient_email: str, subject: str, html_body: str) -> bool:
    """Send email using Resend HTTPS API."""
    try:
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": RESEND_FROM_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html_body,
        }
        response = requests.post(
            RESEND_API_URL,
            headers=headers,
            json=payload,
            timeout=SMTP_TIMEOUT_SECONDS,
        )
        if response.status_code in (200, 202):
            print(f"[OK] Email sent via Resend to {recipient_email}")
            return True

        print(f"[FAIL] Resend API error: {response.status_code} {response.text}")
        return False
    except Exception as e:
        print(f"[FAIL] Resend send error: {str(e)}")
        return False


def _send_email(recipient_email: str, subject: str, html_body: str) -> bool:
    """Try configured providers in priority order until one succeeds."""
    providers = _provider_order()
    if not providers:
        print("[FAIL] No email provider configured")
        return False

    for provider in providers:
        if provider == "resend":
            if _send_email_via_resend(recipient_email, subject, html_body):
                return True
        elif provider == "smtp":
            if _send_email_via_smtp(recipient_email, subject, html_body):
                return True

    print("[FAIL] All configured email providers failed")
    return False
