# """
# Palm Secure SDK Constants
# =========================

# This module defines constants used throughout the PalmSecure SDK.
# """

# # Device identifiers
# PALM_SECURE_VID = 0x04C5  # Fujitsu Frontech Limited Vendor ID
# PALM_SECURE_PID = 0x125A  # PalmSecure Product ID

# # Device states
# DEVICE_STATES = {
#     "DISCONNECTED": "disconnected",
#     "CONNECTED": "connected",
#     "READY": "ready",
#     "BUSY": "busy",
#     "ERROR": "error"
# }

# # Control endpoint commands - these would need to be replaced with actual values
# # from the device protocol documentation
# CONTROL_ENDPOINTS = {
#     "GET_STATUS": 0x01,
#     "GET_VERSION": 0x02,
#     "GET_FIRMWARE": 0x03,
#     "INITIALIZE": 0x04,
#     "RESET": 0x05,
#     "START_SCAN": 0x06,
#     "STOP_SCAN": 0x07,
#     "GET_IMAGE": 0x08,
#     "SET_PARAM": 0x09,
#     "GET_PARAM": 0x0A
# }

# # Connection/operation timeouts in milliseconds
# CONNECTION_TIMEOUT = 5000  # 5 seconds
# OPERATION_TIMEOUT = 10000  # 10 seconds
# SCAN_TIMEOUT = 30000  # 30 seconds

# # Driver compatibility information
# COMPATIBLE_DRIVER_VERSIONS = [
#     "3.1.6.3",  # Older version observed in logs
#     "3.1.7.4",  # Middle version observed in logs
#     "3.2.0.1"   # Newest version observed in logs
# ]

# # Default device parameters
# DEFAULT_PARAMS = {
#     "EXPOSURE": 100,  # Default exposure value
#     "GAIN": 50,       # Default gain value
#     "THRESHOLD": 128, # Default threshold value
#     "TIMEOUT": 10000  # Default operation timeout in milliseconds
# }

# # Error codes
# ERROR_CODES = {
#     0x00: "Success",
#     0x01: "General Error",
#     0x02: "Not Connected",
#     0x03: "Invalid Parameter",
#     0x04: "Timeout",
#     0x05: "Device Busy",
#     0x06: "Feature Not Supported",
#     0x07: "Permission Denied",
#     0x08: "Out of Memory",
#     0x09: "Firmware Error",
#     0x0A: "Device Not Initialized",
#     0x0B: "Data Invalid",
#     0x0C: "Sensor Error",
#     0xC0000034: "Device Not Found",
#     0xC0000719: "Device Settings Migration Failed",
# }

# # USB Interface class codes
# USB_CLASS_CODES = {
#     0x00: "Device",
#     0x01: "Audio",
#     0x02: "Communications and CDC Control",
#     0x03: "Human Interface Device",
#     0x05: "Physical",
#     0x06: "Image",
#     0x07: "Printer",
#     0x08: "Mass Storage",
#     0x09: "Hub",
#     0x0A: "CDC-Data",
#     0x0B: "Smart Card",
#     0x0D: "Content Security",
#     0x0E: "Video",
#     0x0F: "Personal Healthcare",
#     0x10: "Audio/Video Devices",
#     0x11: "Billboard Device Class",
#     0xDC: "Diagnostic Device",
#     0xE0: "Wireless Controller",
#     0xEF: "Miscellaneous",
#     0xFE: "Application Specific",
#     0xFF: "Vendor Specific"
# }

# # Known device GUID
# PALM_SECURE_GUID = "{c6cf0a04-cc5d-4d64-89ad-9dd862ed4c6a}"


# -- 2 --
"""
Palm Secure SDK Constants
=========================

This module defines constants used throughout the PalmSecure SDK.
"""

# Device identifiers
PALM_SECURE_VID = 0x04C5  # Fujitsu Frontech Limited Vendor ID
PALM_SECURE_PID = 0x125A  # PalmSecure Product ID

# Add the required vendor and product ID lists
VENDOR_IDS = [
    0x04C5,  # Fujitsu
    0x0BF8,  # Fujitsu Component Limited
]

PRODUCT_IDS = [
    0x1000,  # Generic PalmSecure
    0x1001,  # PalmSecure V2
    0x1002,  # PalmSecure F-Pro
    0x125A,  # PalmSecure Product ID from your constants
]

