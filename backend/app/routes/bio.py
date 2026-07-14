"""
Bio Blueprint — /api/scan_bio_id, /api/scan_auth_feature, /api/validate_bio

NOTE (Pack 5): run_java_bridge, last_scan_time, and SCAN_COOLDOWN are currently
undefined in the original codebase. Stubs are provided here so the app starts
without crashing — they will be completed in Pack 5 (code quality fixes).
"""

import os
import time
import base64
import logging
import subprocess
from flask import Blueprint, request, jsonify

from palm_secure.db import SessionLocal
from palm_secure.models import User
from palm_secure.jwt_utils import generate_token
from palm_secure.securityLayer import PalmVeinPaymentEncryption
from app.middleware import token_required

logger = logging.getLogger(__name__)

bio_bp = Blueprint("bio", __name__)

SIMULATE = os.getenv("SIMULATE", "false").lower() == "true"

# Scan cooldown in seconds (prevent back-to-back hardware scans)
SCAN_COOLDOWN = 3
_last_scan_time: float = 0.0

# Encryption layer for stored biometric templates
encryption_layer = PalmVeinPaymentEncryption()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run_java_bridge(args: list, timeout: int = 30) -> str:
    """
    Invoke the Java SDK bridge process and return its stdout.

    TODO (Pack 5): wire up the actual Java bridge JAR path via env var.
    """
    jar_path = os.getenv("JAVA_BRIDGE_JAR")
    if not jar_path:
        raise RuntimeError(
            "JAVA_BRIDGE_JAR environment variable is not set. "
            "Set it to the absolute path of the PalmSecure Java bridge JAR."
        )
    result = subprocess.run(
        ["java", "-jar", jar_path] + args,
        capture_output=True, text=True, timeout=timeout,
    )
    return result.stdout


def _extract_clean_template(raw_output: str):
    """Extract a high-quality Base64 template from raw Java SDK output."""
    try:
        lines = raw_output.split("\n")
        for line in lines:
            line = line.strip()
            if (len(line) > 100
                    and line.replace("=", "").replace("+", "").replace("/", "").isalnum()
                    and not line.startswith("FALLBACK")
                    and not line.startswith("ERROR")):
                return line
        # Fallback: any valid Base64 of reasonable length
        for line in lines:
            line = line.strip()
            if len(line) > 50 and line.replace("=", "").replace("+", "").replace("/", "").isalnum():
                return line
        return None
    except Exception as e:
        logger.error(f"Template extraction failed: {e}")
        return None


def _scan_cooldown_check():
    """Returns an error response tuple if the scan cooldown has not elapsed, else None."""
    global _last_scan_time
    current = time.time()
    remaining = SCAN_COOLDOWN - (current - _last_scan_time)
    if remaining > 0:
        return jsonify({"error": f"Please wait {remaining:.1f} seconds between scans"}), 429
    _last_scan_time = current
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@bio_bp.route("/api/scan_bio_id", methods=["GET", "POST"])
def scan_bio_id():
    """Capture biometric template for ENROLLMENT (registration only)."""
    cooldown_error = _scan_cooldown_check()
    if cooldown_error:
        return cooldown_error

    try:
        if SIMULATE:
            simulated = base64.b64encode(b"ENROLLMENT_TEMPLATE").decode()
            logger.info(f"[SIMULATED ENROLLMENT SCAN] length={len(simulated)}")
            return jsonify({"bio_id_base64": simulated, "status": "success"})

        bio = _run_java_bridge(["capture"], timeout=45)
        if not bio:
            return jsonify({"error": "Empty capture from Java bridge"}), 500

        clean_bio = _extract_clean_template(bio)
        if clean_bio and len(clean_bio) > 100:
            logger.info(f"[HARDWARE ENROLLMENT SCAN] length={len(clean_bio)}")
            return jsonify({
                "bio_id_base64": clean_bio,
                "status": "success",
                "template_length": len(clean_bio),
                "template_type": "enrollment",
            })
        logger.warning("No valid enrollment template found in response")
        return jsonify({"error": "No valid enrollment data captured"}), 500

    except Exception as e:
        logger.error(f"Enrollment scan error: {e}")
        return jsonify({"error": str(e)}), 500


