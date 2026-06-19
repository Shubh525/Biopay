# app.py

import eventlet
eventlet.monkey_patch()

import os
import sys
import time
import base64
import random
import logging
import warnings
import datetime
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
from dotenv import load_dotenv
import uuid
# --- Load env FIRST ---
load_dotenv()

# --- Your project modules ---
from palm_secure.jwt_utils import generate_token, decode_token
from palm_secure import PalmSecureDevice, find_devices, get_version
from palm_secure.exceptions import DeviceNotFoundError, ConnectionError
from palm_secure.diagnostics import DiagnosticsManager
from palm_secure.securityLayer import PalmVeinPaymentEncryption
from palm_secure.db import SessionLocal, init_db
from palm_secure.models import User, ContactMessage, Transaction

# -----------------------------------------------------------------------------
# Config & Globals
# -----------------------------------------------------------------------------

SIMULATE = os.getenv("SIMULATE", "false").lower() == "true"

# Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

ALLOWED_ORIGINS = [
    os.environ.get("FRONTEND_URL", "http://localhost:5173"),
    "http://127.0.0.1:5173",
]

CORS(
    app,
    resources={r"/api/*": {
        "origins": ALLOWED_ORIGINS
    }},
    supports_credentials=True
)

# Realtime, rate limiting
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])


encryption_layer = PalmVeinPaymentEncryption()

app_state = {
    "devices": [],
    "connected_device": None,
    "diagnostic_results": None,
    "last_refresh": 0,
    "backend_available": True,
}

# api for extract bio id of new user 
@app.route("/api/scan_bio_id", methods=["GET", "POST"])
def scan_bio_id():
    """Capture biometric template for ENROLLMENT (registration only)"""
    global last_scan_time
    current_time = time.time()
    
    if current_time - last_scan_time < SCAN_COOLDOWN:
        return jsonify({
            "error": f"Please wait {SCAN_COOLDOWN - (current_time - last_scan_time):.1f} seconds between scans"
        }), 429
    
    last_scan_time = current_time
    
    try:
        if SIMULATE:
            simulated = base64.b64encode(b"ENROLLMENT_TEMPLATE").decode()
            logging.info(f"[SIMULATED ENROLLMENT SCAN] bio_id_base64={simulated}")
            return jsonify({"bio_id_base64": simulated, "status": "success"})
        
        # ✅ Use "capture" for ENROLLMENT templates
        bio = run_java_bridge(["capture"], timeout=45)
        
        if not bio:
            return jsonify({"error": "Empty capture from Java bridge"}), 500

        # Extract clean Base64 template from verbose output
        clean_bio = extract_clean_template(bio)
        
        if clean_bio and len(clean_bio) > 100:
            logging.info(f"[HARDWARE ENROLLMENT SCAN] Extracted enrollment template length={len(clean_bio)}")
            return jsonify({
                "bio_id_base64": clean_bio,
                "status": "success", 
                "template_length": len(clean_bio),
                "template_type": "enrollment"
            })
        else:
            logging.warning("No valid enrollment template found in response")
            return jsonify({"error": "No valid enrollment data captured"}), 500
            
    except Exception as e:
        logging.error(f"Enrollment scan error: {e}")
        return jsonify({"error": str(e)}), 500
