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
import json
import numpy as np
from typing import Dict, Any, List, Optional
from PIL import Image
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, Response
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
    sigma: float = 0.0

class AblationRunRequest(BaseModel):
    domain: str = "all"
    sigma: float = 0.05
    include_1280: bool = True
    force_rerun: bool = True



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
    domain: str = Query("all"),
    sigma: float = Query(0.05),
    force_rerun: bool = Query(False),
    include_1280: bool = Query(True),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Returns the real multi-dimensionality ablation benchmark across actual dataset images.
    Provides separate results for:
      - Experiment A: Clean Dimensionality Reduction (Zero Noise)
      - Experiment B: Calibrated Differential Noise Injection (sigma)
    """
    if hasattr(sigma, 'default'):
        sigma = sigma.default
    sigma = float(sigma)
    if hasattr(domain, 'default'):
        domain = domain.default
    if hasattr(force_rerun, 'default'):
        force_rerun = force_rerun.default
    if hasattr(include_1280, 'default'):
        include_1280 = include_1280.default

    runner = AblationExperimentRunner.get_instance()
    try:
        data = runner.run_ablation_study(
            domain=domain,
            sigma=sigma,
            include_1280=include_1280,
            force_rerun=force_rerun
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation study error: {str(e)}")


@router.post("/ablation/run")
def run_ablation_experiment(
    req: AblationRunRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Executes a fresh, reproducible dimensionality ablation experiment on the real dataset.
    """
    runner = AblationExperimentRunner.get_instance()
    try:
        data = runner.run_ablation_study(
            domain=req.domain,
            sigma=req.sigma,
            include_1280=req.include_1280,
            force_rerun=req.force_rerun
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation execution error: {str(e)}")


@router.get("/ablation/export")
def export_ablation_results(
    format: str = Query("csv"), # 'csv' or 'json'
    domain: str = Query("all"),
    sigma: float = Query(0.05),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Exports scientifically reproducible dimensionality ablation experiment records
    as academic CSV or JSON reports.
    """
    if hasattr(sigma, 'default'):
        sigma = sigma.default
    sigma = float(sigma)
    if hasattr(domain, 'default'):
        domain = domain.default
    if hasattr(format, 'default'):
        format = format.default

    runner = AblationExperimentRunner.get_instance()
    try:
        data = runner.run_ablation_study(domain=domain, sigma=sigma, force_rerun=False)
        if format.lower() == "json":
            return Response(
                content=json.dumps(data, indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f'attachment; filename="ablation_benchmark_{domain}.json"'}
            )
        else:
            csv_str = runner.export_csv(data)
            return Response(
                content=csv_str,
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="ablation_benchmark_{domain}.csv"'}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")



@router.post("/ablation/query-compare")
def compare_query_across_dimensions(
    req: QueryCompareRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Executes a multi-dimensional retrieval query across 512, 256, 128, 64, 32, 16-D
    for a chosen query image, returning Top-K matches per dimension for visual inspection.
    """
    runner = AblationExperimentRunner.get_instance()
    try:
        res = runner.compare_query_across_dimensions(
            image_id=req.image_id,
            protected_vector=req.protected_vector,
            top_k=req.top_k,
            sigma=req.sigma
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


@router.get("/export/csv")
def export_research_csv(
    study_type: str = Query("combined"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Generates and downloads CSV benchmark data for academic paper reporting.
    Sets Content-Disposition to attachment and uses safe lookups.
    """
    output_lines = []
    
    if study_type in ["noise", "combined"]:
        from research.noise_analysis.noise_evaluation import NoiseEvaluator
        try:
            data = NoiseEvaluator.get_instance().run_noise_benchmark() or {}
        except Exception:
            data = {}
            
        output_lines.append("# --- NOISE-BASED VECTOR PRIVACY BENCHMARK ---")
        output_lines.append("Level,Noise_Sigma,Precision@5,Precision@10,Recall@5,Recall@10,mAP@5,mAP@10,Top1_ID_Acc_Pct,Top5_ID_Acc_Pct,Identity_Protection_Pct,Expected_SSIM,Expected_PSNR_dB,Mean_Latency_ms")
        for r in (data.get("results") or []):
            name = r.get("name", "Unknown")
            sigma = r.get("sigma", 0.0)
            rm = r.get("retrieval_metrics") or {}
            ia = r.get("identification_attack") or {}
            rr = r.get("reconstruction_resistance") or {}
            lat = r.get("latency_breakdown") or {}
            
            p5 = rm.get("precision_at_5", 0.0)
            p10 = rm.get("precision_at_10", 0.0)
            r5 = rm.get("recall_at_5", 0.0)
            r10 = rm.get("recall_at_10", 0.0)
            m5 = rm.get("map_at_5", 0.0)
            m10 = rm.get("map_at_10", 0.0)
            
            top1_acc = ia.get("top_1_accuracy_percent", "0.0%")
            top5_acc = ia.get("top_5_accuracy_percent", "0.0%")
            id_prot = ia.get("identity_protection_percent", "0.0%")
            
            ssim = rr.get("ssim", 0.0)
            psnr = rr.get("psnr_db", 0.0)
            total_lat = lat.get("total_ms", 0.0)
            output_lines.append(f"{name},{sigma},{p5},{p10},{r5},{r10},{m5},{m10},{top1_acc},{top5_acc},{id_prot},{ssim},{psnr},{total_lat}")
        output_lines.append("")

    if study_type in ["ablation", "combined"]:
        runner = AblationExperimentRunner.get_instance()
        try:
            data = runner.run_full_study() or {}
        except Exception:
            data = {}
            
        output_lines.append("# --- DIMENSIONALITY REDUCTION ABLATION BENCHMARK ---")
        output_lines.append("Technique,Dimension,Retained_Percent,Precision@5,Precision@10,Recall@5,Recall@10,mAP@5,mAP@10,Avg_Latency_ms,Bytes_Per_Vector")
        for tech_key, tech_results in (data.get("results_by_technique") or {}).items():
            for r in (tech_results or []):
                dim = r.get("dimension", 0)
                ret = r.get("retained_percent", 0.0)
                tech = r.get("technique", tech_key)
                p5 = r.get("precision_at_5", 0.0)
                p10 = r.get("precision_at_10", 0.0)
                r5 = r.get("recall_at_5", 0.0)
                r10 = r.get("recall_at_10", 0.0)
                m5 = r.get("map_at_5", 0.0)
                m10 = r.get("map_at_10", 0.0)
                lat = r.get("avg_latency_ms", 0.0)
                storage_dict = r.get("storage") or {}
                bytes_vec = storage_dict.get("bytes_per_vector", dim * 4 if dim else 0)
                output_lines.append(f"{tech},{dim},{ret}%,{p5},{p10},{r5},{r10},{m5},{m10},{lat},{bytes_vec}")

    csv_content = "\n".join(output_lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="research_export.csv"'}
    )
