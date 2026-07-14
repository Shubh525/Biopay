import os
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )


def generate_token(user_data, expires_in=3600):
    payload = {
        "user": user_data,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["user"]
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"