# route for google login
@app.route("/api/google-login", methods=["POST", "OPTIONS"])
def google_login():
    if request.method == "OPTIONS":
        return "", 200

    data = request.json or {}
    email = (data.get("email") or "").strip()
    google_id = (data.get("google_id") or "").strip()

    if not email or not google_id:
        return jsonify({"error": "Missing Google credentials"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()

        if not user:
            return jsonify({
                "error": "NO_BIO_REGISTRATION",
                "message": "Google login detected but biometric registration required"
            }), 403

        token = generate_token({
            "username": user.username,
            "email": user.email
        })

        return jsonify({
            "msg": "login successful",
            "token": token,
            "name": user.username
        }), 200
    finally:
        session.close()
#created for capturing bio id of existing users does not store just for comparing but never completed
@app.route("/api/scan_auth_feature", methods=["GET", "POST"]) 
def scan_auth_feature():
    """Extract authentication features (NOT enrollment)"""
    global last_scan_time
    current_time = time.time()
    
    if current_time - last_scan_time < SCAN_COOLDOWN:
        return jsonify({
            "error": f"Please wait {SCAN_COOLDOWN - (current_time - last_scan_time):.1f} seconds between scans"
        }), 429
    
    last_scan_time = current_time
    
    try:
        if SIMULATE:
            simulated = base64.b64encode(b"AUTH_FEATURE").decode()
            logging.info(f"[SIMULATED AUTH SCAN] auth_feature={simulated}")
            return jsonify({"auth_feature": simulated, "status": "success"})
        
        # ✅ Use "extract_auth" for AUTHENTICATION features
        bio = run_java_bridge(["extract_auth"], timeout=30)
        
        if not bio:
            return jsonify({"error": "Empty auth feature from Java bridge"}), 500

        # Extract clean Base64 template from verbose output
        clean_bio = extract_clean_template(bio)
        
        if clean_bio and len(clean_bio) > 100:
            logging.info(f"[HARDWARE AUTH SCAN] Extracted auth feature length={len(clean_bio)}")
            return jsonify({
                "auth_feature": clean_bio,
                "status": "success",
                "feature_length": len(clean_bio),
                "template_type": "authentication"
            })
        else:
            logging.warning("No valid authentication feature found in response")
            return jsonify({"error": "No valid authentication data captured"}), 500
            
    except Exception as e:
        logging.error(f"Auth scan error: {e}")
        return jsonify({"error": str(e)}), 500
# old SDK sometimes returns text mixed with logs + Base64 instead of pure Base64
def extract_clean_template(raw_output):
    """Extract high-quality template from raw Java output"""
    try:
        lines = raw_output.split('\n')
        for line in lines:
            line = line.strip()
            # Look for valid Base64 that's not a fallback
            if (len(line) > 100 and
                line.replace('=', '').replace('+', '').replace('/', '').isalnum() and
                not line.startswith('FALLBACK') and
                not line.startswith('ERROR')):
                return line
        
        # Fallback: look for any valid Base64
        for line in lines:
            line = line.strip()
            if len(line) > 50 and line.replace('=', '').replace('+', '').replace('/', '').isalnum():
                return line
        
        return None
    except Exception as e:
        logger.error(f"Template extraction failed: {e}")
        return None

#created for validating existing bio id but not completed
@app.route("/api/validate_bio", methods=["POST"])
def validate_bio():
    """Validate using proper enrollment vs authentication template comparison"""
    data = request.json or {}
    auth_feature = (data.get("bio_id") or "").strip()  # This should be AUTH feature now
    
    if not auth_feature:
        return jsonify({"match": False, "error": "Authentication feature required"}), 400
    
    # ✅ VALIDATE INPUT FIRST
    if len(auth_feature) < 100 or not auth_feature.replace('=', '').replace('+', '').replace('/', '').isalnum():
        logger.warning(f"Invalid auth feature format: {auth_feature[:20]}...")
        return jsonify({"match": False, "verdict": "INVALID_TEMPLATE"}), 400
    
    # ✅ REJECT FAKE TEMPLATES
    if any(fake in auth_feature.upper() for fake in ["FAKE", "TEST", "MOCK", "DUMMY"]):
        logger.warning(f"Fake auth feature detected: {auth_feature[:20]}...")
        return jsonify({"match": False, "verdict": "FAKE_TEMPLATE"}), 400

    session = SessionLocal()
    try:
        users = session.query(User).all()
        
        if not users:
            logger.info("No users in database")
            return jsonify({"match": False, "verdict": "NO_USERS"}), 404
        
        for user in users:
            try:
                # Decrypt stored ENROLLMENT template
                enrollment_template = encryption_layer.decrypt_bio_template(user.bio_id_encrypted)
                if not enrollment_template:
                    logger.warning(f"Could not decrypt enrollment template for {user.username}")
                    continue

                # ✅ LOG THE COMPARISON
                logger.info(f"Comparing templates for {user.username}")
                logger.debug(f"Stored enrollment template: {enrollment_template[:50]}...")
                logger.debug(f"Live auth feature: {auth_feature[:50]}...")

                # ✅ PROPER SDK COMPARISON - enrollment template vs auth feature
                comparison_result = run_java_bridge([
                    "compare", enrollment_template, auth_feature
                ], timeout=15)
                
                logger.info(f"Java bridge result for {user.username}: {comparison_result}")

                # ✅ STRICT MATCH CHECKING
                if comparison_result and "MATCH" in str(comparison_result).upper() and "NO_MATCH" not in str(comparison_result).upper():
                    token = generate_token({
                        "username": user.username,
                        "email": user.email
                    })
                    
                    logger.info(f"✅ SUCCESSFUL MATCH for {user.username}")
                    return jsonify({
                        "match": True,
                        "verdict": "SDK_MATCH",
                        "user": {
                            "username": user.username,
                            "email": user.email,
                            "phone": user.phone
                        },
                        "token": token
                    }), 200
                else:
                    logger.info(f"❌ No match for {user.username}: {comparison_result}")

            except Exception as e:
                logger.warning(f"Comparison failed for {user.username}: {e}")
                continue

        logger.info("No matching user found")
        return jsonify({
            "match": False,
            "verdict": "NO_MATCH"
        }), 404

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"match": False, "error": str(e)}), 500
    finally:
        session.close()
