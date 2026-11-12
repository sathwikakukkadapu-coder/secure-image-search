import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Authenticate as Admin
login_res = client.post("/api/auth/login", json={"user_id": "USR_ADM_00", "password": "password"})
token = login_res.json().get("token")
headers = {"Authorization": f"Bearer {token}"}
print(f"Logged in as USR_ADM_00: token={'OK' if token else 'FAIL'}")

# Module 1: Evaluation APIs
print("\n--- Testing Module 1: Evaluation APIs ---")
res_eval_ds = client.get("/api/evaluation/datasets", headers=headers)
print(f"/api/evaluation/datasets: status={res_eval_ds.status_code}")

# Module 2: Privacy Center APIs
print("\n--- Testing Module 2: Privacy Center APIs ---")
res_priv_ov = client.get("/api/privacy/overview", headers=headers)
print(f"/api/privacy/overview: status={res_priv_ov.status_code}")

# Module 3: Security & Audit APIs
print("\n--- Testing Module 3: Security & Audit APIs ---")
res_sec_audit = client.get("/api/security/audit-trail", headers=headers)
print(f"/api/security/audit-trail: status={res_sec_audit.status_code}")

res_sec_verify = client.get("/api/security/verify-audit", headers=headers)
print(f"/api/security/verify-audit: status={res_sec_verify.status_code}")

# Module 4: Vector Index Management APIs
print("\n--- Testing Module 4: Vector Index Management APIs ---")
res_idx_status = client.get("/api/index/status", headers=headers)
print(f"/api/index/status: status={res_idx_status.status_code}")

# Module 5: Overview Stats API
print("\n--- Testing Module 5: Overview Stats API ---")
res_stats = client.get("/api/admin/stats", headers=headers)
print(f"/api/admin/stats: status={res_stats.status_code}")

print("\n>>> ALL API HEALTH CHECKS COMPLETED <<<")
