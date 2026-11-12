import os
import csv
import hashlib
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image

import backend.database.db as db
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer

class DomainClassifier:
    """
    Domain Detection & Domain-Aware Retrieval Service for PrivateLens.
    Supported Domains:
    - MEDICAL (radiographs, CT, MRI, ultrasound, histology)
    - BIOMETRICS (fingerprints, iris, faces, vein patterns)
    - NATURE (landscapes, water, vegetation, weather, wildlife)
    - VEHICLES (cars, two-wheelers, commercial, aviation, maritime)
    """
    _instance = None
    
    DOMAINS = ["medical", "biometrics", "nature", "vehicles"]
    DOMAIN_DISPLAY_NAMES = {
        "medical": "Medical Imaging",
        "biometrics": "Biometric Authentication",
        "nature": "Natural Scenes",
        "vehicles": "Vehicles & Transport"
    }

    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.metadata_csv = os.path.join(self.base_dir, "dataset", "metadata.csv")
        self.cache_path = os.path.join(self.base_dir, "vector_db", "domain_centroids.npz")
        self.metadata_lookup: Dict[str, Dict[str, Any]] = {}
        self.sha_lookup: Dict[str, str] = {}
        self.domain_centroids: Dict[str, np.ndarray] = {}
        
        self._load_metadata()
        self._compute_centroids()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_metadata(self):
        if not os.path.exists(self.metadata_csv):
            return
        try:
            with open(self.metadata_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = row.get("filename", "").lower()
                    sha = row.get("sha256", "").lower()
                    dom = row.get("domain", "").lower()
                    if fname and dom:
                        self.metadata_lookup[fname] = row
                    if sha and dom:
                        self.sha_lookup[sha] = dom
        except Exception as e:
            print(f"[DomainClassifier] Metadata load notice: {e}")

    def _compute_centroids(self):
        """Precomputes or loads cached 512-D domain centroids."""
        if os.path.exists(self.cache_path):
            try:
                data = np.load(self.cache_path)
                for dom in self.DOMAINS:
                    if dom in data:
                        self.domain_centroids[dom] = data[dom].astype(np.float32)
                if len(self.domain_centroids) == len(self.DOMAINS):
                    return
            except Exception as e:
                print(f"[DomainClassifier] Cache read notice: {e}")

        try:
            protector = PrivacyProtectionLayer.get_instance()
            extractor = FeatureExtractor.get_instance()
            Q = protector.projection_matrix
            
            # Load sample vectors from each category in the dataset directory
            dataset_dir = os.path.join(self.base_dir, "dataset")
            if not os.path.exists(dataset_dir):
                return
                
            for dom in self.DOMAINS:
                dom_path = os.path.join(dataset_dir, dom)
                if not os.path.exists(dom_path):
                    continue
                    
                vectors = []
                for root, _, files in os.walk(dom_path):
                    for f in files:
                        if f.lower().endswith((".jpg", ".jpeg", ".png")):
                            fpath = os.path.join(root, f)
                            try:
                                with Image.open(fpath) as img:
                                    raw, _, _ = extractor.extract_features(img)
                                    proj = np.dot(raw, Q)
                                    proj /= np.linalg.norm(proj)
                                    vectors.append(proj)
                            except Exception:
                                pass
                            if len(vectors) >= 40:
                                break
                    if len(vectors) >= 40:
                        break
                        
                if vectors:
                    c = np.mean(np.array(vectors), axis=0)
                    c /= np.linalg.norm(c)
                    self.domain_centroids[dom] = c.astype(np.float32)
        except Exception as e:
            print(f"[DomainClassifier] Centroid computation notice: {e}")

    def classify_image(
        self,
        raw_features: Optional[np.ndarray] = None,
        filename: Optional[str] = None,
        image_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Determines the query image domain using:
        1. Exact SHA-256 hash match against catalog metadata.
        2. Exact filename match against catalog metadata.
        3. Visual feature cosine similarity against domain centroids.
        """
        # 1. Exact SHA-256 match
        if image_bytes:
            sha = hashlib.sha256(image_bytes).hexdigest().lower()
            if sha in self.sha_lookup:
                dom = self.sha_lookup[sha]
                return {
                    "domain": dom,
                    "display_name": self.DOMAIN_DISPLAY_NAMES.get(dom, dom.capitalize()),
                    "confidence": 1.0,
                    "confidence_label": "High (Verified Catalog Match)",
                    "method": "sha256_metadata_catalog",
                    "scores": {d: (1.0 if d == dom else 0.0) for d in self.DOMAINS}
                }

        # 2. Known catalog filename match
        if filename:
            clean_fn = os.path.basename(filename).lower()
            if clean_fn in self.metadata_lookup:
                dom = self.metadata_lookup[clean_fn]["domain"].lower()
                return {
                    "domain": dom,
                    "display_name": self.DOMAIN_DISPLAY_NAMES.get(dom, dom.capitalize()),
                    "confidence": 1.0,
                    "confidence_label": "High (Known Catalog Filename)",
                    "method": "filename_metadata_catalog",
                    "scores": {d: (1.0 if d == dom else 0.0) for d in self.DOMAINS}
                }
                
            # Rule-based filename heuristics if filename has clear indicators
            for dom_indicator, dom_target in [
                ("xray", "medical"), ("ct", "medical"), ("mri", "medical"), ("medical", "medical"),
                ("face", "biometrics"), ("iris", "biometrics"), ("fingerprint", "biometrics"), ("biometric", "biometrics"),
                ("car", "vehicles"), ("bike", "vehicles"), ("vehicle", "vehicles"), ("truck", "vehicles"),
                ("nature", "nature"), ("water", "nature"), ("mountain", "nature"), ("forest", "nature")
            ]:
                if dom_indicator in clean_fn:
                    return {
                        "domain": dom_target,
                        "display_name": self.DOMAIN_DISPLAY_NAMES.get(dom_target, dom_target.capitalize()),
                        "confidence": 0.95,
                        "confidence_label": "High (Verified Filename Tag)",
                        "method": "heuristic_tag_match",
                        "scores": {d: (0.95 if d == dom_target else 0.05) for d in self.DOMAINS}
                    }

        # 3. Visual feature centroid classification
        if raw_features is not None and len(self.domain_centroids) > 0:
            protector = PrivacyProtectionLayer.get_instance()
            proj = np.dot(raw_features, protector.projection_matrix)
            proj_norm = np.linalg.norm(proj)
            if proj_norm > 0:
                proj /= proj_norm
                
            scores = {}
            for dom, centroid in self.domain_centroids.items():
                scores[dom] = float(np.dot(proj, centroid))
                
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_dom, top_score = sorted_scores[0]
            second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
            margin = top_score - second_score
            
            conf = min(0.99, max(0.50, round(0.50 + margin * 2.5, 3)))
            conf_label = "High" if margin > 0.05 else ("Medium" if margin > 0.02 else "Low (Ambiguous)")
            
            return {
                "domain": top_dom,
                "display_name": self.DOMAIN_DISPLAY_NAMES.get(top_dom, top_dom.capitalize()),
                "confidence": conf,
                "confidence_label": conf_label,
                "method": "visual_feature_centroid_projection",
                "scores": {d: round(s, 4) for d, s in scores.items()}
            }

        # Default fallback
        return {
            "domain": "medical",
            "display_name": "Medical Imaging (Default)",
            "confidence": 0.5,
            "confidence_label": "Uncertain",
            "method": "default_fallback",
            "scores": {d: 0.25 for d in self.DOMAINS}
        }

    def classify_protected_vector(self, protected_vec: np.ndarray) -> Dict[str, Any]:
        """
        Zero-Pixel Domain Classifier:
        Determines domain directly from a 512-D protected vector using precomputed centroids.
        Receives NO raw pixels.
        """
        vec = np.array(protected_vec, dtype=np.float32).flatten()
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            return {
                "domain": "medical",
                "display_name": "Medical Imaging (Default)",
                "confidence": 0.25,
                "confidence_label": "Zero-Vector Fallback",
                "method": "zero_vector_fallback",
                "scores": {d: 0.25 for d in self.DOMAINS}
            }

        scores = {}
        for dom, centroid in self.domain_centroids.items():
            scores[dom] = float(np.dot(vec, centroid))

        if not scores:
            return {
                "domain": "medical",
                "display_name": "Medical Imaging (Default)",
                "confidence": 0.50,
                "confidence_label": "Default Fallback",
                "method": "default_fallback",
                "scores": {d: 0.25 for d in self.DOMAINS}
            }

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_dom, top_score = sorted_scores[0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
        margin = top_score - second_score

        conf = min(0.99, max(0.50, round(0.50 + margin * 2.5, 3)))
        conf_label = "High" if margin > 0.05 else ("Medium" if margin > 0.02 else "Low (Ambiguous)")

        return {
            "domain": top_dom,
            "display_name": self.DOMAIN_DISPLAY_NAMES.get(top_dom, top_dom.capitalize()),
            "confidence": conf,
            "confidence_label": conf_label,
            "method": "protected_vector_centroid_projection",
            "scores": {d: round(s, 4) for d, s in scores.items()}
        }
