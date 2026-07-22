"""
Auth Blueprint — /api/register_user, /api/login, /api/login/verify-otp,
                 /api/enroll_bio, /api/google-login
"""

import logging
import re
import bcrypt
from flask import Blueprint, request, jsonify

from palm_secure.db import SessionLocal
from palm_secure.models import User
from palm_secure.jwt_utils import generate_token
from palm_secure.securityLayer import PalmVeinPaymentEncryption
from app.extensions import limiter
from app.middleware import token_required

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Encryption layer — reads PALM_AUTH_AES_KEY from env (crashes if missing)
encryption_layer = PalmVeinPaymentEncryption()

# Temporary store for pending login sessions (identifier → user info)
# Maps identifier to user data after successful password check, awaiting OTP
# TODO: Replace with Redis for multi-worker safety
_pending_logins: dict = {}

# Pending signups awaiting phone OTP: { 10-digit-phone → {username, email, phone, password_hash} }
_pending_registrations: dict = {}


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/api/register_user", methods=["POST"])
@limiter.limit("5/minute")
def register_user():
    """
    Step 1 of registration: validate fields and check for duplicates.
    Does NOT write to DB yet — user is held in _pending_registrations.
    The DB write only happens in /verify-otp after Firebase OTP is confirmed.
    """
    data = request.json or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    password = (data.get("password") or "").encode("utf-8")

    if not all([username, email, phone, password]):
        return jsonify({"error": "Missing fields"}), 400

    session = SessionLocal()
    try:
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "User with this email already exists."}), 400

        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "User with this username already exists."}), 400

        if session.query(User).filter_by(phone=phone).first():
            return jsonify({"error": "User with this phone number already exists."}), 400
    finally:
        session.close()

    # Hash password and store pending — DB write happens only after OTP is confirmed
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode("utf-8")
    _pending_registrations[phone] = {
        "username": username,
        "email": email,
        "phone": phone,
        "password_hash": password_hash,
    }

    # Return full E.164 phone for Firebase (default +91 for 10-digit numbers)
    e164_phone = phone if phone.startswith("+") else f"+91{phone}"

    logger.info(f"REGISTRATION PENDING (awaiting OTP): {username} ({email})")
    return jsonify({
        "otp_required": True,
        "phone": e164_phone,
        "message": "OTP sent to your registered phone number",
    }), 200


# ── Register (Step 2 — OTP Verified → Issue JWT) ──────────────────────────────

@auth_bp.route("/api/register_user/verify-otp", methods=["POST"])
@limiter.limit("10/minute")
def register_verify_otp():
    """
    Step 2 of registration: called after Firebase Phone OTP is confirmed.
    Only now is the user written to the DB and a JWT issued.
    If the OTP was never confirmed, no user record is ever created.
    """
    data = request.json or {}
    phone_full = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()

    if not phone_full:
        return jsonify({"error": "Phone number required"}), 400

    # Extract the 10-digit number (strip country code prefix)
    phone_digits = re.sub(r"\D", "", phone_full)
    phone_10 = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits

    # Retrieve the pending registration (must exist — no DB fallback allowed here)
    pending = _pending_registrations.pop(phone_10, None)

    if not pending:
        return jsonify({"error": "Registration session not found or already completed. Please register again."}), 401

    # OTP confirmed — now write the user to the DB
    import uuid
    session = SessionLocal()
    try:
        # Double-check no duplicate snuck in during the OTP window
        if session.query(User).filter(
            (User.email == pending["email"]) |
            (User.phone == phone_10) |
            (User.username == pending["username"])
        ).first():
            return jsonify({"error": "Account already exists. Please log in."}), 409

        user = User(
            id=str(uuid.uuid4()),
            username=pending["username"],
            email=pending["email"],
            phone=phone_10,
            password_hash=pending["password_hash"],
            bio_id_hash=None,
            bio_id_encrypted=None,
        )
        session.add(user)
        session.commit()

        token = generate_token({"username": pending["username"], "email": pending["email"]})
        logger.info(f"REGISTRATION COMPLETE (OTP verified, user saved): {pending['username']}")

        return jsonify({
            "message": "Registration complete",
            "token": token,
            "name": pending["username"],
        }), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save user after OTP: {e}")
        return jsonify({"error": "Registration failed during account creation."}), 500
    finally:
        session.close()


# ── Login (Direct — Password → JWT) ──────────────────────────────────────────

