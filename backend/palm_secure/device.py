# """
# PalmSecure Device Module
# ========================

# This module provides the main interface for interacting with PalmSecure devices.
# """

# import logging
# import time
# import platform
# from typing import List, Optional, Dict, Any, Tuple

# import usb.core
# import usb.util

# from .exceptions import DeviceNotFoundError, ConnectionError, OperationError
# from .constants import (
#     PALM_SECURE_VID,
#     PALM_SECURE_PID,
#     DEVICE_STATES,
#     CONTROL_ENDPOINTS,
#     CONNECTION_TIMEOUT
# )
# from .utils import parse_device_info

# logger = logging.getLogger(__name__)


# def find_devices() -> List[Dict[str, Any]]:
#     """
#     Find all connected PalmSecure devices.

#     Returns:
#         List of dicts containing device information.
        
#     Raises:
#         DeviceNotFoundError: If no devices are found.
#     """
#     try:
#         devices = usb.core.find(
#             find_all=True,
#             idVendor=PALM_SECURE_VID,
#             idProduct=PALM_SECURE_PID
#         )
        
#         device_list = []
#         for device in devices:
#             device_info = {
#                 'bus': device.bus,
#                 'address': device.address,
#                 'serial_number': _get_serial_number(device),
#                 'manufacturer': _get_manufacturer(device),
#                 'product': _get_product(device),
#                 'version': _get_version_info(device)
#             }
#             device_list.append(device_info)
        
#         if not device_list:
#             raise DeviceNotFoundError("No PalmSecure devices found")
            
#         return device_list
    
#     except usb.core.USBError as e:
#         logger.error(f"USB error when finding devices: {str(e)}")
#         raise DeviceNotFoundError(f"Error finding devices: {str(e)}")


# def _get_serial_number(device: usb.core.Device) -> str:
#     """Get device serial number if available."""
#     try:
#         return usb.util.get_string(device, device.iSerialNumber)
#     except (ValueError, usb.core.USBError):
#         return "Unknown"


# def _get_manufacturer(device: usb.core.Device) -> str:
#     """Get device manufacturer if available."""
#     try:
#         return usb.util.get_string(device, device.iManufacturer)
#     except (ValueError, usb.core.USBError):
#         return "FUJITSU FRONTECH LIMITED"


# def _get_product(device: usb.core.Device) -> str:
#     """Get device product name if available."""
#     try:
#         return usb.util.get_string(device, device.iProduct)
#     except (ValueError, usb.core.USBError):
#         return "PalmSecure"


# def _get_version_info(device: usb.core.Device) -> Dict[str, Any]:
#     """Get device driver and firmware version info."""
#     # This would typically involve sending specific commands to the device
#     # For now, we return a placeholder dictionary
#     return {
#         'driver': "Unknown",
#         'firmware': "Unknown"
#     }


# class PalmSecureDevice:
#     """
#     Main class for interacting with PalmSecure devices.
    
#     Attributes:
#         device_path (str): Path or identifier for the device
#         is_connected (bool): Whether the device is currently connected
#         device_info (dict): Information about the connected device
#     """
    
#     def __init__(self, device_info: Optional[Dict[str, Any]] = None, auto_connect: bool = False):
#         """
#         Initialize a PalmSecureDevice instance.
        
#         Args:
#             device_info: Device information dictionary (from find_devices)
#             auto_connect: Whether to automatically connect to the device
#         """
#         self.device_info = device_info
#         self.device = None
#         self.is_connected = False
#         self.interface = None
#         self.state = DEVICE_STATES["DISCONNECTED"]
        
#         if auto_connect and device_info:
#             self.connect()
    
#     def connect(self) -> bool:
#         """
#         Connect to the PalmSecure device.
        
#         Returns:
#             bool: True if connection is successful, False otherwise.
            
#         Raises:
#             ConnectionError: If connection fails.
#         """
#         if self.is_connected:
#             logger.warning("Device is already connected")
#             return True
        
#         try:
#             # Find the device by vendor ID and product ID
#             if not self.device_info:
#                 devices = find_devices()
#                 if devices:
#                     self.device_info = devices[0]
#                 else:
#                     raise DeviceNotFoundError("No PalmSecure devices found")
            
#             # Get the device from the bus and address in device_info
#             bus = self.device_info.get('bus')
#             address = self.device_info.get('address')
            
