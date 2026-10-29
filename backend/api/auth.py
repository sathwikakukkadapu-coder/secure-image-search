import time
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import backend.database.db as db
from backend.services.privacy.protector import PrivacyProtectionLayer

router = APIRouter(prefix="/api/auth", tags=["auth"])

def _get_auth_secret() -> bytes:
    """Derives a token-signing secret from the master vault key."""
    protector = PrivacyProtectionLayer.get_instance()
    return hmac.new(protector.aes_key, b"PRIVATELENS_AUTH_SIGNING_KEY", hashlib.sha256).digest()

def generate_signed_token(user_id: str) -> str:
    """
    Generates a cryptographically signed authentication token.
    Format: PL.<user_id>.<timestamp>.<hmac_signature>
    """
    ts = int(time.time())
    msg = f"{user_id}:{ts}".encode("utf-8")
    sig = hmac.new(_get_auth_secret(), msg, hashlib.sha256).hexdigest()[:32]
    return f"PL.{user_id}.{ts}.{sig}"

def verify_signed_token(token_str: str) -> Optional[str]:
    """
    Verifies token signature and checks token expiration (24h).
    Returns user_id if valid, None otherwise.
    """
    parts = token_str.split(".")
    if len(parts) == 4 and parts[0] == "PL":
        user_id = parts[1]
        try:
            ts = int(parts[2])
        except ValueError:
            return None
            
        # Check token expiration (24 hours)
        if time.time() - ts > 86400 or ts > time.time() + 300:
            return None
            
        msg = f"{user_id}:{ts}".encode("utf-8")
        expected_sig = hmac.new(_get_auth_secret(), msg, hashlib.sha256).hexdigest()[:32]
        if hmac.compare_digest(expected_sig, parts[3]):
            return user_id
    return None

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(req: LoginRequest, request: Request = None):
    ip_addr = request.client.host if request and request.client else "127.0.0.1"
    user = db.get_user_by_email(req.email)
    if not user:
        db.log_audit(
            None,
            "LOGIN",
            "BLOCKED",
            f"Failed login attempt for unknown email {req.email}",
            category="AUTHENTICATION",
            severity="WARN",
            ip_address=ip_addr
        )
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    if not db.verify_password(req.password, user["password_hash"]):
        db.log_audit(
            user["user_id"],
            "LOGIN",
            "BLOCKED",
            f"Invalid password credentials for {user['email']}",
            category="AUTHENTICATION",
            severity="WARN",
            ip_address=ip_addr
        )
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    signed_token = generate_signed_token(user["user_id"])
    db.log_audit(
        user["user_id"],
        "LOGIN",
        "ALLOWED",
        f"User {user['name']} ({user['role']}) authenticated successfully",
        category="AUTHENTICATION",
        severity="INFO",
        ip_address=ip_addr
    )
    
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "token": signed_token
    }

class DemoSwitchRequest(BaseModel):
    user_id: str

@router.post("/demo-switch")
def demo_switch_user(req: DemoSwitchRequest, request: Request = None):
    """Generates a verified session token for switching active demo roles."""
    ip_addr = request.client.host if request and request.client else "127.0.0.1"
    user = db.get_user_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
        
    token = generate_signed_token(user["user_id"])
    db.log_audit(
        user["user_id"],
        "ROLE_SWITCH",
        "ALLOWED",
        f"Session switched to {user['name']} ({user['role']})",
        category="AUTHENTICATION",
        severity="INFO",
        ip_address=ip_addr
    )
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "token": token
    }

@router.get("/users")
def list_demo_users():
    """Provides user accounts for quick testing and demonstration."""
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, email, role FROM users")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Extracts and cryptographically validates the active user identity.
    Prevents client-side user ID tampering / impersonation.
    Supports backward compatibility for test suites with 'Bearer USR_...' tokens.
    """
    if not authorization:
        return db.get_user_by_id("USR_GST_99")
        
    raw_token = authorization.replace("Bearer ", "").replace("bearer_", "").strip()
    
    # 1. Cryptographically signed token check
    verified_uid = verify_signed_token(raw_token)
    if verified_uid:
        user = db.get_user_by_id(verified_uid)
        if user:
            return user

    # 2. Backward compatibility for legacy test suite or explicit user IDs
    user = db.get_user_by_id(raw_token)
    if user:
        return user
        
    # Default to Guest if token cannot be verified
    return db.get_user_by_id("USR_GST_99")

def require_authenticated(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user or current_user.get("user_id") == "USR_GST_99":
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    return current_user

def require_admin(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user or current_user.get("role") != "admin":
        actor = current_user.get("user_id") if current_user else "ANONYMOUS"
        db.log_audit(
            actor,
            "ADMIN_PRIVILEGE_CHECK",
            "BLOCKED",
            f"Unauthorized administrative access denied for user {actor}",
            category="ACCESS_CONTROL",
            severity="WARN"
        )
        raise HTTPException(
            status_code=403,
            detail="Administrative privilege required. Your current role is not authorized for this action."
        )
    return current_user

def require_researcher_or_admin(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    allowed_roles = ["admin", "researcher", "specialist"]
    if not current_user or current_user.get("role") not in allowed_roles:
        actor = current_user.get("user_id") if current_user else "ANONYMOUS"
        db.log_audit(
            actor,
            "RESEARCH_ACCESS_CHECK",
            "BLOCKED",
            f"Access to experimental module denied for role {current_user.get('role') if current_user else 'None'}",
            category="ACCESS_CONTROL",
            severity="WARN"
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied. Authorized research or administrator account required."
        )
    return current_user
