import os
import uuid
from typing import Tuple, Dict, Any, Optional
from backend.services.privacy.protector import PrivacyProtectionLayer

class PrivateImageVault:
    """
    Decoupled Private Image Storage Layer.
    
    Enforces strict physical separation:
    - Original full-resolution image binaries are stored solely in this private vault.
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
        Stores image in private vault under randomized UUID filename.
        Returns: (vault_filename: str, encrypted_storage_ref: str)
        """
        ext = os.path.splitext(original_filename)[1].lower()
        if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"
            
        safe_name = f"vault_{image_id}_{uuid.uuid4().hex[:8]}{ext}"
        full_path = os.path.join(self.storage_dir, safe_name)
        
        with open(full_path, "wb") as f:
            f.write(image_bytes)
            
        encrypted_ref = self.protector.encrypt_string(safe_name)
        return safe_name, encrypted_ref

    def retrieve_image_bytes(self, encrypted_storage_ref: str) -> bytes:
        """Decrypts the storage reference handle and loads raw image bytes from the private vault."""
        vault_filename = self.protector.decrypt_string(encrypted_storage_ref)
        full_path = os.path.join(self.storage_dir, vault_filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Vault image {vault_filename} not found in private storage.")
        with open(full_path, "rb") as f:
            return f.read()

    def check_authorization(self, user: Dict[str, Any], image_record: Dict[str, Any]) -> Tuple[bool, str]:
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
            return False, "Unauthorized: Authentication required."
            
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