#called for checking device status
@app.route("/api/device/status", methods=["GET"])
def device_status():
    """
    Real-time detection of Palm Vein Scanner status.
    Automatically refreshes app_state with live hardware info.
    """
    try:
        # Always refresh the device list
        devices = find_devices()
        app_state["devices"] = devices
        app_state["last_refresh"] = time.time()

        # If no devices found
        if not devices:
            app_state["connected_device"] = None
            return jsonify({
                "name": "No device detected",
                "id": "N/A",
                "firmware": "—",
                "connected": False,
                "timestamp": time.time()
            })

        # Pick the first available device
        selected_device = devices[0]

        # If not already connected or different device connected, connect it
        if (app_state["connected_device"] is None or
                getattr(app_state["connected_device"], "device_id", None) != selected_device.device_id):
            try:
                connected = PalmSecureDevice(selected_device.device_id)
                connected.connect()
                app_state["connected_device"] = connected
                logger.info(f"✅ Connected to device {connected.device_id}")
            except Exception as e:
                logger.error(f"❌ Failed to connect device: {e}")
                return jsonify({
                    "name": selected_device.device_name,
                    "id": selected_device.device_id,
                    "firmware": "—",
                    "connected": False,
                    "error": str(e),
                    "timestamp": time.time()
                }), 500

        # Pull firmware info (if SDK supports)
        firmware = getattr(app_state["connected_device"], "firmware_version", "Unknown")

        return jsonify({
            "name": getattr(app_state["connected_device"], "device_name", "Palm Vein Sensor"),
            "id": getattr(app_state["connected_device"], "device_id", "Unknown"),
            "firmware": firmware,
            "connected": True,
            "timestamp": time.time()
        })

    except Exception as e:
        logger.error(f"Device status check failed: {e}")
        app_state["connected_device"] = None
        return jsonify({
            "name": "Error detecting device",
            "id": "—",
            "firmware": "—",
            "connected": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

#called on diagnostic page
@app.route("/api/diagnostics/run", methods=["GET"])
def run_diagnostics():
    """Run full hardware and system diagnostics using DiagnosticsManager"""
    try:
        diag = DiagnosticsManager()
        results = diag.run_all_diagnostics()
        overall = results.get("overall", {})
        device_detect = results.get("device_detection", {})

        response = {
            "usb_subsystem": results["usb_subsystem"].get("status"),
            "driver_status": results["drivers"].get("status"),
            "permissions": results["permissions"].get("status"),
            "device_detection": results["device_detection"].get("status"),
            "network": results["network"].get("status"),
            "devices_found": device_detect.get("devices_found", 0),
            "ready": overall.get("ready", False),
            "message": overall.get("message"),
            "issues": overall.get("issues", []),
        }

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# Registration / Auth
# -----------------------------------------------------------------------------
#Api for regestering new user
@app.route("/api/register_user", methods=["POST"])
@limiter.limit("5/minute")
def register_user():
    data = request.json or {}
    bio_id = (data.get("bio_id") or "").strip()  # This should be ENROLLMENT template
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip() 
    phone = (data.get("phone") or "").strip()
    password = (data.get("password") or "").encode("utf-8")
    
    if not all([bio_id, username, email, phone, password]):
        return jsonify({"error": "Missing fields"}), 400

    # Enhanced validation
    if len(bio_id) < 100:
        return jsonify({"error": "Enrollment template quality insufficient"}), 422

    session = SessionLocal()
    try:
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "User with this email already exists."}), 400
        
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "User with this username already exists."}), 400

        # Enhanced security hashing
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode("utf-8")
        bio_id_hash = bcrypt.hashpw(bio_id.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        bio_id_encrypted = encryption_layer.encrypt_bio_template(bio_id)

        user = User(
            id=str(__import__("uuid").uuid4()),
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            bio_id_hash=bio_id_hash,
            bio_id_encrypted=bio_id_encrypted
        )

        session.add(user)
        session.commit()

        token = generate_token({
            "username": username,
            "email": email,
            "registration": "enhanced"
        })

        logger.info(f"✅ USER REGISTERED: {username} ({email}) with enrollment template")
        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id,
            "token": token
        }), 201

    except Exception as e:
        session.rollback()
        logger.error(f"Registration failed: {e}")
        return jsonify({"error": "Registration failed"}), 500
    finally:
        session.close()

