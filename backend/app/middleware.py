"""
Authentication middleware — @token_required decorator.

Apply to any route that should reject unauthenticated callers.
The decoded user payload is injected as the first positional arg.
"""

import functools
import logging
from flask import request, jsonify
from palm_secure.jwt_utils import decode_token

logger = logging.getLogger(__name__)


def token_required(fn):
    """
    Decorator that validates the JWT in the Authorization header.

    Usage::

        @app.route("/api/protected")
        @token_required
        def protected_route(current_user):
            # current_user is the decoded JWT payload (dict)
            ...

    Expected header format::

        Authorization: Bearer <token>
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        decoded = decode_token(token)

        # decode_token returns a string on error, dict on success
        if isinstance(decoded, str):
            logger.warning(f"Token validation failed: {decoded}")
            return jsonify({"error": decoded}), 401

        return fn(decoded, *args, **kwargs)

    return wrapper
