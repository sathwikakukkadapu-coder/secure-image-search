import os
import json
import time
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss

class FAISSRetrievalEngine:
    """
    FAISS Vector Similarity Search Engine.
    
    Uses IndexFlatIP on L2-normalized protected representations.
    Inner Product on unit-length vectors equals Cosine Similarity:
        <u, v> = cos(theta) when ||u|| = ||v|| = 1.
        
    Invariant:
        The FAISS index stores strictly numerical Float32 coordinate vectors and integer row IDs.
        Zero image pixel data, file bytes, or unencrypted metadata are ever added to the index.
    """
    _instance = None

    def __init__(self, dimension: int = 512, index_dir: str = None):
        self.dimension = dimension
        if index_dir is None:
            self.index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "vector_db"))
        else:
            self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.index_dir, "faiss_index.bin")
        self.map_path = os.path.join(self.index_dir, "id_map.json")
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map: Dict[int, str] = {} # maps int row index -> image_id
        
        self.load_index()

    @classmethod
    def get_instance(cls, dimension: int = 512):
        if cls._instance is None:
            cls._instance = cls(dimension=dimension)
        return cls._instance

    def add_vector(self, protected_vector: np.ndarray, image_id: str) -> int:
        """Adds a single protected representation and maps its integer row ID to Image_ID."""
        if protected_vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension {protected_vector.shape[0]} does not match index dimension {self.dimension}")
            
        vec = protected_vector.reshape(1, self.dimension).astype(np.float32)
        row_id = self.index.ntotal
        self.index.add(vec)
        self.id_map[row_id] = image_id
        return row_id

    def add_batch(self, protected_vectors: np.ndarray, image_ids: List[str]):
        """Adds a batch of protected representations."""
        count = len(image_ids)
        if count == 0:
            return
        vecs = protected_vectors.astype(np.float32)
        start_row = self.index.ntotal
        self.index.add(vecs)
        for i, img_id in enumerate(image_ids):
            self.id_map[start_row + i] = img_id

    def search(self, query_protected_vector: np.ndarray, top_k: int = 5) -> Tuple[List[Dict[str, Any]], float]:
        """
        Executes nearest-neighbor cosine similarity query over protected vector space.
        Returns: (ranked_results: List[Dict], search_ms: float)
        """
        t0 = time.time()
        if self.index.ntotal == 0:
            return [], (time.time() - t0) * 1000

        k = min(top_k, self.index.ntotal)
        query = query_protected_vector.reshape(1, self.dimension).astype(np.float32)
        
        distances, indices = self.index.search(query, k)
        search_ms = (time.time() - t0) * 1000
        
        results = []
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
            if idx in self.id_map:
                img_id = self.id_map[idx]
                sim = float(dist) # Inner product is cosine similarity
                # Clamp similarity between 0.0 and 1.0
                sim_clamped = max(0.0, min(1.0, sim))
                pct = round(sim_clamped * 100.0, 1)
                results.append({
                    "rank": rank,
                    "image_id": img_id,
                    "similarity": round(sim, 4),
                    "similarity_percent": f"{pct}%",
                    "vector_row_id": int(idx)
                })
        return results, search_ms

    def save_index(self):
        """Persists the FAISS index and id mapping to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in self.id_map.items()}, f, indent=2)
        print(f"[FAISS Engine] Index saved ({self.index.ntotal} vectors).")

    def load_index(self):
        """Loads FAISS index from disk if available."""
        if os.path.exists(self.index_path) and os.path.exists(self.map_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.map_path, "r", encoding="utf-8") as f:
                    raw_map = json.load(f)
                    self.id_map = {int(k): v for k, v in raw_map.items()}
                print(f"[FAISS Engine] Loaded index with {self.index.ntotal} vectors from {self.index_path}.")
            except Exception as e:
                print(f"[FAISS Engine] Error loading index: {e}. Starting fresh.")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.id_map = {}

    def count(self) -> int:
        return self.index.ntotal
