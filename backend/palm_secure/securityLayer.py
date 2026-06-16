import os
import base64
import hashlib
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


class PalmVeinPaymentEncryption:
    def __init__(self, key=None):
        if key is None:
            key = os.getenv('PALM_AUTH_AES_KEY')
        
        if not key:
            raise RuntimeError(
                "PALM_AUTH_AES_KEY environment variable is not set. "
                "This key protects all stored biometric data and must never have a default value."
            )
        
        # Create consistent 256-bit key from string
        if isinstance(key, str):
            self.key = hashlib.sha256(key.encode()).digest()
        else:
            self.key = key
    
    def encrypt_bio_template(self, bio_template):
        """Encrypt biometric template with deterministic encryption"""
        try:
            # Normalize template first
            normalized_template = self.normalize_template(bio_template)
            
            # Create deterministic IV from template hash
            template_hash = hashlib.sha256(normalized_template.encode()).digest()
            iv = template_hash[:16]  # Use first 16 bytes as IV
            
            # Create cipher
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Pad data to AES block size (16 bytes)
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(normalized_template.encode()) + padder.finalize()
            
            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Return IV + encrypted data as base64
            return base64.b64encode(iv + encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"Encryption error: {e}")
            raise
    
    def decrypt_bio_template(self, encrypted_template):
        """Decrypt biometric template"""
        try:
            if not encrypted_template:
                return None
                
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_template)
            
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Create cipher
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode('utf-8')
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def normalize_template(self, template):
        """Normalize bio template for consistent processing"""
        if not template:
            return template
            
        # Remove all whitespace
        cleaned = ''.join(template.split())
        
        # Fix Base64 padding
        remainder = len(cleaned) % 4
        if remainder:
            cleaned += '=' * (4 - remainder)
        
        # Validate and re-encode for consistency
        try:
            decoded = base64.b64decode(cleaned)
            return base64.b64encode(decoded).decode('utf-8')
        except:
            return cleaned


# Alternative AES class (for other uses if needed)
class AESEncryption:
    def __init__(self, key=None):
        """Initialize AES encryption with a consistent key"""
        if key is None:
            key_source = os.getenv('PALM_AUTH_AES_KEY')
            if not key_source:
                raise RuntimeError(
                    "PALM_AUTH_AES_KEY environment variable is not set. "
                    "This key protects all stored biometric data and must never have a default value."
                )
            self.key = hashlib.sha256(key_source.encode('utf-8')).digest()
        else:
            if isinstance(key, str):
                key = key.encode('utf-8')
            self.key = hashlib.sha256(key).digest()
    
    def encrypt(self, data):
        """Encrypt data using AES-256-CBC"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate a random IV for each encryption
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + encrypted data as base64
        return base64.b64encode(iv + encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """Decrypt data using AES-256-CBC"""
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # Extract IV and encrypted data
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')


# Test the implementation
if __name__ == "__main__":
    # Test palm vein encryption
    palm_encryption = PalmVeinPaymentEncryption()
    
    test_template = "IAEBAAAAAACu7nv/hQN++or8ZAnOAnz+RvzeBWUGe/8e/TMF8QFpC3n"
    print(f"Original Template: {test_template}")
    
    encrypted = palm_encryption.encrypt_bio_template(test_template)
    print(f"Encrypted: {encrypted}")
    
    decrypted = palm_encryption.decrypt_bio_template(encrypted)
    print(f"Decrypted: {decrypted}")
    
    print(f"Match: {test_template == decrypted}")