#             if bus is not None and address is not None:
#                 devices = usb.core.find(
#                     find_all=True,
#                     idVendor=PALM_SECURE_VID,
#                     idProduct=PALM_SECURE_PID
#                 )
                
#                 self.device = None
#                 for dev in devices:
#                     if dev.bus == bus and dev.address == address:
#                         self.device = dev
#                         break
#             else:
#                 # Fallback to first device if bus/address not specified
#                 self.device = usb.core.find(
#                     idVendor=PALM_SECURE_VID,
#                     idProduct=PALM_SECURE_PID
#                 )
            
#             if self.device is None:
#                 raise DeviceNotFoundError("Device not found on the specified bus/address")
            
#             # On Windows, we need to set the configuration and claim the interface
#             if platform.system() == "Windows":
#                 # Detach kernel driver if it's attached
#                 for config in self.device:
#                     for interface in range(config.bNumInterfaces):
#                         if self.device.is_kernel_driver_active(interface):
#                             try:
#                                 self.device.detach_kernel_driver(interface)
#                             except usb.core.USBError as e:
#                                 logger.warning(f"Could not detach kernel driver: {str(e)}")
                
#                 # Set configuration
#                 self.device.set_configuration()
                
#                 # Find and claim the first interface
#                 cfg = self.device.get_active_configuration()
#                 interface_number = cfg[(0, 0)].bInterfaceNumber
#                 self.interface = interface_number
                
#                 # Claim the interface
#                 usb.util.claim_interface(self.device, interface_number)
            
#             self.is_connected = True
#             self.state = DEVICE_STATES["CONNECTED"]
#             logger.info("Successfully connected to PalmSecure device")
            
#             # Get full device information
#             self._update_device_info()
            
#             return True
        
#         except usb.core.USBError as e:
#             logger.error(f"USB error when connecting: {str(e)}")
#             self.device = None
#             self.is_connected = False
#             self.state = DEVICE_STATES["ERROR"]
#             raise ConnectionError(f"Failed to connect to device: {str(e)}")
    
#     def disconnect(self) -> bool:
#         """
#         Disconnect from the PalmSecure device.
        
#         Returns:
#             bool: True if disconnection is successful.
#         """
#         if not self.is_connected:
#             logger.warning("Device is not connected")
#             return True
        
#         try:
#             if self.device and self.interface is not None and platform.system() == "Windows":
#                 usb.util.release_interface(self.device, self.interface)
                
#                 try:
#                     # Reattach the kernel driver if we've detached it
#                     self.device.attach_kernel_driver(self.interface)
#                 except (usb.core.USBError, AttributeError):
#                     # This may not be supported on all platforms
#                     pass
            
#             # Release resources
#             usb.util.dispose_resources(self.device)
            
#             self.device = None
#             self.is_connected = False
#             self.state = DEVICE_STATES["DISCONNECTED"]
#             logger.info("Disconnected from PalmSecure device")
            
#             return True
        
#         except usb.core.USBError as e:
#             logger.error(f"Error during disconnect: {str(e)}")
#             # Even on error, we consider the device disconnected
#             self.device = None
#             self.is_connected = False
#             self.state = DEVICE_STATES["ERROR"]
#             return False
    
#     def _update_device_info(self) -> None:
#         """
#         Update device information from the connected device.
#         """
#         if not self.is_connected or not self.device:
#             raise ConnectionError("Device not connected")
        
#         try:
#             # Get device descriptor information
#             manufacturer = _get_manufacturer(self.device)
#             product = _get_product(self.device)
#             serial_number = _get_serial_number(self.device)
            
#             # Read device configuration through control endpoints
#             # This is a simplified implementation
#             version_info = self._get_device_version()
            
#             # Update device info dictionary
#             if not self.device_info:
#                 self.device_info = {}
            
#             self.device_info.update({
#                 'manufacturer': manufacturer,
#                 'product': product,
#                 'serial_number': serial_number,
#                 'version': version_info,
#                 'bus': self.device.bus,
#                 'address': self.device.address
#             })
        
#         except usb.core.USBError as e:
#             logger.error(f"Error updating device info: {str(e)}")
#             self.state = DEVICE_STATES["ERROR"]
    
#     def _get_device_version(self) -> Dict[str, str]:
#         """
#         Get device driver and firmware version information.
        
