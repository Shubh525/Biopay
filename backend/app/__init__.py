"""
BioPay Backend — Application Factory
=====================================
Creates and configures the Flask app.
Import this module to get a fully wired app instance.
"""

import eventlet
eventlet.monkey_patch()

import os
import logging
import warnings
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from .extensions import socketio, limiter


def create_app() -> Flask:
    """
    Application factory.  Returns a fully configured Flask app.
    All blueprints, extensions, and error handlers are registered here.
    """
    app = Flask(__name__)

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    warnings.filterwarnings("ignore")

    # ── Config ────────────────────────────────────────────────────────────────
    app.secret_key = os.environ.get("SESSION_SECRET")
    if not app.secret_key:
        raise RuntimeError(
            "SESSION_SECRET environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # ── CORS — single source of truth ────────────────────────────────────────
    allowed_origins = [
        os.environ.get("FRONTEND_URL", "http://localhost:5173"),
        "http://127.0.0.1:5173",
    ]
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    # ── Extensions ────────────────────────────────────────────────────────────
    socketio.init_app(app, cors_allowed_origins=allowed_origins)
    limiter.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.bio import bio_bp
    from .routes.device import device_bp
    from .routes.transactions import transactions_bp
    from .routes.otp import otp_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bio_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(otp_bp)

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"error": "Endpoint not found", "message": str(e)}), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import jsonify
        logging.getLogger(__name__).error(f"Server error: {e}")
        return jsonify({"error": "Server error", "message": str(e)}), 500

    return app
