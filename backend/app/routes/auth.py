"""
Auth Blueprint — /api/register_user, /api/login, /api/google-login
"""

import logging
import bcrypt
from flask import Blueprint, request, jsonify

from palm_secure.db import SessionLocal
from palm_secure.models import User
from palm_secure.jwt_utils import generate_token
from palm_secure.securityLayer import PalmVeinPaymentEncryption
from app.extensions import limiter

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Encryption layer — reads PALM_AUTH_AES_KEY from env (crashes if missing)
encryption_layer = PalmVeinPaymentEncryption()


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/api/register_user", methods=["POST"])
@limiter.limit("5/minute")
def register_user():
    """Register a new user with biometric enrollment template."""
    data = request.json or {}
    bio_id    = (data.get("bio_id")    or "").strip()
    username  = (data.get("username")  or "").strip()
    email     = (data.get("email")     or "").strip()
    phone     = (data.get("phone")     or "").strip()
    password  = (data.get("password")  or "").encode("utf-8")

    if not all([bio_id, username, email, phone, password]):
        return jsonify({"error": "Missing fields"}), 400

    if len(bio_id) < 100:
        return jsonify({"error": "Enrollment template quality insufficient"}), 422

    session = SessionLocal()
    try:
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "User with this email already exists."}), 400

        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "User with this username already exists."}), 400

        import uuid
        password_hash    = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode("utf-8")
        bio_id_hash      = bcrypt.hashpw(bio_id.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        bio_id_encrypted = encryption_layer.encrypt_bio_template(bio_id)

        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            bio_id_hash=bio_id_hash,
            bio_id_encrypted=bio_id_encrypted,
        )
        session.add(user)
        session.commit()

        token = generate_token({"username": username, "email": email, "registration": "enhanced"})

        logger.info(f"USER REGISTERED: {username} ({email})")
        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id,
            "token": token,
        }), 201

    except Exception as e:
        session.rollback()
        logger.error(f"Registration failed: {e}")
        return jsonify({"error": "Registration failed"}), 500
    finally:
        session.close()


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/api/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    """Authenticate with email/phone + password."""
    data = request.json or {}
    identifier = (data.get("identifier") or "").strip()   # email or phone
    password   = (data.get("password")   or "").encode("utf-8")

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
        return jsonify({"msg": "login successful", "token": token, "name": user.username}), 200

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()


# ── Google login ───────────────────────────────────────────────────────────────

@auth_bp.route("/api/google-login", methods=["POST", "OPTIONS"])
def google_login():
    """Login via Google OAuth — requires prior biometric registration."""
    if request.method == "OPTIONS":
        return "", 200

    data      = request.json or {}
    email     = (data.get("email")     or "").strip()
    google_id = (data.get("google_id") or "").strip()

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

        token = generate_token({"username": user.username, "email": user.email})
        return jsonify({"msg": "login successful", "token": token, "name": user.username}), 200

    finally:
        session.close()
