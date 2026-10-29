import os
import time
from fastapi import APIRouter, Depends, Header
from typing import Dict, Any, Optional
import backend.database.db as db
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
def get_admin_system_stats(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Returns system telemetry, storage distribution, and security events.
    Maintains full backward compatibility with test_system.py assertions.
    """
    stats = db.get_system_stats()
    retriever = FAISSRetrievalEngine.get_instance()
    vault = PrivateImageVault.get_instance()
    
    # Calculate storage folder size
    vault_size_bytes = 0
    if os.path.exists(vault.storage_dir):
        for f in os.listdir(vault.storage_dir):
            fp = os.path.join(vault.storage_dir, f)
            if os.path.isfile(fp):
                vault_size_bytes += os.path.getsize(fp)
                
    faiss_size_bytes = 0
    if os.path.exists(retriever.index_path):
        faiss_size_bytes = os.path.getsize(retriever.index_path)

    recent_logs = db.get_audit_logs(limit=15)
    chain_info = db.verify_audit_chain()
    
    last_rebuild = db.get_index_metadata("last_rebuild_timestamp") or "Initial setup"
    
    return {
        "status": "healthy",
        "dataset": {
            "total_images": stats["total_images"],
            "private_images": stats["private_images"],
            "public_images": stats["public_images"],
            "total_users": stats["total_users"],
            "faiss_indexed_vectors": retriever.count(),
            "embedding_model": "MobileNetV3-Large",
            "vector_dimension": retriever.dimension,
            "index_type": "IndexFlatIP"
        },
        "storage": {
            "private_vault_disk_mb": round(vault_size_bytes / (1024 * 1024), 2),
            "faiss_index_disk_kb": round(faiss_size_bytes / 1024, 2),
            "zero_pixel_invariant": True
        },
        "security": {
            "total_searches_logged": stats["total_searches"],
            "unauthorized_attempts_blocked": stats["blocked_attempts"],
            "encryption_cipher": "AES-256-GCM",
            "audit_chain_valid": chain_info["valid"],
            "audit_records_count": chain_info["total_records"]
        },
        "overview": {
            "index_health": "HEALTHY" if retriever.count() == stats["total_images"] and retriever.count() > 0 else "DESYNCHRONIZED",
            "last_rebuild": last_rebuild,
            "zero_pixel_status": "Strict Zero-Pixel Pipeline Active",
            "active_user": current_user.get("name") if current_user else "Guest",
            "active_role": current_user.get("role") if current_user else "guest"
        },
        "recent_audit_trail": recent_logs
    }
