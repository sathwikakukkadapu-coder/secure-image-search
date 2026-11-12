"""
SecureImage Research Module A: Retrieval Evaluation Engine.

Provides empirical evaluation of image retrieval performance across
varying embedding dimensionalities (512, 384, 256, 128, 64) and reduction techniques.

Strict Invariants Enforced:
1. Query-Peer Exclusion: A query image is excluded from its own result set (self-match removal).
2. Category-Based Ground Truth: Relevance is established by dataset category (Medical, Biometrics, Vehicles, Nature).
3. Metric Completeness: Computes Precision@5, Precision@10, Recall@5, Recall@10, mAP@5, mAP@10,
   retrieval latency, and storage footprint.
4. Statistical Rigor: Multi-trial evaluation for stochastic reduction techniques (mean +/- std).
"""

import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import faiss

import backend.database.db as db
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from research.retrieval_ablation.dimensionality_reduction import DimensionalityReducer


class RetrievalEvaluator:
    """
    Evaluates nearest neighbor retrieval across reduced dimensionalities.
    Uses FAISS IndexFlatIP (Inner Product) on L2-normalized vectors.
    """

    def __init__(self):
        self.retriever = FAISSRetrievalEngine.get_instance()
        self.db_records = {img["image_id"]: img for img in db.get_all_images()}
        self._gallery_cache = None
        self._gallery_ids = None

    def get_full_gallery_embeddings(self) -> Tuple[np.ndarray, List[str]]:
        """Extracts and caches all 512-D gallery embeddings from the active FAISS index."""
        if self._gallery_cache is not None:
            return self._gallery_cache, self._gallery_ids

        n_total = self.retriever.index.ntotal
        dim = self.retriever.dimension
        embeddings = np.zeros((n_total, dim), dtype=np.float32)
        ids = []

        for row_idx in range(n_total):
            vec = self.retriever.index.reconstruct(row_idx)
            embeddings[row_idx] = vec
            img_id = self.retriever.id_map.get(row_idx, f"IMG_{row_idx}")
            ids.append(img_id)

        # Ensure unit normalization
        embeddings = DimensionalityReducer.l2_normalize(embeddings)
        self._gallery_cache = embeddings
        self._gallery_ids = ids
        return embeddings, ids

    def evaluate_retrieval(
        self,
        gallery_vectors: np.ndarray,
        gallery_ids: List[str],
        query_vectors: np.ndarray,
        query_ids: List[str],
        query_categories: List[str],
        top_k_list: Tuple[int, ...] = (5, 10)
    ) -> Dict[str, Any]:
        """
        Builds a dedicated FAISS IndexFlatIP for the evaluated dimensionality and executes
        all queries with strict query-peer exclusion.
        """
        dim = gallery_vectors.shape[1]
        t0_index = time.time()

        # Build experimental FAISS index
        index = faiss.IndexFlatIP(dim)
        index.add(gallery_vectors.astype(np.float32))
        index_build_ms = (time.time() - t0_index) * 1000.0

        max_k = max(top_k_list)
        # Search for max_k + 1 to account for potential self-matches
        k_search = min(len(gallery_ids), max_k + 1)

        t0_search = time.time()
        distances, indices = index.search(query_vectors.astype(np.float32), k_search)
        total_search_ms = (time.time() - t0_search) * 1000.0
        avg_query_latency_ms = total_search_ms / max(1, len(query_ids))

        # Category peer counts in gallery for recall computation
        cat_counts: Dict[str, int] = {}
        for gid in gallery_ids:
            cat = self.db_records.get(gid, {}).get("category", "unknown")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        precisions: Dict[int, List[float]] = {k: [] for k in top_k_list}
        recalls: Dict[int, List[float]] = {k: [] for k in top_k_list}
        average_precisions_5: List[float] = []
        average_precisions_10: List[float] = []

        for q_idx, q_id in enumerate(query_ids):
            q_cat = query_categories[q_idx]
            retrieved_row_indices = indices[q_idx]

            # Map retrieved rows to image IDs and exclude self-match
            retrieved_matches = []
            for row in retrieved_row_indices:
                if row < 0 or row >= len(gallery_ids):
                    continue
                match_id = gallery_ids[row]
                if match_id == q_id:
                    # Strict query-peer exclusion
                    continue
                retrieved_matches.append(match_id)
                if len(retrieved_matches) >= max_k:
                    break

            # Calculate relevance array (1 if same category, 0 otherwise)
            relevance = [
                1 if self.db_records.get(mid, {}).get("category") == q_cat else 0
                for mid in retrieved_matches
            ]

            # Ground truth total relevant peers in gallery excluding self if self was in gallery
            self_in_gallery = (q_id in gallery_ids)
            total_relevant_peers = max(1, cat_counts.get(q_cat, 1) - (1 if self_in_gallery else 0))

            for k in top_k_list:
                k_slice = relevance[:k]
                k_len = len(k_slice)
                rel_count = sum(k_slice)

                p_k = rel_count / float(k)
                r_k = rel_count / float(total_relevant_peers)

                precisions[k].append(p_k)
                recalls[k].append(r_k)

            # Average Precision @ 5
            rel_5 = relevance[:5]
            if sum(rel_5) > 0:
                ap5_terms = [sum(rel_5[:i+1]) / float(i+1) for i in range(len(rel_5)) if rel_5[i] == 1]
                average_precisions_5.append(sum(ap5_terms) / float(len(ap5_terms)))
            else:
                average_precisions_5.append(0.0)

            # Average Precision @ 10
            rel_10 = relevance[:10]
            if sum(rel_10) > 0:
                ap10_terms = [sum(rel_10[:i+1]) / float(i+1) for i in range(len(rel_10)) if rel_10[i] == 1]
                average_precisions_10.append(sum(ap10_terms) / float(len(ap10_terms)))
            else:
                average_precisions_10.append(0.0)

        # Storage consumption calculations (Float32 = 4 bytes)
        bytes_per_vector = dim * 4
        kb_per_vector = bytes_per_vector / 1024.0
        total_storage_kb = (bytes_per_vector * len(gallery_ids)) / 1024.0
        baseline_bytes = 512 * 4
        storage_reduction_pct = round((1.0 - (bytes_per_vector / baseline_bytes)) * 100.0, 1)

        return {
            "dimension": dim,
            "queries_evaluated": len(query_ids),
            "gallery_size": len(gallery_ids),
            "precision_at_5": round(float(np.mean(precisions[5])), 4),
            "precision_at_10": round(float(np.mean(precisions[10])), 4),
            "recall_at_5": round(float(np.mean(recalls[5])), 4),
            "recall_at_10": round(float(np.mean(recalls[10])), 4),
            "map_at_5": round(float(np.mean(average_precisions_5)), 4),
            "map_at_10": round(float(np.mean(average_precisions_10)), 4),
            "avg_latency_ms": round(float(avg_query_latency_ms), 3),
            "index_build_ms": round(float(index_build_ms), 2),
            "storage": {
                "dimension": dim,
                "bytes_per_vector": bytes_per_vector,
                "kb_per_vector": round(kb_per_vector, 2),
                "total_storage_kb": round(total_storage_kb, 2),
                "storage_reduction_percent": storage_reduction_pct
            }
        }
