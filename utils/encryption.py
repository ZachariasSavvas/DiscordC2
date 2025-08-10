from cryptography.fernet import Fernet
import base64

def generate_key():
    """Generate a new encryption key."""
    return Fernet.generate_key().decode()

def validate_key(key):
    """Validate that the key is a 32-byte, URL-safe base64-encoded string."""
    try:
        key_bytes = base64.urlsafe_b64decode(key.encode())
        if len(key_bytes) != 32:
            raise ValueError("Fernet key must be 32 bytes long.")
        return True
    except Exception as e:
        raise ValueError(f"Invalid Fernet key: {str(e)}")

def encrypt_message(message, key):
    """Encrypt a message using the provided key."""
    validate_key(key)
    try:
        f = Fernet(key.encode())
        return base64.b64encode(f.encrypt(message.encode())).decode()
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_message(message, key):
    """Decrypt a message using the provided key."""
    validate_key(key)
    if message.startswith("ENC:"):
        message = message[4:]
    try:
        f = Fernet(key.encode())
        return f.decrypt(base64.b64decode(message)).decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")