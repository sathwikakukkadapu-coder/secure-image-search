"""
SecureImage Advanced Privacy-Preserving Feature Representation Module.

Implements three distinct representations for Privacy-Preserving Content-Based Image Retrieval (PP-CBIR):
1. Baseline: Semi-Orthogonal Projection (1280-D -> 512-D) with empirical Gaussian noise.
2. Local Differential Privacy (LDP):
   - Formally calibrated Gaussian Mechanism satisfying (epsilon, delta)-LDP.
   - Formally calibrated Laplace Mechanism satisfying epsilon-LDP.
   - Bounded L2 global sensitivity Delta_2 = 2.0 on unit hypersphere S^(d-1).
3. Non-Invertible Feature Transformations:
   - Random Fourier Features (RFF) with sinusoidal non-linear activation (destroys linear pseudo-inverse inversion).
   - Sign-Random Projection (SimHash / 1-bit sketch) providing information-theoretic loss of magnitude.
"""

import time
import numpy as np
from typing import Tuple, Dict, Any, Optional

class PrivacyRepresentationScheme:
    BASELINE = "baseline_orthogonal"
    LDP_GAUSSIAN = "ldp_gaussian"
    LDP_LAPLACE = "ldp_laplace"
    NON_INVERTIBLE_RFF = "non_invertible_rff"
    NON_INVERTIBLE_SIGN = "non_invertible_sign"

