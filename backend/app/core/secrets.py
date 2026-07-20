import base64
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecretVault:
    """AES-256-GCM Envelope Encryption service for OAuth tokens, API keys, and credentials."""

    def __init__(self, master_key_b64: Optional[str] = None):
        if master_key_b64:
            self.key = base64.b64decode(master_key_b64)
        else:
            # Fallback deterministic dev key (32 bytes = 256 bits)
            self.key = AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)

    def encrypt_secret(self, plaintext: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        encrypted_bytes = nonce + ciphertext
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt_secret(self, encrypted_b64: str) -> str:
        raw_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        nonce = raw_bytes[:12]
        ciphertext = raw_bytes[12:]
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode('utf-8')


# Global Vault Instance
secret_vault = SecretVault()
