"""
BioPay Backend — Entry Point

Run with:
    python main.py                    (development)
    eventlet wsgi main:app            (production — single worker)
    gunicorn -k eventlet -w 1 main:app (production — gunicorn)
"""
import eventlet
eventlet.monkey_patch()

import os  # noqa: E402
import socket  # noqa: E402
from app import create_app  # noqa: E402
from app.extensions import socketio  # noqa: E402
from palm_secure.db import init_db  # noqa: E402
from account import seed_mock_account  # noqa: E402


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

    init_db()

    # Only seed mock data when explicitly opted in (local dev only).
    # Never set SEED_MOCK_DATA=true on the production server.
    if os.getenv("SEED_MOCK_DATA", "false").lower() == "true":
        seed_mock_account()
    else:
        import logging  # noqa: E402
        logging.getLogger(__name__).info(
            "Mock seeding skipped (SEED_MOCK_DATA is not 'true'). "
            "Set SEED_MOCK_DATA=true in .env for local development only."
        )

    port = int(os.getenv("PORT", 5000))
    local_ip = get_local_ip()
    print("\nServer is running!")
    print("Access it on:")
    print(f"   Localhost  ->  http://127.0.0.1:{port}/api/health")
    print(f"   Network    ->  http://{local_ip}:{port}/api/health\n")

    socketio.run(app, host="0.0.0.0", port=port, debug=False)
