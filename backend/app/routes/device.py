"""
Device Blueprint — /api/device/status, /api/diagnostics/run
"""

import time
import logging
from flask import Blueprint, jsonify

from palm_secure import PalmSecureDevice, find_devices
from palm_secure.diagnostics import DiagnosticsManager

logger = logging.getLogger(__name__)

device_bp = Blueprint("device", __name__)

# Module-level device state (single process — see Pack 4 for Redis migration)
_app_state = {
    "devices": [],
    "connected_device": None,
    "last_refresh": 0,
}


# ── Routes ────────────────────────────────────────────────────────────────────

@device_bp.route("/api/device/status", methods=["GET"])
def device_status():
    """Real-time detection of Palm Vein Scanner status."""
    import os
    SIMULATE = os.getenv("SIMULATE", "false").lower() == "true"

    if SIMULATE:
        return jsonify({
            "name": "Fujitsu PalmSecure F Pro (Simulated)",
            "id": "SIM-DEV-12345",
            "firmware": "1.0.0-sim",
            "connected": True,
            "timestamp": time.time(),
        })

    try:
        try:
            devices = find_devices()
        except Exception as e:
            logger.warning(f"Error calling find_devices: {e}")
            devices = []

        _app_state["devices"] = devices
        _app_state["last_refresh"] = time.time()

        if not devices:
            _app_state["connected_device"] = None
            return jsonify({
                "name": "No device detected",
                "id": "N/A",
                "firmware": "—",
                "connected": False,
                "timestamp": time.time(),
            })

        selected = devices[0]

        # selected can be a dict (from find_devices) or device object
        selected_id = getattr(selected, "device_id", None) or selected.get("device_id") or selected.get("serial_number")
        selected_name = getattr(selected, "device_name", None) or selected.get("device_name") or selected.get("product") or "PalmSecure Sensor"

        if (
            _app_state["connected_device"] is None
            or getattr(_app_state["connected_device"], "device_id", None) != selected_id
        ):
            try:
                connected = PalmSecureDevice(selected_id)
                connected.connect()
                _app_state["connected_device"] = connected
                logger.info(f"Connected to device {selected_id}")
            except Exception as e:
                logger.error(f"Failed to connect device: {e}")
                return jsonify({
                    "name": selected_name,
                    "id": selected_id,
                    "firmware": "—",
                    "connected": False,
                    "error": str(e),
                    "timestamp": time.time(),
                }), 500

        device = _app_state["connected_device"]
        return jsonify({
            "name": getattr(device, "device_name", "Palm Vein Sensor"),
            "id": getattr(device, "device_id", "Unknown"),
            "firmware": getattr(device, "firmware_version", "Unknown"),
            "connected": True,
            "timestamp": time.time(),
        })

    except Exception as e:
        logger.error(f"Device status check failed: {e}")
        _app_state["connected_device"] = None
        return jsonify({
            "name": "Error detecting device",
            "id": "—",
            "firmware": "—",
            "connected": False,
            "error": str(e),
            "timestamp": time.time(),
        }), 500


@device_bp.route("/api/diagnostics/run", methods=["GET"])
def run_diagnostics():
    """Run full hardware and system diagnostics."""
    import os
    SIMULATE = os.getenv("SIMULATE", "false").lower() == "true"

    if SIMULATE:
        return jsonify({
            "usb_subsystem": "OK",
            "driver_status": "OK",
            "permissions": "OK",
            "device_detection": "OK",
            "network": "OK",
            "devices_found": 1,
            "ready": True,
            "message": "Diagnostics clean. Device simulated and ready.",
            "issues": [],
        }), 200

    try:
        diag = DiagnosticsManager()
        results = diag.run_all_diagnostics()
        overall = results.get("overall", {})
        device_detect = results.get("device_detection", {})

        return jsonify({
            "usb_subsystem": results["usb_subsystem"].get("status"),
            "driver_status": results["drivers"].get("status"),
            "permissions": results["permissions"].get("status"),
            "device_detection": results["device_detection"].get("status"),
            "network": results["network"].get("status"),
            "devices_found": device_detect.get("devices_found", 0),
            "ready": overall.get("ready", False),
            "message": overall.get("message"),
            "issues": overall.get("issues", []),
        }), 200

    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        return jsonify({"error": str(e)}), 500


@device_bp.teardown_app_request
def cleanup_device(exception=None):
    """Disconnect device on app context teardown."""
    device = _app_state.get("connected_device")
    if device is not None:
        try:
            device.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting device during cleanup: {e}")
        _app_state["connected_device"] = None
