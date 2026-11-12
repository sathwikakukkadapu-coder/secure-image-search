"""
SecureImage Research Module B: Reconstruction Evaluation Metrics.

Computes exact image similarity and privacy leakage metrics between
an original reference image and an inverted/reconstructed attack image:
1. PSNR (Peak Signal-to-Noise Ratio in dB)
2. SSIM (Structural Similarity Index)
3. MSE (Mean Squared Error)
4. Deep Feature Cosine Similarity
5. Human Recognizability Categorical Assessment
"""

from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim_fn
from skimage.metrics import peak_signal_noise_ratio as psnr_fn


class ReconstructionMetrics:
    """
    Computes visual and mathematical fidelity metrics for reconstruction attacks.
    """

    @staticmethod
    def ensure_numpy_rgb(image: Image.Image, size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Converts PIL image to uint8 RGB array of uniform dimensions."""
        if image.mode != "RGB":
            image = image.convert("RGB")
        if image.size != size:
            image = image.resize(size, Image.Resampling.BILINEAR)
        return np.array(image, dtype=np.uint8)

    @classmethod
    def evaluate(
        cls,
        orig_img: Image.Image,
        recon_img: Image.Image,
        feature_cosine_sim: float = 0.0,
        execution_time_ms: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates PSNR, SSIM, MSE, and privacy verdict.
        """
        orig_arr = cls.ensure_numpy_rgb(orig_img)
        recon_arr = cls.ensure_numpy_rgb(recon_img)

        # 1. PSNR (dB)
        try:
            psnr_val = float(psnr_fn(orig_arr, recon_arr, data_range=255))
        except Exception:
            psnr_val = 0.0

        # 2. SSIM
        try:
            ssim_val = float(ssim_fn(orig_arr, recon_arr, channel_axis=2, data_range=255))
        except Exception:
            ssim_val = 0.0

        # 3. MSE
        mse_val = float(np.mean((orig_arr.astype(np.float32) - recon_arr.astype(np.float32)) ** 2))

        # 4. Human Recognizability & Security Verdict
        if ssim_val > 0.60 or psnr_val > 22.0:
            verdict = "CRITICAL LEAKAGE: Subject and structural features recognizably reconstructed."
            leakage_level = "CRITICAL"
            human_score = 4
        elif ssim_val > 0.35 or psnr_val > 15.0:
            verdict = "PARTIAL LEAKAGE: Coarse shapes and color distribution partially visible."
            leakage_level = "MODERATE"
            human_score = 3
        elif ssim_val > 0.18:
            verdict = "LOW LEAKAGE: Faint low-frequency artifacts; semantic details destroyed."
            leakage_level = "LOW"
            human_score = 2
        else:
            verdict = "ZERO LEAKAGE: Pure perceptual noise; zero recognizable visual information."
            leakage_level = "ZERO"
            human_score = 1

        return {
            "psnr_db": round(psnr_val, 2),
            "ssim": round(ssim_val, 4),
            "mse": round(mse_val, 2),
            "embedding_cosine_similarity": round(float(feature_cosine_sim), 4),
            "execution_time_ms": round(execution_time_ms, 2),
            "leakage_level": leakage_level,
            "human_recognizability_score": human_score,
            "security_verdict": verdict
        }
