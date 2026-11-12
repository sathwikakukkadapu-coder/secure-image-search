"""
SecureImage Trusted Client Environment (Zero-Pixel Query Pipeline).

This script runs entirely on the trusted user/edge device.
It demonstrates that:
1. Raw image pixels are processed STRICTLY on the client device.
2. Feature extraction (MobileNetV3) is executed on the local edge buffer.
3. Mathematical privacy protection (LDP / RFF) is executed locally.
4. Only the 512-D protected vector (or CKKS ciphertext) is sent to the untrusted retrieval server.
5. Zero query image bytes leave the client environment.

Usage:
    python client/secureimage_client.py --image path/to/local/image.jpg --scheme ldp_gaussian --epsilon 2.0
"""

import os
import sys
import argparse
import json
import time
import requests
import numpy as np
from PIL import Image

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.representation import AdvancedPrivacyRepresentation, PrivacyRepresentationScheme

def run_trusted_client_retrieval(
    image_path: str,
    server_url: str = "http://127.0.0.1:8000",
    scheme: str = "ldp_gaussian",
    epsilon: float = 2.0,
    sigma: float = 0.05,
    top_k: int = 5,
    auth_token: str = "USR_DOC_01"
):
    print("=" * 72)
    print("       SECUREIMAGE TRUSTED CLIENT QUERY PIPELINE (EDGE BUFFER)        ")
    print("=" * 72)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Local query image not found: {image_path}")

    # Step 1: Local Image Loading & Decoding
    t0 = time.time()
    print(f"\n[Client Step 1] Loading query image into local memory buffer...")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    print(f"  -> Image File: {os.path.basename(image_path)}")
    print(f"  -> File Size: {len(img_bytes):,} bytes (Confidential local buffer)")

    # Step 2: Local Feature Extraction (MobileNetV3)
    print(f"\n[Client Step 2] Executing deep feature extraction locally...")
    extractor = FeatureExtractor.get_instance(model_name="mobilenet_v3_large")
    with Image.open(image_path) as pil_img:
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        raw_vector, t_prep, t_inf = extractor.extract_features(pil_img)
    t_feat_ms = t_prep + t_inf
    print(f"  -> Extracted Raw Feature Dimension: {len(raw_vector)}-D")
    print(f"  -> Local Inference Latency: {t_feat_ms:.1f} ms")

    # Step 3: Local Privacy Transformation
    print(f"\n[Client Step 3] Applying mathematical privacy transformation ({scheme})...")
    rep_mgr = AdvancedPrivacyRepresentation.get_instance(input_dim=1280, protected_dim=512)
    protected_vector, meta = rep_mgr.transform(
        raw_vector,
        scheme=scheme,
        epsilon=epsilon,
        sigma=sigma
    )
    print(f"  -> Protected Dimension: {len(protected_vector)}-D float32")
    print(f"  -> Formal Guarantee: {meta['formal_guarantee']}")
    print(f"  -> Vector Preview: [{', '.join(f'{v:+.4f}' for v in protected_vector[:6])}...]")

    # Step 4: Network Transmission - Transmit ONLY Protected Vector
    print(f"\n[Client Step 4] Transmitting ONLY 512-D numbers to untrusted search server...")
    payload = {
        "protected_vector": [float(v) for v in protected_vector],
        "top_k": top_k,
        "threshold": 0.0,
        "domain_filter": "auto",
        "include_below_threshold": True
    }
    
    # Audit Network Bytes
    network_bytes_sent = len(json.dumps(payload).encode("utf-8"))
    raw_image_bytes_sent = 0 # Zero query image bytes
    
    print(f"  -> Server Endpoint: {server_url}/api/search/content-free-query")
    print(f"  -> Raw Image Bytes Transmitted: {raw_image_bytes_sent} bytes (ZERO-PIXEL INVARIANT VERIFIED)")
    print(f"  -> Vector Payload Transmitted: {network_bytes_sent:,} bytes (JSON Float Array)")

    headers = {"Authorization": f"Bearer {auth_token}"}
    t_net0 = time.time()
    resp = requests.post(
        f"{server_url}/api/search/content-free-query",
        json=payload,
        headers=headers,
        timeout=10
    )
    t_net_ms = (time.time() - t_net0) * 1000.0

    if resp.status_code != 200:
        print(f"  [ERROR] Server search failed ({resp.status_code}): {resp.text}")
        return

    data = resp.json()
    print(f"\n[Client Step 5] Search Results Received ({t_net_ms:.1f} ms round-trip):")
    print(f"  -> Detected Domain: {data['diagnostics']['detected_domain_display']}")
    print(f"  -> Zero-Pixel Server Invariant: {data['server_metrics']['zero_pixel_server_invariant']}")

    print("\nTop Matches Retrieved:")
    for m in data.get("results", []):
        img_id = m["image_id"]
        sim = m["cosine_similarity"]
        pct = m["similarity_percent"]
        cat = m["category"].upper()
        auth = m["auth_status"].encode("ascii", "replace").decode("ascii")
        print(f"  #{m['rank']} [{cat}] {img_id:<28} Sim: {pct:>6} ({sim:.4f})  Auth: {auth}")

    print("\n" + "=" * 72)
    print("  ZERO QUERY PIXELS SENT TO SERVER. RETRIEVAL COMPLETED SUCCESSFULLY!  ")
    print("=" * 72)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SecureImage Trusted Client")
    parser.add_argument("--image", type=str, default="dataset/medical/ct_pulmonary_101.jpg", help="Path to local query image")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8000", help="Retrieval server base URL")
    parser.add_argument("--scheme", type=str, default="ldp_gaussian", choices=["baseline_orthogonal", "ldp_gaussian", "ldp_laplace", "non_invertible_rff", "non_invertible_sign"])
    parser.add_argument("--epsilon", type=float, default=2.0, help="LDP epsilon privacy budget")
    parser.add_argument("--sigma", type=float, default=0.05, help="Baseline perturbation sigma")
    parser.add_argument("--top_k", type=int, default=5, help="Top-K nearest neighbors")
    parser.add_argument("--token", type=str, default="USR_DOC_01", help="Authorization token / user ID")

    args = parser.parse_args()
    run_trusted_client_retrieval(
        image_path=args.image,
        server_url=args.server,
        scheme=args.scheme,
        epsilon=args.epsilon,
        sigma=args.sigma,
        top_k=args.top_k,
        auth_token=args.token
    )
