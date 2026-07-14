# """
# Palm Secure SDK Utilities
# =========================

# This module provides utility functions for the PalmSecure SDK.
# """

# import re
# import platform
# import subprocess
# import sys
# import logging
# from typing import Dict, Any, List, Optional, Tuple
# import usb.core
# import usb.util

# from .constants import PALM_SECURE_VID, PALM_SECURE_PID

# logger = logging.getLogger(__name__)


# def parse_device_info(info_text: str) -> Dict[str, Any]:
#     """
#     Parse device information from text (like Windows device manager output).
    
#     Args:
#         info_text: Text containing device information
        
#     Returns:
#         Dict containing parsed device information
#     """
#     device_info = {
#         'vid': None,
#         'pid': None,
#         'driver_name': None,
#         'driver_version': None,
#         'driver_date': None,
#         'driver_provider': None,
#         'status': 'unknown'
#     }
    
#     # Parse VID and PID
#     vid_pid_match = re.search(r'USB\\VID_([0-9A-F]{4})&PID_([0-9A-F]{4})', info_text)
#     if vid_pid_match:
#         device_info['vid'] = int(vid_pid_match.group(1), 16)
#         device_info['pid'] = int(vid_pid_match.group(2), 16)
    
#     # Parse driver information
#     driver_name_match = re.search(r'Driver Name:\s*(.*)', info_text)
#     if driver_name_match:
#         device_info['driver_name'] = driver_name_match.group(1).strip()
    
#     driver_version_match = re.search(r'Driver Version:\s*([\d\.]+)', info_text)
#     if driver_version_match:
#         device_info['driver_version'] = driver_version_match.group(1).strip()
    
#     driver_date_match = re.search(r'Driver Date:\s*([\d/]+)', info_text)
#     if driver_date_match:
#         device_info['driver_date'] = driver_date_match.group(1).strip()
    
#     driver_provider_match = re.search(r'Driver Provider:\s*(.*)', info_text)
#     if driver_provider_match:
#         device_info['driver_provider'] = driver_provider_match.group(1).strip()
    
#     # Parse device status
#     if 'was configured' in info_text:
#         device_info['status'] = 'configured'
#     elif 'was started' in info_text:
#         device_info['status'] = 'started'
#     elif 'was deleted' in info_text:
#         device_info['status'] = 'deleted'
#     elif 'had a problem starting' in info_text:
#         device_info['status'] = 'error'
    
#     return device_info


# def is_admin() -> bool:
#     """
#     Check if the script is running with administrative privileges.
    
#     Returns:
#         bool: True if running as admin/root, False otherwise
#     """
#     if platform.system() == 'Windows':
#         try:
#             import ctypes
#             return ctypes.windll.shell32.IsUserAnAdmin() != 0
#         except:
#             return False
#     else:
#         # For Unix-like systems, check if user is root
#         return os.geteuid() == 0 if hasattr(os, 'geteuid') else False


# def get_system_usb_devices() -> List[Dict[str, Any]]:
#     """
#     Get information about all USB devices on the system.
    
#     Returns:
#         List of dictionaries containing device information
#     """
#     devices = []
    
#     try:
#         # Use libusb to get all USB devices
#         for dev in usb.core.find(find_all=True):
#             try:
#                 device_info = {
#                     'vid': dev.idVendor,
#                     'pid': dev.idProduct,
#                     'bus': dev.bus,
#                     'address': dev.address,
#                     'manufacturer': 'Unknown',
#                     'product': 'Unknown',
#                     'serial_number': 'Unknown'
#                 }
                
#                 try:
#                     # Try to get string descriptors (may fail for some devices)
#                     device_info['manufacturer'] = usb.util.get_string(dev, dev.iManufacturer)
#                     device_info['product'] = usb.util.get_string(dev, dev.iProduct)
#                     device_info['serial_number'] = usb.util.get_string(dev, dev.iSerialNumber)
#                 except (ValueError, usb.core.USBError) as e:
#                     # Skip if string descriptors can't be read
#                     pass
                
#                 devices.append(device_info)
            
#             except usb.core.USBError:
#                 # Skip devices that cause errors
#                 continue
    
#     except Exception as e:
#         logger.error(f"Error enumerating USB devices: {str(e)}")
    
#     return devices


# def find_palm_secure_devices() -> List[Dict[str, Any]]:
#     """
#     Find all PalmSecure devices connected to the system.
    
#     Returns:
#         List of dictionaries containing device information
#     """
#     palm_devices = []
    
#     # Get all USB devices
#     all_devices = get_system_usb_devices()
    
