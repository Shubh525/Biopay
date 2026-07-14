"""
Transactions Blueprint — /api/transactions, /api/transactions/<id>

All routes require a valid JWT in the Authorization header.
"""

import uuid
import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from palm_secure.db import SessionLocal
from palm_secure.models import Transaction
from app.middleware import token_required

logger = logging.getLogger(__name__)

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/api/transactions", methods=["POST"])
@token_required
def create_transaction(current_user):
    """Create a new transaction."""
    data = request.json or {}
    user_id = data.get("user_id")
    amount = data.get("amount")
    description = data.get("description", "")
    status = data.get("status", "pending")

    if not user_id or amount is None:
        return jsonify({"error": "user_id and amount are required"}), 400

    session = SessionLocal()
    try:
        txn = Transaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=float(amount),
            description=description,
            status=status,
        )
        session.add(txn)
        session.commit()

        return jsonify({
            "message": "Transaction created",
            "transaction": {
                "id": txn.id,
                "user_id": txn.user_id,
                "amount": txn.amount,
                "description": txn.description,
                "status": txn.status,
                "timestamp": txn.timestamp.isoformat(),
            },
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Transaction insert failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()


@transactions_bp.route("/api/transactions", methods=["GET"])
@token_required
def list_transactions(current_user):
    """Return all transactions, newest first."""
    session = SessionLocal()
    try:
        txns = session.query(Transaction).order_by(Transaction.timestamp.desc()).all()
        return jsonify([
            {
                "id": t.id,
                "user_id": t.user_id,
                "amount": t.amount,
                "description": t.description,
                "status": t.status,
                "timestamp": t.timestamp.isoformat(),
            }
            for t in txns
        ])
    except SQLAlchemyError as e:
        logger.error(f"Transaction fetch failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()


@transactions_bp.route("/api/transactions/<string:txn_id>", methods=["GET"])
@token_required
def get_transaction(current_user, txn_id: str):
    """Return a single transaction by ID."""
    session = SessionLocal()
    try:
        txn = session.query(Transaction).filter_by(id=txn_id).first()
        if not txn:
            return jsonify({"error": "Transaction not found"}), 404

        return jsonify({
            "id": txn.id,
            "user_id": txn.user_id,
            "amount": txn.amount,
            "description": txn.description,
            "status": txn.status,
            "timestamp": txn.timestamp.isoformat(),
        })
    except SQLAlchemyError as e:
        logger.error(f"Transaction fetch failed: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()