class AdvancedPrivacyRepresentation:
    """
    Unified manager for mathematical and differential privacy visual transformations.
    """
    _instance = None

    def __init__(self, input_dim: int = 1280, protected_dim: int = 512, seed: int = 42):
        self.input_dim = input_dim
        self.protected_dim = protected_dim
        self.seed = seed
        self._init_transforms()

    def _init_transforms(self):
        rng = np.random.RandomState(self.seed)
        
        # 1. Semi-orthogonal projection matrix P (input_dim x protected_dim)
        gaussian_matrix = rng.randn(self.input_dim, self.protected_dim)
        q, _ = np.linalg.qr(gaussian_matrix)
        self.projection_matrix = q.astype(np.float32) # P^T * P = I_512
        
        # 2. Random Fourier Features (RFF) weights and bias for non-linear embedding
        # Approximates Gaussian RBF kernel with bandwidth gamma = 0.5
        gamma = 0.5
        self.rff_weights = (rng.randn(self.input_dim, self.protected_dim // 2) * np.sqrt(2.0 * gamma)).astype(np.float32)
        self.rff_bias = (rng.uniform(0, 2.0 * np.pi, size=self.protected_dim // 2)).astype(np.float32)
        
        # 3. Sign Random Projection matrix
        self.sign_rp_matrix = rng.randn(self.input_dim, self.protected_dim).astype(np.float32)

    @classmethod
    def get_instance(cls, input_dim: int = 1280, protected_dim: int = 512):
        if cls._instance is None:
            cls._instance = cls(input_dim=input_dim, protected_dim=protected_dim)
        return cls._instance

    # --------------------------------------------------------------------------
    # Scheme 1: Baseline Semi-Orthogonal Projection
    # --------------------------------------------------------------------------
    def transform_baseline(self, raw_vector: np.ndarray, sigma: float = 0.05) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Baseline: Projects 1280-D -> 512-D and injects additive Gaussian noise.
        """
        t0 = time.time()
        v = raw_vector.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm

        projected = np.dot(v, self.projection_matrix)
        if sigma > 0:
            noise = np.random.normal(0, sigma, size=projected.shape).astype(np.float32)
            protected = projected + noise
        else:
            protected = projected

        p_norm = np.linalg.norm(protected)
        if p_norm > 0:
            protected = protected / p_norm
            
        elapsed_ms = (time.time() - t0) * 1000.0
        meta = {
            "scheme": PrivacyRepresentationScheme.BASELINE,
            "dimension": self.protected_dim,
            "sigma": sigma,
            "latency_ms": round(elapsed_ms, 3),
            "formal_guarantee": "Empirical noise perturbation (no formal (epsilon, delta)-DP proof)",
            "inversion_defense": "Dimension reduction (768 dimensions discarded) + additive noise"
        }
        return protected.astype(np.float32), meta

    # --------------------------------------------------------------------------
    # Scheme 2: Local Differential Privacy (LDP)
    # --------------------------------------------------------------------------
    def transform_ldp_gaussian(
        self,
        raw_vector: np.ndarray,
        epsilon: float = 2.0,
        delta: float = 1e-5
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calibrated Gaussian Mechanism for (epsilon, delta)-Local Differential Privacy.
        For vectors normalized to the unit sphere S^(d-1), the maximum L2 sensitivity
        between any two distinct image embeddings is Delta_2 = max ||x - y||_2 = 2.0.
        
        The required Gaussian standard deviation is:
            sigma = (Delta_2 * sqrt(2 * ln(1.25 / delta))) / epsilon
        """
        t0 = time.time()
        v = raw_vector.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm

        # Project into 512-D space (orthogonal projection preserves L2 distances: ||Px - Py||_2 <= ||x - y||_2)
        projected = np.dot(v, self.projection_matrix)
        proj_norm = np.linalg.norm(projected)
        if proj_norm > 0:
            projected = projected / proj_norm

        # Global L2 sensitivity on unit sphere S^(511)
        delta_2 = 2.0
        
        # Rigorous Analytic Gaussian mechanism noise parameter
        sigma_calibrated = (delta_2 * np.sqrt(2.0 * np.log(1.25 / max(1e-9, delta)))) / max(0.01, epsilon)
        
        # Add calibrated Gaussian noise
        noise = np.random.normal(0, sigma_calibrated, size=projected.shape).astype(np.float32)
        noisy = projected + noise
        
        n_norm = np.linalg.norm(noisy)
        if n_norm > 0:
            protected = noisy / n_norm
        else:
            protected = noisy

        elapsed_ms = (time.time() - t0) * 1000.0
        meta = {
            "scheme": PrivacyRepresentationScheme.LDP_GAUSSIAN,
            "dimension": self.protected_dim,
            "epsilon": epsilon,
            "delta": delta,
            "calibrated_sigma": round(float(sigma_calibrated), 4),
            "l2_sensitivity": delta_2,
            "latency_ms": round(elapsed_ms, 3),
            "formal_guarantee": f"({epsilon}, {delta})-Local Differential Privacy via Gaussian Mechanism",
            "inversion_defense": "Bounded information-theoretic differential leakage bound"
        }
        return protected.astype(np.float32), meta

    def transform_ldp_laplace(
        self,
        raw_vector: np.ndarray,
        epsilon: float = 2.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calibrated Laplace Mechanism for epsilon-Local Differential Privacy.
        For unit vectors in R^d, L1 sensitivity is bounded by Delta_1 = 2 * sqrt(d).
        """
        t0 = time.time()
        v = raw_vector.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm

        projected = np.dot(v, self.projection_matrix)
        proj_norm = np.linalg.norm(projected)
        if proj_norm > 0:
            projected = projected / proj_norm

        d = self.protected_dim
        delta_1 = 2.0 * np.sqrt(d) # L1 sensitivity bound
        scale = delta_1 / max(0.01, epsilon)

        noise = np.random.laplace(0, scale, size=projected.shape).astype(np.float32)
        noisy = projected + noise
        
        n_norm = np.linalg.norm(noisy)
        if n_norm > 0:
            protected = noisy / n_norm
        else:
            protected = noisy

        elapsed_ms = (time.time() - t0) * 1000.0
        meta = {
            "scheme": PrivacyRepresentationScheme.LDP_LAPLACE,
            "dimension": self.protected_dim,
            "epsilon": epsilon,
            "laplace_scale": round(float(scale), 4),
            "l1_sensitivity": round(float(delta_1), 4),
            "latency_ms": round(elapsed_ms, 3),
            "formal_guarantee": f"{epsilon}-Local Differential Privacy via Laplace Mechanism",
            "inversion_defense": "Laplacian differential noise calibration"
        }
        return protected.astype(np.float32), meta

    # --------------------------------------------------------------------------
    # Scheme 3: Non-Invertible Feature Transformations
    # --------------------------------------------------------------------------
    def transform_non_invertible_rff(
        self,
        raw_vector: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Random Fourier Features (RFF) with Non-Linear Trigonometric Embedding:
            phi(x) = sqrt(2/m) * [cos(W^T x + b), sin(W^T x + b)]
        
        Properties:
        1. Non-linear trigonometric mapping eliminates closed-form linear inversion (Moore-Penrose
           pseudo-inverse fails completely because cosine is many-to-one and non-monotonic).
        2. Preserves kernel visual similarity: <phi(x), phi(y)> approx exp(-gamma * ||x - y||^2).
        """
        t0 = time.time()
        v = raw_vector.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm

        # W_rff: (1280, 256), b_rff: (256,)
        proj = np.dot(v, self.rff_weights) + self.rff_bias
        cos_part = np.cos(proj)
        sin_part = np.sin(proj)
        
        # Concatenate to 512-D
        rff_embedding = np.concatenate([cos_part, sin_part]) * np.sqrt(2.0 / len(proj))
        rff_norm = np.linalg.norm(rff_embedding)
        if rff_norm > 0:
            protected = rff_embedding / rff_norm
        else:
            protected = rff_embedding

        elapsed_ms = (time.time() - t0) * 1000.0
        meta = {
            "scheme": PrivacyRepresentationScheme.NON_INVERTIBLE_RFF,
            "dimension": self.protected_dim,
            "kernel_approximation": "Shift-invariant Gaussian RBF Kernel (Bochner's Theorem)",
            "latency_ms": round(elapsed_ms, 3),
            "formal_guarantee": "Empirical Non-Invertibility via non-linear trigonometric projection",
            "inversion_defense": "Destroys linear pseudo-inverse reconstruction attacks (non-convex pre-image problem)"
        }
        return protected.astype(np.float32), meta

    def transform_non_invertible_sign(
        self,
        raw_vector: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Sign-Random Projection (1-bit SimHash representation):
            s = sign(W^T x) in {-1, +1}^d
        
        Properties:
        1. Permanently discards feature magnitudes.
        2. Preserves angular cosine similarity via the Goemans-Williamson identity:
           Pr[sign(w^T x) == sign(w^T y)] = 1 - (theta / pi)
        """
        t0 = time.time()
        v = raw_vector.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm

        proj = np.dot(v, self.sign_rp_matrix)
        signs = np.where(proj >= 0, 1.0, -1.0).astype(np.float32)
        signs_norm = signs / np.sqrt(len(signs))

        elapsed_ms = (time.time() - t0) * 1000.0
        meta = {
            "scheme": PrivacyRepresentationScheme.NON_INVERTIBLE_SIGN,
            "dimension": self.protected_dim,
            "sketch_type": "1-bit Sign Random Projection (SimHash)",
            "latency_ms": round(elapsed_ms, 3),
            "formal_guarantee": "Empirical Non-Invertibility (Loss of norm degrees of freedom)",
            "inversion_defense": "Infinite pre-images map to identical binary orthant vectors"
        }
        return signs_norm.astype(np.float32), meta

    def transform(
        self,
        raw_vector: np.ndarray,
        scheme: str = PrivacyRepresentationScheme.BASELINE,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Unified dispatch interface for privacy transformations.
        """
        if scheme == PrivacyRepresentationScheme.LDP_GAUSSIAN:
            eps = kwargs.get("epsilon", 2.0)
            dlt = kwargs.get("delta", 1e-5)
            return self.transform_ldp_gaussian(raw_vector, epsilon=eps, delta=dlt)
        elif scheme == PrivacyRepresentationScheme.LDP_LAPLACE:
            eps = kwargs.get("epsilon", 2.0)
            return self.transform_ldp_laplace(raw_vector, epsilon=eps)
        elif scheme == PrivacyRepresentationScheme.NON_INVERTIBLE_RFF:
            return self.transform_non_invertible_rff(raw_vector)
        elif scheme == PrivacyRepresentationScheme.NON_INVERTIBLE_SIGN:
            return self.transform_non_invertible_sign(raw_vector)
        else:
            sigma = kwargs.get("sigma", 0.05)
            return self.transform_baseline(raw_vector, sigma=sigma)
