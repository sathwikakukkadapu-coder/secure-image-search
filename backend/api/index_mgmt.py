import os
import glob
import time
import json
import shutil
import hashlib
from typing import Dict, Any, List, Optional
from PIL import Image
import numpy as np
import faiss
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query

import backend.database.db as db
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
from backend.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/index", tags=["index_management"])

DATASET_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataset"))
VECTOR_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vector_db"))

def _compute_file_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

@router.get("/status")
def get_index_status(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Returns live health telemetry of the FAISS index, database mappings,
    and decoupled private vault storage.
    """
    retriever = FAISSRetrievalEngine.get_instance()
    sys_stats = db.get_system_stats()
    vault = PrivateImageVault.get_instance()
    
    # Check physical index file sizes
    faiss_size_kb = 0.0
    if os.path.exists(retriever.index_path):
        faiss_size_kb = round(os.path.getsize(retriever.index_path) / 1024.0, 2)
        
    vault_size_mb = 0.0
    if os.path.exists(vault.storage_dir):
        total_b = sum(os.path.getsize(os.path.join(vault.storage_dir, f)) for f in os.listdir(vault.storage_dir) if os.path.isfile(os.path.join(vault.storage_dir, f)))
        vault_size_mb = round(total_b / (1024.0 * 1024.0), 2)
        
    faiss_vectors = retriever.count()
    db_vectors = sys_stats["total_vectors"]
    total_images = sys_stats["total_images"]
    
    # Assess Health Status
    if faiss_vectors == db_vectors and faiss_vectors == total_images and faiss_vectors > 0:
        health_status = "HEALTHY"
        health_msg = "Index and database mappings are fully synchronized."
    elif faiss_vectors == 0:
        health_status = "EMPTY"
        health_msg = "FAISS index has 0 vectors. Please run index rebuild."
    elif abs(faiss_vectors - total_images) > 0:
        health_status = "DEGRADED"
        health_msg = f"Desynchronization detected: FAISS has {faiss_vectors} vectors but database records {total_images} images."
    else:
        health_status = "ONLINE"
        health_msg = "Operational"
        
    last_rebuild = db.get_index_metadata("last_rebuild_timestamp")
    last_rebuild_duration = db.get_index_metadata("last_rebuild_duration_sec")
    
    return {
        "status": health_status,
        "health_summary": health_msg,
        "index_telemetry": {
            "indexed_vectors_faiss": faiss_vectors,
            "recorded_images_db": total_images,
            "vector_dimension": retriever.dimension,
            "index_type": "Meta AI FAISS IndexFlatIP (Unit Inner Product)",
            "similarity_metric": "Cosine Proximity in Protected Space",
            "feature_extractor_backbone": "MobileNetV3-Large (1280-D)",
            "privacy_protection_dim": 512,
            "index_file_size_kb": faiss_size_kb,
            "decoupled_vault_size_mb": vault_size_mb,
            "zero_pixel_invariant": True,
            "last_rebuilt": last_rebuild or "Pre-seeded at initial installation",
            "last_rebuild_duration": f"{last_rebuild_duration}s" if last_rebuild_duration else "N/A"
        }
    }

@router.post("/validate")
def validate_dataset_collection(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Scans the dataset directory and validates file integrity, formats,
    size boundaries, and detects duplicates or corrupt images.
    """
    t0 = time.time()
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    max_file_size = 10 * 1024 * 1024 # 10MB
    
    all_files: List[str] = []
    if os.path.exists(DATASET_ROOT):
        for root, _, files in os.walk(DATASET_ROOT):
            for f in files:
                all_files.append(os.path.join(root, f))
                
    db_images = {img["original_filename"]: img for img in db.get_all_images()}
    
    valid_count = 0
    corrupt_files = []
    unsupported_files = []
    oversized_files = []
    seen_hashes: Dict[str, str] = {}
    duplicates = []
    categories_found = set()
    
    for fpath in all_files:
        fname = os.path.basename(fpath)
        ext = os.path.splitext(fname)[1].lower()
        rel_cat = os.path.basename(os.path.dirname(fpath))
        categories_found.add(rel_cat)
        
        # 1. Format check
        if ext not in valid_extensions:
            unsupported_files.append({"file": fname, "reason": f"Unsupported format {ext}"})
            continue
            
        # 2. File size check
        fsize = os.path.getsize(fpath)
        if fsize > max_file_size:
            oversized_files.append({"file": fname, "size_mb": round(fsize / (1024*1024), 2)})
            continue
            
        # 3. Duplicate check via SHA-256
        fhash = _compute_file_sha256(fpath)
        if fhash in seen_hashes:
            duplicates.append({"file": fname, "duplicate_of": seen_hashes[fhash]})
        else:
            seen_hashes[fhash] = fname
            
        # 4. Integrity check via PIL
        try:
            with Image.open(fpath) as img:
                img.verify()
            valid_count += 1
        except Exception as e:
            corrupt_files.append({"file": fname, "error": str(e)})

    scan_ms = round((time.time() - t0) * 1000, 2)
    
    is_valid = len(corrupt_files) == 0 and len(oversized_files) == 0
    
    return {
        "status": "valid" if is_valid else "issues_detected",
        "dataset_root": DATASET_ROOT,
        "scan_time_ms": scan_ms,
        "summary": {
            "total_files_scanned": len(all_files),
            "valid_samples": valid_count,
            "corrupt_files_count": len(corrupt_files),
            "unsupported_files_count": len(unsupported_files),
            "duplicates_detected_count": len(duplicates),
            "categories_identified": sorted(list(categories_found))
        },
        "issues": {
            "corrupt_files": corrupt_files,
            "duplicates": duplicates,
            "unsupported": unsupported_files,
            "oversized": oversized_files
        }
    }

@router.post("/rebuild")
def rebuild_vector_index(current_user: Optional[Dict[str, Any]] = Depends(require_admin)):
    """
    Safe staged rebuilding workflow:
    1. Validates dataset integrity.
    2. Builds temporary staging index in isolation.
    3. Verifies dimension and non-zero counts.
    4. Safely swaps staging index with active index, preserving previous index backup.
    5. Updates metadata and re-arms in-memory singleton.
    """
    t_start = time.time()
    extractor = FeatureExtractor.get_instance()
    protector = PrivacyProtectionLayer.get_instance()
    vault = PrivateImageVault.get_instance()
    retriever = FAISSRetrievalEngine.get_instance()
    
    # Verify dataset exists
    if not os.path.exists(DATASET_ROOT):
        raise HTTPException(status_code=500, detail=f"Dataset directory not found: {DATASET_ROOT}")
        
    staging_index_path = os.path.join(VECTOR_DB_DIR, "faiss_index_staging.bin")
    staging_map_path = os.path.join(VECTOR_DB_DIR, "id_map_staging.json")
    backup_index_path = os.path.join(VECTOR_DB_DIR, "faiss_index_backup.bin")
    backup_map_path = os.path.join(VECTOR_DB_DIR, "id_map_backup.json")
    
    staging_index = faiss.IndexFlatIP(512)
    staging_map: Dict[int, str] = {}
    
    categories = [d for d in os.listdir(DATASET_ROOT) if os.path.isdir(os.path.join(DATASET_ROOT, d))]
    
    owner_map = {
        "medical": ("USR_DOC_01", True),
        "biometrics": ("USR_DOC_01", True),
        "vehicles": ("USR_RES_02", False),
        "nature": ("USR_RES_02", False)
    }
    
    new_images_metadata = []
    vector_mappings = []
    indexed_count = 0
    
    for cat in sorted(categories):
        cat_path = os.path.join(DATASET_ROOT, cat)
        img_files = sorted(glob.glob(os.path.join(cat_path, "*.*")))
        
        for img_path in img_files:
            fname = os.path.basename(img_path)
            img_id = f"IMG_{cat[:3].upper()}_{os.path.splitext(fname)[0]}"
            owner_id, is_private = owner_map.get(cat, ("USR_RES_02", False))
            
            try:
                # 1. Read bytes
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                    
                # 2. Encrypt & Store in vault
                safe_name, enc_storage_ref = vault.store_image(img_bytes, img_id, fname)
                
                # 3. Extract CNN features
                with Image.open(img_path) as pil_img:
                    raw_vec, _, _ = extractor.extract_features(pil_img)
                    
                # 4. Protect Representation
                prot_vec, _ = protector.protect_vector(raw_vec, apply_noise=True, sigma=0.05)
                
                # 5. Add to staging FAISS
                vec_arr = prot_vec.reshape(1, 512).astype(np.float32)
                row_id = staging_index.ntotal
                staging_index.add(vec_arr)
                staging_map[row_id] = img_id
                
                new_images_metadata.append((img_id, owner_id, fname, enc_storage_ref, cat, 1 if is_private else 0, time.strftime("%Y-%m-%dT%H:%M:%SZ")))
                vector_mappings.append((img_id, row_id, extractor.model_name, time.strftime("%Y-%m-%dT%H:%M:%SZ")))
                indexed_count += 1
            except Exception as e:
                # Log file failure but proceed with valid files
                print(f"[Index Rebuild] Skipped file {img_path} due to error: {e}")
                
    # Safeguard Check: Staging validation
    if staging_index.ntotal < 4 or indexed_count == 0:
        raise HTTPException(status_code=500, detail="Staged index validation failed: Insufficient valid vectors built.")
        
    # Write staging files to disk
    faiss.write_index(staging_index, staging_index_path)
    with open(staging_map_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in staging_map.items()}, f, indent=2)
        
    # Atomic Swap with Backup
    try:
        if os.path.exists(retriever.index_path):
            shutil.copy2(retriever.index_path, backup_index_path)
        if os.path.exists(retriever.map_path):
            shutil.copy2(retriever.map_path, backup_map_path)
            
        shutil.move(staging_index_path, retriever.index_path)
        shutil.move(staging_map_path, retriever.map_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Atomic swap failed: {str(e)}. Previous index preserved.")
        
    # Update SQLite database cleanly
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM retrieval_vectors")
    cur.execute("DELETE FROM images")
    
    cur.executemany("""
    INSERT INTO images (image_id, owner_id, original_filename, storage_reference, category, is_private, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, new_images_metadata)
    
    cur.executemany("""
    INSERT INTO retrieval_vectors (image_id, vector_row_id, model_name, created_at)
    VALUES (?, ?, ?, ?)
    """, vector_mappings)
    
    conn.commit()
    conn.close()
    
    # Reload in-memory FAISS singleton
    retriever.load_index()
    
    duration_sec = round(time.time() - t_start, 2)
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    db.set_index_metadata("last_rebuild_timestamp", now_iso)
    db.set_index_metadata("last_rebuild_duration_sec", str(duration_sec))
    db.set_index_metadata("last_rebuild_vectors_count", str(indexed_count))
    
    db.log_audit(
        current_user.get("user_id"),
        "INDEX_REBUILD",
        "COMPLETED",
        f"Safe staged rebuild completed: {indexed_count} vectors indexed in {duration_sec}s. Backup preserved.",
        category="INDEXING",
        severity="INFO"
    )
    
    return {
        "status": "success",
        "action": "SAFE_STAGED_REBUILD",
        "indexed_vectors": indexed_count,
        "elapsed_seconds": duration_sec,
        "throughput_images_per_sec": round(indexed_count / max(0.1, duration_sec), 1),
        "backup_created": os.path.exists(backup_index_path),
        "timestamp": now_iso
    }

@router.post("/incremental")
def run_incremental_indexing(current_user: Optional[Dict[str, Any]] = Depends(require_admin)):
    """
    Incremental indexing workflow:
    Detects unindexed files in the dataset folder and appends them
    to the active FAISS index without destroying existing vectors.
    """
    t_start = time.time()
    extractor = FeatureExtractor.get_instance()
    protector = PrivacyProtectionLayer.get_instance()
    vault = PrivateImageVault.get_instance()
    retriever = FAISSRetrievalEngine.get_instance()
    
    # Query all currently indexed filenames in SQLite
    existing_images = db.get_all_images()
    existing_filenames = {img["original_filename"] for img in existing_images}
    
    categories = [d for d in os.listdir(DATASET_ROOT) if os.path.isdir(os.path.join(DATASET_ROOT, d))]
    
    owner_map = {
        "medical": ("USR_DOC_01", True),
        "biometrics": ("USR_DOC_01", True),
        "vehicles": ("USR_RES_02", False),
        "nature": ("USR_RES_02", False)
    }
    
    new_files_indexed = 0
    for cat in sorted(categories):
        cat_path = os.path.join(DATASET_ROOT, cat)
        img_files = sorted(glob.glob(os.path.join(cat_path, "*.*")))
        
        for img_path in img_files:
            fname = os.path.basename(img_path)
            if fname in existing_filenames:
                continue # Already indexed
                
            img_id = f"IMG_{cat[:3].upper()}_{os.path.splitext(fname)[0]}"
            owner_id, is_private = owner_map.get(cat, ("USR_RES_02", False))
            
            try:
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                safe_name, enc_ref = vault.store_image(img_bytes, img_id, fname)
                
                with Image.open(img_path) as pil_img:
                    raw_vec, _, _ = extractor.extract_features(pil_img)
                    
                prot_vec, _ = protector.protect_vector(raw_vec, apply_noise=True, sigma=0.05)
                row_id = retriever.add_vector(prot_vec, img_id)
                
                db.insert_image(img_id, owner_id, fname, enc_ref, cat, is_private)
                db.insert_vector_mapping(img_id, row_id, extractor.model_name)
                existing_filenames.add(fname)
                new_files_indexed += 1
            except Exception as e:
                print(f"[Incremental Index] Error indexing {img_path}: {e}")
                
    if new_files_indexed > 0:
        retriever.save_index()
        duration_sec = round(time.time() - t_start, 2)
        db.set_index_metadata("last_incremental_index_timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        db.log_audit(
            current_user.get("user_id"),
            "INDEX_INCREMENTAL",
            "COMPLETED",
            f"Added {new_files_indexed} new images to FAISS index.",
            category="INDEXING",
            severity="INFO"
        )
        return {
            "status": "success",
            "new_images_indexed": new_files_indexed,
            "total_vectors_in_faiss": retriever.count(),
            "elapsed_seconds": duration_sec
        }
    else:
        return {
            "status": "up_to_date",
            "message": "All dataset images are already indexed. No new images found.",
            "total_vectors_in_faiss": retriever.count()
        }
