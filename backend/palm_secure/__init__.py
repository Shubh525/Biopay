"""
Fujitsu PalmSecure SDK - Python Interface
=========================================

This package provides a Python SDK for interfacing with Fujitsu PalmSecure biometric devices.

Classes:
    PalmSecureDevice: Main interface for interacting with PalmSecure devices.
    DeviceNotFoundError: Exception raised when a device can't be found.
    ConnectionError: Exception raised when connection to a device fails.
    OperationError: Exception raised when a device operation fails.

Functions:
    find_devices(): Find available PalmSecure devices.
    get_version(): Get the SDK version.
"""

from .device import PalmSecureDevice, find_devices
from .exceptions import DeviceNotFoundError, ConnectionError, OperationError
from .diagnostics import DiagnosticsManager

__version__ = "0.1.0"


def get_version():
    """Return the current version of the SDK."""
    return __version__