#     # Filter for PalmSecure devices
#     for device in all_devices:
#         if device['vid'] == PALM_SECURE_VID and device['pid'] == PALM_SECURE_PID:
#             palm_devices.append(device)
    
#     return palm_devices


# def get_device_path(bus: int, address: int) -> str:
#     """
#     Get the system path for a USB device.
    
#     Args:
#         bus: USB bus number
#         address: Device address on the bus
        
#     Returns:
#         String containing the device path
#     """
#     if platform.system() == 'Windows':
#         return f"USB\\VID_{PALM_SECURE_VID:04X}&PID_{PALM_SECURE_PID:04X}\\{bus}&{address}"
#     elif platform.system() == 'Linux':
#         return f"/dev/bus/usb/{bus:03d}/{address:03d}"
#     else:
#         return f"bus-{bus:03d}:{address:03d}"


# def is_driver_installed() -> Tuple[bool, Optional[str]]:
#     """
#     Check if the PalmSecure driver is installed on the system.
    
#     Returns:
#         Tuple of (is_installed, driver_version)
#     """
#     if platform.system() == 'Windows':
#         # On Windows, check for driver files and registry entries
#         try:
#             import winreg
            
#             # Check the registry for PalmSecure drivers
#             try:
#                 key_path = r"SYSTEM\CurrentControlSet\Services\WUDFRd\Parameters\Drivers"
#                 with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
#                     # Look for PalmSecure driver keys
#                     i = 0
#                     while True:
#                         try:
#                             subkey_name = winreg.EnumKey(key, i)
#                             if 'palm' in subkey_name.lower() or 'fujitsu' in subkey_name.lower():
#                                 # Found a potential match - get version
#                                 with winreg.OpenKey(key, subkey_name) as driver_key:
#                                     version, _ = winreg.QueryValueEx(driver_key, "Version")
#                                     return True, version
#                             i += 1
#                         except OSError:
#                             break
#             except OSError:
#                 pass
            
#             # Alternative check - look for the inf file
#             from pathlib import Path
#             driver_paths = [
#                 Path(r"C:\Windows\INF"),
#                 Path(r"C:\Windows\System32\DriverStore\FileRepository")
#             ]
            
#             for path in driver_paths:
#                 if path.exists():
#                     for inf_file in path.glob("**/f3bc5*.inf"):
#                         # Found a PalmSecure inf file
#                         return True, str(inf_file)
            
#             return False, None
            
#         except Exception as e:
#             logger.error(f"Error checking for driver: {str(e)}")
#             return False, None
    
#     elif platform.system() == 'Linux':
#         # On Linux, check if the device is recognized when connected
#         try:
#             result = subprocess.run(
#                 ["lsusb", "-d", f"{PALM_SECURE_VID:04x}:{PALM_SECURE_PID:04x}"],
#                 capture_output=True,
#                 text=True
#             )
            
#             if result.returncode == 0 and result.stdout.strip():
#                 # Device is recognized
#                 return True, "System driver"
#             else:
#                 return False, None
                
#         except Exception as e:
#             logger.error(f"Error checking for driver: {str(e)}")
#             return False, None
    
#     else:
#         # Not implemented for other platforms
#         return False, f"Not supported on {platform.system()}"


# def check_compatibility() -> Dict[str, Any]:
#     """
#     Check system compatibility for using PalmSecure devices.
    
#     Returns:
#         Dict containing compatibility information
#     """
#     compatibility = {
#         'os_supported': False,
#         'libusb_available': False,
#         'drivers_available': False,
#         'admin_access': False,
#         'python_version_ok': False,
#         'overall': False,
#         'message': ""
#     }
    
#     # Check Python version
#     py_version = sys.version_info
#     compatibility['python_version_ok'] = py_version.major >= 3 and py_version.minor >= 6
    
#     # Check OS
#     os_name = platform.system()
#     compatibility['os_supported'] = os_name in ['Windows', 'Linux']
    
#     # Check libusb availability
#     try:
#         import usb.core
#         compatibility['libusb_available'] = True
#     except ImportError:
#         compatibility['libusb_available'] = False
    
#     # Check admin access
#     compatibility['admin_access'] = is_admin()
    
#     # Check for drivers
#     drivers_installed, driver_info = is_driver_installed()
#     compatibility['drivers_available'] = drivers_installed
    
#     # Overall compatibility
#     if (compatibility['os_supported'] and 
#         compatibility['libusb_available'] and 
#         compatibility['python_version_ok']):
        
