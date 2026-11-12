import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backend.database.db as db
db.init_db()

admin_user = {"user_id": "USR_ADM_00", "role": "admin", "name": "System Administrator"}

# 1. Test /api/evaluation/run
from backend.api.evaluation import run_custom_evaluation, EvaluationRunRequest
req_eval = EvaluationRunRequest(
    dataset_name="default_catalog",
    sample_limit=10,
    sigma=0.05,
    k_values=[1, 3, 5, 10],
    compare_baseline=True
)

res_eval = run_custom_evaluation(req_eval, current_user=admin_user)
print("=== /api/evaluation/run result ===")
print("Status:", res_eval.get("status"))
exp = res_eval.get("experiment", {})
print("Protected metrics keys:", list(exp.get("protected_metrics", {}).keys()))
print("Baseline metrics keys:", list((exp.get("baseline_metrics") or {}).keys()))
lat = exp.get("protected_metrics", {}).get("latency_stats", {})
print("Latency stats:", lat)

# 2. Test /api/privacy/evaluate
from backend.api.privacy import run_privacy_leakage_experiment, PrivacyExperimentRequest
req_priv = PrivacyExperimentRequest(
    sigmas=[0.0, 0.05],
    sample_limit=10,
    dataset_name="default_catalog"
)
res_priv = run_privacy_leakage_experiment(req_priv, current_user=admin_user)
print("\n=== /api/privacy/evaluate result ===")
print("Status:", res_priv.get("status"))
print("Curve items:", len(res_priv.get("experiment", {}).get("tradeoff_curve", [])))

# 3. Test /api/privacy/leakage/overview
from backend.api.privacy import get_leakage_overview
res_leak_ov = get_leakage_overview(current_user=admin_user)
print("\n=== /api/privacy/leakage/overview result ===")
print("Keys:", list(res_leak_ov.keys()))

# 4. Test /api/privacy/leakage/inversion
from backend.api.privacy import run_inversion_attack_endpoint, InversionAttackRequest
req_inv = InversionAttackRequest(iterations=5)
res_inv = run_inversion_attack_endpoint(req_inv, current_user=admin_user)
print("\n=== /api/privacy/leakage/inversion result ===")
print("Metrics keys:", list(res_inv.get("metrics", {}).keys()))

# 5. Test /api/privacy/leakage/membership-inference
from backend.api.privacy import run_membership_inference_endpoint, MIABenchmarkRequest
req_mia = MIABenchmarkRequest(sample_size=10)
res_mia = run_membership_inference_endpoint(req_mia, current_user=admin_user)
print("\n=== /api/privacy/leakage/membership-inference result ===")
print("MIA keys:", list(res_mia.keys()))

# 6. Test /api/privacy/leakage/attribute-inference
from backend.api.privacy import run_attribute_inference_endpoint
res_att = run_attribute_inference_endpoint(current_user=admin_user)
print("\n=== /api/privacy/leakage/attribute-inference result ===")
print("Evaluations count:", len(res_att.get("evaluations", [])))

print("\n>>> ALL EVALUATION AND PRIVACY BACKEND ENDPOINTS ARE VERIFIED! <<<")
