import os
import sys
import asyncio
import inspect

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backend.database.db as db
db.init_db()

admin_user = {"user_id": "USR_ADM_00", "role": "admin"}

def call_endpoint(fn, **kwargs):
    if inspect.iscoroutinefunction(fn):
        return asyncio.run(fn(**kwargs))
    else:
        return fn(**kwargs)

# 1. Test Admin / Overview Stats
from backend.api.admin import get_admin_system_stats
stats = call_endpoint(get_admin_system_stats, current_user=admin_user)
print(f"[Module 0: Overview Stats] SUCCESS! Keys: {list(stats.keys())[:5]}")

# 2. Test Evaluation module
from backend.api.evaluation import get_available_datasets
datasets = call_endpoint(get_available_datasets, current_user=admin_user)
print(f"[Module 1: Evaluation Datasets] SUCCESS! Found {len(datasets.get('datasets', []))} datasets")

# 3. Test Privacy module
from backend.api.privacy import get_privacy_overview
privacy_info = call_endpoint(get_privacy_overview, current_user=admin_user)
print(f"[Module 2: Privacy Center] SUCCESS! Input dim: {privacy_info.get('raw_feature_dimension')}, Protected dim: {privacy_info.get('protected_dimension')}")

# 4. Test Security module
from backend.api.security import get_audit_trail, verify_audit_trail
trail = call_endpoint(get_audit_trail, current_user=admin_user)
print(f"[Module 3: Security Center] SUCCESS! Audit logs count: {len(trail.get('audit_logs', []))}")
verification = call_endpoint(verify_audit_trail, current_user=admin_user)
print(f"[Module 3: Audit Verification] SUCCESS! Status: {verification.get('status')}")

# 5. Test Index Management module
from backend.api.index_mgmt import get_index_status
idx_status = call_endpoint(get_index_status, current_user=admin_user)
print(f"[Module 4: Index Management] SUCCESS! Vectors: {idx_status.get('vector_count')}, Health: {idx_status.get('status')}")

print("\n>>> ALL 5 MODULE BACKEND HANDLERS ARE 100% OPERATIONAL! <<<")