#         if not compatibility['drivers_available']:
#             compatibility['overall'] = False
#             compatibility['message'] = "PalmSecure drivers are not installed"
#         elif not compatibility['admin_access'] and os_name == 'Windows':
#             compatibility['overall'] = False
#             compatibility['message'] = "Administrative access required to interface with the device"
#         else:
#             compatibility['overall'] = True
#             compatibility['message'] = "System is compatible with PalmSecure SDK"
#     else:
#         compatibility['overall'] = False
#         if not compatibility['os_supported']:
#             compatibility['message'] = f"Operating system {os_name} is not fully supported"
#         elif not compatibility['libusb_available']:
#             compatibility['message'] = "Missing libusb dependency"
#         elif not compatibility['python_version_ok']:
#             compatibility['message'] = f"Python {py_version.major}.{py_version.minor} is not supported, need 3.6+"
    
#     return compatibility


# -- 2 --
"""
Palm Secure SDK Utilities
=========================

This module provides utility functions for the PalmSecure SDK.
"""
import os
import sys
import platform
import ctypes
from typing import Dict, Any, List, Tuple, Optional

import usb.core
import usb.util

from palm_secure.constants import VENDOR_IDS, PRODUCT_IDS, DEVICE_CLASSES


def parse_device_info(info_text: str) -> Dict[str, Any]:
    """
    Parse device information from text (like Windows device manager output).
    
    Args:
        info_text: Text containing device information
        
    Returns:
        Dict containing parsed device information
    """
    info = {
        'name': 'Unknown Device',
        'manufacturer': 'Unknown',
        'serial': 'Unknown',
        'driver': 'Unknown',
        'driver_version': 'Unknown',
        'status': 'Unknown',
        'device_id': 'Unknown',
    }
    
    lines = info_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        if ': ' in line:
            key, value = line.split(': ', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if 'name' in key:
                info['name'] = value
            elif 'manufacturer' in key:
                info['manufacturer'] = value
            elif 'serial' in key:
                info['serial'] = value
            elif 'driver version' in key:
                info['driver_version'] = value
            elif 'driver' in key:
                info['driver'] = value
            elif 'status' in key:
                info['status'] = value
            elif 'device id' in key or 'hardware id' in key:
                info['device_id'] = value
    
    return info


def is_admin() -> bool:
    """
    Check if the script is running with administrative privileges.
    
    Returns:
        bool: True if running as admin/root, False otherwise
    """
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif platform.system() in ('Linux', 'Darwin'):
            return os.geteuid() == 0
        else:
            return False
    except Exception:
        return False


def get_system_usb_devices() -> List[Dict[str, Any]]:
    """
    Get information about all USB devices on the system.
    
    Returns:
        List of dictionaries containing device information
    """
    devices = []
    
    try:
        # Check if we have a custom backend
        try:
            from usb_config import get_usb_backend
            backend = get_usb_backend()
        except ImportError:
            backend = None
            
        # Find all USB devices
        usb_devices = list(usb.core.find(find_all=True, backend=backend))
        
        for device in usb_devices:
            try:
                # Get basic device information
                dev_info = {
                    'bus': device.bus,
                    'address': device.address,
                    'vendor_id': device.idVendor,
                    'product_id': device.idProduct,
                    'device_class': device.bDeviceClass,
                    'path': get_device_path(device.bus, device.address),
                }
                
                # Try to get additional information
                try:
                    dev_info['manufacturer'] = usb.util.get_string(device, device.iManufacturer)
                except (usb.core.USBError, ValueError, AttributeError):
                    dev_info['manufacturer'] = 'Unknown'
                
                try:
                    dev_info['product'] = usb.util.get_string(device, device.iProduct)
                except (usb.core.USBError, ValueError, AttributeError):
                    dev_info['product'] = 'Unknown'
                
                try:
                    dev_info['serial_number'] = usb.util.get_string(device, device.iSerialNumber)
                except (usb.core.USBError, ValueError, AttributeError):
                    dev_info['serial_number'] = 'Unknown'
                
                devices.append(dev_info)
            except Exception as e:
                # If we can't get complete information for a device, add what we can
                devices.append({
                    'bus': getattr(device, 'bus', 0),
                    'address': getattr(device, 'address', 0),
                    'vendor_id': getattr(device, 'idVendor', 0),
                    'product_id': getattr(device, 'idProduct', 0),
                    'error': str(e),
                })
    except Exception as e:
        # If we can't enumerate devices at all, return an error entry
        devices.append({
            'error': f"Failed to enumerate USB devices: {str(e)}",
        })
    
    return devices


def find_palm_secure_devices() -> List[Dict[str, Any]]:
    """
    Find all PalmSecure devices connected to the system.
    
    Returns:
        List of dictionaries containing device information
    """
    # First get all USB devices on the system
    all_devices = get_system_usb_devices()
    
    # Filter for PalmSecure devices
    palm_devices = []
    
    for device in all_devices:
        # Skip entries that have errors
        if 'error' in device:
            continue
        
        # Check if the device matches any of our known PalmSecure devices
        is_palm_device = (
            device.get('vendor_id') in VENDOR_IDS and
            device.get('product_id') in PRODUCT_IDS
        ) or (
            device.get('device_class') in DEVICE_CLASSES
        )
        
        if is_palm_device:
            palm_devices.append(device)
    
    return palm_devices


def get_device_path(bus: int, address: int) -> str:
    """
    Get the system path for a USB device.
    
    Args:
        bus: USB bus number
        address: Device address on the bus
        
    Returns:
        String containing the device path
    """
    if platform.system() == 'Windows':
        return f"\\\\?\\usb#vid_{VENDOR_IDS[0]:04x}&pid_{PRODUCT_IDS[0]:04x}#{bus}.{address}"
    elif platform.system() == 'Linux':
        return f"/dev/bus/usb/{bus:03d}/{address:03d}"
    elif platform.system() == 'Darwin':
        return f"/dev/usb.{bus}.{address}"
    else:
        return f"unknown://{bus}.{address}"


def is_driver_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if the PalmSecure driver is installed on the system.
    
    Returns:
        Tuple of (is_installed, driver_version)
    """
    # Check for our custom driver info file
    driver_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fujitsu_driver_info.txt')
    if os.path.exists(driver_info_path):
        with open(driver_info_path, 'r') as f:
            for line in f:
                if line.startswith('driver_version='):
                    version = line.strip().split('=', 1)[1]
                    return True, version
                    
    # Platform-specific checks
    if platform.system() == 'Windows':
        try:
            import winreg
            drivers_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Class\{36FC9E60-C465-11CF-8056-444553540000}"
            )
            
            # Look for PalmSecure driver entries
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(drivers_key, i)
                    subkey = winreg.OpenKey(drivers_key, subkey_name)
                    
                    try:
                        driver_desc, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                        if "palm" in driver_desc.lower() or "fujitsu" in driver_desc.lower():
                            driver_ver, _ = winreg.QueryValueEx(subkey, "DriverVersion")
                            return True, driver_ver
                    except (FileNotFoundError, WindowsError):
                        pass
                    
                    i += 1
                except (FileNotFoundError, WindowsError):
                    break
        except Exception:
            pass
    elif platform.system() == 'Linux':
        # Check for linux driver modules or udev rules
        if os.path.exists('/etc/udev/rules.d/99-palmsecure.rules'):
            # If we have udev rules, the driver is considered "installed"
            # However, on Linux we're likely using libusb directly
            return True, "1.0.0"
    
    # If we can connect to a device, we can assume the driver is installed
    try:
        # Look for devices using our configured backend
        try:
            from usb_config import get_usb_backend
            backend = get_usb_backend()
            
            for vid in VENDOR_IDS:
                for pid in PRODUCT_IDS:
                    device = usb.core.find(idVendor=vid, idProduct=pid, backend=backend)
                    if device:
                        # We found a device, assume driver is working
                        return True, "Unknown"
        except ImportError:
            pass
    except Exception:
        pass
    
    return False, None


def check_compatibility() -> Dict[str, Any]:
    """
    Check system compatibility for using PalmSecure devices.
    
    Returns:
        Dict containing compatibility information
    """
    result = {
        'status': 'OK',
        'os_supported': True,
        'driver_compatible': True,
        'python_compatible': True,
        'message': 'System is compatible',
    }

    # Check operating system
    os_name = platform.system()
    result['os'] = os_name

    if os_name not in ('Windows', 'Linux'):
        result['status'] = 'ERROR'
        result['os_supported'] = False
        result['message'] = f"Unsupported operating system: {os_name}"
        return result

    # Check Python version
    python_version = platform.python_version_tuple()
    result['python_version'] = '.'.join(python_version)

    if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 6):
        result['status'] = 'ERROR'
        result['python_compatible'] = False
        result['message'] = f"Unsupported Python version: {result['python_version']}. Python 3.6 or higher is required."
        return result

    # Check if the driver is installed and compatible
    is_installed, driver_version = is_driver_installed()
    result['driver_installed'] = is_installed
    result['driver_version'] = driver_version

    if not is_installed:
        result['status'] = 'ERROR'
        result['driver_compatible'] = False
        result['message'] = "PalmSecure driver not installed"

    # Check if running as admin/root
    result['is_admin'] = is_admin()
    if not result['is_admin'] and os_name == 'Windows':
        result['status'] = 'WARNING'
        result['message'] = "Not running as administrator. Some functions may be limited."

    return result
