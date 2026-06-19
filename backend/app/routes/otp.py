"""
OTP Blueprint — /api/send-otp/email, /api/verify-otp

NOTE (Pack 4): otp_store is an in-memory dict. In a multi-worker deployment
this will break — each worker has its own store. Replace with Redis before
going to production with multiple gunicorn workers.
"""

import os
import random
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

otp_bp = Blueprint("otp", __name__)

# In-memory OTP store: { email_or_phone: { "otp": str, "expiry": datetime } }
# TODO (Pack 4): replace with Redis for multi-worker safety
_otp_store: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _send_otp_email(to_email: str, otp: str) -> None:
    """Send a 6-digit OTP to the given email address via SMTP."""
    from_email    = os.environ.get("SMTP_EMAIL")
    from_password = os.environ.get("SMTP_PASSWORD")

    if not from_email or not from_password:
        logger.warning("SMTP credentials not configured; skipping real email send.")
        return

    msg = MIMEMultipart()
    msg["From"]    = from_email
    msg["To"]      = to_email
    msg["Subject"] = "Your BioPay OTP Code"
    msg.attach(MIMEText(f"Your OTP code is: {otp}\n\nIt expires in 5 minutes.", "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        logger.info(f"OTP email sent to {to_email}")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────

@otp_bp.route("/api/send-otp/email", methods=["POST"])
def send_otp_email_route():
    """Generate an OTP and send it to the provided email address."""
    data  = request.json or request.form or {}
    email = (data.get("email") or "").strip()

    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    otp    = str(random.randint(100000, 999999))
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
    _otp_store[email] = {"otp": otp, "expiry": expiry}

    logger.info(f"Generated OTP for {email}")
    _send_otp_email(email, otp)

    return jsonify({"status": "success", "message": "OTP sent successfully", "email": email})


@otp_bp.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    """Verify the OTP submitted by the user."""
    data  = request.json or request.form or {}
    otp   = (data.get("otp")   or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not otp:
        return jsonify({"status": "error", "message": "OTP is required"}), 400

    key = email or phone
    if not key or key not in _otp_store:
        return jsonify({"status": "error", "message": "No OTP sent to this user"}), 404

    stored = _otp_store[key]
    if datetime.datetime.now() > stored["expiry"]:
        _otp_store.pop(key, None)
        return jsonify({"status": "error", "message": "OTP expired"}), 410

    if stored["otp"] == otp:
        _otp_store.pop(key, None)
        return jsonify({"status": "success", "message": "OTP verified"})

    return jsonify({"status": "error", "message": "Invalid OTP"}), 401
