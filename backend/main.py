"""
PalmSecure SDK Demo Web Application - Main Entry Point

This file serves as the entry point for the Flask web application.
"""

from demo_app import socketio, app
import eventlet
eventlet.monkey_patch()
from palm_secure.db import init_db
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

if __name__ == "__main__":
    local_ip = get_local_ip()
    init_db()
    print(f"\nServer is running!")
    print(f"Access it on:")
    print(f"   • Localhost  →  http://127.0.0.1:5000")
    print(f"   • Network    →  http://{local_ip}:5000\n")

    socketio.run(app, host="0.0.0.0", port=5000, debug=False)


