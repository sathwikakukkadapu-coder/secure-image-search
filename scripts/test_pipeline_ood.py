import os
import sys
from PIL import Image

sys.path.insert(0, os.getcwd())
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.retrieval.domain_classifier import DomainClassifier

extractor = FeatureExtractor.get_instance()
protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
classifier = DomainClassifier.get_instance()
retriever = FAISSRetrievalEngine.get_instance(dimension=512)

# Make sure paper.png exists or create synthetic paper
if not os.path.exists("test_dataset/paper.png"):
    paper_img = Image.new("RGB", (400, 400), color=(245, 245, 245))
    paper_img.save("test_dataset/paper.png")

# Also synthetic red can / coca-cola tin
if not os.path.exists("test_dataset/coca_cola_tin.png"):
    coke_img = Image.new("RGB", (300, 450), color=(210, 25, 25))
    coke_img.save("test_dataset/coca_cola_tin.png")

test_paths = [
    "test_dataset/01_Medical/test_medical_xray_05.jpg",
    "test_dataset/03_Vehicles/test_vehicles_cars_01.jpg",
    "test_dataset/02_Biometrics/test_biometrics_face_01.jpg",
    "test_dataset/04_Nature/test_nature_general_01.jpg",
    "test_dataset/paper.png",
    "test_dataset/coca_cola_tin.png"
]

for p in test_paths:
    if os.path.exists(p):
        img = Image.open(p).convert("RGB")
        raw, _, _ = extractor.extract_features(img)
        prot, _ = protector.protect_vector(raw, apply_noise=True, sigma=0.05)
        dom = classifier.classify_image(raw, os.path.basename(p))
        dom_prot = classifier.classify_protected_vector(prot)
        matches, below, diag = retriever.search_domain_aware(
            prot, domain_filter=dom["domain"], top_k=5, threshold=0.20
        )
        top_sim = matches[0]["similarity"] if matches else (below[0]["similarity"] if below else 0)
        top_sim_cal = top_sim / (1.0 / (1.0 + 512 * 0.05**2)**0.5)
        print(f"{os.path.basename(p):<25} | domain={dom['domain']:<10} (conf={dom['confidence']:.2f}) | matches>0.2={len(matches)} | top_sim={top_sim:.4f} (cal={top_sim_cal:.4f})")
