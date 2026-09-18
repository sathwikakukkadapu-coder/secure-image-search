from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import backend.database.db as db

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    pw_hash = db.hash_password(req.password)
    if user["password_hash"] != pw_hash:
        db.log_audit(user["user_id"], "LOGIN", "BLOCKED", "Invalid credentials entered")
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    db.log_audit(user["user_id"], "LOGIN", "ALLOWED", f"User {user['name']} logged in successfully")
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "token": f"bearer_{user['user_id']}"
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
    """Helper to extract active user from Authorization header or default to guest."""
    if not authorization:
        return db.get_user_by_id("USR_GST_99")
        
    user_id = authorization.replace("Bearer ", "").replace("bearer_", "").strip()
    user = db.get_user_by_id(user_id)
    if not user:
        return db.get_user_by_id("USR_GST_99")
    return user