#         Returns:
#             Dict with driver and firmware version strings.
#         """
#         # This would need to implement the actual protocol for querying version info
#         # Since we don't have the actual protocol specifications, this is a placeholder
#         return {
#             'driver': self._read_driver_version(),
#             'firmware': self._read_firmware_version()
#         }
    
#     def _read_driver_version(self) -> str:
#         """Read the driver version from the device."""
#         # This is a simplified implementation without actual protocol knowledge
#         try:
#             # Attempt to get version info via control transfer
#             # These values would need to be adjusted based on actual device protocol
#             result = self.device.ctrl_transfer(
#                 bmRequestType=0xC0,  # Device to host, vendor specific
#                 bRequest=CONTROL_ENDPOINTS.get("GET_VERSION", 0x01),
#                 wValue=0x0000,
#                 wIndex=0x0000,
#                 data_or_wLength=64
#             )
            
#             if result:
#                 # Parse the version string from the result
#                 version_str = ''.join(chr(x) for x in result if x > 0 and x < 128)
#                 return version_str.strip('\0')
            
#             return "Unknown"
        
#         except usb.core.USBError:
#             return "Unknown"
    
#     def _read_firmware_version(self) -> str:
#         """Read the firmware version from the device."""
#         # This is a simplified implementation without actual protocol knowledge
#         try:
#             # Attempt to get firmware version via control transfer
#             result = self.device.ctrl_transfer(
#                 bmRequestType=0xC0,  # Device to host, vendor specific
#                 bRequest=CONTROL_ENDPOINTS.get("GET_FIRMWARE", 0x02),
#                 wValue=0x0000,
#                 wIndex=0x0000,
#                 data_or_wLength=64
#             )
            
#             if result:
#                 # Parse the version string from the result
#                 version_str = ''.join(chr(x) for x in result if x > 0 and x < 128)
#                 return version_str.strip('\0')
            
#             return "Unknown"
        
#         except usb.core.USBError:
#             return "Unknown"
    
#     def get_device_info(self) -> Dict[str, Any]:
#         """
#         Get information about the connected device.
        
#         Returns:
#             Dict containing device information.
            
#         Raises:
#             ConnectionError: If device is not connected.
#         """
#         if not self.is_connected:
#             raise ConnectionError("Device not connected")
        
#         return self.device_info
    
#     def get_status(self) -> Dict[str, Any]:
#         """
#         Get current device status.
        
#         Returns:
#             Dict containing status information.
            
#         Raises:
#             ConnectionError: If device is not connected.
#         """
#         if not self.is_connected:
#             raise ConnectionError("Device not connected")
        
#         try:
#             # This would typically involve sending specific commands to query status
#             # For a real implementation, you'd need to know the device protocol
#             status = {
#                 'state': self.state,
#                 'connected': self.is_connected,
#                 'device_id': f"{self.device_info.get('bus', 0):03d}:{self.device_info.get('address', 0):03d}",
#                 'last_error': None,
#                 'ready': self.state == DEVICE_STATES["CONNECTED"]
#             }
            
#             return status
        
#         except usb.core.USBError as e:
#             logger.error(f"Error getting device status: {str(e)}")
#             self.state = DEVICE_STATES["ERROR"]
#             raise OperationError(f"Failed to get device status: {str(e)}")
    
#     def send_command(self, command: int, data: bytes = None, timeout: int = CONNECTION_TIMEOUT) -> bytes:
#         """
#         Send a command to the device.
        
#         Args:
#             command: Command identifier
#             data: Optional data to send with the command
#             timeout: Timeout in milliseconds
            
#         Returns:
#             Response data from the device
            
#         Raises:
#             ConnectionError: If device is not connected
#             OperationError: If command fails
#         """
#         if not self.is_connected or not self.device:
#             raise ConnectionError("Device not connected")
        
#         try:
#             # This is a simplified implementation - real commands would depend on the device protocol
#             # For control transfers, we use a vendor-specific request type
#             bmRequestType = 0x40  # Host to device, vendor specific
            
