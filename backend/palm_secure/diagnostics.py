# """
# Palm Secure Diagnostics Module
# ==============================

# This module provides diagnostic functions for PalmSecure devices.
# """

# import logging
# import platform
# import sys
# import os
# import time
# import socket
# from typing import Dict, Any, List, Optional, Tuple, Union
# import usb.core
# import usb.util

# from .exceptions import DeviceNotFoundError, ConnectionError, OperationError
# from .constants import (
#     PALM_SECURE_VID,
#     PALM_SECURE_PID,
#     DEVICE_STATES,
#     ERROR_CODES,
#     COMPATIBLE_DRIVER_VERSIONS,
#     PALM_SECURE_GUID
# )
# from .utils import (
#     parse_device_info,
#     get_system_usb_devices,
#     is_driver_installed,
#     check_compatibility
# )

# logger = logging.getLogger(__name__)


# class DiagnosticsManager:
#     """
#     Class to perform diagnostics on PalmSecure devices.
#     """
    
#     def __init__(self):
#         """Initialize the diagnostics manager."""
#         self.results = {}
    
#     def run_all_diagnostics(self) -> Dict[str, Any]:
#         """
#         Run all available diagnostic tests.
        
#         Returns:
#             Dict containing all diagnostic results
#         """
#         self.results = {}
        
#         # System compatibility check
#         self.results['system_compatibility'] = check_compatibility()
        
#         # USB subsystem check
#         self.results['usb_subsystem'] = self.check_usb_subsystem()
        
#         # Driver check
#         self.results['driver_check'] = self.check_drivers()
        
#         # Permissions check
#         self.results['permissions'] = self.check_permissions()
        
#         # Device detection
#         self.results['device_detection'] = self.check_device_detection()
        
#         # Network connectivity (for potential cloud/network features)
#         self.results['network'] = self.check_network()
        
#         # Create overall assessment
#         self.results['overall'] = self.get_overall_assessment()
        
#         return self.results
    
#     def check_usb_subsystem(self) -> Dict[str, Any]:
#         """
#         Check the USB subsystem on the host machine.
        
#         Returns:
#             Dict containing USB subsystem diagnostic results
#         """
#         result = {
#             'status': 'unknown',
#             'details': [],
#             'message': '',
#             'usb_devices_count': 0,
#             'has_issues': False
#         }
        
#         try:
#             # Try to enumerate all USB devices
#             devices = get_system_usb_devices()
#             result['usb_devices_count'] = len(devices)
            
#             if len(devices) > 0:
#                 result['status'] = 'ok'
#                 result['message'] = f"Found {len(devices)} USB devices"
#                 result['has_issues'] = False
#             else:
#                 result['status'] = 'warning'
#                 result['message'] = "No USB devices found, which is unusual"
#                 result['has_issues'] = True
            
#             # Check for specific USB controller issues
#             if platform.system() == 'Windows':
#                 # On Windows, check if any USB controllers have issues
#                 import winreg
                
#                 try:
#                     key_path = r"SYSTEM\CurrentControlSet\Enum\USB"
#                     with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
#                         i = 0
#                         while True:
#                             try:
#                                 subkey_name = winreg.EnumKey(key, i)
#                                 # Look for USB controllers/hubs
#                                 if 'ROOT_HUB' in subkey_name or 'HOST' in subkey_name:
#                                     with winreg.OpenKey(key, subkey_name) as controller_key:
#                                         # Check controller status
#                                         pass  # This would require deeper registry access
#                                 i += 1
#                             except OSError:
#                                 break
#                 except Exception as e:
#                     result['details'].append(f"Error checking USB controllers: {str(e)}")
            
#             elif platform.system() == 'Linux':
#                 # On Linux, check usb devices with lsusb
#                 try:
#                     import subprocess
#                     proc = subprocess.run(['lsusb'], capture_output=True, text=True)
#                     if proc.returncode == 0:
#                         result['details'].append("USB subsystem appears functional")
#                     else:
#                         result['status'] = 'error'
#                         result['message'] = "Error running lsusb command"
#                         result['has_issues'] = True
#                 except Exception as e:
#                     result['details'].append(f"Error checking USB system: {str(e)}")
        
#         except Exception as e:
#             result['status'] = 'error'
#             result['message'] = f"Error checking USB subsystem: {str(e)}"
#             result['details'].append(str(e))
#             result['has_issues'] = True
        
#         return result
    
#     def check_drivers(self) -> Dict[str, Any]:
#         """
#         Check if required drivers are installed and working.
        
#         Returns:
#             Dict containing driver diagnostic results
#         """
#         result = {
#             'status': 'unknown',
#             'installed': False,
#             'version': None,
#             'compatible': False,
#             'details': [],
#             'message': '',
#             'has_issues': True
#         }
        
#         try:
#             # Check if PalmSecure drivers are installed
#             installed, driver_info = is_driver_installed()
#             result['installed'] = installed
            
#             if installed:
#                 result['status'] = 'ok'
#                 result['message'] = f"PalmSecure driver is installed: {driver_info}"
#                 result['has_issues'] = False
                
#                 # Check if the version is compatible
#                 if isinstance(driver_info, str) and any(version in driver_info for version in COMPATIBLE_DRIVER_VERSIONS):
#                     result['compatible'] = True
#                     result['version'] = next((v for v in COMPATIBLE_DRIVER_VERSIONS if v in driver_info), None)
#                 elif driver_info == "System driver":
#                     # Linux system driver
#                     result['compatible'] = True
#                     result['version'] = "System driver"
#                 else:
#                     result['compatible'] = False
#                     result['message'] = f"Driver version may not be compatible: {driver_info}"
#                     result['has_issues'] = True
#             else:
#                 result['status'] = 'error'
#                 result['message'] = "PalmSecure driver is not installed"
#                 result['has_issues'] = True
            
#             # Check WinUSB on Windows
#             if platform.system() == 'Windows':
#                 try:
#                     import winreg
                    
#                     # Check for WinUSB driver
#                     key_path = r"SYSTEM\CurrentControlSet\Services\WinUSB"
#                     try:
#                         with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
#                             # WinUSB is installed
#                             result['details'].append("WinUSB driver is installed")
#                     except OSError:
#                         result['details'].append("WinUSB driver may not be installed")
#                         if result['installed']:
#                             result['status'] = 'warning'
#                             result['message'] += ". WinUSB driver may be missing."
#                             result['has_issues'] = True
                
#                 except Exception as e:
#                     result['details'].append(f"Error checking WinUSB driver: {str(e)}")
        
#         except Exception as e:
#             result['status'] = 'error'
#             result['message'] = f"Error checking drivers: {str(e)}"
#             result['details'].append(str(e))
#             result['has_issues'] = True
        
