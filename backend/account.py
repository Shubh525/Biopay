"""
BioPay — Mock Account for End-to-End Testing
=============================================

Contains a single pre-defined user whose fields match exactly what
Register.jsx sends to POST /api/register_user:

    { bio_id, username, email, phone, password }

Call `seed_mock_account()` at startup to ensure this user exists in the
database.  The function is idempotent — it silently skips if the email
is already registered.

Login credentials (for /api/login):
    identifier : mock@biopay.dev   OR   9999900000
    password   : Mock@1234
"""

import logging
import bcrypt
from palm_secure.db import SessionLocal
from palm_secure.models import User
from palm_secure.securityLayer import PalmVeinPaymentEncryption

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Plain-text credentials  (use these in the frontend / Postman / tests)
# ---------------------------------------------------------------------------
MOCK_USERNAME = "MockUser"
MOCK_EMAIL = "mock@biopay.dev"
MOCK_PHONE = "9999900000"
MOCK_PASSWORD = "Mock@1234"

# A realistic-length Base64 biometric template (>100 chars as required by the
# registration endpoint).  This is a deterministic fake — it will never match
# real hardware, but it lets the full register → login → transaction flow work.
MOCK_BIO_ID = (
    "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB"
    "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB"
    "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB"
    "QUFBQUFBQUFBQUFBQUFBQUFBQQ=="
)

# Fixed UUID so the account is always the same across restarts
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------

def seed_mock_account() -> bool:
    """
    Insert the mock account into the database if it does not already exist.

    Returns True if the account was created, False if it already existed.
    """
    encryption_layer = PalmVeinPaymentEncryption()
    session = SessionLocal()

    try:
        existing = session.query(User).filter_by(email=MOCK_EMAIL).first()
        if existing:
            logger.info(f"Mock account already exists: {MOCK_EMAIL}")
            return False

        password_hash = bcrypt.hashpw(
            MOCK_PASSWORD.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

        bio_id_hash = bcrypt.hashpw(
            MOCK_BIO_ID.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

        bio_id_encrypted = encryption_layer.encrypt_bio_template(MOCK_BIO_ID)

        user = User(
            id=MOCK_USER_ID,
            username=MOCK_USERNAME,
            email=MOCK_EMAIL,
            phone=MOCK_PHONE,
            password_hash=password_hash,
            bio_id_hash=bio_id_hash,
            bio_id_encrypted=bio_id_encrypted,
        )

        session.add(user)
        session.commit()

        logger.info(
            f"✅ Mock account seeded: {MOCK_USERNAME} ({MOCK_EMAIL}) "
            f"| password: {MOCK_PASSWORD} | phone: {MOCK_PHONE}"
        )
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to seed mock account: {e}")
        return False
    finally:
        session.close()
