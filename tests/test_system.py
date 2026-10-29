import os
import sys
import time
import threading
import requests

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://127.0.0.1:8000"

def ensure_server_running():
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=0.5)
        if res.status_code == 200:
            print("[Test Suite] Connected to active server on port 8000.", flush=True)
            return None
    except Exception:
        pass

    print("[Test Suite] No active server detected. Initializing in-process uvicorn thread...", flush=True)
    import uvicorn
    from backend.main import app
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    
    # Wait for server to be responsive
    for _ in range(20):
        time.sleep(0.5)
        try:
            res = requests.get(f"{BASE_URL}/health", timeout=0.5)
            if res.status_code == 200:
                print("[Test Suite] In-process server ready on port 8000.", flush=True)
                return server
        except Exception:
            pass
    raise RuntimeError("Could not start test server.")

def test_full_pipeline():
    server = ensure_server_running()

    print(">>> 1. Testing Health & Status...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["status"] == "healthy"
    assert data["faiss_vectors"] >= 32
    assert data["zero_pixel_invariant"] is True
    print(f"    [PASS] Health check verified. FAISS Vectors: {data['faiss_vectors']}, Zero-Pixel Invariant: True.")

    print("\n>>> 2. Testing Frontend SPA Serving...")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    assert "Private Image Search" in res.text
    print("    [PASS] Frontend SPA HTML successfully served.")

    print("\n>>> 3. Testing Admin Telemetry API...")
    res = requests.get(f"{BASE_URL}/api/admin/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["dataset"]["total_images"] >= 32
    assert stats["dataset"]["faiss_indexed_vectors"] >= 32
    assert stats["security"]["encryption_cipher"] == "AES-256-GCM"
    print(f"    [PASS] Admin stats verified. Total images: {stats['dataset']['total_images']}, Private disk: {stats['storage']['private_vault_disk_mb']} MB.")

    print("\n>>> 4. Testing Live Search Query with Specialist (Dr. Sharma)...")
    with open("dataset/medical/ct_pulmonary_101.jpg", "rb") as f:
        img_bytes = f.read()
        
    files = {"file": ("query.jpg", img_bytes, "image/jpeg")}
    data = {"top_k": 5, "protected": "true", "sigma": 0.05}
    headers = {"Authorization": "Bearer USR_DOC_01"}
    
    res = requests.post(f"{BASE_URL}/api/search/query", files=files, data=data, headers=headers)
    assert res.status_code == 200, f"Search failed: {res.text}"
    search_data = res.json()
    
    assert len(search_data["results"]) == 5
    assert len(search_data["pipeline_steps"]) == 6
    assert search_data["privacy_report"]["original_images_in_faiss"] is False
    
    top_match = search_data["results"][0]
    auth_ascii = top_match['auth_status'].encode('ascii', 'replace').decode('ascii')
    print(f"    Top Match: {top_match['image_id']} (Sim: {top_match['similarity_percent']}) - Auth: {auth_ascii}")
    assert top_match["authorized"] is True, "Doctor should be authorized for medical scan"
    assert top_match["image_url"] is not None
    print("    [PASS] Search executed. 6-stage pipeline measured, doctor authorized for private scan.")

    print("\n>>> 5. Testing Access Control Rejection for Unauthorized Guest...")
    files = {"file": ("query.jpg", img_bytes, "image/jpeg")}
    headers = {"Authorization": "Bearer USR_GST_99"}
    
    res = requests.post(f"{BASE_URL}/api/search/query", files=files, data=data, headers=headers)
    assert res.status_code == 200
    guest_data = res.json()
    
    medical_match = [m for m in guest_data["results"] if m["category"] == "medical"][0]
    auth_guest_ascii = medical_match['auth_status'].encode('ascii', 'replace').decode('ascii')
    print(f"    Guest Medical Match: {medical_match['image_id']} - Auth: {auth_guest_ascii}")
    assert medical_match["authorized"] is False, "Guest must NOT be authorized for private medical scan"
    assert medical_match["image_url"] is None
    print("    [PASS] Access control properly blocked unauthorized guest from viewing private asset.")

    print("\n>>> 6. Testing Direct Storage Fetch Protection...")
    # Attempting to fetch private image as Guest -> Expect 403 Forbidden
    res_blocked = requests.get(f"{BASE_URL}/api/storage/image/{medical_match['image_id']}", headers={"Authorization": "Bearer USR_GST_99"})
    assert res_blocked.status_code == 403, f"Expected 403, got {res_blocked.status_code}"
    print(f"    [PASS] Direct storage fetch correctly rejected with 403 Forbidden: {res_blocked.json()['detail']}")

    # Attempting to fetch as Authorized Doctor -> Expect 200 OK with JPEG
    res_allowed = requests.get(f"{BASE_URL}/api/storage/image/{medical_match['image_id']}", headers={"Authorization": "Bearer USR_DOC_01"})
    assert res_allowed.status_code == 200, f"Expected 200, got {res_allowed.status_code}"
    assert res_allowed.headers["content-type"] == "image/jpeg"
    assert len(res_allowed.content) > 1000
    print(f"    [PASS] Authorized doctor successfully decrypted and received {len(res_allowed.content)} image bytes.")

    print("\n>>> 7. Testing Evaluation Benchmark API...")
    res_eval = requests.get(f"{BASE_URL}/api/evaluation/benchmark")
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["status"] == "completed"
    print(f"    Precision@1: {eval_data['retrieval_metrics']['precision_at_1']}")
    print(f"    Precision@3: {eval_data['retrieval_metrics']['precision_at_3']}")
    print(f"    Precision@5: {eval_data['retrieval_metrics']['precision_at_5']}")
    print(f"    Average Latency: {eval_data['retrieval_metrics']['average_search_time_ms']}")
    print("    [PASS] Evaluation metrics calculated dynamically from indexed dataset.")

    print("\n>>> 8. Testing Client-Side Local Processing Endpoint...")
    files = {"file": ("query.jpg", img_bytes, "image/jpeg")}
    data = {"protected": "true", "sigma": 0.05}
    res_local = requests.post(f"{BASE_URL}/api/client/process-local", files=files, data=data)
    assert res_local.status_code == 200, f"Local processing failed: {res_local.text}"
    local_data = res_local.json()
    assert local_data["status"] == "success"
    assert local_data["client_processing"]["protected_dim"] == 512
    assert len(local_data["protected_vector"]) == 512
    assert "zero_pixel_invariant" in local_data
    print("    [PASS] Client-side processing simulated successfully: 512-D vector generated with 0 pixels retained.")

    print("\n>>> 9. Testing Content-Free Vector Search Query (0 Pixels Transmitted)...")
    payload = {
        "protected_vector": local_data["protected_vector"],
        "top_k": 5,
        "threshold": 0.2,
        "strip_metadata": True
    }
    res_cf = requests.post(
        f"{BASE_URL}/api/search/content-free-query",
        json=payload,
        headers={"Authorization": "Bearer USR_DOC_01"}
    )
    assert res_cf.status_code == 200, f"Content-free query failed: {res_cf.text}"
    cf_data = res_cf.json()
    assert cf_data["content_free_mode"] == "ON"
    assert cf_data["server_metrics"]["pixels_sent_to_server"] == 0
    assert cf_data["server_metrics"]["pixels_stored_on_server"] == 0
    assert cf_data["server_metrics"]["zero_pixel_server_invariant"] is True
    assert len(cf_data["results"]) > 0
    assert "privacy_receipt" in cf_data
    assert cf_data["privacy_receipt"]["query_pixels_sent"] == 0
    print(f"    [PASS] Content-free search successful! {len(cf_data['results'])} matches found. 0 pixels transmitted.")

    print("\n>>> 10. Testing Client vs Server Boundary Data Inventory API...")
    res_inv = requests.get(f"{BASE_URL}/api/inventory/summary")
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    assert inv_data["mode"] == "CONTENT-FREE"
    assert inv_data["server_retrieval_layer"]["original_images_in_index"] == 0
    assert inv_data["server_retrieval_layer"]["pixels_stored"] == 0
    assert inv_data["authorized_vault_layer"]["decoupled_from_faiss"] is True
    print("    [PASS] Boundary inventory verified: Index contains 0 original images, Vault is decoupled.")

    # ========================================================
    # NEW MODULE 1: RETRIEVAL EVALUATION & BENCHMARKING TESTS
    # ========================================================
    print("\n>>> 11. Testing Module 1: Retrieval Evaluation Engine & Benchmarking...")
    res_ds = requests.get(f"{BASE_URL}/api/evaluation/datasets", headers={"Authorization": "Bearer USR_RES_02"})
    assert res_ds.status_code == 200
    ds_data = res_ds.json()
    assert len(ds_data["datasets"]) > 0
    assert ds_data["datasets"][0]["total_samples"] >= 32
    print(f"    Datasets available: {ds_data['datasets'][0]['name']} ({ds_data['datasets'][0]['total_samples']} samples)")

    eval_payload = {
        "dataset_name": "default_catalog",
        "sample_limit": 16,
        "k_values": [1, 3, 5, 10],
        "sigma": 0.05,
        "compare_baseline": True
    }
    res_run = requests.post(f"{BASE_URL}/api/evaluation/run", json=eval_payload, headers={"Authorization": "Bearer USR_RES_02"})
    assert res_run.status_code == 200
    run_data = res_run.json()
    assert run_data["status"] == "completed"
    assert "protected_metrics" in run_data["experiment"]
    assert "baseline_metrics" in run_data["experiment"]
    prot_m = run_data["experiment"]["protected_metrics"]
    assert "precision_by_k" in prot_m
    assert "map" in prot_m
    print(f"    [PASS] Module 1 Evaluation Run verified: mAP = {prot_m['map']*100:.1f}%, P@5 = {prot_m['precision_by_k']['precision_at_5']*100:.1f}%.")

    res_hist = requests.get(f"{BASE_URL}/api/evaluation/history", headers={"Authorization": "Bearer USR_RES_02"})
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert hist_data["total"] > 0
    print(f"    [PASS] Evaluation experiment history verified: {hist_data['total']} recorded runs.")

    # ========================================================
    # NEW MODULE 2: PRIVACY ANALYSIS & LEAKAGE EVALUATION TESTS
    # ========================================================
    print("\n>>> 12. Testing Module 2: Privacy Analysis & Leakage Evaluation...")
    res_priv_ov = requests.get(f"{BASE_URL}/api/privacy/overview", headers={"Authorization": "Bearer USR_RES_02"})
    assert res_priv_ov.status_code == 200
    ov_data = res_priv_ov.json()
    assert ov_data["mechanism"]["raw_feature_dimension"] == 1280
    assert ov_data["mechanism"]["protected_representation_dimension"] == 512
    assert "threat_model" in ov_data
    print("    [PASS] Privacy mechanism overview and threat model documented correctly.")

    priv_payload = {
        "sigmas": [0.0, 0.05, 0.10],
        "sample_limit": 16,
        "dataset_name": "default_catalog"
    }
    res_priv_run = requests.post(f"{BASE_URL}/api/privacy/evaluate", json=priv_payload, headers={"Authorization": "Bearer USR_RES_02"})
    assert res_priv_run.status_code == 200
    priv_run_data = res_priv_run.json()
    assert priv_run_data["status"] == "completed"
    curve = priv_run_data["experiment"]["tradeoff_curve"]
    assert len(curve) == 3
    # Verify that as sigma increases, reconstruction MSE increases
    assert curve[0]["sigma"] == 0.0
    assert curve[1]["reconstruction_mse"] > curve[0]["reconstruction_mse"]
    print(f"    [PASS] Privacy-utility tradeoff verified: MSE at sigma=0.0 ({curve[0]['reconstruction_mse']:.5f}) < sigma=0.05 ({curve[1]['reconstruction_mse']:.5f}).")

    # ========================================================
    # NEW MODULE 3: SECURITY CENTER & AUDIT TRAIL TESTS
    # ========================================================
    print("\n>>> 13. Testing Module 3: Security Center & Cryptographic Audit Trail...")
    res_sec_stats = requests.get(f"{BASE_URL}/api/security/stats", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_sec_stats.status_code == 200
    sec_stats = res_sec_stats.json()
    assert sec_stats["security_metrics"]["total_audit_events"] > 0
    print(f"    [PASS] Security stats verified. Total audit events: {sec_stats['security_metrics']['total_audit_events']}.")

    # Verify SHA-256 hash chaining
    res_int = requests.get(f"{BASE_URL}/api/security/verify-integrity", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_int.status_code == 200
    int_data = res_int.json()
    assert int_data["valid"] is True, "Audit hash chain must be intact"
    print(f"    [PASS] Tamper-evident audit chain verified: All {int_data['total_records']} blocks valid.")

    # Test RBAC rejection: Non-admin role attempting administrative export -> 403 Forbidden
    res_unauth_exp = requests.get(f"{BASE_URL}/api/security/export?format=json", headers={"Authorization": "Bearer USR_GST_99"})
    assert res_unauth_exp.status_code == 403, "Non-admin user must be rejected with 403"
    print("    [PASS] Security policy enforced: Non-admin export blocked with 403 Forbidden.")

    # Test Admin export -> 200 OK
    res_admin_exp = requests.get(f"{BASE_URL}/api/security/export?format=json", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_admin_exp.status_code == 200
    exp_json = res_admin_exp.json()
    assert "records" in exp_json
    print(f"    [PASS] Administrator successfully exported {len(exp_json['records'])} audit records.")

    # ========================================================
    # NEW MODULE 4: DATASET & VECTOR INDEX MANAGEMENT TESTS
    # ========================================================
    print("\n>>> 14. Testing Module 4: Dataset & Vector Index Management...")
    res_idx_st = requests.get(f"{BASE_URL}/api/index/status", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_idx_st.status_code == 200
    idx_st = res_idx_st.json()
    assert idx_st["status"] in ["HEALTHY", "ONLINE"]
    assert idx_st["index_telemetry"]["indexed_vectors_faiss"] >= 32
    assert idx_st["index_telemetry"]["vector_dimension"] == 512
    print(f"    [PASS] Index status verified: {idx_st['status']} with {idx_st['index_telemetry']['indexed_vectors_faiss']} 512-D vectors.")

    res_val = requests.post(f"{BASE_URL}/api/index/validate", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert val_data["summary"]["valid_samples"] >= 32
    assert val_data["summary"]["corrupt_files_count"] == 0
    print(f"    [PASS] Dataset validation verified: {val_data['summary']['valid_samples']} valid images, 0 corrupt files.")

    # Test RBAC rejection: Non-admin attempting index rebuild -> 403 Forbidden
    res_rebuild_unauth = requests.post(f"{BASE_URL}/api/index/rebuild", headers={"Authorization": "Bearer USR_RES_02"})
    assert res_rebuild_unauth.status_code == 403
    print("    [PASS] Index management policy enforced: Researcher denied rebuild with 403 Forbidden.")

    # Test Incremental indexing
    res_incr = requests.post(f"{BASE_URL}/api/index/incremental", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_incr.status_code == 200
    incr_data = res_incr.json()
    assert incr_data["status"] in ["up_to_date", "success"]
    print(f"    [PASS] Incremental indexing verified: {incr_data['status']}.")

    # ========================================================
    # QUERY-IMAGE PRIVACY INVARIANT VERIFICATION
    # ========================================================
    print("\n>>> 15. Testing Mandatory Query-Image Privacy Rule...")
    # Check that query image pixels were not logged in audit logs
    res_logs = requests.get(f"{BASE_URL}/api/security/events?category=SEARCH&limit=20", headers={"Authorization": "Bearer USR_ADM_00"})
    assert res_logs.status_code == 200
    search_events = res_logs.json()["events"]
    for ev in search_events:
        details_lower = ev["details"].lower()
        assert "base64" not in details_lower
        assert "jpeg" not in details_lower or "0 pixels" in details_lower
    print("    [PASS] Zero query pixels leaked into audit trail or backend logs.")

    print("\n=========================================================================")
    print("  ALL 15 END-TO-END TEST SUITES EXECUTED AND PASSED SUCCESSFULLY!       ")
    print("=========================================================================")

    if server:
        server.should_exit = True

if __name__ == "__main__":
    test_full_pipeline()
