"""
Palm Secure SDK Exceptions
==========================

This module contains custom exceptions for the PalmSecure SDK.

NOTE: The original class names ConnectionError, TimeoutError, and PermissionError
shadow Python builtins. They are kept as aliases for backward compatibility
(device.py uses them extensively), but new code should use the Device* prefixed names.
"""


class DeviceNotFoundError(Exception):
    """Exception raised when a PalmSecure device cannot be found."""
    pass


class DeviceConnectionError(Exception):
    """Exception raised when there is an error connecting to a device."""
    pass


# Backward-compatible alias — shadows the builtin, but device.py depends on this name.
ConnectionError = DeviceConnectionError


class OperationError(Exception):
    """Exception raised when a device operation fails."""
    pass


class InitializationError(Exception):
    """Exception raised when device initialization fails."""
    pass


class DeviceTimeoutError(Exception):
    """Exception raised when a device operation times out."""
    pass


# Backward-compatible alias — shadows the builtin, but device.py depends on this name.
TimeoutError = DeviceTimeoutError


class DriverCompatibilityError(Exception):
    """Exception raised when there is a driver compatibility issue."""
    pass


class FirmwareError(Exception):
    """Exception raised when there is a firmware related error."""
    pass


class DevicePermissionError(Exception):
    """Exception raised when there is insufficient permissions to access the device."""
    pass


# Backward-compatible alias — shadows the builtin, but kept for compatibility.
PermissionError = DevicePermissionError
