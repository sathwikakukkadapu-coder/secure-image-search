"""
SecureImage Research Module A: Dimensionality Reduction Algorithms.

Implements three distinct techniques for reducing the dimensionality of protected
visual embeddings (512-D baseline down to 384-D, 256-D, 128-D, 64-D):
1. Truncation: Deterministic prefix subvector retention.
2. Random Dimension Selection: Stochastic subspace projection with reproducible seed control
   and multi-trial support.
3. Principal Component Analysis (PCA): Data-driven variance maximization fitted strictly
   on gallery/training vectors to prevent data leakage.

All output representations are strictly re-normalized to the unit sphere (L2 norm = 1.0),
ensuring that inner product similarity in FAISS corresponds to exact cosine similarity.
"""

from typing import Tuple, List, Optional, Dict, Any
import numpy as np
from sklearn.decomposition import PCA


class DimensionalityReducer:
    """
    Applies dimensionality reduction to embedding matrices.
    Guarantees strict L2 normalization post-reduction.
    """

    @staticmethod
    def l2_normalize(matrix: np.ndarray) -> np.ndarray:
        """Normalizes each row vector to unit length (L2 norm = 1.0)."""
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        return (matrix / norms).astype(np.float32)

    @classmethod
    def apply_truncation(cls, vectors: np.ndarray, target_dim: int) -> np.ndarray:
        """
        Technique 1: Truncation
        Retains the first `target_dim` coordinates of each vector and re-normalizes.
        """
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        orig_dim = vectors.shape[1]
        if target_dim > orig_dim:
            raise ValueError(f"Target dimension {target_dim} exceeds original dimension {orig_dim}")
        if target_dim == orig_dim:
            return cls.l2_normalize(vectors)

        reduced = vectors[:, :target_dim]
        return cls.l2_normalize(reduced)

    @classmethod
    def apply_random_selection(
        cls,
        vectors: np.ndarray,
        target_dim: int,
        seed: int = 42
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Technique 2: Random Dimension Selection
        Stochastically samples `target_dim` coordinates without replacement.
        Returns: (reduced_vectors, selected_indices)
        """
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        orig_dim = vectors.shape[1]
        if target_dim > orig_dim:
            raise ValueError(f"Target dimension {target_dim} exceeds original dimension {orig_dim}")
        if target_dim == orig_dim:
            return cls.l2_normalize(vectors), np.arange(orig_dim)

        rng = np.random.RandomState(seed)
        selected_indices = np.sort(rng.choice(orig_dim, size=target_dim, replace=False))
        reduced = vectors[:, selected_indices]
        return cls.l2_normalize(reduced), selected_indices

    @classmethod
    def fit_and_apply_pca(
        cls,
        gallery_vectors: np.ndarray,
        query_vectors: Optional[np.ndarray] = None,
        target_dim: int = 256,
        seed: int = 42
    ) -> Tuple[np.ndarray, Optional[np.ndarray], PCA]:
        """
        Technique 3: Principal Component Analysis (PCA)
        Fits PCA strictly on gallery_vectors to prevent train/test leakage.
        Projects gallery and (optional) query vectors into the learned principal subspace.
        Returns: (reduced_gallery, reduced_query, fitted_pca_model)
        """
        if gallery_vectors.ndim == 1:
            gallery_vectors = gallery_vectors.reshape(1, -1)
        orig_dim = gallery_vectors.shape[1]
        if target_dim > orig_dim:
            raise ValueError(f"Target dimension {target_dim} exceeds original dimension {orig_dim}")

        if target_dim == orig_dim:
            norm_gallery = cls.l2_normalize(gallery_vectors)
            norm_queries = cls.l2_normalize(query_vectors) if query_vectors is not None else None
            dummy_pca = PCA(n_components=target_dim, random_state=seed)
            dummy_pca.fit(gallery_vectors)
            return norm_gallery, norm_queries, dummy_pca

        max_possible = min(gallery_vectors.shape[0], gallery_vectors.shape[1])
        actual_comp = min(target_dim, max_possible)

        # Fit PCA on gallery only
        pca = PCA(n_components=actual_comp, random_state=seed)
        reduced_gallery = pca.fit_transform(gallery_vectors)

        # If actual components were less than target_dim, zero-pad
        if actual_comp < target_dim:
            pad_width = target_dim - actual_comp
            reduced_gallery = np.pad(reduced_gallery, ((0, 0), (0, pad_width)), mode='constant')

        reduced_gallery_norm = cls.l2_normalize(reduced_gallery)

        reduced_query_norm = None
        if query_vectors is not None:
            if query_vectors.ndim == 1:
                query_vectors = query_vectors.reshape(1, -1)
            reduced_query = pca.transform(query_vectors)
            if actual_comp < target_dim:
                pad_width = target_dim - actual_comp
                reduced_query = np.pad(reduced_query, ((0, 0), (0, pad_width)), mode='constant')
            reduced_query_norm = cls.l2_normalize(reduced_query)

        return reduced_gallery_norm, reduced_query_norm, pca
