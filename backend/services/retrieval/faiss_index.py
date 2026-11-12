import os
import json
import time
from typing import List, Dict, Any, Tuple, Optional
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
        
        # Verify finite values
        if not np.isfinite(query).all():
            return [], (time.time() - t0) * 1000
            
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

    def search_domain_aware(
        self,
        query_protected_vector: np.ndarray,
        domain_filter: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.0,
        include_below_threshold: bool = False
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes domain-aware similarity search with threshold enforcement.
        Returns: (matching_results, below_threshold_results, diagnostics)
        """
        import backend.database.db as db
        t0 = time.time()
        
        diagnostics = {
            "total_indexed_records": self.index.ntotal,
            "vector_dimension": self.dimension,
            "domain_filter_requested": domain_filter or "all",
            "similarity_threshold": threshold,
            "top_k_requested": top_k,
            "candidates_retrieved_from_faiss": 0,
            "candidates_matching_domain": 0,
            "records_passed_threshold": 0,
            "records_rejected_threshold": 0,
            "search_latency_ms": 0.0,
            "error": None
        }

        if self.index.ntotal == 0:
            diagnostics["search_latency_ms"] = round((time.time() - t0) * 1000, 3)
            return [], [], diagnostics

        query = query_protected_vector.reshape(1, self.dimension).astype(np.float32)
        if not np.isfinite(query).all():
            diagnostics["error"] = "Query vector contains non-finite values (NaN or Inf)"
            diagnostics["search_latency_ms"] = round((time.time() - t0) * 1000, 3)
            return [], [], diagnostics
            
        norm = np.linalg.norm(query)
        if norm == 0:
            diagnostics["error"] = "Query vector is zero-length"
            diagnostics["search_latency_ms"] = round((time.time() - t0) * 1000, 3)
            return [], [], diagnostics

        # Normalize query vector to unit length for exact cosine similarity
        query = query / norm

        # Determine candidate search pool
        clean_dom = (domain_filter or "all").lower().strip()
        if clean_dom in ["all", "any", "none", "*"]:
            k_search = min(self.index.ntotal, max(top_k * 15, 60))
            active_domain = None
        else:
            # Need an expanded pool to ensure Top-K domain matches are found
            k_search = min(self.index.ntotal, max(top_k * 40, 400))
            active_domain = clean_dom

        distances, indices = self.index.search(query, k_search)
        faiss_ms = (time.time() - t0) * 1000
        diagnostics["candidates_retrieved_from_faiss"] = len(indices[0])

        candidates = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx in self.id_map:
                img_id = self.id_map[idx]
                sim = float(dist)
                sim_clamped = max(0.0, min(1.0, sim))
                candidates.append((img_id, int(idx), sim_clamped))

        # Lookup categories in database
        candidate_ids = [c[0] for c in candidates]
        db_records = db.get_images_by_ids(candidate_ids) if hasattr(db, "get_images_by_ids") else {}
        if not db_records:
            # Fallback to individual get_image
            db_records = {cid: db.get_image(cid) for cid in candidate_ids}

        matching_domain_candidates = []
        for img_id, row_id, sim in candidates:
            rec = db_records.get(img_id)
            if not rec:
                continue
            cat = (rec.get("category") or "").lower()
            
            # Domain check
            if active_domain:
                # Support subcategories under domain
                if active_domain == "medical" and cat in ["medical", "ct", "xray", "mri"]:
                    is_dom_match = True
                elif active_domain in ["biometrics", "face", "face biometric"] and cat in ["biometrics", "faces", "fingerprints", "iris"]:
                    is_dom_match = True
                elif active_domain in ["vehicles", "vehicle"] and cat in ["vehicles", "cars", "two_wheelers", "commercial"]:
                    is_dom_match = True
                elif active_domain == "nature" and cat in ["nature", "landscapes", "water", "vegetation", "weather", "wildlife"]:
                    is_dom_match = True
                else:
                    is_dom_match = (cat == active_domain)
                    
                if not is_dom_match:
                    continue
                    
            matching_domain_candidates.append({
                "image_id": img_id,
                "vector_row_id": row_id,
                "similarity": sim,
                "similarity_percent": f"{round(sim * 100.0, 1)}%",
                "category": rec.get("category", ""),
                "owner_id": rec.get("owner_id", ""),
                "is_private": bool(rec.get("is_private", 0))
            })

        diagnostics["candidates_matching_domain"] = len(matching_domain_candidates)

        # Sort strictly by cosine similarity descending
        matching_domain_candidates.sort(key=lambda x: x["similarity"], reverse=True)

        # Apply threshold filtering
        passed_threshold = []
        below_threshold = []

        for item in matching_domain_candidates:
            if item["similarity"] >= threshold:
                passed_threshold.append(item)
            else:
                below_threshold.append(item)

        diagnostics["records_passed_threshold"] = len(passed_threshold)
        diagnostics["records_rejected_threshold"] = len(below_threshold)

        # Assign ranks
        results = passed_threshold[:top_k]
        for rank, res in enumerate(results, start=1):
            res["rank"] = rank

        # If below threshold requested or needed for fallback
        for rank, res in enumerate(below_threshold[:top_k], start=1):
            res["rank"] = rank

        diagnostics["final_result_count"] = len(results)
        diagnostics["search_latency_ms"] = round((time.time() - t0) * 1000, 3)

        return results, below_threshold, diagnostics

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
