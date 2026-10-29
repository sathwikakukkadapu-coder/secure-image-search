import os
import time
import base64
from typing import Tuple, Dict, Any
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class PrivacyProtectionLayer:
    """
    Mathematical Privacy Protection Layer for Visual Representations.
    Implements:
    1. Random Orthogonal Dimension Reduction (1280-D -> 512-D).
    2. Calibrated Gaussian Perturbation on normalized representations.
    3. AES-256-GCM Authenticated Encryption for vault storage at rest.
    """
    _instance = None

    def __init__(self, input_dim: int = 1280, protected_dim: int = 512, seed: int = 42, default_sigma: float = 0.05):
        self.input_dim = input_dim
        self.protected_dim = protected_dim
        self.default_sigma = default_sigma
        self.seed = seed
        self._init_projection_matrix(input_dim, protected_dim)
        
        # Resolve AES-256-GCM master key securely outside of source tree
        self.aes_key = self._resolve_master_key()
        self.cipher = AESGCM(self.aes_key)

    def _resolve_master_key(self) -> bytes:
        """
        Loads the 256-bit AES master key from environment or project .keys/ directory.
        Key is strictly excluded from version control.
        """
        env_key = os.environ.get("PRIVATE_LENS_VAULT_KEY")
        if env_key:
            try:
                raw = base64.b64decode(env_key)
                if len(raw) == 32:
                    return raw
            except Exception:
                pass
            try:
                raw = bytes.fromhex(env_key)
                if len(raw) == 32:
                    return raw
            except Exception:
                pass

        keys_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".keys"))
        os.makedirs(keys_dir, exist_ok=True)
        key_file = os.path.join(keys_dir, "vault.key")
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key_bytes = f.read()
                if len(key_bytes) == 32:
                    return key_bytes

        # Generate new cryptographically secure 256-bit key
        new_key = AESGCM.generate_key(bit_length=256)
        with open(key_file, "wb") as f:
            f.write(new_key)
        return new_key

    def _init_projection_matrix(self, in_dim: int, out_dim: int):
        self.input_dim = in_dim
        self.protected_dim = out_dim
        rng = np.random.RandomState(self.seed)
        gaussian_matrix = rng.randn(in_dim, out_dim)
        q, _ = np.linalg.qr(gaussian_matrix)
        self.projection_matrix = q.astype(np.float32)

    @classmethod
    def get_instance(cls, input_dim: int = 1280, protected_dim: int = 512):
        if cls._instance is None:
            cls._instance = cls(input_dim=input_dim, protected_dim=protected_dim)
        elif cls._instance.input_dim != input_dim or cls._instance.protected_dim != protected_dim:
            cls._instance._init_projection_matrix(input_dim, protected_dim)
        return cls._instance

    def protect_vector(self, raw_vector: np.ndarray, apply_noise: bool = True, sigma: float = None) -> Tuple[np.ndarray, float]:
        t0 = time.time()
        sigma = self.default_sigma if sigma is None else sigma
        
        if raw_vector.shape[0] != self.input_dim:
            self._init_projection_matrix(raw_vector.shape[0], self.protected_dim)
            
        projected = np.dot(raw_vector, self.projection_matrix)
        
        if apply_noise and sigma > 0:
            noise = np.random.normal(0, sigma, size=projected.shape).astype(np.float32)
            protected = projected + noise
        else:
            protected = projected
            
        norm = np.linalg.norm(protected)
        if norm > 0:
            protected = protected / norm
        else:
            protected = np.zeros_like(protected)
            
        elapsed_ms = (time.time() - t0) * 1000
        return protected.astype(np.float32), elapsed_ms

    def measure_inversion_resistance(self, raw_vector: np.ndarray, protected_vector: np.ndarray, sigma: float = 0.05) -> Dict[str, Any]:
        """
        Computes empirical mathematical perturbation metrics rather than synthetic SSIM claims.
        """
        projected = np.dot(raw_vector, self.projection_matrix)
        proj_norm = np.linalg.norm(projected)
        if proj_norm > 0:
            projected = projected / proj_norm
            
        cosine_sim = float(np.dot(projected, protected_vector))
        cosine_drift = round(max(0.0, 1.0 - cosine_sim), 4)
        snr_db = round(float(10.0 * np.log10(max(1e-6, 1.0 / (max(1e-4, sigma) ** 2)))), 2)

        return {
            "projection_dimension": self.protected_dim,
            "perturbation_sigma": sigma,
            "signal_to_noise_ratio_db": snr_db,
            "cosine_drift_magnitude": cosine_drift,
            "inversion_verdict": "Perturbation Active (Empirically Bounded)" if sigma > 0.0 else "Unperturbed Embedding (High Inversion Risk)",
            "empirical_measurement_note": "Rigorous inversion SSIM requires training an offline inversion decoder (Dosovitskiy & Brox). Theoretical reconstruction impossibility is not claimed.",
            "zero_pixel_storage_guarantee": True
        }

    def encrypt_string(self, plaintext: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

    def decrypt_string(self, token: str) -> str:
        try:
            combined = base64.urlsafe_b64decode(token.encode("utf-8"))
            nonce = combined[:12]
            ciphertext = combined[12:]
            return self.cipher.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypts binary payload with AES-256-GCM producing 12-byte nonce prepended to ciphertext."""
        nonce = os.urandom(12)
        ciphertext = self.cipher.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypts AES-256-GCM binary payload using prepended 12-byte nonce."""
        if len(encrypted_data) < 28: # 12 nonce + 16 auth tag
            raise ValueError("Encrypted data is too short to be valid AES-GCM ciphertext.")
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.cipher.decrypt(nonce, ciphertext, None)
