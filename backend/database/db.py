import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "private_search.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        image_id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        storage_reference TEXT NOT NULL,
        category TEXT NOT NULL,
        is_private INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES users (user_id)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS retrieval_vectors (
        vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_id TEXT NOT NULL,
        vector_row_id INTEGER NOT NULL,
        model_name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (image_id) REFERENCES images (image_id)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id TEXT,
        action TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT
    )
    """)
    
    # Pre-seed realistic users
    seed_users = [
        ("USR_DOC_01", "Dr. R. Sharma", "doctor@hospital.org", hash_password("doctor123"), "specialist"),
        ("USR_RES_02", "Alex Verma", "researcher@lab.org", hash_password("research123"), "researcher"),
        ("USR_ADM_00", "System Security Admin", "admin@security.org", hash_password("admin123"), "admin"),
        ("USR_GST_99", "Public Guest", "guest@demo.org", hash_password("guest123"), "guest")
    ]
    
    for uid, name, email, pw, role in seed_users:
        cur.execute("""
        INSERT OR IGNORE INTO users (user_id, name, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (uid, name, email, pw, role, datetime.now().isoformat()))
        
    conn.commit()
    conn.close()
    print("[Database] SQLite database initialized and seeded.")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def insert_image(image_id: str, owner_id: str, original_filename: str, storage_reference: str, category: str, is_private: bool = True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO images (image_id, owner_id, original_filename, storage_reference, category, is_private, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (image_id, owner_id, original_filename, storage_reference, category, 1 if is_private else 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_image(image_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM images WHERE image_id = ?", (image_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_images() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM images")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_vector_mapping(image_id: str, vector_row_id: int, model_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO retrieval_vectors (image_id, vector_row_id, model_name, created_at)
    VALUES (?, ?, ?, ?)
    """, (image_id, vector_row_id, model_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_audit(user_id: Optional[str], action: str, status: str, details: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO audit_logs (timestamp, user_id, action, status, details)
    VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), user_id or "ANONYMOUS", action, status, details))
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_system_stats() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM images")
    total_images = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM images WHERE is_private = 1")
    private_images = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM retrieval_vectors")
    total_vectors = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'VECTOR_SEARCH'")
    total_searches = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE status = 'BLOCKED'")
    blocked_attempts = cur.fetchone()[0]
    
    conn.close()
    return {
        "total_images": total_images,
        "private_images": private_images,
        "public_images": total_images - private_images,
        "total_vectors": total_vectors,
        "total_users": total_users,
        "total_searches": total_searches,
        "blocked_attempts": blocked_attempts,
        "zero_pixel_database": True
    }