#             if data:
#                 result = self.device.ctrl_transfer(
#                     bmRequestType=bmRequestType,
#                     bRequest=command,
#                     wValue=0x0000,
#                     wIndex=0x0000,
#                     data_or_wLength=data,
#                     timeout=timeout
#                 )
#             else:
#                 result = self.device.ctrl_transfer(
#                     bmRequestType=bmRequestType,
#                     bRequest=command,
#                     wValue=0x0000,
#                     wIndex=0x0000,
#                     data_or_wLength=64,  # Just get 64 bytes
#                     timeout=timeout
#                 )
            
#             return result
        
#         except usb.core.USBError as e:
#             logger.error(f"Error sending command: {str(e)}")
#             raise OperationError(f"Failed to send command: {str(e)}")
    
#     def initialize(self) -> bool:
#         """
#         Initialize the device for operation.
        
#         Returns:
#             bool: True if initialization is successful
            
#         Raises:
#             ConnectionError: If device is not connected
#             OperationError: If initialization fails
#         """
#         if not self.is_connected:
#             raise ConnectionError("Device not connected")
        
#         try:
#             # This would implement the initialization sequence for the device
#             # Since we don't know the actual protocol, this is a placeholder
            
#             # Example: Send initialization commands
#             self.send_command(CONTROL_ENDPOINTS.get("INITIALIZE", 0x03))
            
#             # Wait for device to be ready
#             time.sleep(0.5)
            
#             # Check if device is ready
#             result = self.send_command(CONTROL_ENDPOINTS.get("GET_STATUS", 0x04))
            
#             # Parse result to determine if initialization was successful
#             if result and result[0] == 0x01:  # Example success code
#                 self.state = DEVICE_STATES["READY"]
#                 return True
#             else:
#                 self.state = DEVICE_STATES["ERROR"]
#                 return False
        
#         except OperationError as e:
#             self.state = DEVICE_STATES["ERROR"]
#             raise OperationError(f"Failed to initialize device: {str(e)}")
    
#     def reset(self) -> bool:
#         """
#         Reset the device.
        
#         Returns:
#             bool: True if reset is successful
            
#         Raises:
#             ConnectionError: If device is not connected
#             OperationError: If reset fails
#         """
#         if not self.is_connected:
#             raise ConnectionError("Device not connected")
        
#         try:
#             # Send reset command
#             self.send_command(CONTROL_ENDPOINTS.get("RESET", 0x05))
            
#             # Wait for device to reset
#             time.sleep(1.0)
            
#             # Reconnect to the device
#             self.disconnect()
#             time.sleep(0.5)
#             return self.connect()
        
#         except (ConnectionError, OperationError) as e:
#             logger.error(f"Error resetting device: {str(e)}")
#             self.state = DEVICE_STATES["ERROR"]
#             raise OperationError(f"Failed to reset device: {str(e)}")
    
#     def __enter__(self):
#         """Context manager enter method."""
#         if not self.is_connected:
#             self.connect()
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Context manager exit method."""
#         self.disconnect()

#     def __repr__(self):
#         """String representation of the device."""
#         if self.is_connected and self.device_info:
#             return f"PalmSecureDevice(bus={self.device_info.get('bus')}, address={self.device_info.get('address')}, connected=True)"
#         else:
#             return "PalmSecureDevice(connected=False)"



## -- 2 --
"""
PalmSecure Device Module
========================