#         return result
    
#     def check_permissions(self) -> Dict[str, Any]:
#         """
#         Check if the current user has sufficient permissions.
        
#         Returns:
#             Dict containing permissions diagnostic results
#         """
#         result = {
#             'status': 'unknown',
#             'admin': False,
#             'device_access': False,
#             'details': [],
#             'message': '',
#             'has_issues': True
#         }
        
#         try:
#             # Check if running as admin/root
#             if platform.system() == 'Windows':
#                 try:
#                     import ctypes
#                     result['admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
#                 except Exception as e:
#                     result['details'].append(f"Error checking admin status: {str(e)}")
            
#             elif platform.system() == 'Linux':
#                 result['admin'] = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
            
#             # Check if we can access USB devices
#             try:
#                 devices = usb.core.find(find_all=True)
#                 device_count = sum(1 for _ in devices)
#                 if device_count > 0:
#                     result['device_access'] = True
#                     result['details'].append(f"Can access {device_count} USB devices")
#                 else:
#                     result['details'].append("No USB devices accessible (might need permissions)")
#                     result['device_access'] = False
#             except Exception as e:
#                 result['details'].append(f"Error accessing USB devices: {str(e)}")
#                 result['device_access'] = False
            
#             # Determine overall status
#             if result['admin'] and result['device_access']:
#                 result['status'] = 'ok'
#                 result['message'] = "User has sufficient permissions"
#                 result['has_issues'] = False
#             elif result['device_access']:
#                 result['status'] = 'warning'
#                 result['message'] = "User can access devices but is not an administrator"
#                 result['has_issues'] = False
#             else:
#                 result['status'] = 'error'
#                 result['message'] = "User lacks permission to access USB devices"
#                 result['has_issues'] = True
        
#         except Exception as e:
#             result['status'] = 'error'
#             result['message'] = f"Error checking permissions: {str(e)}"
#             result['details'].append(str(e))
#             result['has_issues'] = True
        
#         return result
    
#     def check_device_detection(self) -> Dict[str, Any]:
#         """
#         Check if PalmSecure devices can be detected.
        
#         Returns:
#             Dict containing device detection diagnostic results
#         """
#         result = {
#             'status': 'unknown',
#             'devices_found': 0,
#             'device_details': [],
#             'details': [],
#             'message': '',
#             'has_issues': True
#         }
        
#         try:
#             # Try to find PalmSecure devices
#             devices = usb.core.find(
#                 find_all=True,
#                 idVendor=PALM_SECURE_VID,
#                 idProduct=PALM_SECURE_PID
#             )
            
#             # Convert generator to list to get count
#             device_list = list(devices)
#             result['devices_found'] = len(device_list)
            
#             if len(device_list) > 0:
#                 result['status'] = 'ok'
#                 result['message'] = f"Found {len(device_list)} PalmSecure device(s)"
#                 result['has_issues'] = False
                
#                 # Get details for each device
#                 for idx, dev in enumerate(device_list):
#                     device_info = {
#                         'index': idx,
#                         'bus': dev.bus,
#                         'address': dev.address,
#                         'manufacturer': 'Unknown',
#                         'product': 'Unknown',
#                         'serial_number': 'Unknown'
#                     }
                    
#                     try:
#                         # Try to get string descriptors
#                         device_info['manufacturer'] = usb.util.get_string(dev, dev.iManufacturer)
#                         device_info['product'] = usb.util.get_string(dev, dev.iProduct)
#                         device_info['serial_number'] = usb.util.get_string(dev, dev.iSerialNumber)
#                     except (ValueError, usb.core.USBError):
#                         pass
                    
#                     result['device_details'].append(device_info)
#             else:
#                 result['status'] = 'error'
#                 result['message'] = "No PalmSecure devices found"
#                 result['has_issues'] = True
                
#                 # Check if any USB devices are found at all
#                 all_devices = list(usb.core.find(find_all=True))
#                 if len(all_devices) > 0:
#                     result['details'].append(f"Found {len(all_devices)} other USB devices")
                    
#                     # Look for similar devices that might be PalmSecure but with different VID/PID
#                     for dev in all_devices:
#                         if (
#                             (dev.idVendor == PALM_SECURE_VID and dev.idProduct != PALM_SECURE_PID) or
#                             (any('palm' in usb.util.get_string(dev, dev.iProduct).lower() for dev in all_devices 
#                                 if hasattr(dev, 'iProduct') and dev.iProduct > 0))
#                         ):
#                             result['details'].append(
#                                 f"Found potential similar device: VID_{dev.idVendor:04X}&PID_{dev.idProduct:04X}"
#                             )
#                 else:
#                     result['details'].append("No USB devices found at all")
        
#         except Exception as e:
#             result['status'] = 'error'
#             result['message'] = f"Error detecting devices: {str(e)}"
#             result['details'].append(str(e))
#             result['has_issues'] = True
        
#         return result
    
#     def check_network(self) -> Dict[str, Any]:
#         """
#         Check network connectivity, which may be needed for certain features.
        
#         Returns:
#             Dict containing network diagnostic results
#         """
#         result = {
#             'status': 'unknown',
#             'connectivity': False,
#             'details': [],
#             'message': '',
#             'has_issues': False  # Not critical for basic functionality
#         }
        
#         try:
#             # Check basic internet connectivity
#             host = "8.8.8.8"  # Google DNS
#             port = 53  # DNS port
            
#             try:
#                 socket.setdefaulttimeout(3)
#                 socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
#                 result['connectivity'] = True
#                 result['status'] = 'ok'
#                 result['message'] = "Network connectivity available"
#             except Exception as e:
#                 result['connectivity'] = False
#                 result['status'] = 'warning'
#                 result['message'] = "No network connectivity detected"
#                 result['details'].append(str(e))
#                 result['has_issues'] = True
        
#         except Exception as e:
#             result['status'] = 'error'
#             result['message'] = f"Error checking network: {str(e)}"
#             result['details'].append(str(e))
#             result['has_issues'] = True
        
#         return result
    
#     def get_overall_assessment(self) -> Dict[str, Any]:
#         """
#         Get an overall assessment of the system's ability to use PalmSecure devices.
        
#         Returns:
#             Dict containing overall assessment
#         """
#         critical_issues = []
#         warnings = []
        
#         # Check for critical issues
#         if self.results.get('driver_check', {}).get('has_issues', True):
#             critical_issues.append("Driver issues: " + self.results.get('driver_check', {}).get('message', 'Unknown'))
        
