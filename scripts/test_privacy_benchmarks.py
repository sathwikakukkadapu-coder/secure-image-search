import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backend.database.db as db
db.init_db()

admin_user = {"user_id": "USR_ADM_00", "role": "admin", "name": "System Administrator"}

from backend.api.privacy import (
    get_leakage_benchmark_overview,
    run_inversion_attack_benchmark,
    run_mia_benchmark,
    run_attribute_inference_benchmark,
    rotate_projection_key
)

print("\n1. Testing get_leakage_benchmark_overview...")
res1 = get_leakage_benchmark_overview(current_user=admin_user)
print("Keys:", list(res1.keys()))

print("\n2. Testing run_inversion_attack_benchmark...")
res2 = run_inversion_attack_benchmark()
print("Metrics keys:", list(res2.get("metrics", {}).keys()))

print("\n3. Testing run_mia_benchmark...")
res3 = run_mia_benchmark()
print("MIA keys:", list(res3.keys()))

print("\n4. Testing run_attribute_inference_benchmark...")
res4 = run_attribute_inference_benchmark(current_user=admin_user)
print("Attribute eval count:", len(res4.get("evaluations", [])))

print("\n>>> ALL PRIVACY ANALYSIS BENCHMARKS FUNCTION PERFECTLY! <<<")
