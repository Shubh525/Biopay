"""
Palm Secure SDK Exceptions
==========================

This module contains custom exceptions for the PalmSecure SDK.
"""


class DeviceNotFoundError(Exception):
    """Exception raised when a PalmSecure device cannot be found."""
    pass


class ConnectionError(Exception):
    """Exception raised when there is an error connecting to a device."""
    pass


class OperationError(Exception):
    """Exception raised when a device operation fails."""
    pass


class InitializationError(Exception):
    """Exception raised when device initialization fails."""
    pass


class TimeoutError(Exception):
    """Exception raised when a device operation times out."""
    pass


class DriverCompatibilityError(Exception):
    """Exception raised when there is a driver compatibility issue."""
    pass


class FirmwareError(Exception):
    """Exception raised when there is a firmware related error."""
    pass


class PermissionError(Exception):
    """Exception raised when there is insufficient permissions to access the device."""
    pass