#         if self.results.get('device_detection', {}).get('has_issues', True):
#             critical_issues.append("Device detection issues: " + 
#                                   self.results.get('device_detection', {}).get('message', 'Unknown'))
        
#         if self.results.get('permissions', {}).get('has_issues', True):
#             critical_issues.append("Permission issues: " + 
#                                   self.results.get('permissions', {}).get('message', 'Unknown'))
        
#         if self.results.get('usb_subsystem', {}).get('has_issues', True):
#             critical_issues.append("USB subsystem issues: " + 
#                                   self.results.get('usb_subsystem', {}).get('message', 'Unknown'))
        
#         # Check for warnings
#         if self.results.get('system_compatibility', {}).get('overall', False) is False:
#             warnings.append("System compatibility issues: " + 
#                            self.results.get('system_compatibility', {}).get('message', 'Unknown'))
        
#         if self.results.get('network', {}).get('has_issues', False):
#             warnings.append("Network connectivity issues: " + 
#                            self.results.get('network', {}).get('message', 'Unknown'))
        
#         # Determine overall status
#         if critical_issues:
#             status = 'error'
#             message = "Critical issues detected that will prevent PalmSecure device operation"
#         elif warnings:
#             status = 'warning'
#             message = "Warnings detected that may affect PalmSecure device operation"
#         else:
#             status = 'ok'
#             message = "System is ready for PalmSecure device operation"
        
#         return {
#             'status': status,
#             'message': message,
#             'critical_issues': critical_issues,
#             'warnings': warnings,
#             'ready': status == 'ok'
#         }
    
#     def generate_report(self) -> str:
#         """
#         Generate a human-readable diagnostic report.
        
#         Returns:
#             String containing the report
#         """
#         if not self.results:
#             self.run_all_diagnostics()
        
#         report = []
#         report.append("PalmSecure Device Diagnostic Report")
#         report.append("=" * 40)
#         report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
#         report.append(f"System: {platform.system()} {platform.release()} {platform.machine()}")
#         report.append(f"Python: {platform.python_version()}")
#         report.append("-" * 40)
        
#         # Overall assessment
#         overall = self.results.get('overall', {})
#         report.append(f"Overall Status: {overall.get('status', 'Unknown').upper()}")
#         report.append(f"Assessment: {overall.get('message', 'Unknown')}")
        
#         if overall.get('critical_issues'):
#             report.append("\nCritical Issues:")
#             for issue in overall.get('critical_issues', []):
#                 report.append(f"- {issue}")
        
#         if overall.get('warnings'):
#             report.append("\nWarnings:")
#             for warning in overall.get('warnings', []):
#                 report.append(f"- {warning}")
        
#         # System compatibility
#         report.append("\nSystem Compatibility:")
#         compat = self.results.get('system_compatibility', {})
#         report.append(f"  OS Supported: {compat.get('os_supported', False)}")
#         report.append(f"  Python Version OK: {compat.get('python_version_ok', False)}")
#         report.append(f"  LibUSB Available: {compat.get('libusb_available', False)}")
#         report.append(f"  Admin Access: {compat.get('admin_access', False)}")
#         report.append(f"  Drivers Available: {compat.get('drivers_available', False)}")
        
#         # USB subsystem
#         report.append("\nUSB Subsystem:")
#         usb_check = self.results.get('usb_subsystem', {})
#         report.append(f"  Status: {usb_check.get('status', 'Unknown').upper()}")
#         report.append(f"  USB Devices Count: {usb_check.get('usb_devices_count', 0)}")
#         for detail in usb_check.get('details', []):
#             report.append(f"  - {detail}")
        
#         # Driver check
#         report.append("\nDriver Status:")
#         driver = self.results.get('driver_check', {})
#         report.append(f"  Status: {driver.get('status', 'Unknown').upper()}")
#         report.append(f"  Installed: {driver.get('installed', False)}")
#         report.append(f"  Version: {driver.get('version', 'Unknown')}")
#         report.append(f"  Compatible: {driver.get('compatible', False)}")
#         for detail in driver.get('details', []):
#             report.append(f"  - {detail}")
        
#         # Permissions
#         report.append("\nPermissions:")
#         perm = self.results.get('permissions', {})
#         report.append(f"  Status: {perm.get('status', 'Unknown').upper()}")
#         report.append(f"  Admin Access: {perm.get('admin', False)}")
#         report.append(f"  Device Access: {perm.get('device_access', False)}")
#         for detail in perm.get('details', []):
#             report.append(f"  - {detail}")
        
#         # Device detection
#         report.append("\nPalmSecure Device Detection:")
#         detect = self.results.get('device_detection', {})
#         report.append(f"  Status: {detect.get('status', 'Unknown').upper()}")
#         report.append(f"  Devices Found: {detect.get('devices_found', 0)}")
        
#         if detect.get('device_details'):
#             report.append("  Device Details:")
#             for dev in detect.get('device_details', []):
#                 report.append(f"    Device {dev.get('index', 0)+1}:")
#                 report.append(f"    - Bus/Address: {dev.get('bus', 0)}/{dev.get('address', 0)}")
#                 report.append(f"    - Manufacturer: {dev.get('manufacturer', 'Unknown')}")
#                 report.append(f"    - Product: {dev.get('product', 'Unknown')}")
#                 report.append(f"    - Serial: {dev.get('serial_number', 'Unknown')}")
        
#         for detail in detect.get('details', []):
#             report.append(f"  - {detail}")
        
#         # Network connectivity
#         report.append("\nNetwork Connectivity:")
#         net = self.results.get('network', {})
#         report.append(f"  Status: {net.get('status', 'Unknown').upper()}")
#         report.append(f"  Connectivity: {net.get('connectivity', False)}")
#         for detail in net.get('details', []):
#             report.append(f"  - {detail}")
        
#         # Finish report
#         report.append("\n" + "=" * 40)
#         report.append("End of Diagnostic Report")
        
#         return "\n".join(report)



# -- 2 --
# """
# Palm Secure Diagnostics Module
# ==============================

# This module provides diagnostic functions for PalmSecure devices.
# """
# import os
# import platform
# import sys
# import time
# from typing import Dict, Any, List, Tuple

# import usb.core
# import usb.util

# from palm_secure.device import find_devices
# from palm_secure.utils import is_admin, is_driver_installed, check_compatibility


# class DiagnosticsManager:
#     """
#     Class to perform diagnostics on PalmSecure devices.
#     """
    
#     def __init__(self):
#         """Initialize the diagnostics manager."""
#         self.results = {}
    
#     def run_all_diagnostics(self) -> Dict[str, Any]:
#         """
#         Run all available diagnostic tests.
        
