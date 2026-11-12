import os
import uuid
import base64
from typing import Tuple, Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import backend.database.db as db
from backend.services.privacy.protector import PrivacyProtectionLayer

class PrivateImageVault:
    """
    Decoupled Private Image Storage Layer with True Envelope Encryption-at-Rest.
    
    Enforces strict physical separation:
    - Original full-resolution image binaries are stored solely in this private vault.
    - Each image is encrypted with a unique Data Encryption Key (DEK).
    - DEKs are securely wrapped using the Master Key Encryption Key (KEK) and stored in DB.
    - Vector database (FAISS) holds ZERO image pixels.
    - Retrieval pointers are stored as AES-256 encrypted storage reference handles.
    - Image assets are released only upon passing owner-based or role-based authorization.
    """
    _instance = None

    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "private_storage"))
        else:
            self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.protector = PrivacyProtectionLayer.get_instance()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def store_image(self, image_bytes: bytes, image_id: str, original_filename: str) -> Tuple[str, str]:
        """
        Stores image in private vault under randomized UUID filename with AES-256-GCM envelope encryption.
        Returns: (vault_filename: str, encrypted_storage_ref: str)
        """
        ext = os.path.splitext(original_filename)[1].lower()
        if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"
            
        safe_name = f"vault_{image_id}_{uuid.uuid4().hex[:8]}{ext}"
        full_path = os.path.join(self.storage_dir, safe_name)
        
        # 1. Generate unique 256-bit Data Encryption Key (DEK)
        dek = AESGCM.generate_key(bit_length=256)
        
        # 2. Encrypt image bytes with DEK
        img_nonce = os.urandom(12)
        encrypted_payload = img_nonce + AESGCM(dek).encrypt(img_nonce, image_bytes, None)
        
        with open(full_path, "wb") as f:
            f.write(encrypted_payload)
            
        # 3. Wrap DEK with Master Key (KEK)
        kek_nonce = os.urandom(12)
        wrapped_dek = AESGCM(self.protector.aes_key).encrypt(kek_nonce, dek, None)
        
        # 4. Store wrapped DEK in database
        db.store_image_encryption_key(
            image_id=image_id,
            wrapped_dek=base64.b64encode(wrapped_dek).decode("utf-8"),
            dek_nonce=base64.b64encode(kek_nonce).decode("utf-8")
        )
            
        encrypted_ref = self.protector.encrypt_string(safe_name)
        return safe_name, encrypted_ref

    def retrieve_image_bytes(self, encrypted_storage_ref: str, image_id: Optional[str] = None) -> bytes:
        """
        Decrypts storage reference, unwraps DEK using Master KEK, and decrypts ciphertext into plaintext bytes.
        """
        vault_filename = self.protector.decrypt_string(encrypted_storage_ref)
        full_path = os.path.join(self.storage_dir, vault_filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Vault image {vault_filename} not found in private storage.")
            
        with open(full_path, "rb") as f:
            stored_data = f.read()
            
        # Support seamless migration if reading a legacy unencrypted file
        if stored_data.startswith(b"\xff\xd8\xff") or stored_data.startswith(b"\x89PNG"):
            return stored_data
            
        # Try Envelope unwrapping if image_id is provided or can be parsed from filename
        target_id = image_id
        if not target_id and vault_filename.startswith("vault_"):
            parts = vault_filename.split("_")
            if len(parts) >= 3:
                target_id = "_".join(parts[1:-1])

        if target_id:
            key_rec = db.get_image_encryption_key(target_id)
            if key_rec:
                try:
                    wrapped_dek = base64.b64decode(key_rec["wrapped_dek"])
                    kek_nonce = base64.b64decode(key_rec["dek_nonce"])
                    dek = AESGCM(self.protector.aes_key).decrypt(kek_nonce, wrapped_dek, None)
                    
                    img_nonce = stored_data[:12]
                    ciphertext = stored_data[12:]
                    return AESGCM(dek).decrypt(img_nonce, ciphertext, None)
                except Exception:
                    pass # Fall back to direct KEK decrypt
            
        try:
            return self.protector.decrypt_bytes(stored_data)
        except Exception as e:
            raise ValueError(f"Vault decryption failed for image asset: {str(e)}")

    def check_authorization(self, user: Optional[Dict[str, Any]], image_record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates Owner-Based and Role-Based Access Control (RBAC):
        - Public images: permitted to any authenticated user.
        - Private images:
            * Admins: permitted.
            * Image Owner (owner_id matches user_id): permitted.
            * Specialists (medical doctors): permitted to medical category diagnostics.
            * Otherwise: strictly rejected.
        """
        if not user:
            return False, "Unauthorized: Authentication token required."
            
        is_private = bool(image_record.get("is_private", False))
        if not is_private:
            return True, "Authorized: Public image catalog asset."
            
        user_id = user.get("user_id")
        user_role = user.get("role", "guest")
        owner_id = image_record.get("owner_id")
        
        # 1. Admin Override
        if user_role == "admin":
            return True, "Authorized: Administrator privilege."
            
        # 2. Owner-Based Access
        if owner_id and user_id and owner_id == user_id:
            return True, "Authorized: Image owner verified."
            
        # 3. Role-Based Access for Specialists (e.g. Doctor accessing medical scans)
        category = image_record.get("category", "").lower()
        if user_role == "specialist" and category in ["medical", "ct", "xray"]:
            return True, "Authorized: Specialist medical authorization."
            
        return False, f"Access Denied: Private asset owned by '{owner_id}'. Your role '{user_role}' lacks permissions."
