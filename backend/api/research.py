"""
SecureImage Research Platform API.

Exposes REST endpoints for:
1. Module A: Dimensionality Reduction & Retrieval Ablation (512, 384, 256, 128, 64-D)
2. Module B: Optimization-Based Image Reconstruction Attacks (Attacker A vs Attacker B)
3. Module C: Privacy Transformation Comparative Analysis & Pareto Frontier
"""

import os
import io
import time
import numpy as np
from typing import Dict, Any, List, Optional
from PIL import Image
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form

import backend.database.db as db
from backend.api.auth import get_current_user, generate_signed_token
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from research.retrieval_ablation.experiment_runner import AblationExperimentRunner
from research.reconstruction.inversion_attack import ImageInversionAttacker
from research.privacy_analysis.threat_models import ThreatModelRegistry
from research.privacy_analysis.privacy_comparison import PrivacyTransformationComparator

router = APIRouter(prefix="/api/research", tags=["research"])

RECON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "assets", "reconstructions"))


class QueryCompareRequest(BaseModel):
    image_id: Optional[str] = None
    protected_vector: Optional[List[float]] = None
    technique: str = "truncation" # 'truncation', 'random', 'pca'
    top_k: int = 5



class IdentificationAttackRequest(BaseModel):
    query_vector: List[float]
    sigma: float = 0.05

class InversionRunRequest(BaseModel):
    image_id: Optional[str] = None
    target_dim: int = 512
    threat_model: str = "known_key" # 'known_key' or 'restricted_key'
    iterations: int = 25


