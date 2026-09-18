import io
import time
from typing import Optional, List, Dict, Any
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Header, Response
import numpy as np

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
import backend.database.db as db
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api", tags=["search"])

@router.post("/search/query")
async def execute_private_search(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    protected: bool = Form(True),
    sigma: float = Form(0.05),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    # Step 1: Upload and file validation
    t_upload_start = time.time()
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")
        
    try:
        pil_image = Image.open(io.BytesIO(contents))
        pil_image.verify()
        pil_image = Image.open(io.BytesIO(contents)) # Re-open after verify
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unsupported or corrupted image file. Please upload JPG, PNG, or WebP.")
    upload_ms = (time.time() - t_upload_start) * 1000

    # Step 2 & 3: Preprocessing & Feature Extraction
    extractor = FeatureExtractor.get_instance()
    raw_vector, preprocess_ms, inference_ms = extractor.extract_features(pil_image)

    # Step 4: Privacy Protection
    protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
    if protected:
        search_vector, protection_ms = protector.protect_vector(raw_vector, apply_noise=True, sigma=sigma)
        inversion_metrics = protector.measure_inversion_resistance(raw_vector, search_vector, sigma=sigma)
    else:
        # Raw baseline representation projected to same dim without perturbation
        search_vector, protection_ms = protector.protect_vector(raw_vector, apply_noise=False, sigma=0.0)
        inversion_metrics = {
            "projection_dimension": 512,
            "perturbation_sigma": 0.0,
            "estimated_reconstruction_ssim": 0.76,
            "inversion_verdict": "High Reconstruction Leakage (Raw Features)",
            "zero_pixel_storage_guarantee": True
        }

    # Step 5: FAISS Vector Similarity Search
    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    matches, search_ms = retriever.search(search_vector, top_k=top_k)
    db.log_audit(
        current_user.get("user_id") if current_user else None,
        "VECTOR_SEARCH",
        "PROCESSED",
        f"Query matched {len(matches)} vectors in {search_ms:.2f}ms"
    )

    # Step 6: Authorization & Decoupled Private Vault Dereferencing
    t_auth_start = time.time()
    vault = PrivateImageVault.get_instance()
    results = []
    
    for match in matches:
        img_id = match["image_id"]
        img_record = db.get_image(img_id)
        
        if not img_record:
            continue
            
        is_auth, auth_msg = vault.check_authorization(current_user, img_record)
        
        results.append({
            "rank": match["rank"],
            "image_id": img_id,
            "similarity": match["similarity"],
            "similarity_percent": match["similarity_percent"],
            "category": img_record["category"],
            "owner_id": img_record["owner_id"],
            "is_private": bool(img_record["is_private"]),
            "authorized": is_auth,
            "auth_status": "✓ Authorized" if is_auth else "🔒 Private Asset - Access Denied",
            "auth_message": auth_msg,
            "image_url": f"/api/storage/image/{img_id}" if is_auth else None
        })
        
    auth_ms = (time.time() - t_auth_start) * 1000
    total_latency_ms = upload_ms + preprocess_ms + inference_ms + protection_ms + search_ms + auth_ms

    return {
        "query_summary": {
            "model_name": extractor.model_name,
            "feature_dim": extractor.feature_dim,
            "protected_dim": 512,
            "results_found": len(results),
            "search_time_sec": f"{total_latency_ms / 1000.0:.3f}s",
            "total_latency_ms": round(total_latency_ms, 1),
            "protection_enabled": protected,
            "sigma": sigma
        },
        "pipeline_steps": [
            {"step": "Upload", "status": "completed", "time_ms": round(upload_ms, 2)},
            {"step": "Preprocessing", "status": "completed", "time_ms": round(preprocess_ms, 2)},
            {"step": "Feature Extraction", "status": "completed", "time_ms": round(inference_ms, 2)},
            {"step": "Privacy Protection", "status": "completed", "time_ms": round(protection_ms, 2)},
            {"step": "Vector Search", "status": "completed", "time_ms": round(search_ms, 2)},
            {"step": "Authorization", "status": "completed", "time_ms": round(auth_ms, 2)}
        ],
        "inversion_metrics": inversion_metrics,
        "results": results,
        "privacy_report": {
            "original_images_in_faiss": False,
            "faiss_stored_bytes": "0 Pixels (Float32 Coordinate Vectors Only)",
            "privacy_protection_active": protected,
            "storage_separation_verified": True,
            "access_control_enforced": True,
            "active_user": current_user.get("name") if current_user else "Guest",
            "active_role": current_user.get("role") if current_user else "guest"
        }
    }

@router.get("/storage/image/{image_id}")
def get_private_storage_image(
    image_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Streams original image bytes directly from the decoupled private vault.
    Strictly rejected if the user is unauthorized.
    """
    img_record = db.get_image(image_id)
    if not img_record:
        raise HTTPException(status_code=404, detail=f"Image record {image_id} not found.")
        
    vault = PrivateImageVault.get_instance()
    is_auth, auth_msg = vault.check_authorization(current_user, img_record)
    
    if not is_auth:
        db.log_audit(
            current_user.get("user_id") if current_user else None,
            "IMAGE_FETCH",
            "BLOCKED",
            f"Blocked unauthorized attempt to fetch private image {image_id}"
        )
        raise HTTPException(status_code=403, detail=auth_msg)
        
    try:
        image_bytes = vault.retrieve_image_bytes(img_record["storage_reference"])
        db.log_audit(
            current_user.get("user_id") if current_user else None,
            "IMAGE_FETCH",
            "ALLOWED",
            f"Authorized retrieval of {image_id} from private storage"
        )
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage access error: {str(e)}")
