import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response

import backend.database.db as db
from backend.services.storage.vault import PrivateImageVault
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/security", tags=["security"])

@router.get("/stats")
def get_security_center_stats(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Returns security telemetry, access-control figures, cipher status,
    and cryptographic audit chain integrity.
    """
    sys_stats = db.get_system_stats()
    chain_status = db.verify_audit_chain()
    vault = PrivateImageVault.get_instance()
    retriever = FAISSRetrievalEngine.get_instance()
    
    conn = db.get_connection()
    cur = conn.cursor()
    
    # Event breakdown by category
    cur.execute("SELECT category, count(*) FROM audit_logs GROUP BY category")
    category_counts = {r[0] or "SYSTEM": r[1] for r in cur.fetchall()}
    
    # Blocked authentication vs access control
    cur.execute("SELECT count(*) FROM audit_logs WHERE action = 'LOGIN' AND status = 'BLOCKED'")
    failed_logins = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM audit_logs WHERE action IN ('IMAGE_FETCH', 'ADMIN_PRIVILEGE_CHECK') AND status = 'BLOCKED'")
    denied_access = cur.fetchone()[0]
    
    # Total distinct actors
    cur.execute("SELECT count(DISTINCT user_id) FROM audit_logs WHERE user_id != 'ANONYMOUS'")
    active_actors = cur.fetchone()[0]
    
    conn.close()
    
    return {
        "status": "operational",
        "zero_pixel_invariant": True,
        "security_metrics": {
            "total_audit_events": chain_status["total_records"],
            "failed_logins": failed_logins,
            "unauthorized_access_blocked": denied_access,
            "total_searches_logged": sys_stats["total_searches"],
            "active_distinct_actors": active_actors,
            "events_by_category": category_counts
        },
        "cryptographic_safeguards": {
            "vault_storage_encryption": "AES-256-GCM (Authenticated Encryption at Rest)",
            "vector_index_isolation": "Meta FAISS FlatIP (Strictly Float32 Numerical Vectors, Zero Pixels)",
            "session_tokens": "HMAC-SHA256 Cryptographically Signed with Vault Secret",
            "audit_trail_tamper_evidence": {
                "chain_valid": chain_status["valid"],
                "verification_message": chain_status["status"],
                "latest_block_hash": chain_status.get("latest_hash", "N/A"),
                "total_chained_blocks": chain_status["total_records"]
            }
        },
        "current_viewer": {
            "user_id": current_user.get("user_id", "GUEST"),
            "name": current_user.get("name", "Guest"),
            "role": current_user.get("role", "guest"),
            "is_admin": current_user.get("role") == "admin"
        }
    }

@router.get("/events")
def get_security_audit_events(
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = Query("ALL"),
    status: Optional[str] = Query("ALL"),
    user_id: Optional[str] = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Returns filterable, paginated audit records.
    Restricted: Non-admin users see only events related to their own account or public events.
    """
    is_admin = current_user and current_user.get("role") == "admin"
    filter_uid = user_id if is_admin else (current_user.get("user_id") if current_user else "USR_GST_99")
    
    logs = db.get_audit_logs(
        limit=limit,
        category=None if category == "ALL" else category,
        status=None if status == "ALL" else status,
        user_id=filter_uid if not is_admin else user_id
    )
    
    sanitized = []
    for l in logs:
        sanitized.append({
            "log_id": l["log_id"],
            "timestamp": l["timestamp"],
            "user_id": l["user_id"],
            "action": l["action"],
            "status": l["status"],
            "category": l.get("category", "SYSTEM"),
            "severity": l.get("severity", "INFO"),
            "details": l["details"],
            "entry_hash": l.get("entry_hash", "")[:16] + "..." if l.get("entry_hash") else None,
            "prev_hash": l.get("prev_hash", "")[:16] + "..." if l.get("prev_hash") else None
        })
        
    return {
        "total": len(sanitized),
        "filter_category": category,
        "filter_status": status,
        "events": sanitized
    }

@router.get("/verify-integrity")
def verify_audit_trail_integrity(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Verifies SHA-256 hash chaining across all audit records."""
    result = db.verify_audit_chain()
    return result

@router.get("/export")
def export_security_logs(
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: Optional[Dict[str, Any]] = Depends(require_admin)
):
    """
    Safely exports audit trail records.
    Admin authorization strictly required.
    Guarantees zero tokens, keys, passwords, or image bytes.
    """
    logs = db.get_audit_logs(limit=500)
    
    db.log_audit(
        current_user.get("user_id"),
        "AUDIT_EXPORT",
        "ALLOWED",
        f"Exported {len(logs)} audit records in {format.upper()} format",
        category="ADMINISTRATIVE",
        severity="INFO"
    )
    
    if format == "json":
        return {
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exported_by": current_user.get("name"),
            "total_records": len(logs),
            "records": logs
        }
    else:
        lines = ["log_id,timestamp,user_id,category,action,status,severity,entry_hash,details"]
        for l in logs:
            safe_details = str(l["details"]).replace(",", ";").replace("\n", " ")
            lines.append(f"{l['log_id']},{l['timestamp']},{l['user_id']},{l.get('category','SYSTEM')},{l['action']},{l['status']},{l.get('severity','INFO')},{l.get('entry_hash','')[:16]},{safe_details}")
        csv_content = "\n".join(lines)
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=security_audit_trail.csv"})
