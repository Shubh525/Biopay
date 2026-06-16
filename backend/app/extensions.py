"""
Shared Flask extension singletons.
Import these in blueprints instead of creating new instances.
"""

from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialised without app — bound in create_app() via init_app()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