#         Returns:
#             Dict containing all diagnostic results
#         """
#         # Check USB subsystem
#         usb_results = self.check_usb_subsystem()
#         self.results['usb_subsystem'] = usb_results
        
#         # Check drivers
#         driver_results = self.check_drivers()
#         self.results['drivers'] = driver_results
        
#         # Check permissions
#         permission_results = self.check_permissions()
#         self.results['permissions'] = permission_results
        
#         # Check device detection
#         device_results = self.check_device_detection()
#         self.results['device_detection'] = device_results
        
#         # Check network
#         network_results = self.check_network()
#         self.results['network'] = network_results
        
#         # Get overall assessment
#         self.results['overall'] = self.get_overall_assessment()
        
#         return self.results
    
#     def check_usb_subsystem(self) -> Dict[str, Any]:
#         """
#         Check the USB subsystem on the host machine.
        
#         Returns:
#             Dict containing USB subsystem diagnostic results
#         """
#         results = {
#             'status': 'OK',
#             'details': [],
#             'usb_version': 'Unknown',
#             'usb_controllers': [],
#             'pyusb_version': 'Unknown',
#             'backend': 'Unknown',
#         }
        
#         # Check PyUSB version
#         try:
#             import usb
#             results['pyusb_version'] = usb.__version__
#             results['details'].append(f"PyUSB version: {usb.__version__}")
#         except ImportError:
#             results['status'] = 'ERROR'
#             results['details'].append("PyUSB not installed")
        
#         # Check USB backend
#         try:
#             backend = usb.backend.libusb1.get_backend()
#             if backend:
#                 results['backend'] = 'libusb1'
#                 results['details'].append("USB backend: libusb1")
#             else:
#                 # Try to check if we can import our custom backend
#                 try:
#                     from usb_config import get_usb_backend
#                     backend = get_usb_backend()
#                     if backend:
#                         results['backend'] = 'custom_libusb1'
#                         results['details'].append("USB backend: custom libusb1")
#                     else:
#                         results['status'] = 'WARNING'
#                         results['details'].append("Custom USB backend failed to load")
#                 except ImportError:
#                     results['status'] = 'ERROR'
#                     results['details'].append("No USB backend available")
#         except Exception as e:
#             results['status'] = 'ERROR'
#             results['details'].append(f"Error checking USB backend: {str(e)}")
        
#         # Check USB controllers
#         try:
#             devices = list(usb.core.find(find_all=True))
#             host_controllers = set()
            
#             for dev in devices:
#                 if dev.bDeviceClass == 9:  # Hub class
#                     host_controllers.add((dev.idVendor, dev.idProduct))
            
#             results['usb_controllers'] = [
#                 {'vendor_id': vc[0], 'product_id': vc[1]} for vc in host_controllers
#             ]
            
#             results['details'].append(f"Found {len(host_controllers)} USB controllers")
            
#             if not host_controllers:
#                 results['status'] = 'WARNING'
#                 results['details'].append("No USB controllers detected")
#         except Exception as e:
#             results['status'] = 'ERROR'
#             results['details'].append(f"Error checking USB controllers: {str(e)}")
        
#         # Check if we can enumerate USB devices
#         try:
#             devices = list(usb.core.find(find_all=True))
#             results['details'].append(f"Found {len(devices)} USB devices")
            
#             if not devices:
#                 results['status'] = 'WARNING'
#                 results['details'].append("No USB devices detected")
#         except Exception as e:
#             results['status'] = 'ERROR'
#             results['details'].append(f"Error enumerating USB devices: {str(e)}")
        
#         return results
    
#     def check_drivers(self) -> Dict[str, Any]:
#         """
#         Check if required drivers are installed and working.
        
#         Returns:
#             Dict containing driver diagnostic results
#         """
#         # Check for our custom driver info file
#         driver_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fujitsu_driver_info.txt')
#         if os.path.exists(driver_info_path):
#             with open(driver_info_path, 'r') as f:
#                 driver_info = {}
#                 for line in f:
#                     if '=' in line:
#                         key, value = line.strip().split('=', 1)
#                         driver_info[key] = value
                
#                 return {
#                     'status': 'OK',
#                     'installed': True,
#                     'version': driver_info.get('driver_version', 'Unknown'),
#                     'compatible': driver_info.get('driver_compatible', 'false').lower() == 'true',
#                     'details': f"Driver found at: {driver_info.get('driver_path', 'Unknown')}"
#                 }

#         # If custom driver info not found, check system drivers
#         results = {
#             'status': 'OK',
#             'installed': False,
#             'version': 'Unknown',
#             'compatible': False,
#             'details': [],
#         }
        
#         # Check if PalmSecure driver is installed
#         is_installed, version = is_driver_installed()
#         results['installed'] = is_installed
#         results['version'] = version if version else 'Unknown'
        
#         if is_installed:
#             results['details'].append(f"PalmSecure driver installed (version: {version})")
#             results['compatible'] = True
#         else:
#             results['status'] = 'ERROR'
#             results['details'].append("PalmSecure driver not installed")
        
#         # Check compatibility of the driver with the system
#         compatibility = check_compatibility()
#         results['details'].append(f"System compatibility: {compatibility.get('status', 'Unknown')}")
        
#         if compatibility.get('status') == 'ERROR':
#             results['status'] = 'ERROR'
#             results['compatible'] = False
#             results['details'].append(compatibility.get('message', 'Incompatible system'))
        
#         return results
    
#     def check_permissions(self) -> Dict[str, Any]:
#         """
#         Check if the current user has sufficient permissions.
        
#         Returns:
#             Dict containing permissions diagnostic results
#         """
#         results = {
#             'status': 'OK',
#             'is_admin': False,
#             'can_access_usb': False,
#             'details': [],
#         }
        
#         # Check if running as admin/root
#         is_admin_user = is_admin()
#         results['is_admin'] = is_admin_user
        
#         if is_admin_user:
#             results['details'].append("Running with administrative privileges")
#         else:
#             if platform.system() == 'Windows':
#                 results['status'] = 'WARNING'
#                 results['details'].append("Not running as administrator. Some functions may be limited.")
#             elif platform.system() in ('Linux', 'Darwin'):
#                 results['status'] = 'WARNING'
#                 results['details'].append("Not running as root. USB access may be limited.")
        
#         # Check if we can access USB devices
#         try:
#             devices = list(usb.core.find(find_all=True))
#             if devices:
#                 # Try to get a descriptor from the first device
#                 try:
#                     device = devices[0]
#                     # Just try to read a descriptor
#                     device.get_active_configuration()
#                     results['can_access_usb'] = True
#                     results['details'].append("Can access USB devices")
#                 except Exception as e:
#                     results['status'] = 'WARNING'
#                     results['can_access_usb'] = False
#                     results['details'].append(f"Cannot access USB devices: {str(e)}")
#             else:
#                 results['details'].append("No USB devices to test access permissions")
#         except Exception as e:
#             results['status'] = 'ERROR'
#             results['can_access_usb'] = False
#             results['details'].append(f"Error checking USB access permissions: {str(e)}")
        
