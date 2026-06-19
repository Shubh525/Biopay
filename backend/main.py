"""
BioPay Backend — Entry Point

Run with:
    python main.py                    (development)
    eventlet wsgi main:app            (production — single worker)
    gunicorn -k eventlet -w 1 main:app (production — gunicorn)
"""

import socket
from app import create_app
from app.extensions import socketio
from palm_secure.db import init_db


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


# Module-level app so gunicorn can find it as `main:app`
app = create_app()


if __name__ == "__main__":
    import os
    import sys

    init_db()

    local_ip = get_local_ip()
    print(f"\nServer is running!")
    print(f"Access it on:")
    print(f"   • Localhost  →  http://127.0.0.1:5000")
    print(f"   • Network    →  http://{local_ip}:5000\n")

    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
