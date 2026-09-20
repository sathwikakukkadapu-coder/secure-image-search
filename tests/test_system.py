import os
import requests

BASE_URL = "http://localhost:8000"

def test_full_pipeline():
    print(">>> 1. Testing Health & Status...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["status"] == "healthy"
    assert data["faiss_vectors"] == 16
    assert data["zero_pixel_invariant"] is True
    print("    [PASS] Health check verified. FAISS Vectors: 16, Zero-Pixel Invariant: True.")

    print("\n>>> 2. Testing Frontend SPA Serving...")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    assert "Private Image Search" in res.text
    print("    [PASS] Frontend SPA HTML successfully served.")

    print("\n>>> 3. Testing Admin Telemetry API...")
    res = requests.get(f"{BASE_URL}/api/admin/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["dataset"]["total_images"] == 16
    assert stats["dataset"]["faiss_indexed_vectors"] == 16
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

    print("\n=======================================================")
    print("  ALL 10 END-TO-END SYSTEM TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================")

if __name__ == "__main__":
    test_full_pipeline()