#         return results
    
#     def check_device_detection(self) -> Dict[str, Any]:
#         """
#         Check if PalmSecure devices can be detected.
        
#         Returns:
#             Dict containing device detection diagnostic results
#         """
#         results = {
#             'status': 'OK',
#             'devices_found': False,
#             'device_count': 0,
#             'devices': [],
#             'details': [],
#         }
        
#         # Try to find PalmSecure devices
#         try:
#             devices = find_devices()
#             results['devices_found'] = len(devices) > 0
#             results['device_count'] = len(devices)
#             results['devices'] = devices
            
#             if devices:
#                 results['details'].append(f"Found {len(devices)} PalmSecure devices")
#                 for i, device in enumerate(devices):
#                     device_desc = (
#                         f"Device {i+1}: "
#                         f"{device.get('manufacturer', 'Unknown')} "
#                         f"{device.get('product', 'Unknown')} "
#                         f"(ID: {device.get('vendor_id', 0):04x}:{device.get('product_id', 0):04x})"
#                     )
#                     results['details'].append(device_desc)
#             else:
#                 results['status'] = 'WARNING'
#                 results['details'].append("No PalmSecure devices found")
                
#                 # Check if any USB devices are available at all
#                 try:
#                     all_devices = list(usb.core.find(find_all=True))
#                     if all_devices:
#                         results['details'].append(f"Found {len(all_devices)} USB devices, but none identified as PalmSecure")
#                     else:
#                         results['details'].append("No USB devices found at all")
#                 except Exception as e:
#                     results['details'].append(f"Error enumerating USB devices: {str(e)}")
#         except Exception as e:
#             results['status'] = 'ERROR'
#             results['details'].append(f"Error detecting PalmSecure devices: {str(e)}")
        
#         return results
    
#     def check_network(self) -> Dict[str, Any]:
#         """
#         Check network connectivity, which may be needed for certain features.
        
#         Returns:
#             Dict containing network diagnostic results
#         """
#         results = {
#             'status': 'OK',
#             'internet_available': False,
#             'firewall_status': 'Unknown',
#             'details': [],
#         }
        
#         # Check internet connectivity
#         try:
#             import socket
#             socket.create_connection(("www.google.com", 80), timeout=5)
#             results['internet_available'] = True
#             results['details'].append("Internet connection available")
#         except OSError:
#             try:
#                 # Try another domain in case google.com is blocked
#                 socket.create_connection(("www.example.com", 80), timeout=5)
#                 results['internet_available'] = True
#                 results['details'].append("Internet connection available")
#             except OSError:
#                 results['internet_available'] = False
#                 results['details'].append("No internet connection available")
#                 # Not a critical error for most local device operations
#                 results['status'] = 'INFO'
        
#         # Check firewall status on Windows
#         if platform.system() == 'Windows':
#             try:
#                 import subprocess
#                 output = subprocess.check_output(['netsh', 'advfirewall', 'show', 'allprofiles'], 
#                                                universal_newlines=True)
                
#                 if 'ON' in output:
#                     results['firewall_status'] = 'ON'
#                     results['details'].append("Windows Firewall is enabled")
#                 else:
#                     results['firewall_status'] = 'OFF'
#                     results['details'].append("Windows Firewall is disabled")
#             except Exception:
#                 results['details'].append("Could not determine Windows Firewall status")
        
#         return results
    
#     def get_overall_assessment(self) -> Dict[str, Any]:
#         """
#         Get an overall assessment of the system's ability to use PalmSecure devices.
        
#         Returns:
#             Dict containing overall assessment
#         """
#         results = {
#             'status': 'OK',
#             'can_use_devices': True,
#             'issues': [],
#             'recommendations': [],
#         }
        
#         # Check for critical issues in all diagnostic results
#         if not self.results:
#             # Run all diagnostics if not done yet
#             self.run_all_diagnostics()
        
#         # Check USB subsystem
#         usb_results = self.results.get('usb_subsystem', {})
#         if usb_results.get('status') == 'ERROR':
#             results['status'] = 'ERROR'
#             results['can_use_devices'] = False
#             results['issues'].append("USB subsystem issues detected")
#             results['recommendations'].append("Install or update USB libraries")
        
#         # Check drivers
#         driver_results = self.results.get('drivers', {})
#         if not driver_results.get('installed', False):
#             results['status'] = 'ERROR'
#             results['can_use_devices'] = False
#             results['issues'].append("PalmSecure drivers not installed")
#             results['recommendations'].append("Install PalmSecure drivers")
#         elif not driver_results.get('compatible', False):
#             results['status'] = 'ERROR'
#             results['can_use_devices'] = False
#             results['issues'].append("Incompatible PalmSecure drivers")
#             results['recommendations'].append("Update to compatible drivers")
        
#         # Check permissions
#         permission_results = self.results.get('permissions', {})
#         if not permission_results.get('is_admin', False) and platform.system() == 'Windows':
#             results['status'] = 'WARNING'
#             results['issues'].append("Not running as administrator")
#             results['recommendations'].append("Run as administrator for full functionality")
        
#         if not permission_results.get('can_access_usb', False):
#             results['status'] = 'ERROR'
#             results['can_use_devices'] = False
#             results['issues'].append("Cannot access USB devices")
#             if platform.system() == 'Linux':
#                 results['recommendations'].append("Add user to 'plugdev' group and create appropriate udev rules")
#             else:
#                 results['recommendations'].append("Run as administrator/root")
        
#         # Check device detection
#         device_results = self.results.get('device_detection', {})
#         if not device_results.get('devices_found', False):
#             results['status'] = 'WARNING'
#             results['issues'].append("No PalmSecure devices detected")
#             results['recommendations'].append("Connect a PalmSecure device")
        
#         return results
    
#     def generate_report(self) -> str:
#         """
#         Generate a human-readable diagnostic report.
        
#         Returns:
#             String containing the report
#         """
#         if not self.results:
#             self.run_all_diagnostics()
        
#         report = []
        
#         # Add header
#         report.append("=" * 60)
#         report.append("PalmSecure SDK Diagnostic Report")
#         report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
#         report.append("=" * 60)
#         report.append("")
        