#Api for login with form inputs
@app.route("/api/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    data = request.json or {}
    identifier = (data.get("identifier") or "").strip()  # phone or email
    password = (data.get("password") or "").encode("utf-8")

    if not identifier or not password:
        return jsonify({"error": "Missing credentials"}), 400

    session = SessionLocal()
    try:
        # Find user by email or phone
        user = session.query(User).filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()

        if not user:
            return jsonify({"msg": "user not register"}), 404

        # Check password
        if not bcrypt.checkpw(password, user.password_hash.encode("utf-8")):
            return jsonify({"msg": "incorrect password"}), 401

        # Generate token
        token = generate_token({
            "username": user.username,
            "email": user.email
        })

        logger.info(f"✅ LOGIN SUCCESS: {user.username}")
        return jsonify({
            "msg": "login successful",
            "token": token,
            "name": user.username
        }), 200

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()



# -----------------------------------------------------------------------------
# Error handlers
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found", "message": str(e)}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Server error", "message": str(e)}), 500

# -----------------------------------------------------------------------------
# OTP functionality (keeping your existing implementation)
# -----------------------------------------------------------------------------
# Function to send otp on email
def send_otp_email(to_email, otp):
    from_email = os.environ.get("SMTP_EMAIL")
    from_password = os.environ.get("SMTP_PASSWORD")
    subject = "Your OTP Code"
    body = f"Your OTP code is: {otp}"
    
    if not from_email or not from_password:
        logger.warning("SMTP credentials not configured; skipping real email send.")
        return

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"OTP email sent to {to_email}")
    except Exception as e:
        logging.error(f"Email sending failed: {e}")

