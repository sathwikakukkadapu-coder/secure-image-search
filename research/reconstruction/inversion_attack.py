"""
SecureImage Research Module B: Optimization-Based Image Inversion Attack.

Implements differentiable gradient-based pre-image reconstruction attacks
targeting visual embeddings (512-D down to 64-D):
1. Attacker A (Restricted-Key Attacker): Does not possess the 256-bit secret key;
   attempts inversion using surrogate orthogonal basis / pseudo-inverse.
2. Attacker B (Known-Key Attacker): Possesses the secret projection key;
   inverts directly through the true projection subspace.
3. Multi-Dimensional Ablation: Compares reconstruction fidelity across
   100% (512-D), 75% (384-D), 50% (256-D), 25% (128-D), and 12.5% (64-D).

Uses PyTorch autograd through the existing MobileNetV3 backbone and projection matrix.
Saves actual reconstructed image files and generates side-by-side previews.
"""

import os
import time
import io
import base64
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from research.reconstruction.reconstruction_metrics import ReconstructionMetrics

RECON_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "assets", "reconstructions"))


def pil_to_base64_data_uri(img: Image.Image) -> str:
    """Encodes PIL Image to Base64 PNG data URI for immediate frontend rendering."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


class ImageInversionAttacker:
    """
    Executes optimization-based pre-image reconstruction attacks on visual embeddings.
    """
    _instance = None

    def __init__(self):
        self.extractor = FeatureExtractor.get_instance()
        self.keyed_mgr = KeyedProjectionManager.get_instance()
        os.makedirs(RECON_OUTPUT_DIR, exist_ok=True)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run_inversion(
        self,
        target_image: Image.Image,
        target_dim: int = 512,
        threat_model: str = "known_key",
        iterations: int = 30,
        apply_noise_to_target: bool = False,
        noise_sigma: float = 0.05
    ) -> Dict[str, Any]:
        """
        Executes a single optimization-based reconstruction attack.
        - threat_model: 'known_key' (Attacker B) or 'restricted_key' (Attacker A)
        - target_dim: Dimensionality retained [512, 384, 256, 128, 64]
        """
        t0 = time.time()
        threat_clean = threat_model.lower().strip()

        # 1. Resize original image to standard 224x224
        orig_224 = target_image.convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)

        # 2. Extract true raw 1280-D features from target image
        raw_feat, _, _ = self.extractor.extract_features(orig_224)
        raw_tensor = torch.tensor(raw_feat, dtype=torch.float32).unsqueeze(0)

        # 3. Compute true 512-D keyed protected representation
        true_proj_matrix = self.keyed_mgr.projection_matrix # 1280 x 512
        true_512 = np.dot(raw_feat, true_proj_matrix)
        if apply_noise_to_target and noise_sigma > 0:
            rng_noise = np.random.RandomState(42)
            noise = rng_noise.normal(0, noise_sigma, size=true_512.shape).astype(np.float32)
            true_512 = true_512 + noise
        
        # Unit normalization
        norm_512 = np.linalg.norm(true_512)
        true_512 = (true_512 / norm_512) if norm_512 > 0 else true_512

        # 4. Truncate to target_dim for partial dimensionality evaluation
        target_embedding_np = true_512[:target_dim]
        norm_dim = np.linalg.norm(target_embedding_np)
        target_embedding_np = (target_embedding_np / norm_dim) if norm_dim > 0 else target_embedding_np
        target_tensor = torch.tensor(target_embedding_np, dtype=torch.float32)

        # 5. Formulate Attacker's projection operator
        if threat_clean == "restricted_key":
            # Attacker A: Doesn't have secret key. Uses surrogate orthogonal basis.
            rng = np.random.RandomState(999)
            surrogate_mat = rng.randn(1280, target_dim).astype(np.float32)
            surrogate_mat, _ = np.linalg.qr(surrogate_mat)
            attacker_proj_matrix = torch.tensor(surrogate_mat, dtype=torch.float32)
            attacker_description = "Attacker A: Restricted Key (Surrogate Orthogonal Projection)"
        else: # known_key default (Attacker B)
            # Attacker B: Possesses secret key. Slices first target_dim columns of true matrix.
            sub_matrix = true_proj_matrix[:, :target_dim].astype(np.float32)
            attacker_proj_matrix = torch.tensor(sub_matrix, dtype=torch.float32)
            attacker_description = "Attacker B: Known Key (True Orthonormal Secret Subspace)"

        # 6. Initialize candidate image with smooth gray noise
        rng_init = np.random.RandomState(42)
        init_canvas = rng_init.normal(0.48, 0.05, (1, 3, 224, 224)).astype(np.float32)
        init_canvas = np.clip(init_canvas, 0.0, 1.0)

        param_img = nn.Parameter(torch.tensor(init_canvas, requires_grad=True))
        optimizer = optim.Adam([param_img], lr=0.08)

        norm_mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        norm_std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

        model = self.extractor.model
        model.eval()

        loss_history = []

        # 7. Optimization Loop
        for it in range(iterations):
            optimizer.zero_grad()
            clamped = torch.sigmoid(param_img * 3.0)
            norm_in = (clamped - norm_mean) / norm_std

            out = model(norm_in).squeeze()
            out_norm = torch.norm(out)
            pred_raw = out / out_norm if out_norm > 0 else out

            # Project through attacker's projection matrix
            projected = torch.matmul(pred_raw, attacker_proj_matrix)
            p_norm = torch.norm(projected)
            pred_comp = projected / p_norm if p_norm > 0 else projected

            # Embedding cosine loss
            cos_sim = torch.dot(pred_comp, target_tensor)
            cos_loss = 1.0 - cos_sim

            # Total variation regularizer
            diff_h = clamped[:, :, 1:, :] - clamped[:, :, :-1, :]
            diff_w = clamped[:, :, :, 1:] - clamped[:, :, :, :-1]
            tv_loss = torch.mean(torch.abs(diff_h)) + torch.mean(torch.abs(diff_w))

            total_loss = cos_loss + 0.0005 * tv_loss
            total_loss.backward()
            optimizer.step()

            if it % 5 == 0 or it == iterations - 1:
                loss_history.append({
                    "iteration": it + 1,
                    "total_loss": round(float(total_loss.item()), 4),
                    "cosine_similarity": round(float(cos_sim.item()), 4)
                })

        # 8. Render final reconstructed image
        with torch.no_grad():
            final_clamped = torch.sigmoid(param_img * 3.0).squeeze().cpu().numpy()
            final_clamped = np.transpose(final_clamped, (1, 2, 0)) # H, W, C
            final_clamped = np.clip(final_clamped * 255.0, 0.0, 255.0).astype(np.uint8)
            recon_img = Image.fromarray(final_clamped)

        elapsed_ms = (time.time() - t0) * 1000.0

        # 9. Evaluate visual & security metrics
        final_cos_sim = float(loss_history[-1]["cosine_similarity"]) if loss_history else 0.0
        metrics = ReconstructionMetrics.evaluate(
            orig_img=orig_224,
            recon_img=recon_img,
            feature_cosine_sim=final_cos_sim,
            execution_time_ms=elapsed_ms
        )

        # 10. Persist reconstructed image artifact
        timestamp = int(time.time())
        filename = f"recon_{timestamp}_{target_dim}d_{threat_clean}.png"
        filepath = os.path.join(RECON_OUTPUT_DIR, filename)
        recon_img.save(filepath, format="PNG")

        return {
            "status": "success",
            "threat_model": threat_clean,
            "threat_model_description": attacker_description,
            "dimension": target_dim,
            "retained_percent": round((target_dim / 512.0) * 100.0, 1),
            "iterations": iterations,
            "metrics": metrics,
            "loss_history": loss_history,
            "artifacts": {
                "filename": filename,
                "file_url": f"/static/assets/reconstructions/{filename}",
                "original_data_uri": pil_to_base64_data_uri(orig_224),
                "reconstructed_data_uri": pil_to_base64_data_uri(recon_img)
            }
        }

    def run_multi_dimension_sweep(
        self,
        target_image: Image.Image,
        threat_model: str = "known_key",
        iterations: int = 25
    ) -> Dict[str, Any]:
        """
        Executes reconstruction attacks across all 5 standard dimensions:
        100% (512-D), 75% (384-D), 50% (256-D), 25% (128-D), 12.5% (64-D).
        Returns a side-by-side comparative dictionary.
        """
        dimensions = [512, 384, 256, 128, 64]
        results_by_dim = {}

        orig_224 = target_image.convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)
        orig_uri = pil_to_base64_data_uri(orig_224)

        for d in dimensions:
            res = self.run_inversion(
                target_image=orig_224,
                target_dim=d,
                threat_model=threat_model,
                iterations=iterations
            )
            results_by_dim[str(d)] = {
                "dimension": d,
                "retained_percent": round((d / 512.0) * 100.0, 1),
                "psnr_db": res["metrics"]["psnr_db"],
                "ssim": res["metrics"]["ssim"],
                "leakage_level": res["metrics"]["leakage_level"],
                "security_verdict": res["metrics"]["security_verdict"],
                "reconstructed_image_uri": res["artifacts"]["reconstructed_data_uri"],
                "reconstructed_file_url": res["artifacts"]["file_url"]
            }

        return {
            "status": "success",
            "threat_model": threat_model,
            "original_image_uri": orig_uri,
            "comparisons": results_by_dim,
            "sweep_dimensions": dimensions
        }
