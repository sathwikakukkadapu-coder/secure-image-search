import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.getcwd())
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.retrieval.domain_classifier import DomainClassifier
import backend.database.db as db

extractor = FeatureExtractor.get_instance()
protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
classifier = DomainClassifier.get_instance()
retriever = FAISSRetrievalEngine.get_instance(dimension=512)

# Ensure sample OOD images exist
if not os.path.exists("test_dataset/paper.png"):
    Image.new("RGB", (400, 400), color=(245, 245, 245)).save("test_dataset/paper.png")
if not os.path.exists("test_dataset/coca_cola_tin.png"):
    Image.new("RGB", (300, 450), color=(210, 25, 25)).save("test_dataset/coca_cola_tin.png")

queries = [
    ("test_dataset/01_Medical/test_medical_xray_05.jpg", "IN_DOMAIN", "medical"),
    ("test_dataset/03_Vehicles/test_vehicles_cars_01.jpg", "IN_DOMAIN", "vehicles"),
    ("test_dataset/04_Nature/test_nature_general_01.jpg", "IN_DOMAIN", "nature"),
    ("test_dataset/paper.png", "OUT_OF_DOMAIN", "auto"),
    ("test_dataset/coca_cola_tin.png", "OUT_OF_DOMAIN", "auto")
]

print("="*75)
print("VERIFYING IN-DOMAIN VS OUT-OF-DOMAIN THRESHOLD RETRIEVAL")
print("="*75)

for path, expected_type, domain_hint in queries:
    img = Image.open(path).convert("RGB")
    raw, _, _ = extractor.extract_features(img)
    prot, _ = protector.protect_vector(raw, apply_noise=True, sigma=0.05)
    
    dom_info = classifier.classify_image(raw, os.path.basename(path))
    effective_domain = dom_info["domain"] if domain_hint == "auto" else domain_hint

    matches, below_matches, diag = retriever.search_domain_aware(
        prot,
        domain_filter=effective_domain,
        top_k=5,
        threshold=0.20,
        include_below_threshold=True
    )

    top_sim = matches[0]["similarity"] if matches else (below_matches[0]["similarity"] if below_matches else 0.0)
    top_pct = f"{round(top_sim * 100.0, 1)}%"
    
    if expected_type == "IN_DOMAIN":
        assert len(matches) > 0, f"Expected matches for in-domain query {path}, got 0"
        status = "PASS (Valid Catalog Matches Returned)"
        print(f"[OK] {os.path.basename(path):<26} [{expected_type}]: {status} | Top Sim: {top_pct} | Matches >= 0.20: {len(matches)}")
    else:
        assert len(matches) == 0, f"Expected 0 matches above threshold for OOD query {path}, got {len(matches)}"
        status = "PASS (Irrelevant Matches Suppressed by Threshold)"
        print(f"[OK] {os.path.basename(path):<26} [{expected_type}]: {status} | Top Sim: {top_pct} (Suppressed) | Matches >= 0.20: 0")

print("="*75)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