#Route which generate otp and call above function to send otp on email
@app.route("/api/send-otp/email", methods=["POST"])
def send_otp_email_route():
    data = request.json or request.form or {}
    email = (data.get("email") or "").strip()
    
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    
    otp = str(random.randint(100000, 999999))
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
    otp_store[email] = {"otp": otp, "expiry": expiry}
    
    logging.info(f"Generated OTP for {email}: {otp}")
    send_otp_email(email, otp)
    return jsonify({"status": "success", "message": "OTP sent successfully", "email": email})

# Used to verify otp
@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or request.form or {}
    otp = (data.get("otp") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    
    if not otp:
        return jsonify({"status": "error", "message": "OTP is required"}), 400
    
    key = email or phone
    if not key or key not in otp_store:
        return jsonify({"status": "error", "message": "No OTP sent to this user"}), 404
    
    stored = otp_store.get(key)
    if datetime.datetime.now() > stored["expiry"]:
        otp_store.pop(key, None)
        return jsonify({"status": "error", "message": "OTP expired"}), 410
    
    if stored["otp"] == otp:
        otp_store.pop(key, None)
        return jsonify({"status": "success", "message": "OTP verified"})
    
    return jsonify({"status": "error", "message": "Invalid OTP"}), 401

# -----------------------------------------------------------------------------
# Cleanup & Entrypoint  
# -----------------------------------------------------------------------------

@app.teardown_appcontext
def cleanup(exception=None):
    if app_state["connected_device"] is not None:
        try:
            app_state["connected_device"].disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting device during cleanup: {str(e)}")
        app_state["connected_device"] = None

if __name__ == "__main__":
    try:
        logger.info("🚀 Starting Enhanced Palm Vein Authentication System")
        logger.info("📊 Working Project Algorithm: ACTIVE")
        logger.info("✅ Proper Enrollment vs Authentication Template Separation")
        
        init_db()
        socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
        
    except Exception as e:
        logger.error(f"Error starting app: {e}")
        sys.exit(1)


# -------------------------------
# Transaction Endpoints
# -------------------------------
#Add New Transaction
@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    """Create a new transaction"""
    data = request.json or {}
    user_id = data.get("user_id")
    amount = data.get("amount")
    description = data.get("description", "")
    status = data.get("status", "pending")

    if not user_id or amount is None:
        return jsonify({"error": "user_id and amount are required"}), 400

    session = SessionLocal()
    try:
        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=float(amount),
            description=description,
            status=status
        )
        session.add(transaction)
        session.commit()

        return jsonify({
            "message": "Transaction created",
            "transaction": {
                "id": transaction.id,
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "description": transaction.description,
                "status": transaction.status,
                "timestamp": transaction.timestamp.isoformat()
            }
        }), 201
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Transaction insert failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()

# Used to print all transactions
@app.route("/api/transactions", methods=["GET"])
def list_transactions():
    """Get all transactions"""
    session = SessionLocal()
    try:
        transactions = session.query(Transaction).order_by(Transaction.timestamp.desc()).all()
        return jsonify([
            {
                "id": t.id,
                "user_id": t.user_id,
                "amount": t.amount,
                "description": t.description,
                "status": t.status,
                "timestamp": t.timestamp.isoformat()
            } for t in transactions
        ])
    except SQLAlchemyError as e:
        logger.error(f"Transaction fetch failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()

# Used to fetch transaction by its id
@app.route("/api/transactions/<string:txn_id>", methods=["GET"])
def get_transaction(txn_id):
    """Get a single transaction by ID"""
    session = SessionLocal()
    try:
        transaction = session.query(Transaction).filter_by(id=txn_id).first()
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        return jsonify({
            "id": transaction.id,
            "user_id": transaction.user_id,
            "amount": transaction.amount,
            "description": transaction.description,
            "status": transaction.status,
            "timestamp": transaction.timestamp.isoformat()
        })
    except SQLAlchemyError as e:
        logger.error(f"Transaction fetch failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()
