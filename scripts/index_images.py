import os
import sys
import glob
from PIL import Image, ImageDraw, ImageFilter

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
import backend.database.db as db

def generate_sample_images():
    """Generates sample synthetic dataset across 4 categories if empty."""
    dataset_dir = os.path.join(BASE_DIR, "dataset")
    categories = {
        "medical": [
            ("ct_pulmonary_101.jpg", "#0d1b2a", "#38bdf8", "CHEST CT #PULM-801"),
            ("ct_pulmonary_102.jpg", "#0d1b2a", "#0284c7", "CHEST CT #PULM-802"),
            ("xray_thorax_103.jpg", "#0a1128", "#7dd3fc", "THORAX X-RAY #TX-440"),
            ("xray_thorax_104.jpg", "#0a1128", "#38bdf8", "THORAX X-RAY #TX-441"),
        ],
        "biometrics": [
            ("face_biometric_201.jpg", "#1e1b4b", "#a78bfa", "BIOMETRIC #ID-201"),
            ("face_biometric_202.jpg", "#1e1b4b", "#c084fc", "BIOMETRIC #ID-202"),
            ("face_profile_203.jpg", "#2e1065", "#e879f9", "FACE PROFILE #FP-11"),
            ("face_profile_204.jpg", "#2e1065", "#c084fc", "FACE PROFILE #FP-12"),
        ],
        "vehicles": [
            ("car_sedan_301.jpg", "#14532d", "#4ade80", "SEDAN MOTOR #V-301"),
            ("car_sport_302.jpg", "#166534", "#22c55e", "SPORTS COUPE #V-302"),
            ("bike_cruiser_303.jpg", "#064e3b", "#34d399", "CRUISER BIKE #B-09"),
            ("bike_sport_304.jpg", "#064e3b", "#10b981", "SPORT BIKE #B-10"),
        ],
        "nature": [
            ("nature_mountain_401.jpg", "#1e293b", "#94a3b8", "ALPINE RIDGE #GEO-1"),
            ("nature_forest_402.jpg", "#0f172a", "#64748b", "FOREST CANOPY #GEO-2"),
            ("building_tower_403.jpg", "#312e81", "#818cf8", "ARCH SKYSCRAPER #ARC-1"),
            ("building_bridge_404.jpg", "#1e1b4b", "#6366f1", "SUSPENSION ARCH #ARC-2")
        ]
    }
    
    for cat, items in categories.items():
        cat_dir = os.path.join(dataset_dir, cat)
        os.makedirs(cat_dir, exist_ok=True)
        for fname, bg_col, stroke_col, label in items:
            fpath = os.path.join(cat_dir, fname)
            if not os.path.exists(fpath):
                img = Image.new("RGB", (320, 320), color=bg_col)
                draw = ImageDraw.Draw(img)
                # Geometric patterns to provide distinct convolutional features
                if cat == "medical":
                    draw.ellipse([80, 60, 140, 240], fill="#1e293b", outline=stroke_col, width=3)
                    draw.ellipse([180, 60, 240, 240], fill="#1e293b", outline=stroke_col, width=3)
                    draw.line([160, 40, 160, 260], fill="#64748b", width=4)
                    draw.ellipse([150, 150, 170, 170], fill="#ef4444")
                elif cat == "biometrics":
                    draw.ellipse([90, 70, 230, 230], fill="#312e81", outline=stroke_col, width=3)
                    draw.ellipse([120, 120, 140, 140], fill="#38bdf8")
                    draw.ellipse([180, 120, 200, 140], fill="#38bdf8")
                    draw.arc([130, 160, 190, 200], start=0, end=180, fill=stroke_col, width=3)
                elif cat == "vehicles":
                    draw.rectangle([60, 140, 260, 220], fill="#022c22", outline=stroke_col, width=3)
                    draw.polygon([(100, 140), (140, 90), (220, 90), (240, 140)], fill="#065f46", outline=stroke_col)
                    draw.ellipse([80, 200, 130, 250], fill="#0f172a", outline="#facc15", width=4)
                    draw.ellipse([190, 200, 240, 250], fill="#0f172a", outline="#facc15", width=4)
                else:
                    draw.polygon([(40, 260), (160, 80), (280, 260)], fill="#334155", outline=stroke_col, width=3)
                    draw.ellipse([220, 50, 270, 100], fill="#fbbf24")
                    draw.line([20, 260, 300, 260], fill="#64748b", width=3)
                    
                draw.text((20, 290), label, fill="#f8fafc")
                img.save(fpath, "JPEG", quality=92)

def index_all():
    print("==================================================")
    print("  Private Image Search - Dataset Indexing Engine  ")
    print("==================================================")
    
    generate_sample_images()
    db.init_db()
    
    extractor = FeatureExtractor.get_instance(model_name="mobilenet_v3_large")
    protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    vault = PrivateImageVault.get_instance()
    
    dataset_dir = os.path.join(BASE_DIR, "dataset")
    categories = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    
    # Ownership assignment
    # Medical images owned by Dr. Sharma (specialist)
    # Vehicles & Nature are public or owned by Alex Verma (researcher)
    owner_map = {
        "medical": ("USR_DOC_01", True),      # Private, Doctor owned
        "biometrics": ("USR_DOC_01", True),   # Private, Doctor owned
        "vehicles": ("USR_RES_02", False),    # Public catalog
        "nature": ("USR_RES_02", False)       # Public catalog
    }
    
    indexed_count = 0
    
    for cat in categories:
        cat_path = os.path.join(dataset_dir, cat)
        img_files = glob.glob(os.path.join(cat_path, "*.*"))
        
        for img_path in img_files:
            fname = os.path.basename(img_path)
            img_id = f"IMG_{cat[:3].upper()}_{os.path.splitext(fname)[0]}"
            
            owner_id, is_private = owner_map.get(cat, ("USR_RES_02", False))
            
            # 1. Read image bytes
            with open(img_path, "rb") as f:
                img_bytes = f.read()
                
            # 2. Store in decoupled Private Vault (NOT in FAISS)
            safe_name, enc_storage_ref = vault.store_image(img_bytes, img_id, fname)
            
            # 3. Preprocess and Extract CNN Features
            pil_img = Image.open(img_path)
            raw_vector, _, _ = extractor.extract_features(pil_img)
            
            # 4. Apply Privacy Protection (Orthogonal Projection + Noise)
            protected_vector, _ = protector.protect_vector(raw_vector, apply_noise=True, sigma=0.05)
            
            # 5. Add to FAISS Vector Index (Stores ONLY Float32 Vector, ZERO pixels)
            row_id = retriever.add_vector(protected_vector, img_id)
            
            # 6. Record metadata in SQLite
            db.insert_image(
                image_id=img_id,
                owner_id=owner_id,
                original_filename=fname,
                storage_reference=enc_storage_ref,
                category=cat,
                is_private=is_private
            )
            db.insert_vector_mapping(img_id, row_id, extractor.model_name)
            
            indexed_count += 1
            print(f"  [Indexed] {img_id:<24} | Category: {cat:<10} | Private: {is_private} | FAISS Row: {row_id}")
            
    retriever.save_index()
    print("--------------------------------------------------")
    print(f"Indexing Complete! Successfully indexed {indexed_count} images.")
    print(f"FAISS Vectors: {retriever.count()} | Storage Vault: {vault.storage_dir}")
    print("Strict Invariant: Zero image pixels in the vector database.")
    print("==================================================")

if __name__ == "__main__":
    index_all()