# ==============================================================================
# MODULE A: RETRIEVAL ABLATION ENDPOINTS
# ==============================================================================
@router.get("/ablation/benchmark")
def get_ablation_benchmark(
    force_rerun: bool = Query(False),
    num_queries: int = Query(40),
    num_random_trials: int = Query(10),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Returns the complete multi-dimensionality benchmark across Truncation,
    Random Dimension Selection (10 trials with mean/std), and PCA.
    """
    runner = AblationExperimentRunner.get_instance()
    try:
        data = runner.run_full_study(
            num_queries=num_queries,
            num_random_trials=num_random_trials,
            force_rerun=force_rerun
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation study error: {str(e)}")


@router.post("/ablation/query-compare")
def compare_query_across_dimensions(
    req: QueryCompareRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Executes a multi-dimensional retrieval query across 512, 384, 256, 128, 64-D
    for a chosen query image, returning Top-K matches per dimension for visual inspection.
    """
    runner = AblationExperimentRunner.get_instance()
    user_token = generate_signed_token(current_user["user_id"]) if current_user else ""

    # Resolve query vector
    if req.protected_vector and len(req.protected_vector) == 512:
        q_vec = np.array(req.protected_vector, dtype=np.float32)
    elif req.image_id:
        img_rec = db.get_image(req.image_id)
        if not img_rec:
            raise HTTPException(status_code=404, detail=f"Image ID {req.image_id} not found in database.")
        
        # Look up vector in FAISS id_map
        retriever = runner.evaluator.retriever
        rev_map = {v: k for k, v in retriever.id_map.items()}
        row_id = rev_map.get(req.image_id)
        if row_id is None:
            raise HTTPException(status_code=404, detail=f"Vector for {req.image_id} not indexed in FAISS.")
        q_vec = retriever.index.reconstruct(row_id)
    else:
        # Default to first gallery item for demo
        gallery_vecs, _ = runner.evaluator.get_full_gallery_embeddings()
        q_vec = gallery_vecs[0]

    try:
        res = runner.compare_query_across_dimensions(
            query_512=q_vec,
            technique=req.technique,
            top_k=req.top_k,
            user_token=user_token
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query comparison failed: {str(e)}")


# ==============================================================================
# MODULE B: IMAGE RECONSTRUCTION ATTACK ENDPOINTS
# ==============================================================================
@router.post("/reconstruction/run")
async def run_reconstruction_attack(
    file: Optional[UploadFile] = File(None),
    image_id: Optional[str] = Form(None),
    target_dim: int = Form(512),
    threat_model: str = Form("known_key"),
    iterations: int = Form(25),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Runs an optimization-based gradient inversion attack on candidate image pixels.
    """
    attacker = ImageInversionAttacker.get_instance()

    # Load target image
    if file:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
    elif image_id:
        from backend.services.storage.vault import PrivateImageVault
        vault = PrivateImageVault.get_instance()
        img_bytes = vault.get_decrypted_image(image_id)
        if not img_bytes:
            raise HTTPException(status_code=404, detail=f"Could not load image bytes for {image_id}")
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    else:
        # Fallback to test image from test_dataset
        test_path = "test_dataset/01_Medical/test_medical_xray_05.jpg"
        if os.path.exists(test_path):
            pil_img = Image.open(test_path).convert("RGB")
        else:
            raise HTTPException(status_code=400, detail="Please upload an image or provide a valid image_id.")

    try:
        result = attacker.run_inversion(
            target_image=pil_img,
            target_dim=target_dim,
            threat_model=threat_model,
            iterations=iterations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inversion attack failed: {str(e)}")


@router.post("/reconstruction/sweep")
async def run_reconstruction_sweep(
    image_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    threat_model: str = Form("known_key"),
    iterations: int = Form(20),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Runs a multi-dimensional reconstruction sweep across:
    Original | 100% (512-D) | 75% (384-D) | 50% (256-D) | 25% (128-D) | 12.5% (64-D)
    """
    attacker = ImageInversionAttacker.get_instance()

    if file:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
    elif image_id:
        from backend.services.storage.vault import PrivateImageVault
        vault = PrivateImageVault.get_instance()
        img_bytes = vault.get_decrypted_image(image_id)
        if not img_bytes:
            raise HTTPException(status_code=404, detail=f"Could not load image bytes for {image_id}")
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    else:
        test_path = "test_dataset/01_Medical/test_medical_xray_05.jpg"
        if os.path.exists(test_path):
            pil_img = Image.open(test_path).convert("RGB")
        else:
            raise HTTPException(status_code=400, detail="Please upload an image or provide a valid image_id.")

    try:
        sweep_data = attacker.run_multi_dimension_sweep(
            target_image=pil_img,
            threat_model=threat_model,
            iterations=iterations
        )
        return sweep_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconstruction sweep failed: {str(e)}")


@router.get("/reconstruction/history")
def get_reconstruction_history(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Returns list of recently saved reconstruction artifacts on disk."""
    if not os.path.exists(RECON_DIR):
        return {"artifacts": []}

    files = [f for f in os.listdir(RECON_DIR) if f.endswith(".png")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(RECON_DIR, x)), reverse=True)

    artifacts = []
    for f in files[:12]:
        path = os.path.join(RECON_DIR, f)
        artifacts.append({
            "filename": f,
            "url": f"/static/assets/reconstructions/{f}",
            "size_bytes": os.path.getsize(path),
            "modified_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
        })
    return {"artifacts": artifacts}


# ==============================================================================
# MODULE C: PRIVACY TRANSFORMATION ANALYSIS ENDPOINTS
# ==============================================================================
@router.get("/privacy/comparison")
def get_privacy_comparison(
    force_rerun: bool = Query(False),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Returns the 6-stage privacy transformation comparative analysis and Pareto frontier.
    """
    comparator = PrivacyTransformationComparator.get_instance()
    try:
        return comparator.run_comparison(force_rerun=force_rerun)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Privacy comparison failed: {str(e)}")


@router.get("/threat-models")
def get_threat_models():
    """Returns formal specifications of attacker threat models and defenses."""
    return {"threat_models": ThreatModelRegistry.get_all_threat_models()}


# ==============================================================================
# MODULE D: NOISE EVALUATION & PRIVACY-UTILITY BENCHMARK ENDPOINTS
# ==============================================================================
@router.get("/noise/benchmark")
def get_noise_benchmark(
    force_rerun: bool = Query(False),
    num_queries: int = Query(40),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Returns the complete 6-level noise vs retrieval accuracy and identity leakage benchmark.
    """
    from research.noise_analysis.noise_evaluation import NoiseEvaluator
    evaluator = NoiseEvaluator.get_instance()
    try:
        data = evaluator.run_noise_benchmark(num_queries=num_queries, force_rerun=force_rerun)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Noise benchmark error: {str(e)}")


@router.post("/identification/attack")
def run_identification_attack(
    req: IdentificationAttackRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Executes an on-demand nearest neighbor identification attack against the gallery.
    Simulates Scenario 2: Attacker intercepts vector and searches reference DB to deanonymize query.
    """
    from research.noise_analysis.noise_evaluation import NoiseEvaluator
    evaluator = NoiseEvaluator.get_instance()
    try:
        vec = np.array(req.query_vector, dtype=np.float32)
        res = evaluator.run_identification_attack_on_query(vec, sigma=req.sigma)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Identification attack error: {str(e)}")


@router.get("/export/csv", response_class=PlainTextResponse)
def export_research_csv(
    study_type: str = Query("combined"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Generates and downloads CSV benchmark data for academic paper reporting.
    """
    output_lines = []
    
    if study_type in ["noise", "combined"]:
        from research.noise_analysis.noise_evaluation import NoiseEvaluator
        data = NoiseEvaluator.get_instance().run_noise_benchmark()
        output_lines.append("# --- NOISE-BASED VECTOR PRIVACY BENCHMARK ---")
        output_lines.append("Level,Noise_Sigma,Precision@5,Precision@10,Recall@5,Recall@10,mAP@5,mAP@10,Top1_ID_Acc_Pct,Top5_ID_Acc_Pct,Identity_Protection_Pct,Expected_SSIM,Expected_PSNR_dB,Mean_Latency_ms")
        for r in data.get("results", []):
            rm = r["retrieval_metrics"]
            ia = r["identification_attack"]
            rr = r["reconstruction_resistance"]
            lat = r["latency_breakdown"]
            output_lines.append(f"{r['name']},{r['sigma']},{rm['precision_at_5']},{rm['precision_at_10']},{rm['recall_at_5']},{rm['recall_at_10']},{rm['map_at_5']},{rm['map_at_10']},{ia['top_1_accuracy_percent']},{ia['top_5_accuracy_percent']},{ia['identity_protection_percent']},{rr['ssim']},{rr['psnr_db']},{lat['total_ms']}")
        output_lines.append("")

    if study_type in ["ablation", "combined"]:
        runner = AblationExperimentRunner.get_instance()
        data = runner.run_full_study()
        output_lines.append("# --- DIMENSIONALITY REDUCTION ABLATION BENCHMARK ---")
        output_lines.append("Technique,Dimension,Retained_Percent,Precision@5,Precision@10,Recall@5,Recall@10,mAP@5,mAP@10,Avg_Latency_ms,Bytes_Per_Vector")
        for tech_key, tech_results in data.get("results_by_technique", {}).items():
            for r in tech_results:
                dim = r.get("dimension")
                ret = r.get("retained_percent")
                tech = r.get("technique")
                p5 = r.get("precision_at_5")
                p10 = r.get("precision_at_10")
                r5 = r.get("recall_at_5")
                r10 = r.get("recall_at_10")
                m5 = r.get("map_at_5")
                m10 = r.get("map_at_10")
                lat = r.get("avg_latency_ms")
                bytes_vec = r.get("storage", {}).get("bytes_per_vector", dim * 4 if dim else 0)
                output_lines.append(f"{tech},{dim},{ret}%,{p5},{p10},{r5},{r10},{m5},{m10},{lat},{bytes_vec}")

    return "\n".join(output_lines)
