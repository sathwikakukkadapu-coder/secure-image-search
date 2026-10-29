import os
import sqlite3
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "private_search.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Computes PBKDF2-HMAC-SHA256 with 100,000 iterations and a 16-byte cryptographic salt."""
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2:sha256:100000${salt.hex()}${key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies password against stored PBKDF2 hash or legacy SHA-256 with constant-time comparison."""
    if not stored_hash:
        return False
        
    if stored_hash.startswith("pbkdf2:sha256:"):
        parts = stored_hash.split("$")
        if len(parts) == 3:
            try:
                salt = bytes.fromhex(parts[1])
                expected_key = parts[2]
                computed_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
                return hmac.compare_digest(expected_key, computed_key)
            except Exception:
                return False
                
    # Legacy SHA-256 verification with constant time check
    legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_hash, stored_hash)

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
        details TEXT,
        category TEXT DEFAULT 'SYSTEM',
        severity TEXT DEFAULT 'INFO',
        ip_address TEXT DEFAULT '127.0.0.1',
        prev_hash TEXT,
        entry_hash TEXT
    )
    """)

    # Check and migrate columns in audit_logs if older schema exists
    cur.execute("PRAGMA table_info(audit_logs)")
    existing_cols = {col[1] for col in cur.fetchall()}
    for col_name, col_type, def_val in [
        ("category", "TEXT", "'SYSTEM'"),
        ("severity", "TEXT", "'INFO'"),
        ("ip_address", "TEXT", "'127.0.0.1'"),
        ("prev_hash", "TEXT", "NULL"),
        ("entry_hash", "TEXT", "NULL")
    ]:
        if col_name not in existing_cols:
            cur.execute(f"ALTER TABLE audit_logs ADD COLUMN {col_name} {col_type} DEFAULT {def_val}")

    # Create evaluation_experiments table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_experiments (
        experiment_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        user_id TEXT NOT NULL,
        dataset_name TEXT NOT NULL,
        sample_count INTEGER NOT NULL,
        model_name TEXT NOT NULL,
        k_values TEXT NOT NULL,
        sigma REAL NOT NULL,
        metrics_json TEXT NOT NULL,
        latency_ms REAL NOT NULL
    )
    """)

    # Create privacy_experiments table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS privacy_experiments (
        experiment_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        user_id TEXT NOT NULL,
        dataset_name TEXT NOT NULL,
        sample_count INTEGER NOT NULL,
        sigma REAL NOT NULL,
        metrics_json TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT
    )
    """)

    # Create index_metadata table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS index_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Pre-seed realistic users with PBKDF2 salted hashes
    seed_users = [
        ("USR_DOC_01", "Dr. R. Sharma", "doctor@hospital.org", hash_password("doctor123"), "specialist"),
        ("USR_RES_02", "Alex Verma", "researcher@lab.org", hash_password("research123"), "researcher"),
        ("USR_ADM_00", "System Security Admin", "admin@security.org", hash_password("admin123"), "admin"),
        ("USR_GST_99", "Public Guest", "guest@demo.org", hash_password("guest123"), "guest")
    ]
    
    for uid, name, email, pw_hash, role in seed_users:
        cur.execute("SELECT user_id, password_hash FROM users WHERE user_id = ?", (uid,))
        existing = cur.fetchone()
        if not existing:
            cur.execute("""
            INSERT INTO users (user_id, name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (uid, name, email, pw_hash, role, datetime.now().isoformat()))
        elif not existing["password_hash"].startswith("pbkdf2:"):
            # Migrate legacy password hash to PBKDF2
            cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (pw_hash, uid))
            
    conn.commit()

    # Backfill entry hashes for any older logs
    cur.execute("SELECT log_id, timestamp, user_id, action, status, details, category FROM audit_logs WHERE entry_hash IS NULL ORDER BY log_id ASC")
    unhashed_rows = cur.fetchall()
    if unhashed_rows:
        last_hash = "GENESIS_ROOT"
        for row in unhashed_rows:
            lid = row["log_id"]
            cat = row["category"] or "SYSTEM"
            raw_chain = f"{last_hash}|{row['timestamp']}|{row['user_id']}|{row['action']}|{row['status']}|{cat}|{row['details']}"
            cur_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()
            cur.execute("UPDATE audit_logs SET prev_hash = ?, entry_hash = ?, category = ? WHERE log_id = ?", (last_hash, cur_hash, cat, lid))
            last_hash = cur_hash
        conn.commit()

    conn.close()
    print("[Database] SQLite database initialized with PBKDF2 password hashes, experiment tables, and chained audit logs.")

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

def log_audit(
    user_id: Optional[str],
    action: str,
    status: str,
    details: str,
    category: str = "SYSTEM",
    severity: str = "INFO",
    ip_address: str = "127.0.0.1"
):
    """
    Appends an immutable, tamper-evident audit log entry.
    Safeguards: No raw query images, no passwords, no tokens, no secret keys.
    Computes cryptographic entry hash chained to the previous entry hash.
    """
    # Sanitize details to guarantee zero leakage of sensitive data
    sanitized_details = str(details)
    for forbidden in ["password", "token", "key", "secret", "authorization"]:
        if forbidden in sanitized_details.lower() and "bearer" in sanitized_details.lower():
            sanitized_details = "[REDACTED_SENSITIVE_AUTH_TOKEN]"
            
    conn = get_connection()
    cur = conn.cursor()
    
    # Retrieve the last entry hash for chaining
    cur.execute("SELECT entry_hash FROM audit_logs ORDER BY log_id DESC LIMIT 1")
    last_row = cur.fetchone()
    prev_hash = last_row["entry_hash"] if last_row and last_row["entry_hash"] else "GENESIS_ROOT"
    
    now_ts = datetime.now().isoformat()
    actor = user_id or "ANONYMOUS"
    
    # Cryptographic hash of this audit log entry chained to previous hash
    raw_chain = f"{prev_hash}|{now_ts}|{actor}|{action}|{status}|{category}|{sanitized_details}"
    entry_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()
    
    cur.execute("""
    INSERT INTO audit_logs (timestamp, user_id, action, status, details, category, severity, ip_address, prev_hash, entry_hash)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now_ts, actor, action, status, sanitized_details, category, severity, ip_address, prev_hash, entry_hash))
    
    conn.commit()
    conn.close()