#         # Add system information
#         report.append("System Information:")
#         report.append(f"  OS: {platform.system()} {platform.release()} {platform.version()}")
#         report.append(f"  Architecture: {platform.machine()}")
#         report.append(f"  Python: {platform.python_version()}")
#         report.append("")
        
#         # Add overall assessment
#         overall = self.results.get('overall', {})
#         report.append("Overall Assessment:")
#         report.append(f"  Status: {overall.get('status', 'Unknown')}")
#         report.append(f"  Can use PalmSecure devices: {'Yes' if overall.get('can_use_devices', False) else 'No'}")
        
#         if overall.get('issues'):
#             report.append("  Issues:")
#             for issue in overall.get('issues', []):
#                 report.append(f"    - {issue}")
        
#         if overall.get('recommendations'):
#             report.append("  Recommendations:")
#             for rec in overall.get('recommendations', []):
#                 report.append(f"    - {rec}")
        
#         report.append("")
        
#         # Add detailed results for each category
#         categories = [
#             ('USB Subsystem', 'usb_subsystem'),
#             ('Drivers', 'drivers'),
#             ('Permissions', 'permissions'),
#             ('Device Detection', 'device_detection'),
#             ('Network', 'network'),
#         ]
        
#         for title, key in categories:
#             results = self.results.get(key, {})
#             report.append(f"{title}:")
#             report.append(f"  Status: {results.get('status', 'Unknown')}")
            
#             # Add specific information for each category
#             if key == 'usb_subsystem':
#                 report.append(f"  PyUSB version: {results.get('pyusb_version', 'Unknown')}")
#                 report.append(f"  USB backend: {results.get('backend', 'Unknown')}")
#                 report.append(f"  USB controllers: {len(results.get('usb_controllers', []))}")
            
#             elif key == 'drivers':
#                 report.append(f"  Installed: {'Yes' if results.get('installed', False) else 'No'}")
#                 report.append(f"  Version: {results.get('version', 'Unknown')}")
#                 report.append(f"  Compatible: {'Yes' if results.get('compatible', False) else 'No'}")
            
#             elif key == 'permissions':
#                 report.append(f"  Admin privileges: {'Yes' if results.get('is_admin', False) else 'No'}")
#                 report.append(f"  Can access USB: {'Yes' if results.get('can_access_usb', False) else 'No'}")
            
#             elif key == 'device_detection':
#                 report.append(f"  Devices found: {'Yes' if results.get('devices_found', False) else 'No'}")
#                 report.append(f"  Device count: {results.get('device_count', 0)}")
                
#                 if results.get('devices'):
#                     report.append("  Devices:")
#                     for i, device in enumerate(results.get('devices', [])):
#                         device_desc = (
#                             f"    {i+1}. "
#                             f"{device.get('manufacturer', 'Unknown')} "
#                             f"{device.get('product', 'Unknown')} "
#                             f"(ID: {device.get('vendor_id', 0):04x}:{device.get('product_id', 0):04x})"
#                         )
#                         report.append(device_desc)
            
#             elif key == 'network':
#                 report.append(f"  Internet available: {'Yes' if results.get('internet_available', False) else 'No'}")
#                 report.append(f"  Firewall status: {results.get('firewall_status', 'Unknown')}")
            
#             # Add detailed messages
#             if results.get('details'):
#                 report.append("  Details:")
#                 for detail in results.get('details', []):
#                     report.append(f"    - {detail}")
            
#             report.append("")
        
#         # Add footer
#         report.append("=" * 60)
#         report.append("End of Report")
#         report.append("=" * 60)
        
#         return "\n".join(report)


# -- 3 --
"""
Palm Secure Diagnostics Module
==============================

This module provides diagnostic functions for PalmSecure devices.
"""
import os
import platform
import sys
import time
from typing import Dict, Any, List, Tuple

import usb.core
import usb.util

from palm_secure.device import find_devices
from palm_secure.utils import is_admin, is_driver_installed, check_compatibility