@auth_bp.route("/api/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    """Authenticate with email/phone + password. Issues JWT directly."""
    data = request.json or {}
    identifier = (data.get("identifier") or "").strip()
    password = (data.get("password") or "").encode("utf-8")

    if not identifier or not password:
        return jsonify({"error": "Missing credentials"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()

        if not user:
            return jsonify({"msg": "user not registered"}), 404

        if not bcrypt.checkpw(password, user.password_hash.encode("utf-8")):
            return jsonify({"msg": "incorrect password"}), 401

        token = generate_token({"username": user.username, "email": user.email})

        logger.info(f"LOGIN SUCCESS: {user.username}")
        return jsonify({
            "message": "Login successful",
            "token": token,
            "name": user.username,
        }), 200

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()


# ── Login (Step 2 — OTP Verification) ────────────────────────────────────────

@auth_bp.route("/api/login/verify-otp", methods=["POST"])
@limiter.limit("10/minute")
def login_verify_otp():
    """Step 2: After Firebase OTP verification on frontend, issue the JWT token."""
    data = request.json or {}
    identifier = (data.get("identifier") or "").strip()

    if not identifier:
        return jsonify({"error": "Missing identifier"}), 400

    # Look up the pending login
    pending = _pending_logins.pop(identifier, None)

    if not pending:
        return jsonify({"error": "No pending login found. Please log in again."}), 401

    # OTP was verified client-side via Firebase — issue our JWT
    token = generate_token({"username": pending["username"], "email": pending["email"]})
    logger.info(f"LOGIN SUCCESS (OTP verified): {pending['username']}")

    return jsonify({
        "msg": "login successful",
        "token": token,
        "name": pending["username"],
    }), 200


# ── Google login ──────────────────────────────────────────────────────────────

@auth_bp.route("/api/google-login", methods=["POST", "OPTIONS"])
def google_login():
    """Login via Google OAuth — requires phone verification."""
    if request.method == "OPTIONS":
        return "", 200

    data = request.json or {}
    email = (data.get("email") or "").strip()
    google_id = (data.get("google_id") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not email or not google_id:
        return jsonify({"error": "Missing Google credentials"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()

        if not user:
            return jsonify({
                "error": "NO_BIO_REGISTRATION",
                "message": "Google login detected but biometric registration required",
            }), 403

        # If user has no phone number, require it
        if not user.phone and not phone:
            return jsonify({
                "error": "PHONE_REQUIRED",
                "message": "Phone number required for verification",
            }), 200

        # If phone was provided, save it and require OTP verification
        if phone and not user.phone:
            user.phone = phone
            session.commit()

        # Store pending login for OTP verification
        _pending_logins[email] = {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
        }

        masked_phone = "●" * (len(user.phone) - 4) + user.phone[-4:]

        return jsonify({
            "otp_required": True,
            "phone": user.phone,
            "phone_masked": masked_phone,
            "msg": "Phone verification required",
            "name": user.username,
        }), 200

    finally:
        session.close()


# ── Google login — OTP verified ──────────────────────────────────────────────

@auth_bp.route("/api/google-login/verify-otp", methods=["POST"])
@limiter.limit("10/minute")
def google_login_verify_otp():
    """After Firebase OTP verification for Google login, issue the JWT token."""
    data = request.json or {}
    email = (data.get("email") or "").strip()

    if not email:
        return jsonify({"error": "Missing email"}), 400

    pending = _pending_logins.pop(email, None)

    if not pending:
        return jsonify({"error": "No pending login found. Please try again."}), 401

    token = generate_token({"username": pending["username"], "email": pending["email"]})
    logger.info(f"GOOGLE LOGIN SUCCESS (OTP verified): {pending['username']}")

    return jsonify({
        "msg": "login successful",
        "token": token,
        "name": pending["username"],
    }), 200


# ── Forgot Password — Reset ──────────────────────────────────────────────────

@auth_bp.route("/api/reset-password", methods=["POST"])
@limiter.limit("5/minute")
def reset_password():
    """
    Reset user password after Firebase Phone OTP has been verified on the frontend.
    Accepts the full E.164 phone and the new plaintext password.
    """
    data = request.json or {}
    phone_full = (data.get("phone") or "").strip()
    new_password = (data.get("newPassword") or "").strip()

    if not phone_full or not new_password:
        return jsonify({"error": "Phone and new password are required"}), 400

    # Server-side password strength validation
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if not re.search(r"[A-Z]", new_password):
        return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
    if not re.search(r"[a-z]", new_password):
        return jsonify({"error": "Password must contain at least one lowercase letter"}), 400
    if not re.search(r"\d", new_password):
        return jsonify({"error": "Password must contain at least one number"}), 400

    # Extract 10-digit number for DB lookup (strip country code)
    phone_digits = re.sub(r"\D", "", phone_full)
    phone_10 = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.phone == phone_10).first()
        if not user:
            return jsonify({"error": "No account found with this phone number"}), 404

        user.password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")
        session.commit()

        logger.info(f"PASSWORD RESET: {user.username} ({user.phone})")
        return jsonify({"message": "Password reset successfully"}), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Password reset failed: {e}")
        return jsonify({"error": "Password reset failed"}), 500
    finally:
        session.close()


# ── Bio Enrollment (post-registration) ───────────────────────────────────────

@auth_bp.route("/api/enroll_bio", methods=["POST"])
@token_required
def enroll_bio(current_user):
    """Enroll palm vein biometric data for an already-registered user."""
    data = request.json or {}
    bio_id = (data.get("bio_id") or "").strip()

    if not bio_id:
        return jsonify({"error": "bio_id is required"}), 400

    if len(bio_id) < 100:
        return jsonify({"error": "Enrollment template quality insufficient"}), 422

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=current_user.get("email")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        bio_id_hash = bcrypt.hashpw(bio_id.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        bio_id_encrypted = encryption_layer.encrypt_bio_template(bio_id)

        user.bio_id_hash = bio_id_hash
        user.bio_id_encrypted = bio_id_encrypted
        session.commit()

        logger.info(f"BIO ENROLLED: {user.username} ({user.email})")
        return jsonify({"message": "Palm vein enrolled successfully"}), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Bio enrollment failed: {e}")
        return jsonify({"error": "Enrollment failed"}), 500
    finally:
        session.close()