DEVICE_CLASSES = [
    0x00,  # Device class per interface
    0xFF,  # Vendor specific class
]

# Device states
DEVICE_STATES = {
    "DISCONNECTED": "disconnected",
    "CONNECTED": "connected",
    "READY": "ready",
    "BUSY": "busy",
    "ERROR": "error"
}

# Control endpoint commands - these would need to be replaced with actual values
# from the device protocol documentation
CONTROL_ENDPOINTS = {
    "GET_STATUS": 0x01,
    "GET_VERSION": 0x02,
    "GET_FIRMWARE": 0x03,
    "INITIALIZE": 0x04,
    "RESET": 0x05,
    "START_SCAN": 0x06,
    "STOP_SCAN": 0x07,
    "GET_IMAGE": 0x08,
    "SET_PARAM": 0x09,
    "GET_PARAM": 0x0A
}

# Map the constants expected by device.py
COMMAND_INITIALIZE = CONTROL_ENDPOINTS["INITIALIZE"]
COMMAND_RESET = CONTROL_ENDPOINTS["RESET"]
COMMAND_GET_STATUS = CONTROL_ENDPOINTS["GET_STATUS"]

# Connection/operation timeouts in milliseconds
CONNECTION_TIMEOUT = 5000  # 5 seconds
OPERATION_TIMEOUT = 10000  # 10 seconds
SCAN_TIMEOUT = 30000  # 30 seconds

# Driver compatibility information
COMPATIBLE_DRIVER_VERSIONS = [
    "3.1.6.3",  # Older version observed in logs
    "3.1.7.4",  # Middle version observed in logs
    "3.2.0.1"   # Newest version observed in logs
]

# Default device parameters
DEFAULT_PARAMS = {
    "EXPOSURE": 100,  # Default exposure value
    "GAIN": 50,       # Default gain value
    "THRESHOLD": 128,  # Default threshold value
    "TIMEOUT": 10000  # Default operation timeout in milliseconds
}

# Success status code
STATUS_OK = 0x00

# Error codes
ERROR_CODES = {
    'UNKNOWN_ERROR': 0x01,
    'CONNECTION_ERROR': 0x02,
    'INITIALIZATION_ERROR': 0x03,
    'TIMEOUT_ERROR': 0x04,
    'OPERATION_ERROR': 0x05,
    'DEVICE_BUSY': 0x05,
    'INVALID_PARAMETER': 0x03,
    'NOT_INITIALIZED': 0x0A,
    'DEVICE_NOT_FOUND': 0xC0000034,
    'PERMISSION_DENIED': 0x07,
    'FIRMWARE_ERROR': 0x09,
    'DRIVER_ERROR': 0x01,
}

# Legacy error codes mapping
ERROR_CODE_DESCRIPTIONS = {
    0x00: "Success",
    0x01: "General Error",
    0x02: "Not Connected",
    0x03: "Invalid Parameter",
    0x04: "Timeout",
    0x05: "Device Busy",
    0x06: "Feature Not Supported",
    0x07: "Permission Denied",
    0x08: "Out of Memory",
    0x09: "Firmware Error",
    0x0A: "Device Not Initialized",
    0x0B: "Data Invalid",
    0x0C: "Sensor Error",
    0xC0000034: "Device Not Found",
    0xC0000719: "Device Settings Migration Failed",
}

# USB Interface class codes
USB_CLASS_CODES = {
    0x00: "Device",
    0x01: "Audio",
    0x02: "Communications and CDC Control",
    0x03: "Human Interface Device",
    0x05: "Physical",
    0x06: "Image",
    0x07: "Printer",
    0x08: "Mass Storage",
    0x09: "Hub",
    0x0A: "CDC-Data",
    0x0B: "Smart Card",
    0x0D: "Content Security",
    0x0E: "Video",
    0x0F: "Personal Healthcare",
    0x10: "Audio/Video Devices",
    0x11: "Billboard Device Class",
    0xDC: "Diagnostic Device",
    0xE0: "Wireless Controller",
    0xEF: "Miscellaneous",
    0xFE: "Application Specific",
    0xFF: "Vendor Specific"
}

# Known device GUID
PALM_SECURE_GUID = "{c6cf0a04-cc5d-4d64-89ad-9dd862ed4c6a}"
