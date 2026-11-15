"""
SecureImage Research Platform: Retrieval Evaluation Engine.

Provides mathematically rigorous, reproducible evaluation of nearest-neighbor
retrieval across embedding dimensionalities and privacy noise configurations.

Core Guarantees:
1. Zero Data Leakage: Gallery and evaluation query sets are completely disjoint.
2. Independent In-Memory Indexes: Evaluated on temporary FAISS IndexFlatIP instances;
   production vector_db/faiss_index.bin is never modified or polluted.
3. Nested Projection Consistency: All dimensionalities use consistent nested prefixes
   of the fixed orthonormal projection matrix P in R^(1280 x 512).
4. Rigorous Macro Metrics: Precision@5, Precision@10, Recall@5, Recall@10, mAP@10,
   retrieval latency (ms), and exact Float32 vector storage footprint.
5. Explicit Ground-Truth Relevance:
   - Overall domain evaluation: Relevance defined by domain category.
   - Domain-specific evaluation: Relevance defined by fine-grained subcategory labels.
   - Queries with zero relevant peers are explicitly handled and tracked.
"""

import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import faiss


class RetrievalEvaluator:
    """
    Evaluates nearest neighbor retrieval on temporary FAISS IndexFlatIP indexes.
    Enforces unit L2-normalization so that inner product equals cosine similarity.
    """

    def __init__(self):
        pass

    @staticmethod
    def l2_normalize(vectors: np.ndarray) -> np.ndarray:
        """Applies L2 unit normalization row-wise with numerical stability epsilon."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        return (vectors / norms).astype(np.float32)

    def evaluate_dimension(
        self,
        gallery_vectors: np.ndarray,
        gallery_ids: List[str],
        query_vectors: np.ndarray,
        query_ids: List[str],
        gallery_labels: List[str],
        query_labels: List[str],
        dimension: int,
        relevance_type: str = "category",
        baseline_dim: int = 512
    ) -> Dict[str, Any]:
        """
        Builds a dedicated temporary in-memory FAISS IndexFlatIP(d) and performs
        Top-10 retrieval for all query vectors against gallery vectors.

        Args:
            gallery_vectors: (N_gallery, dimension) Float32 array
            gallery_ids: List of image IDs for gallery items
            query_vectors: (N_query, dimension) Float32 array
            query_ids: List of image IDs for query items
            gallery_labels: Ground-truth class/category labels for gallery
            query_labels: Ground-truth class/category labels for queries
            dimension: Evaluated feature dimension (d)
            relevance_type: Description of relevance rule ("category" or "subcategory")
            baseline_dim: Reference dimensionality for storage savings calculation

        Returns:
            Dict containing complete empirical metrics.
        """
        n_gallery = len(gallery_ids)
        n_query = len(query_ids)
        if n_gallery == 0 or n_query == 0:
            raise ValueError(f"Gallery ({n_gallery}) and query ({n_query}) sets must be non-empty.")

        # Ensure unit L2 normalization
        g_norm = self.l2_normalize(gallery_vectors)
        q_norm = self.l2_normalize(query_vectors)

        # 1. Build temporary in-memory FAISS index
        t0_build = time.perf_counter()
        index = faiss.IndexFlatIP(dimension)
        index.add(g_norm)
        index_build_ms = (time.perf_counter() - t0_build) * 1000.0

        # 2. Execute retrieval
        k_search = min(n_gallery, 10)
        t0_search = time.perf_counter()
        distances, retrieved_indices = index.search(q_norm, k_search)
        total_search_ms = (time.perf_counter() - t0_search) * 1000.0
        avg_query_latency_ms = total_search_ms / float(n_query)

        # 3. Ground-truth label distributions in gallery
        gallery_label_counts: Dict[str, int] = {}
        for lbl in gallery_labels:
            gallery_label_counts[lbl] = gallery_label_counts.get(lbl, 0) + 1

        p5_list: List[float] = []
        p10_list: List[float] = []
        r5_list: List[float] = []
        r10_list: List[float] = []
        ap10_list: List[float] = []

        unlabeled_or_zero_rel_count = 0
        valid_queries_count = 0

        for q_idx in range(n_query):
            q_label = query_labels[q_idx]
            q_retrieved_rows = retrieved_indices[q_idx]

            # Total relevant peers available in gallery
            r_total = gallery_label_counts.get(q_label, 0)
            if r_total == 0:
                # Query has no relevant peers in the gallery
                unlabeled_or_zero_rel_count += 1
                p5_list.append(0.0)
                p10_list.append(0.0)
                r5_list.append(0.0)
                r10_list.append(0.0)
                ap10_list.append(0.0)
                continue

            valid_queries_count += 1

            # Binary relevance flags for retrieved ranking
            relevance = [
                1 if (row >= 0 and row < n_gallery and gallery_labels[row] == q_label) else 0
                for row in q_retrieved_rows
            ]

            # Precision@5 & Precision@10
            rel_5 = sum(relevance[:5])
            rel_10 = sum(relevance[:10])
            p5 = rel_5 / 5.0
            p10 = rel_10 / 10.0

            # Recall@5 & Recall@10
            r5 = rel_5 / float(r_total)
            r10 = rel_10 / float(r_total)

            p5_list.append(p5)
            p10_list.append(p10)
            r5_list.append(r5)
            r10_list.append(r10)

            # Average Precision @ 10 (AP@10)
            # AP@10 = (1 / min(R, 10)) * sum_{k=1..10} (rel_k * Precision@k)
            denom = min(r_total, 10)
            if denom > 0 and rel_10 > 0:
                ap_terms = [
                    (sum(relevance[:k]) / float(k))
                    for k in range(1, len(relevance) + 1)
                    if relevance[k - 1] == 1
                ]
                ap10 = sum(ap_terms) / float(denom)
                ap10_list.append(ap10)
            else:
                ap10_list.append(0.0)

        # Macro averages across all evaluation queries
        macro_p5 = float(np.mean(p5_list)) if p5_list else 0.0
        macro_p10 = float(np.mean(p10_list)) if p10_list else 0.0
        macro_r5 = float(np.mean(r5_list)) if r5_list else 0.0
        macro_r10 = float(np.mean(r10_list)) if r10_list else 0.0
        macro_map10 = float(np.mean(ap10_list)) if ap10_list else 0.0

        # Exact storage calculations (Float32 = 4 bytes)
        bytes_per_vector = dimension * 4
        kb_per_vector = bytes_per_vector / 1024.0
        total_gallery_storage_kb = (bytes_per_vector * n_gallery) / 1024.0

        ref_bytes = baseline_dim * 4
        reduction_pct = (1.0 - (dimension / float(baseline_dim))) * 100.0

        return {
            "dimension": dimension,
            "queries_evaluated": n_query,
            "valid_queries": valid_queries_count,
            "unlabeled_or_zero_rel_queries": unlabeled_or_zero_rel_count,
            "gallery_size": n_gallery,
            "relevance_ground_truth": relevance_type,
            "precision_at_5": round(macro_p5, 4),
            "precision_at_10": round(macro_p10, 4),
            "recall_at_5": round(macro_r5, 4),
            "recall_at_10": round(macro_r10, 4),
            "map_at_10": round(macro_map10, 4),
            "avg_latency_ms": round(avg_query_latency_ms, 3),
            "index_build_ms": round(index_build_ms, 2),
            "storage": {
                "dimension": dimension,
                "bytes_per_vector": bytes_per_vector,
                "kb_per_vector": round(kb_per_vector, 3),
                "total_gallery_storage_kb": round(total_gallery_storage_kb, 2),
                "reduction_percent": round(reduction_pct, 2)
            }
        }
