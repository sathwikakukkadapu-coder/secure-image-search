import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import time
import json
import numpy as np
from PIL import Image
from backend.services.storage.vault import PrivateImageVault
from backend.services.feature_extraction.extractor import FeatureExtractor
import backend.database.db as db

OUT_FILE = os.path.join("vector_db", "raw_1280_vectors.npy")

def generate_1280_cache():
    if os.path.exists(OUT_FILE):
        print(f"{OUT_FILE} already exists. Skipping.")
        return

    with open("vector_db/id_map.json", "r", encoding="utf-8") as f:
        id_map = json.load(f)

    n_total = len(id_map)
    vault = PrivateImageVault.get_instance()
    extractor = FeatureExtractor.get_instance()

    vectors = np.zeros((n_total, 1280), dtype=np.float32)
    t0 = time.time()
    success = 0

    print(f"Extracting 1280-D features for {n_total} catalog images...")
    for idx_str, image_id in id_map.items():
        idx = int(idx_str)
        try:
            raw_bytes = vault.get_decrypted_image(image_id)
            if raw_bytes:
                img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                vec, _, _ = extractor.extract_features(img)
                vectors[idx] = vec
                success += 1
        except Exception as e:
            print(f"Error extracting {image_id}: {e}")

        if (idx + 1) % 200 == 0 or idx == n_total - 1:
            elapsed = time.time() - t0
            print(f"Processed {idx + 1}/{n_total} images ({elapsed:.1f}s)...")

    np.save(OUT_FILE, vectors)
    print(f"Successfully cached {success} 1280-D vectors to {OUT_FILE} in {time.time() - t0:.1f}s")

if __name__ == "__main__":
    generate_1280_cache()