class DiagnosticsManager:
    """
    Class to perform diagnostics on PalmSecure devices.
    """
    
    def __init__(self):
        """Initialize the diagnostics manager."""
        self.results = {}
    
    def run_all_diagnostics(self) -> Dict[str, Any]:
        """
        Run all available diagnostic tests.
        
        Returns:
            Dict containing all diagnostic results
        """
        # Check USB subsystem
        usb_results = self.check_usb_subsystem()
        self.results['usb_subsystem'] = usb_results
        
        # Check drivers
        driver_results = self.check_drivers()
        self.results['drivers'] = driver_results
        
        # Check permissions
        permission_results = self.check_permissions()
        self.results['permissions'] = permission_results
        
        # Check device detection
        device_results = self.check_device_detection()
        self.results['device_detection'] = device_results
        
        # Check network
        network_results = self.check_network()
        self.results['network'] = network_results
        
        # Get overall assessment
        self.results['overall'] = self.get_overall_assessment()
        
        return self.results
    
    def check_usb_subsystem(self) -> Dict[str, Any]:
        """
        Check the USB subsystem on the host machine.
        
        Returns:
            Dict containing USB subsystem diagnostic results
        """
        results = {
            'status': 'OK',
            'details': [],
            'usb_version': 'Unknown',
            'usb_controllers': [],
            'pyusb_version': 'Unknown',
            'backend': 'Unknown',
        }
        
        # Check PyUSB version
        try:
            import usb
            results['pyusb_version'] = usb.__version__
            results['details'].append(f"PyUSB version: {usb.__version__}")
        except ImportError:
            results['status'] = 'ERROR'
            results['details'].append("PyUSB not installed")
        
        # Check USB backend
        try:
            backend = usb.backend.libusb1.get_backend()
            if backend:
                results['backend'] = 'libusb1'
                results['details'].append("USB backend: libusb1")
            else:
                # Try to check if we can import our custom backend
                try:
                    from usb_config import get_usb_backend
                    backend = get_usb_backend()
                    if backend:
                        results['backend'] = 'custom_libusb1'
                        results['details'].append("USB backend: custom libusb1")
                    else:
                        results['status'] = 'WARNING'
                        results['details'].append("Custom USB backend failed to load")
                except ImportError:
                    results['status'] = 'ERROR'
                    results['details'].append("No USB backend available")
        except Exception as e:
            results['status'] = 'ERROR'
            results['details'].append(f"Error checking USB backend: {str(e)}")
        
        # Check USB controllers
        try:
            devices = list(usb.core.find(find_all=True))
            host_controllers = set()
            
            for dev in devices:
                if dev.bDeviceClass == 9:  # Hub class
                    host_controllers.add((dev.idVendor, dev.idProduct))
            
            results['usb_controllers'] = [
                {'vendor_id': vc[0], 'product_id': vc[1]} for vc in host_controllers
            ]
            
            results['details'].append(f"Found {len(host_controllers)} USB controllers")
            
            if not host_controllers:
                results['status'] = 'WARNING'
                results['details'].append("No USB controllers detected")
        except Exception as e:
            results['status'] = 'ERROR'
            results['details'].append(f"Error checking USB controllers: {str(e)}")
        
        # Check if we can enumerate USB devices
        try:
            devices = list(usb.core.find(find_all=True))
            results['details'].append(f"Found {len(devices)} USB devices")
            
            if not devices:
                results['status'] = 'WARNING'
                results['details'].append("No USB devices detected")
        except Exception as e:
            results['status'] = 'ERROR'
            results['details'].append(f"Error enumerating USB devices: {str(e)}")
        
        return results
    
    def check_drivers(self) -> Dict[str, Any]:
        """
        Check if required drivers are installed and working.
        
        Returns:
            Dict containing driver diagnostic results
        """
        # Check for our custom driver info file
        driver_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fujitsu_driver_info.txt')
        if os.path.exists(driver_info_path):
            with open(driver_info_path, 'r') as f:
                driver_info = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        driver_info[key] = value
                
                return {
                    'status': 'OK',
                    'installed': True,
                    'version': driver_info.get('driver_version', 'Unknown'),
                    'compatible': driver_info.get('driver_compatible', 'false').lower() == 'true',
                    'details': f"Driver found at: {driver_info.get('driver_path', 'Unknown')}"
                }

        # If custom driver info not found, check system drivers
        results = {
            'status': 'OK',
            'installed': False,
            'version': 'Unknown',
            'compatible': False,
            'details': [],
        }
        
        # Check if PalmSecure driver is installed
        is_installed, version = is_driver_installed()
        results['installed'] = is_installed
        results['version'] = version if version else 'Unknown'
        
        if is_installed:
            results['details'].append(f"PalmSecure driver installed (version: {version})")
            results['compatible'] = True
        else:
            results['status'] = 'ERROR'
            results['details'].append("PalmSecure driver not installed")
        
        # Check compatibility of the driver with the system
        compatibility = check_compatibility()
        results['details'].append(f"System compatibility: {compatibility.get('status', 'Unknown')}")
        
        if compatibility.get('status') == 'ERROR':
            results['status'] = 'ERROR'
            results['compatible'] = False
            results['details'].append(compatibility.get('message', 'Incompatible system'))
        
        return results
    
    def check_permissions(self) -> Dict[str, Any]:
        """
        Check if the current user has sufficient permissions.
        
        Returns:
            Dict containing permissions diagnostic results
        """
        results = {
            'status': 'OK',
            'is_admin': False,
            'can_access_usb': False,
            'details': [],
        }
        
        # Check if running as admin/root
        is_admin_user = is_admin()
        results['is_admin'] = is_admin_user
        
        if is_admin_user:
            results['details'].append("Running with administrative privileges")
        else:
            if platform.system() == 'Windows':
                results['status'] = 'WARNING'
                results['details'].append("Not running as administrator. Some functions may be limited.")
            elif platform.system() in ('Linux', 'Darwin'):
                # On Unix systems, check if the user is in the required groups
                try:
                    import pwd
                    import grp
                    
                    user = pwd.getpwuid(os.getuid()).pw_name
                    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
                    
                    # Check if user is in required groups
                    required_groups = ['dialout', 'usb', 'plugdev']
                    missing_groups = [g for g in required_groups if g not in groups]
                    
                    if missing_groups:
                        results['status'] = 'WARNING'
                        results['details'].append(f"User not in required groups: {', '.join(missing_groups)}")
                    else:
                        results['details'].append(f"User in required groups: {', '.join([g for g in required_groups if g in groups])}")
                        results['can_access_usb'] = True
                except ImportError:
                    results['status'] = 'WARNING'
                    results['details'].append("Could not check user groups")
        
        # Try to access a USB device to check permissions
        try:
            devices = list(usb.core.find(find_all=True))
            if devices:
                # Try to get descriptor for the first device
                try:
                    device = devices[0]
                    device.get_active_configuration()
                    results['can_access_usb'] = True
                    results['details'].append("Successfully accessed USB device")
                except (usb.core.USBError, Exception) as e:
                    if "Insufficient permissions" in str(e) or "Access denied" in str(e):
                        results['status'] = 'ERROR'
                        results['details'].append(f"Insufficient permissions to access USB devices: {str(e)}")
                    else:
                        # Other errors might not be permission-related
                        results['details'].append(f"Could not fully access USB device: {str(e)}")
        except Exception as e:
            results['status'] = 'WARNING'
            results['details'].append(f"Error checking USB access permissions: {str(e)}")
        
        return results
    
    def check_device_detection(self) -> Dict[str, Any]:
        """
        Check if PalmSecure devices can be detected.
        
        Returns:
            Dict containing device detection diagnostic results
        """
        results = {
            'status': 'OK',
            'devices_found': 0,
            'devices': [],
            'details': [],
        }
        
        try:
            # Try to find PalmSecure devices
            devices = find_devices()
            results['devices_found'] = len(devices)
            results['devices'] = devices
            
            if devices:
                results['details'].append(f"Found {len(devices)} PalmSecure devices")
                for i, device in enumerate(devices):
                    vendor_id = device.get('vendor_id', 'Unknown')
                    product_id = device.get('product_id', 'Unknown')
                    manufacturer = device.get('manufacturer', 'Unknown')
                    product = device.get('product', 'Unknown')
                    
                    results['details'].append(f"Device {i+1}: {manufacturer} {product} ({vendor_id:04x}:{product_id:04x})")
            else:
                results['status'] = 'WARNING'
                results['details'].append("No PalmSecure devices found")
                
                # Check if any USB devices are found
                try:
                    all_devices = list(usb.core.find(find_all=True))
                    if all_devices:
                        results['details'].append(f"Found {len(all_devices)} USB devices but none match PalmSecure IDs")
                    else:
                        results['status'] = 'ERROR'
                        results['details'].append("No USB devices found at all")
                except Exception as e:
                    results['details'].append(f"Error checking all USB devices: {str(e)}")
        
        except DeviceNotFoundError:
            results['status'] = 'WARNING'
            results['details'].append("No PalmSecure devices found")
        
        except Exception as e:
            results['status'] = 'ERROR'
            results['details'].append(f"Error detecting devices: {str(e)}")
        
        return results
    
    def check_network(self) -> Dict[str, Any]:
        """
        Check network connectivity, which may be needed for certain features.
        
        Returns:
            Dict containing network diagnostic results
        """
        results = {
            'status': 'OK',
            'details': [],
        }
        
        # This is mostly a placeholder - for a local SDK, network connectivity
        # isn't typically required, but could be useful for cloud features
        results['details'].append("Network connectivity not required for basic PalmSecure operation")
        
        return results
    
    def get_overall_assessment(self) -> Dict[str, Any]:
        """
        Get an overall assessment of the system's ability to use PalmSecure devices.
        
        Returns:
            Dict containing overall assessment
        """
        # Check if we have run diagnostics
        if not self.results:
            self.run_all_diagnostics()
        
        # Initialize the assessment
        assessment = {
            'status': 'OK',
            'message': 'System is ready for PalmSecure devices',
            'ready': True,
            'issues': [],
            'system_compatibility': {
                'status': 'OK',
                'compatible': True,
                'issues': []
            }
        }
        
        # Check if any critical components have errors
        for component, result in self.results.items():
            if component != 'overall' and result.get('status') == 'ERROR':
                assessment['status'] = 'ERROR'
                assessment['ready'] = False
                issue = f"{component}: {result.get('details', ['Unknown error'])[0] if isinstance(result.get('details', []), list) else result.get('details', 'Unknown error')}"
                assessment['issues'].append(issue)
                
                # Add to system compatibility issues too
                assessment['system_compatibility']['issues'].append(issue)
                assessment['system_compatibility']['status'] = 'ERROR'
                assessment['system_compatibility']['compatible'] = False
        
        if not assessment['ready']:
            assessment['message'] = 'System has critical issues that prevent PalmSecure operation'
        
        # Check if any components have warnings
        for component, result in self.results.items():
            if component != 'overall' and result.get('status') == 'WARNING':
                # Only set overall status to warning if it's not already an error
                if assessment['status'] != 'ERROR':
                    assessment['status'] = 'WARNING'
                
                issue = f"{component}: {result.get('details', ['Unknown warning'])[0] if isinstance(result.get('details', []), list) else result.get('details', 'Unknown warning')}"
                assessment['issues'].append(issue)
                
                # Add to system compatibility issues only if not already flagged as error
                if assessment['system_compatibility']['status'] != 'ERROR':
                    assessment['system_compatibility']['issues'].append(issue)
                    assessment['system_compatibility']['status'] = 'WARNING'
        
        return assessment
    
    def generate_report(self) -> str:
        """
        Generate a human-readable diagnostic report.
        
        Returns:
            String containing the report
        """
        # Run diagnostics if not already run
        if not self.results:
            self.run_all_diagnostics()
        
        report = []
        
        # Add report header
        report.append("PalmSecure SDK Diagnostic Report")
        report.append("==============================")
        report.append("")
        report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Platform: {platform.platform()}")
        report.append(f"Python: {platform.python_version()}")
        report.append("")
        
        # Add system assessment
        overall = self.results.get('overall', {})
        report.append("System Assessment")
        report.append("-----------------")
        report.append(f"Status: {overall.get('status', 'Unknown')}")
        report.append(f"Ready for PalmSecure: {'Yes' if overall.get('ready', False) else 'No'}")
        
        # Ensure system_compatibility exists
        if 'system_compatibility' not in overall:
            overall['system_compatibility'] = {
                'status': 'WARNING',
                'compatible': False,
                'issues': ['System compatibility check was not complete']
            }
        
        system_compat = overall.get('system_compatibility', {})
        report.append(f"System compatibility: {system_compat.get('status', 'Unknown')}")
        
        if 'issues' in overall and overall['issues']:
            report.append("")
            report.append("Issues:")
            for issue in overall['issues']:
                report.append(f"- {issue}")
        
        # Add USB subsystem details
        report.append("")
        report.append("USB Subsystem")
        report.append("------------")
        usb = self.results.get('usb_subsystem', {})
        report.append(f"Status: {usb.get('status', 'Unknown')}")
        report.append(f"PyUSB version: {usb.get('pyusb_version', 'Unknown')}")
        report.append(f"Backend: {usb.get('backend', 'Unknown')}")
        
        if 'details' in usb and usb['details']:
            for detail in usb['details']:
                report.append(f"- {detail}")
        
        # Add driver details
        report.append("")
        report.append("PalmSecure Drivers")
        report.append("------------------")
        drivers = self.results.get('drivers', {})
        report.append(f"Status: {drivers.get('status', 'Unknown')}")
        report.append(f"Installed: {'Yes' if drivers.get('installed', False) else 'No'}")
        report.append(f"Version: {drivers.get('version', 'Unknown')}")
        report.append(f"Compatible: {'Yes' if drivers.get('compatible', False) else 'No'}")
        
        if 'details' in drivers and drivers['details']:
            if isinstance(drivers['details'], list):
                for detail in drivers['details']:
                    report.append(f"- {detail}")
            else:
                report.append(f"- {drivers['details']}")
        
        # Add permissions details
        report.append("")
        report.append("Permissions")
        report.append("-----------")
        perms = self.results.get('permissions', {})
        report.append(f"Status: {perms.get('status', 'Unknown')}")
        report.append(f"Administrative privileges: {'Yes' if perms.get('is_admin', False) else 'No'}")
        report.append(f"Can access USB devices: {'Yes' if perms.get('can_access_usb', False) else 'No'}")
        
        if 'details' in perms and perms['details']:
            for detail in perms['details']:
                report.append(f"- {detail}")
        
        # Add device detection details
        report.append("")
        report.append("Device Detection")
        report.append("----------------")
        detect = self.results.get('device_detection', {})
        report.append(f"Status: {detect.get('status', 'Unknown')}")
        report.append(f"Devices found: {detect.get('devices_found', 0)}")
        
        if 'devices' in detect and detect['devices']:
            report.append("")
            report.append("Detected devices:")
            for i, device in enumerate(detect['devices']):
                report.append(f"Device {i+1}:")
                report.append(f"  - Vendor ID: {device.get('vendor_id', 'Unknown')}")
                report.append(f"  - Product ID: {device.get('product_id', 'Unknown')}")
                report.append(f"  - Manufacturer: {device.get('manufacturer', 'Unknown')}")
                report.append(f"  - Product: {device.get('product', 'Unknown')}")
        
        if 'details' in detect and detect['details']:
            report.append("")
            for detail in detect['details']:
                report.append(f"- {detail}")
        
        # Add network details
        report.append("")
        report.append("Network Connectivity")
        report.append("--------------------")
        network = self.results.get('network', {})
        report.append(f"Status: {network.get('status', 'Unknown')}")
        
        if 'details' in network and network['details']:
            for detail in network['details']:
                report.append(f"- {detail}")
        
        # Join all lines and return
        return "\n".join(report)