@bio_bp.route("/api/scan_auth_feature", methods=["GET", "POST"])
def scan_auth_feature():
    """Extract authentication features from a live palm scan (NOT enrollment)."""
    cooldown_error = _scan_cooldown_check()
    if cooldown_error:
        return cooldown_error

    try:
        if SIMULATE:
            simulated = base64.b64encode(b"AUTH_FEATURE").decode()
            logger.info(f"[SIMULATED AUTH SCAN] length={len(simulated)}")
            return jsonify({"auth_feature": simulated, "status": "success"})

        bio = _run_java_bridge(["extract_auth"], timeout=30)
        if not bio:
            return jsonify({"error": "Empty auth feature from Java bridge"}), 500

        clean_bio = _extract_clean_template(bio)
        if clean_bio and len(clean_bio) > 100:
            logger.info(f"[HARDWARE AUTH SCAN] length={len(clean_bio)}")
            return jsonify({
                "auth_feature": clean_bio,
                "status": "success",
                "feature_length": len(clean_bio),
                "template_type": "authentication",
            })
        logger.warning("No valid authentication feature found in response")
        return jsonify({"error": "No valid authentication data captured"}), 500

    except Exception as e:
        logger.error(f"Auth scan error: {e}")
        return jsonify({"error": str(e)}), 500


@bio_bp.route("/api/validate_bio", methods=["POST"])
@token_required
def validate_bio(current_user):
    """Validate a live palm scan against all enrolled users."""
    data = request.json or {}
    auth_feature = (data.get("bio_id") or "").strip()

    if not auth_feature:
        return jsonify({"match": False, "error": "Authentication feature required"}), 400

    # Only enforce high-quality template checks if we are NOT in simulation mode
    if not SIMULATE:
        if len(auth_feature) < 100 or not auth_feature.replace("=", "").replace("+", "").replace("/", "").isalnum():
            logger.warning(f"Invalid auth feature format: {auth_feature[:20]}...")
            return jsonify({"match": False, "verdict": "INVALID_TEMPLATE"}), 400

    if any(fake in auth_feature.upper() for fake in ["FAKE", "TEST", "MOCK", "DUMMY"]):
        logger.warning(f"Fake auth feature detected: {auth_feature[:20]}...")
        return jsonify({"match": False, "verdict": "FAKE_TEMPLATE"}), 400

    session = SessionLocal()
    try:
        users = session.query(User).all()
        if not users:
            return jsonify({"match": False, "verdict": "NO_USERS"}), 404

        # If in simulation mode, return a successful mock match for the first user
        if SIMULATE:
            user = users[0]
            token = generate_token({"username": user.username, "email": user.email})
            logger.info(f"[SIMULATED MATCH] Matched first user: {user.username}")
            return jsonify({
                "match": True,
                "verdict": "SIMULATED_MATCH",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                },
                "token": token,
            }), 200

        for user in users:
            try:
                enrollment_template = encryption_layer.decrypt_bio_template(user.bio_id_encrypted)
                if not enrollment_template:
                    logger.warning(f"Could not decrypt enrollment template for {user.username}")
                    continue

                logger.info(f"Comparing templates for {user.username}")

                comparison_result = _run_java_bridge(
                    ["compare", enrollment_template, auth_feature], timeout=15
                )
                logger.info(f"Java bridge result for {user.username}: {comparison_result}")

                if (comparison_result
                        and "MATCH" in str(comparison_result).upper()
                        and "NO_MATCH" not in str(comparison_result).upper()):
                    token = generate_token({"username": user.username, "email": user.email})
                    logger.info(f"SUCCESSFUL MATCH for {user.username}")
                    return jsonify({
                        "match": True,
                        "verdict": "SDK_MATCH",
                        "user": {
                            "username": user.username,
                            "email": user.email,
                            "phone": user.phone,
                        },
                        "token": token,
                    }), 200

                logger.info(f"No match for {user.username}: {comparison_result}")

            except Exception as e:
                logger.warning(f"Comparison failed for {user.username}: {e}")
                continue

        return jsonify({"match": False, "verdict": "NO_MATCH"}), 404

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"match": False, "error": str(e)}), 500
    finally:
        session.close()