This module provides the main interface for interacting with PalmSecure devices.
"""
import os
import time
from typing import Dict, List, Any, Optional, Tuple

import usb.core
import usb.util

# Import custom backend configuration
try:
    from usb_config import get_usb_backend
    USB_BACKEND = get_usb_backend()
except ImportError:
    USB_BACKEND = None

from palm_secure.constants import (
    VENDOR_IDS,
    PRODUCT_IDS,
    DEVICE_CLASSES,
    CONNECTION_TIMEOUT,
    COMMAND_INITIALIZE,
    COMMAND_RESET,
    COMMAND_GET_STATUS,
    STATUS_OK,
    ERROR_CODES,
)

from palm_secure.exceptions import (
    DeviceNotFoundError,
    ConnectionError,
    OperationError,
    InitializationError,
    TimeoutError,
)


def find_devices() -> List[Dict[str, Any]]:
    """
    Find all connected PalmSecure devices.

    Returns:
        List of dicts containing device information.
        
    Raises:
        DeviceNotFoundError: If no devices are found.
    """
    try:
        # Use our custom backend
        devices = list(usb.core.find(find_all=True, backend=USB_BACKEND))
        
        palm_devices = []
        
        for device in devices:
            # Check if the device matches any of our known PalmSecure devices
            is_palm_device = (
                device.idVendor in VENDOR_IDS and
                device.idProduct in PRODUCT_IDS
            ) or (
                device.bDeviceClass in DEVICE_CLASSES
            )
            
            if is_palm_device:
                device_info = {
                    'bus': device.bus,
                    'address': device.address,
                    'vendor_id': device.idVendor,
                    'product_id': device.idProduct,
                    'serial_number': _get_serial_number(device),
                    'manufacturer': _get_manufacturer(device),
                    'product': _get_product(device),
                    'version_info': _get_version_info(device),
                }
                palm_devices.append(device_info)
        
        if not palm_devices:
            # If we didn't find specific palm devices, grab any device that might be a palm device
            # This is useful for development and debugging
            for device in devices:
                # If the device doesn't have a manufacturer or product string, it may not be initialized
                # or the driver might not be properly installed
                device_info = {
                    'bus': device.bus,
                    'address': device.address,
                    'vendor_id': device.idVendor,
                    'product_id': device.idProduct,
                    'serial_number': _get_serial_number(device),
                    'manufacturer': _get_manufacturer(device),
                    'product': _get_product(device),
                    'version_info': _get_version_info(device),
                    'possible_palm_device': True,
                }
                palm_devices.append(device_info)
        
        return palm_devices
        
    except usb.core.NoBackendError:
        raise DeviceNotFoundError("No USB backend found. Make sure libusb is installed.")
    except Exception as e:
        raise DeviceNotFoundError(f"Error finding devices: {str(e)}")


def _get_serial_number(device: usb.core.Device) -> str:
    """Get device serial number if available."""
    try:
        return usb.util.get_string(device, device.iSerialNumber)
    except (usb.core.USBError, ValueError, AttributeError):
        return "Unknown"


def _get_manufacturer(device: usb.core.Device) -> str:
    """Get device manufacturer if available."""
    try:
        return usb.util.get_string(device, device.iManufacturer)
    except (usb.core.USBError, ValueError, AttributeError):
        return "Unknown"


def _get_product(device: usb.core.Device) -> str:
    """Get device product name if available."""
    try:
        return usb.util.get_string(device, device.iProduct)
    except (usb.core.USBError, ValueError, AttributeError):
        return "Unknown"


def _get_version_info(device: usb.core.Device) -> Dict[str, Any]:
    """Get device driver and firmware version info."""
    # This would typically involve sending a command to the device to request version info
    # For now, we'll return dummy data
    return {
        'driver': '1.0.0',
        'firmware': '1.0.0',
    }


class PalmSecureDevice:
    """
    Main class for interacting with PalmSecure devices.
    
    Attributes:
        device_path (str): Path or identifier for the device
        is_connected (bool): Whether the device is currently connected
        device_info (dict): Information about the connected device
    """
    
    def __init__(self, device_info: Optional[Dict[str, Any]] = None, auto_connect: bool = False):
        """
        Initialize a PalmSecureDevice instance.
        
        Args:
            device_info: Device information dictionary (from find_devices)
            auto_connect: Whether to automatically connect to the device
        """
        self.device_info = device_info or {}
        self.device = None
        self.is_connected = False
        self.interface = None
        self.endpoint_in = None
        self.endpoint_out = None
        
        if auto_connect and device_info:
            self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the PalmSecure device.
        
        Returns:
            bool: True if connection is successful, False otherwise.
            
        Raises:
            ConnectionError: If connection fails.
        """
        if self.is_connected:
            return True
        
        try:
            # Find the device by vendor and product ID
            vendor_id = self.device_info.get('vendor_id')
            product_id = self.device_info.get('product_id')
            
            if not vendor_id or not product_id:
                raise ConnectionError("Device information is incomplete. Missing vendor or product ID.")
            
            # Use our custom backend
            self.device = usb.core.find(idVendor=vendor_id, idProduct=product_id, backend=USB_BACKEND)
            
            if self.device is None:
                raise ConnectionError(f"Device not found: {vendor_id:04x}:{product_id:04x}")
            
            # Check if kernel driver is attached and detach it if needed
            try:
                if self.device.is_kernel_driver_active(0):
                    self.device.detach_kernel_driver(0)
            except (usb.core.USBError, NotImplementedError):
                # Either detaching failed or not supported on this platform
                pass
                
            # Set configuration
            try:
                self.device.set_configuration()
            except usb.core.USBError as e:
                # Some devices don't require this step
                pass
                
            # Get interface
            cfg = self.device.get_active_configuration()
            interface_number = cfg[(0, 0)].bInterfaceNumber
            self.interface = usb.util.find_descriptor(
                cfg, bInterfaceNumber=interface_number
            )
            
            # Get endpoints
            self.endpoint_in = usb.util.find_descriptor(
                self.interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            self.endpoint_out = usb.util.find_descriptor(
                self.interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            if not self.endpoint_in or not self.endpoint_out:
                raise ConnectionError("Could not find necessary endpoints on the device")
            
            self.is_connected = True
            self._update_device_info()
            
            return True
            
        except usb.core.USBError as e:
            raise ConnectionError(f"USB Error: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Connection error: {str(e)}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the PalmSecure device.
        
        Returns:
            bool: True if disconnection is successful.
        """
        if not self.is_connected:
            return True
        
        try:
            # Release the interface if it exists
            if self.interface is not None:
                usb.util.release_interface(self.device, self.interface)
                
            # Reattach kernel driver if needed
            try:
                self.device.attach_kernel_driver(0)
            except (usb.core.USBError, NotImplementedError):
                # Either attaching failed or not supported on this platform
                pass
                
            # Reset the device
            try:
                self.device.reset()
            except usb.core.USBError:
                # Reset might fail if the device is already disconnected
                pass
                
            # Dispose of the device object
            usb.util.dispose_resources(self.device)
            
            self.device = None
            self.interface = None
            self.endpoint_in = None
            self.endpoint_out = None
            self.is_connected = False
            
            return True
            
        except Exception as e:
            # Log the error but don't raise, as we're disconnecting anyway
            print(f"Error during disconnect: {str(e)}")
            
            # Force cleanup of device resources
            self.device = None
            self.interface = None
            self.endpoint_in = None
            self.endpoint_out = None
            self.is_connected = False
            
            return False
    
    def _update_device_info(self) -> None:
        """
        Update device information from the connected device.
        """
        if not self.is_connected or not self.device:
            return
            
        try:
            # Update basic device information
            self.device_info.update({
                'bus': self.device.bus,
                'address': self.device.address,
                'vendor_id': self.device.idVendor,
                'product_id': self.device.idProduct,
                'serial_number': _get_serial_number(self.device),
                'manufacturer': _get_manufacturer(self.device),
                'product': _get_product(self.device),
            })
            
            # Update version information
            version_info = self._get_device_version()
            if version_info:
                self.device_info['version_info'] = version_info
                
        except Exception as e:
            # Log but don't raise, as this is non-critical
            print(f"Error updating device info: {str(e)}")
    
    def _get_device_version(self) -> Dict[str, str]:
        """
        Get device driver and firmware version information.
        
        Returns:
            Dict with driver and firmware version strings.
        """
        try:
            driver_version = self._read_driver_version()
            firmware_version = self._read_firmware_version()
            
            return {
                'driver': driver_version,
                'firmware': firmware_version,
            }
        except Exception as e:
            # Log but don't raise, as this is non-critical
            print(f"Error getting device version: {str(e)}")
            return {
                'driver': 'Unknown',
                'firmware': 'Unknown',
            }
    
    def _read_driver_version(self) -> str:
        """Read the driver version from the device."""
        # This would typically involve sending a command to the device
        # For now, return a dummy version
        return "1.0.0"
    
    def _read_firmware_version(self) -> str:
        """Read the firmware version from the device."""
        # This would typically involve sending a command to the device
        # For now, return a dummy version
        return "1.0.0"
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about the connected device.
        
        Returns:
            Dict containing device information.
            
        Raises:
            ConnectionError: If device is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Device is not connected")
            
        # Ensure we have the latest info
        self._update_device_info()
        
        return self.device_info
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current device status.
        
        Returns:
            Dict containing status information.
            
        Raises:
            ConnectionError: If device is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Device is not connected")
            
        try:
            # Send a status request command and get response
            response = self.send_command(COMMAND_GET_STATUS)
            
            # Parse the response into a status dictionary
            # This is a placeholder implementation
            status = {
                'status': STATUS_OK,
                'ready': True,
                'error_code': 0,
                'error_message': "",
                'timestamp': time.time(),
            }
            
            return status
            
        except Exception as e:
            # If the status command fails, the device might be in an error state
            error_msg = str(e)
            error_code = ERROR_CODES.get('UNKNOWN_ERROR', 0)
            
            # Try to extract a specific error code if available
            for name, code in ERROR_CODES.items():
                if name.lower() in error_msg.lower():
                    error_code = code
                    break
            
            return {
                'status': 'ERROR',
                'ready': False,
                'error_code': error_code,
                'error_message': error_msg,
                'timestamp': time.time(),
            }
    
    def send_command(self, command: int, data: bytes = None, timeout: int = CONNECTION_TIMEOUT) -> bytes:
        """
        Send a command to the device.
        
        Args:
            command: Command identifier
            data: Optional data to send with the command
            timeout: Timeout in milliseconds
            
        Returns:
            Response data from the device
            
        Raises:
            ConnectionError: If device is not connected
            OperationError: If command fails
        """
        if not self.is_connected:
            raise ConnectionError("Device is not connected")
            
        if not self.endpoint_out or not self.endpoint_in:
            raise ConnectionError("Device endpoints not available")
            
        try:
            # Prepare the command packet
            # This is a simplified implementation - actual protocol would depend on the device
            packet = bytearray([command & 0xFF, (command >> 8) & 0xFF])
            
            # Add data if provided
            if data:
                packet.extend(data)
                
            # Send the command
            bytes_sent = self.endpoint_out.write(packet, timeout=timeout)
            
            if bytes_sent != len(packet):
                raise OperationError(f"Failed to send complete command (sent {bytes_sent}/{len(packet)} bytes)")
                
            # Read the response
            response = self.endpoint_in.read(64, timeout=timeout)
            
            # Process the response
            # This is a simplified implementation - actual processing depends on the device protocol
            if len(response) < 2:
                raise OperationError("Invalid response from device (too short)")
                
            status = response[0] | (response[1] << 8)
            
            if status != STATUS_OK:
                error_message = f"Command failed with status: {status}"
                if status in ERROR_CODES.values():
                    for name, code in ERROR_CODES.items():
                        if code == status:
                            error_message = f"Command failed: {name}"
                            break
                
                raise OperationError(error_message)
                
            # Return the payload part of the response (strip status bytes)
            return bytes(response[2:])
            
        except usb.core.USBTimeoutError:
            raise TimeoutError(f"Command timed out after {timeout}ms")
        except usb.core.USBError as e:
            raise OperationError(f"USB error during command: {str(e)}")
        except Exception as e:
            raise OperationError(f"Command failed: {str(e)}")
    
    def initialize(self) -> bool:
        """
        Initialize the device for operation.
        
        Returns:
            bool: True if initialization is successful
            
        Raises:
            ConnectionError: If device is not connected
            OperationError: If initialization fails
        """
        if not self.is_connected:
            raise ConnectionError("Device is not connected")
            
        try:
            # Send initialization command
            self.send_command(COMMAND_INITIALIZE)
            return True
        except Exception as e:
            raise InitializationError(f"Failed to initialize device: {str(e)}")
    
    def reset(self) -> bool:
        """
        Reset the device.
        
        Returns:
            bool: True if reset is successful
            
        Raises:
            ConnectionError: If device is not connected
            OperationError: If reset fails
        """
        if not self.is_connected:
            raise ConnectionError("Device is not connected")
            
        try:
            # Send reset command
            self.send_command(COMMAND_RESET)
            return True
        except Exception as e:
            raise OperationError(f"Failed to reset device: {str(e)}")
    
    def __enter__(self):
        """Context manager enter method."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        self.disconnect()
    
    def __repr__(self):
        """String representation of the device."""
        if self.is_connected:
            return f"PalmSecureDevice(connected, {self.device_info.get('manufacturer', 'Unknown')} {self.device_info.get('product', 'Unknown')})"
        else:
            if self.device_info:
                return f"PalmSecureDevice(disconnected, {self.device_info.get('manufacturer', 'Unknown')} {self.device_info.get('product', 'Unknown')})"
            else:
                return "PalmSecureDevice(disconnected)"