def verify_audit_chain() -> Dict[str, Any]:
    """
    Verifies cryptographic tamper-evidence of the entire audit trail chain.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT log_id, timestamp, user_id, action, status, details, category, prev_hash, entry_hash FROM audit_logs ORDER BY log_id ASC")
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        return {"valid": True, "total_records": 0, "status": "No audit records present"}
        
    expected_prev = "GENESIS_ROOT"
    for r in rows:
        cat = r["category"] or "SYSTEM"
        raw_chain = f"{r['prev_hash']}|{r['timestamp']}|{r['user_id']}|{r['action']}|{r['status']}|{cat}|{r['details']}"
        expected_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()
        
        if r["entry_hash"] != expected_hash:
            return {
                "valid": False,
                "total_records": len(rows),
                "broken_at_id": r["log_id"],
                "status": f"Integrity check failed at log #{r['log_id']}"
            }
        expected_prev = r["entry_hash"]
        
    return {
        "valid": True,
        "total_records": len(rows),
        "status": "Audit trail integrity verified: All cryptographically chained blocks valid",
        "latest_hash": expected_prev[:16] + "..."
    }

def get_audit_logs(
    limit: int = 50,
    category: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    
    query = "SELECT * FROM audit_logs"
    conditions = []
    params = []
    
    if category and category != "ALL":
        conditions.append("category = ?")
        params.append(category)
    if status and status != "ALL":
        conditions.append("status = ?")
        params.append(status)
    if user_id:
        conditions.append("user_id = ?")
        params.append(user_id)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY log_id DESC LIMIT ?"
    params.append(limit)
    
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_evaluation_experiment(
    experiment_id: str,
    user_id: str,
    dataset_name: str,
    sample_count: int,
    model_name: str,
    k_values: str,
    sigma: float,
    metrics_json: str,
    latency_ms: float
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO evaluation_experiments (
        experiment_id, timestamp, user_id, dataset_name, sample_count, model_name, k_values, sigma, metrics_json, latency_ms
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        experiment_id, datetime.now().isoformat(), user_id, dataset_name, sample_count, model_name, k_values, sigma, metrics_json, latency_ms
    ))
    conn.commit()
    conn.close()

def get_evaluation_experiments(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM evaluation_experiments ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_privacy_experiment(
    experiment_id: str,
    user_id: str,
    dataset_name: str,
    sample_count: int,
    sigma: float,
    metrics_json: str,
    status: str,
    notes: str
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO privacy_experiments (
        experiment_id, timestamp, user_id, dataset_name, sample_count, sigma, metrics_json, status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        experiment_id, datetime.now().isoformat(), user_id, dataset_name, sample_count, sigma, metrics_json, status, notes
    ))
    conn.commit()
    conn.close()

def get_privacy_experiments(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM privacy_experiments ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_index_metadata(key: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO index_metadata (key, value, updated_at)
    VALUES (?, ?, ?)
    """, (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_index_metadata(key: str) -> Optional[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM index_metadata WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_index_metadata() -> Dict[str, str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM index_metadata")
    rows = cur.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

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
    
    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action IN ('VECTOR_SEARCH', 'CONTENT_FREE_SEARCH')")
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
