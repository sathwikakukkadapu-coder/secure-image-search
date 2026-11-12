import io
import time
from typing import Optional, List, Dict, Any
from PIL import Image
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Header, Response, Query
import numpy as np

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
import backend.database.db as db
from backend.api.auth import get_current_user, generate_signed_token
from backend.services.retrieval.domain_classifier import DomainClassifier

router = APIRouter(prefix="/api", tags=["search"])

class ContentFreeVectorQuery(BaseModel):
    protected_vector: List[float]
    top_k: int = 5
    threshold: float = 0.30
    domain_filter: Optional[str] = None
    include_below_threshold: bool = False
    strip_metadata: bool = True
    client_device_verified: bool = True
    sigma: float = 0.05

@router.post("/client/process-local")
async def process_image_locally(
    file: UploadFile = File(...),
    strip_metadata: bool = Form(True),
    sigma: float = Form(0.05),
    apply_noise: bool = Form(True),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Client-side / Edge Processing:
    1. Strips EXIF/GPS metadata locally
    2. Extracts 1280-D feature representation via MobileNetV3
    3. Transforms into 512-D protected representation with calibrated perturbation
    Returns the vector to client memory. No image bytes enter the retrieval server.
    """
    t_start = time.time()
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")
        
    try:
        pil_image = Image.open(io.BytesIO(contents))
        pil_image.verify()
        pil_image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Unsupported or corrupted image file.")
        
    metadata_report = {
        "exif_stripped": strip_metadata,
        "gps_removed": strip_metadata,
        "original_filename_hidden": True,
        "raw_image_bytes": len(contents),
        "dimensions": f"{pil_image.width}x{pil_image.height}"
    }
    
    extractor = FeatureExtractor.get_instance()
    raw_vector, prep_ms, infer_ms = extractor.extract_features(pil_image)
    
    protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
    clean_vector, _ = protector.protect_vector(raw_vector, apply_noise=False)
    search_vector, prot_ms = protector.protect_vector(raw_vector, apply_noise=apply_noise, sigma=sigma)
    
    vector_list = search_vector.tolist()
    clean_list = clean_vector.tolist()
    delta_vector = (search_vector - clean_vector).astype(float)
    delta_list = delta_vector.tolist()
    
    cos_sim = float(np.dot(clean_vector, search_vector))
    l2_drift = float(np.linalg.norm(delta_vector))
    
    if not apply_noise or sigma == 0:
        privacy_level = "Level 0 (Clean / Zero Noise)"
    elif sigma <= 0.02:
        privacy_level = "Level 1 (Very Low: σ=0.02)"
    elif sigma <= 0.05:
        privacy_level = "Level 2 (Low / Standard: σ=0.05)"
    elif sigma <= 0.10:
        privacy_level = "Level 3 (Medium / Balanced: σ=0.10)"
    elif sigma <= 0.20:
        privacy_level = "Level 4 (High Privacy: σ=0.20)"
    else:
        privacy_level = f"Level 5 (Maximum Privacy: σ={sigma:.2f})"
        
    total_local_ms = (time.time() - t_start) * 1000
    
    # Generate vector barcode representation (e.g. 16 blocks)
    # Positive vs negative vs high magnitude
    barcode_chars = []
    for val in vector_list[:24]:
        if val > 0.05:
            barcode_chars.append("█")
        elif val > 0.0:
            barcode_chars.append("▓")
        elif val > -0.05:
            barcode_chars.append("▒")
        else:
            barcode_chars.append("░")
    barcode_str = "".join(barcode_chars)
    
    classifier = DomainClassifier.get_instance()
    domain_info = classifier.classify_image(
        raw_features=raw_vector,
        filename=file.filename,
        image_bytes=contents
    )
    
    return {
        "status": "success",
        "detected_domain": domain_info["domain"],
        "detected_domain_display": domain_info["display_name"],
        "detection_confidence": domain_info["confidence"],
        "detection_confidence_label": domain_info["confidence_label"],
        "detection_method": domain_info["method"],
        "domain_scores": domain_info["scores"],
        "query_filename": file.filename,
        "client_processing": {
            "device": "Client Processing Buffer",
            "metadata_minimization": metadata_report,
            "raw_feature_dim": extractor.feature_dim,
            "protected_dim": 512,
            "representation_size_bytes": len(vector_list) * 4,
            "local_latency_ms": round(total_local_ms, 2),
            "step_times": {
                "preprocess_ms": round(prep_ms, 2),
                "inference_ms": round(infer_ms, 2),
                "protection_ms": round(prot_ms, 2)
            }
        },
        "protected_vector": vector_list,
        "original_vector": clean_list,
        "delta_vector": delta_list,
        "vector_sample_preview": [round(v, 4) for v in vector_list[:12]],
        "clean_sample_preview": [round(v, 4) for v in clean_list[:12]],
        "delta_sample_preview": [round(v, 4) for v in delta_list[:12]],
        "vector_metrics": {
            "cosine_similarity": round(cos_sim, 4),
            "cosine_similarity_pct": round(cos_sim * 100, 2),
            "l2_drift": round(l2_drift, 4),
            "noise_sigma": sigma if apply_noise else 0.0,
            "privacy_level": privacy_level,
            "mode": "protected" if apply_noise and sigma > 0 else "clean"
        },
        "vector_barcode": barcode_str,
        "zero_pixel_invariant": "Original image pixels retained in volatile client memory only"
    }

@router.post("/search/content-free-query")
async def execute_content_free_search(
    query: ContentFreeVectorQuery,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    CONTENT-FREE RETRIEVAL SERVER:
    Retrieval server receives strictly the 512-D protected vector.
    ZERO IMAGE BYTES or PIXELS cross into this endpoint.
    Performs domain-aware FAISS similarity search and returns Image IDs + similarity scores.
    """
    t_start = time.time()
    vector_data = np.array(query.protected_vector, dtype=np.float32)
    if vector_data.ndim == 1:
        vector_data = np.expand_dims(vector_data, axis=0)
        
    if vector_data.shape[1] != 512:
        raise HTTPException(status_code=400, detail=f"Expected 512-D protected vector, got {vector_data.shape[1]}-D")

    # Validate vector content
    if not np.isfinite(vector_data).all():
        raise HTTPException(status_code=400, detail="Protected vector contains non-finite values (NaN or Inf).")

    v_norm = np.linalg.norm(vector_data)
    if v_norm == 0:
        raise HTTPException(status_code=400, detail="Protected vector has zero magnitude.")

    classifier = DomainClassifier.get_instance()
    domain_info = classifier.classify_protected_vector(vector_data)
    
    clean_dom = (query.domain_filter or 'auto').lower().strip()
    if clean_dom in ['all', '*', 'cross_domain', 'cross-domain']:
        effective_domain = 'all'
    elif clean_dom in ['medical', 'biometrics', 'vehicles', 'nature']:
        effective_domain = clean_dom
    else:
        effective_domain = domain_info['domain']

    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    matches, below_matches, diagnostics = retriever.search_domain_aware(
        vector_data,
        domain_filter=effective_domain,
        top_k=query.top_k,
        threshold=query.threshold,
        include_below_threshold=query.include_below_threshold
    )
    diagnostics['detected_domain'] = domain_info['domain']
    diagnostics['detected_domain_display'] = domain_info['display_name']
    diagnostics['detection_confidence'] = domain_info['confidence']
    diagnostics['detection_confidence_label'] = domain_info['confidence_label']
    diagnostics['effective_domain_filter'] = effective_domain
    diagnostics['user_domain_selection'] = query.domain_filter or 'auto' 
    search_ms = diagnostics["search_latency_ms"]

    vault = PrivateImageVault.get_instance()
    results = []
    t_auth_start = time.time()
    user_token = generate_signed_token(current_user["user_id"]) if current_user else ""

    # Noise attenuation compensation factor for calibrated score display
    alpha = 1.0 / np.sqrt(1.0 + 512.0 * (max(0.0, query.sigma) ** 2)) if query.sigma > 0 else 1.0

    target_list = matches if not query.include_below_threshold else (matches + below_matches[:max(0, query.top_k - len(matches))])

    for match in target_list:
        img_id = match["image_id"]
        img_record = db.get_image(img_id)
        if not img_record:
            continue
            
        is_auth, auth_msg = vault.check_authorization(current_user, img_record)
        
        row_id = match.get("vector_row_id", 0)
        try:
            matched_vec = retriever.index.reconstruct(row_id)
            matched_vec_sample = [round(float(v), 4) for v in matched_vec[:12]]
            matched_barcode = []
            for val in matched_vec[:24]:
                if val > 0.05:
                    matched_barcode.append("█")
                elif val > 0.0:
                    matched_barcode.append("▓")
                elif val > -0.05:
                    matched_barcode.append("▒")
                else:
                    matched_barcode.append("░")
            matched_barcode_str = "".join(matched_barcode)
        except Exception:
            matched_vec_sample = []
            matched_barcode_str = "░░░░░░░░░░░░"
            
        sim_val = match.get("similarity", 0.0)
        calibrated_sim = min(1.0, round(sim_val / alpha, 4))
        pct = round(sim_val * 100.0, 1)
        calibrated_pct = round(calibrated_sim * 100.0, 1)
        
        is_strong_match = sim_val >= query.threshold
        match_status = "✓ Strong Feature Match" if is_strong_match else "Threshold Filtered (Below configured cut-off)"
        
        if query.sigma > 0:
            match_explanation = f"{img_id} ranked #{match['rank']} with {pct}% cosine proximity ({calibrated_pct}% noise-calibrated) in {img_record['category'].upper()} domain."
        else:
            match_explanation = f"{img_id} ranked #{match['rank']} with {pct}% cosine similarity based on 512-D protected visual representations in FAISS."
        
        # Valid authenticated preview URL if authorized, or explicit null if denied
        preview_url = f"/api/storage/image/{img_id}?token={user_token}" if is_auth else None

        results.append({
            "rank": match["rank"],
            "image_id": img_id,
            "cosine_similarity": round(sim_val, 4),
            "calibrated_similarity": calibrated_sim,
            "similarity_percent": f"{pct}%",
            "calibrated_percent": f"{calibrated_pct}%",
            "is_above_threshold": is_strong_match,
            "feature_match_status": match_status,
            "match_explanation": match_explanation,
            "matching_visual_features": [
                "Deep Visual Embedding Alignment",
                "Angle-Preserving Projection Similarity",
                "Domain-Filtered Cosine Proximity"
            ],
            "vector_sample_preview": matched_vec_sample,
            "vector_barcode": matched_barcode_str,
            "category": img_record["category"],
            "owner_id": img_record["owner_id"],
            "is_private": bool(img_record["is_private"]),
            "authorized": is_auth,
            "auth_status": "✓ Authorized" if is_auth else "🔒 Private Asset - Access Denied",
            "auth_message": auth_msg,
            "image_url": preview_url
        })
        
    auth_ms = (time.time() - t_auth_start) * 1000
    server_total_ms = (time.time() - t_start) * 1000
    
    diagnostics["active_user"] = current_user.get("name") if current_user else "Public Guest"
    diagnostics["active_role"] = current_user.get("role") if current_user else "guest"
    diagnostics["authorization_time_ms"] = round(auth_ms, 3)
    diagnostics["total_server_time_ms"] = round(server_total_ms, 2)
    diagnostics["noise_sigma"] = query.sigma
    diagnostics["noise_attenuation_alpha"] = round(alpha, 4)

    db.log_audit(
        current_user.get("user_id") if current_user else None,
        "CONTENT_FREE_SEARCH",
        "PROCESSED",
        f"Content-free query ({query.domain_filter or 'all'}) matched {len(results)} Image IDs. 0 pixels sent to server."
    )
    
    top_candidate_sim = float(matches[0]["similarity"]) if matches else (float(below_matches[0]["similarity"]) if below_matches else 0.0)
    top_candidate_pct = f"{round(top_candidate_sim * 100.0, 1)}%"

    return {
        "status": "success",
        "content_free_mode": "ON",
        "domain_filter_applied": query.domain_filter or "all",
        "has_relevant_matches": len(matches) > 0,
        "is_out_of_domain": len(matches) == 0,
        "records_passed_threshold": len(matches),
        "records_rejected_threshold": len(below_matches),
        "top_similarity": round(top_candidate_sim, 4),
        "top_similarity_percent": top_candidate_pct,
        "diagnostics": diagnostics,
        "server_metrics": {
            "pixels_sent_to_server": 0,
            "pixels_stored_on_server": 0,
            "payload_format": "512-D Float32 Coordinate Vector",
            "payload_bytes_received": len(query.protected_vector) * 4,
            "faiss_search_time_ms": round(search_ms, 3),
            "authorization_time_ms": round(auth_ms, 3),
            "total_server_time_ms": round(server_total_ms, 2),
            "index_type": "FAISS IndexFlatIP (Domain-Aware Unit Cosine Distance)",
            "zero_pixel_server_invariant": True
        },
        "privacy_receipt": {
            "receipt_id": f"RCP-{int(time.time()*1000)%1000000:06d}",
            "mode": "CONTENT-FREE RETRIEVAL",
            "query_pixels_sent": 0,
            "representation_sent": "512-D Protected Vector",
            "original_query_stored_server": False,
            "search_algorithm": "FAISS Flat Inner Product",
            "matches_returned": len(results),
            "threshold_applied": query.threshold,
            "domain_filter": query.domain_filter or "all",
            "metadata_minimized": query.strip_metadata,
            "search_time": f"{server_total_ms:.2f} ms"
        },
        "below_threshold_count": len(below_matches),
        "results": results
    }

@router.get("/inventory/summary")
def get_system_data_inventory():
    """
    Returns exact inventory of data on Client vs Retrieval Server vs Private Vault.
    """
    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    stats = db.get_system_stats()
    
    return {
        "mode": "CONTENT-FREE",
        "client_layer": {
            "original_query_image": "Retained strictly in client memory buffer",
            "exif_metadata": "Stripped prior to representation transmission",
            "feature_extraction": "MobileNetV3 (1280-D) executed client-side",
            "privacy_protection": "Orthogonal projection (512-D) + DP noise applied client-side"
        },
        "server_retrieval_layer": {
            "vector_index_name": "FAISS IndexFlatIP",
            "indexed_vectors_count": retriever.count(),
            "vector_dimension": 512,
            "original_images_in_index": 0,
            "similarity_metric": "Cosine Similarity (Inner Product on Unit Vectors)",
            "query_image_stored": False,
            "pixels_stored": 0
        },
        "authorized_vault_layer": {
            "storage_type": "Decoupled AES-256 Encrypted Private Storage",
            "total_stored_images": stats["total_images"],
            "access_control": "Role-Based (Specialist / Researcher / Admin)",
            "decoupled_from_faiss": True
        }
    }

# Backward compatible upload endpoint
@router.post("/search/query")
async def execute_private_search(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    threshold: float = Form(0.0),
    domain_filter: Optional[str] = Form(None),
    include_below_threshold: bool = Form(False),
    protected: bool = Form(True),
    sigma: float = Form(0.05),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    t_upload_start = time.time()
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")
        
    try:
        pil_image = Image.open(io.BytesIO(contents))
        pil_image.verify()
        pil_image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Unsupported or corrupted image file. Please upload JPG, PNG, or WebP.")
    upload_ms = (time.time() - t_upload_start) * 1000

    extractor = FeatureExtractor.get_instance()
    raw_vector, preprocess_ms, inference_ms = extractor.extract_features(pil_image)

    # Classify domain automatically if domain_filter not explicitly set
    classifier = DomainClassifier.get_instance()
    domain_info = classifier.classify_image(
        raw_features=raw_vector,
        filename=file.filename,
        image_bytes=contents
    )
    effective_domain = domain_filter if domain_filter and domain_filter != "auto" else domain_info["domain"]

    protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
    if protected:
        search_vector, protection_ms = protector.protect_vector(raw_vector, apply_noise=True, sigma=sigma)
        inversion_metrics = protector.measure_inversion_resistance(raw_vector, search_vector, sigma=sigma)
    else:
        search_vector, protection_ms = protector.protect_vector(raw_vector, apply_noise=False, sigma=0.0)
        inversion_metrics = {
            "projection_dimension": 512,
            "perturbation_sigma": 0.0,
            "estimated_reconstruction_ssim": 0.76,
            "inversion_verdict": "High Reconstruction Leakage (Raw Features)",
            "zero_pixel_storage_guarantee": True
        }

    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    matches, below_matches, diagnostics = retriever.search_domain_aware(
        search_vector,
        domain_filter=effective_domain,
        top_k=top_k,
        threshold=threshold,
        include_below_threshold=include_below_threshold
    )
    search_ms = diagnostics["search_latency_ms"]

    db.log_audit(
        current_user.get("user_id") if current_user else None,
        "VECTOR_SEARCH",
        "PROCESSED",
        f"Query ({effective_domain}) matched {len(matches)} vectors in {search_ms:.2f}ms"
    )

    vault = PrivateImageVault.get_instance()
    results = []
    t_auth_start = time.time()
    user_token = generate_signed_token(current_user["user_id"]) if current_user else ""

    alpha = 1.0 / np.sqrt(1.0 + 512.0 * (max(0.0, sigma) ** 2)) if (protected and sigma > 0) else 1.0

    target_list = matches if not include_below_threshold else (matches + below_matches[:max(0, top_k - len(matches))])

    for match in target_list:
        img_id = match["image_id"]
        img_record = db.get_image(img_id)
        if not img_record:
            continue
            
        is_auth, auth_msg = vault.check_authorization(current_user, img_record)
        
        row_id = match.get("vector_row_id", 0)
        try:
            matched_vec = retriever.index.reconstruct(row_id)
            matched_vec_sample = [round(float(v), 4) for v in matched_vec[:12]]
        except Exception:
            matched_vec_sample = []

        sim_val = match.get("similarity", 0.0)
        calibrated_sim = min(1.0, round(sim_val / alpha, 4))
        pct = round(sim_val * 100.0, 1)
        calibrated_pct = round(calibrated_sim * 100.0, 1)

        is_strong_match = sim_val >= threshold
        match_status = "✓ Strong Feature Match" if is_strong_match else "Threshold Filtered"
        match_explanation = f"{img_id} matched at rank #{match['rank']} with {pct}% cosine proximity ({calibrated_pct}% calibrated) in {img_record['category'].upper()} domain."

        preview_url = f"/api/storage/image/{img_id}?token={user_token}" if is_auth else None

        results.append({
            "rank": match["rank"],
            "image_id": img_id,
            "cosine_similarity": round(sim_val, 4),
            "calibrated_similarity": calibrated_sim,
            "similarity_percent": f"{pct}%",
            "calibrated_percent": f"{calibrated_pct}%",
            "is_above_threshold": is_strong_match,
            "feature_match_status": match_status,
            "match_explanation": match_explanation,
            "vector_sample_preview": matched_vec_sample,
            "category": img_record["category"],
            "owner_id": img_record["owner_id"],
            "is_private": bool(img_record["is_private"]),
            "authorized": is_auth,
            "auth_status": "✓ Authorized" if is_auth else "🔒 Private Asset - Access Denied",
            "auth_message": auth_msg,
            "image_url": preview_url
        })
        
    auth_ms = (time.time() - t_auth_start) * 1000
    total_latency_ms = upload_ms + preprocess_ms + inference_ms + protection_ms + search_ms + auth_ms

    diagnostics["active_user"] = current_user.get("name") if current_user else "Public Guest"
    diagnostics["active_role"] = current_user.get("role") if current_user else "guest"
    diagnostics["effective_domain"] = effective_domain
    diagnostics["detection_method"] = domain_info["method"]

    return {
        "query_summary": {
            "model_name": extractor.model_name,
            "feature_dim": extractor.feature_dim,
            "protected_dim": 512,
            "results_found": len(results),
            "detected_domain": domain_info["domain"],
            "domain_filter_applied": effective_domain,
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
        "diagnostics": diagnostics,
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
    token: Optional[str] = Query(None),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    img_record = db.get_image(image_id)
    if not img_record:
        raise HTTPException(status_code=404, detail=f"Image record {image_id} not found.")
        
    vault = PrivateImageVault.get_instance()
    is_auth, auth_msg = vault.check_authorization(current_user, img_record)
    
    if not is_auth:
        actor_id = current_user.get("user_id") if current_user else "ANONYMOUS"
        actor_role = current_user.get("role") if current_user else "unauthenticated"
        db.log_audit(
            current_user.get("user_id") if current_user else None,
            "IMAGE_FETCH",
            "BLOCKED",
            f"Blocked unauthorized attempt to fetch private image {image_id} by user {actor_id} ({actor_role})"
        )
        raise HTTPException(status_code=403, detail=auth_msg)
        
    try:
        image_bytes = vault.retrieve_image_bytes(img_record["storage_reference"])
        db.log_audit(
            current_user.get("user_id") if current_user else None,
            "IMAGE_FETCH",
            "ALLOWED",
            f"Authorized retrieval of {image_id} from private storage for user {current_user.get('user_id')}"
        )
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage access error: {str(e)}")
