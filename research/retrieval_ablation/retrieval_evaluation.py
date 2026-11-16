"""
SecureImage Research Platform: Retrieval Evaluation Engine.

Provides mathematically rigorous, reproducible evaluation of nearest-neighbor
retrieval across embedding dimensionalities and privacy noise configurations.

Core Guarantees:
1. Zero Data Leakage: Gallery and evaluation query sets are completely disjoint at the source-group level.
2. Independent In-Memory Indexes: Evaluated on temporary FAISS IndexFlatIP instances;
   production vector_db/faiss_index.bin is never modified or polluted.
3. Nested Projection Consistency: All dimensionalities use consistent nested prefixes
   of the fixed orthonormal projection matrix P in R^(1280 x 512).
4. Rigorous Macro Metrics: Precision@5, Precision@10, Recall@5, Recall@10, mAP@10,
   retrieval latency (ms), and exact Float32 vector storage footprint.
5. Explicit Ground-Truth Relevance:
   - Domain-level relevance: Relevance defined by domain category (Medical, Biometrics, Vehicles, Nature).
   - Fine-grained subtype relevance: Relevance defined by explicit taxonomy subtype.
   - Queries with zero relevant peers in the gallery are explicitly tracked, reported, and handled.
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
        if vectors.ndim == 1:
            norm = np.linalg.norm(vectors)
            norm = 1e-12 if norm == 0 else norm
            return (vectors / norm).astype(np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        return (vectors / norms).astype(np.float32)

    def calculate_ranking_metrics(
        self,
        retrieved_indices: np.ndarray,
        gallery_labels: List[str],
        query_labels: List[str],
        gallery_size: int,
        k_eval: int = 10,
        exclude_zero_rel: bool = True
    ) -> Dict[str, Any]:
        """
        Pure, deterministic metric calculation over retrieved rankings.
        Enables hand-calculated toy test verification and production validation.

        Args:
            retrieved_indices: (N_query, K_retrieved) integer array of retrieved gallery row indices.
            gallery_labels: Ground-truth class/category/subtype labels for gallery items.
            query_labels: Ground-truth class/category/subtype labels for queries.
            gallery_size: Total number of gallery items (N_gallery).
            k_eval: Cutoff rank for evaluation (default 10).
            exclude_zero_rel: If True, queries with no relevant gallery items are excluded
                              from the macro average and reported in excluded counts.

        Returns:
            Dict containing macro precision, recall, mAP, and query peer statistics.
        """
        n_query = len(query_labels)
        if n_query == 0 or gallery_size == 0:
            raise ValueError("Gallery and query sets must be non-empty.")

        # Compute total relevant items available in the gallery per label
        gallery_label_counts: Dict[str, int] = {}
        for lbl in gallery_labels:
            if lbl:
                gallery_label_counts[lbl] = gallery_label_counts.get(lbl, 0) + 1

        p5_list: List[float] = []
        p10_list: List[float] = []
        r5_list: List[float] = []
        r10_list: List[float] = []
        ap10_list: List[float] = []
        relevant_peers_list: List[int] = []

        zero_rel_count = 0
        missing_label_count = 0
        valid_queries_count = 0

        for q_idx in range(n_query):
            q_label = query_labels[q_idx]

            # Check missing label
            if not q_label:
                missing_label_count += 1
                if not exclude_zero_rel:
                    p5_list.append(0.0)
                    p10_list.append(0.0)
                    r5_list.append(0.0)
                    r10_list.append(0.0)
                    ap10_list.append(0.0)
                continue

            r_total = gallery_label_counts.get(q_label, 0)
            if r_total == 0:
                zero_rel_count += 1
                if not exclude_zero_rel:
                    p5_list.append(0.0)
                    p10_list.append(0.0)
                    r5_list.append(0.0)
                    r10_list.append(0.0)
                    ap10_list.append(0.0)
                continue

            valid_queries_count += 1
            relevant_peers_list.append(r_total)

            q_rows = retrieved_indices[q_idx]
            relevance = [
                1 if (0 <= row < gallery_size and gallery_labels[row] == q_label) else 0
                for row in q_rows
            ]

            # Precision@5 (denominator is fixed at 5)
            rel_5 = sum(relevance[:5])
            p5 = rel_5 / 5.0

            # Precision@10 (denominator is fixed at 10)
            rel_10 = sum(relevance[:10])
            p10 = rel_10 / 10.0

            # Recall@5 & Recall@10 (denominator is total relevant gallery items r_total)
            r5 = rel_5 / float(r_total)
            r10 = rel_10 / float(r_total)

            p5_list.append(p5)
            p10_list.append(p10)
            r5_list.append(r5)
            r10_list.append(r10)

            # Average Precision @ 10 (AP@10)
            # Standard definition: AP@K = (1 / min(R_total, K)) * sum_{k=1..K} (rel_k * Precision@k)
            denom = min(r_total, 10)
            if denom > 0 and rel_10 > 0:
                ap_terms = [
                    (sum(relevance[:k]) / float(k))
                    for k in range(1, min(len(relevance), 10) + 1)
                    if relevance[k - 1] == 1
                ]
                ap10 = sum(ap_terms) / float(denom)
                ap10_list.append(ap10)
            else:
                ap10_list.append(0.0)

        macro_p5 = float(np.mean(p5_list)) if p5_list else 0.0
        macro_p10 = float(np.mean(p10_list)) if p10_list else 0.0
        macro_r5 = float(np.mean(r5_list)) if r5_list else 0.0
        macro_r10 = float(np.mean(r10_list)) if r10_list else 0.0
        macro_map10 = float(np.mean(ap10_list)) if ap10_list else 0.0

        peer_stats = {
            "mean": round(float(np.mean(relevant_peers_list)), 2) if relevant_peers_list else 0.0,
            "min": int(np.min(relevant_peers_list)) if relevant_peers_list else 0,
            "max": int(np.max(relevant_peers_list)) if relevant_peers_list else 0
        }

        return {
            "queries_evaluated": n_query,
            "valid_queries": valid_queries_count,
            "queries_excluded_zero_rel": zero_rel_count,
            "queries_excluded_missing_labels": missing_label_count,
            "relevant_peers_per_query": peer_stats,
            "precision_at_5": round(macro_p5, 4),
            "precision_at_10": round(macro_p10, 4),
            "recall_at_5": round(macro_r5, 4),
            "recall_at_10": round(macro_r10, 4),
            "map_at_10": round(macro_map10, 4)
        }

    def evaluate_dimension(
        self,
        gallery_vectors: np.ndarray,
        gallery_ids: List[str],
        query_vectors: np.ndarray,
        query_ids: List[str],
        gallery_labels: List[str],
        query_labels: List[str],
        dimension: int,
        relevance_type: str = "domain",
        baseline_dim: int = 512,
        exclude_zero_rel: bool = True
    ) -> Dict[str, Any]:
        """
        Builds a dedicated temporary in-memory FAISS IndexFlatIP(d) and performs
        Top-10 retrieval for all query vectors against gallery vectors.

        Args:
            gallery_vectors: (N_gallery, dimension) Float32 array
            gallery_ids: List of image IDs for gallery items
            query_vectors: (N_query, dimension) Float32 array
            query_ids: List of image IDs for query items
            gallery_labels: Ground-truth class/category/subtype labels for gallery
            query_labels: Ground-truth class/category/subtype labels for queries
            dimension: Evaluated feature dimension (d)
            relevance_type: Description of relevance rule ("domain" or "subtype")
            baseline_dim: Reference dimensionality for storage savings calculation
            exclude_zero_rel: Whether queries with zero relevant gallery items are excluded

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

        # 2. Execute retrieval (handle case where gallery is smaller than 10)
        k_search = min(n_gallery, 10)
        t0_search = time.perf_counter()
        distances, retrieved_indices = index.search(q_norm, k_search)
        total_search_ms = (time.perf_counter() - t0_search) * 1000.0
        avg_query_latency_ms = total_search_ms / float(n_query)

        # 3. Calculate ranking metrics
        ranking_metrics = self.calculate_ranking_metrics(
            retrieved_indices=retrieved_indices,
            gallery_labels=gallery_labels,
            query_labels=query_labels,
            gallery_size=n_gallery,
            k_eval=10,
            exclude_zero_rel=exclude_zero_rel
        )

        # Exact storage calculations (Float32 = 4 bytes per coordinate)
        bytes_per_vector = dimension * 4
        kb_per_vector = bytes_per_vector / 1024.0
        total_gallery_storage_kb = (bytes_per_vector * n_gallery) / 1024.0
        reduction_pct = (1.0 - (dimension / float(baseline_dim))) * 100.0

        result = {
            "dimension": dimension,
            "gallery_size": n_gallery,
            "relevance_ground_truth": relevance_type,
            "queries_evaluated": ranking_metrics["queries_evaluated"],
            "valid_queries": ranking_metrics["valid_queries"],
            "queries_excluded_zero_rel": ranking_metrics["queries_excluded_zero_rel"],
            "queries_excluded_missing_labels": ranking_metrics["queries_excluded_missing_labels"],
            "relevant_peers_per_query": ranking_metrics["relevant_peers_per_query"],
            "precision_at_5": ranking_metrics["precision_at_5"],
            "precision_at_10": ranking_metrics["precision_at_10"],
            "recall_at_5": ranking_metrics["recall_at_5"],
            "recall_at_10": ranking_metrics["recall_at_10"],
            "map_at_10": ranking_metrics["map_at_10"],
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
        return result
