import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend.database.db as db
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine

retriever = FAISSRetrievalEngine.get_instance()
index = retriever.index
id_map = retriever.id_map

print(f"Total vectors in FAISS: {index.ntotal}")

# Group vectors by category
category_vectors = {'medical': [], 'biometrics': [], 'vehicles': [], 'nature': []}

for row_id, img_id in id_map.items():
    rec = db.get_image(img_id)
    if not rec:
        continue
    cat = rec['category']
    if cat in category_vectors:
        vec = index.reconstruct(int(row_id))
        category_vectors[cat].append(vec)

centroids = {}
for cat, vecs in category_vectors.items():
    arr = np.array(vecs, dtype=np.float32)
    mean_vec = np.mean(arr, axis=0)
    norm = np.linalg.norm(mean_vec)
    if norm > 0:
        mean_vec /= norm
    centroids[cat] = mean_vec
    print(f"Centroid for {cat}: computed from {len(vecs)} vectors, norm = {np.linalg.norm(mean_vec):.4f}")

# Save centroids
out_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'domain_centroids.npz')
np.savez_compressed(out_path, **centroids)
print(f"Saved true centroids to {out_path}!")
