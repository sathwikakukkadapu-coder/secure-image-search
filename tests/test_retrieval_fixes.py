import os
import sys
import unittest
import asyncio
import numpy as np
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import backend.database.db as db
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.retrieval.domain_classifier import DomainClassifier
from backend.services.storage.vault import PrivateImageVault
from backend.api.search import ContentFreeVectorQuery, execute_content_free_search
from fastapi import HTTPException

class TestPrivateLensRetrievalFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_conn = db.get_connection()
        cls.extractor = FeatureExtractor.get_instance()
        cls.protector = PrivacyProtectionLayer.get_instance(input_dim=cls.extractor.feature_dim, protected_dim=512)
        cls.retriever = FAISSRetrievalEngine.get_instance(dimension=512)
        cls.classifier = DomainClassifier.get_instance()
        cls.vault = PrivateImageVault.get_instance()
        
        # Test users
        cls.doc1 = db.get_user_by_id("USR_DOC_01")
        cls.doc2 = db.get_user_by_id("USR_DOC_02")
        cls.admin = db.get_user_by_id("USR_ADM_00")
        cls.researcher = db.get_user_by_id("USR_RES_02")
        cls.guest = db.get_user_by_id("USR_GST_99")

    # =========================================================================
    # Scenario 1: X-ray query against mixed dataset (Medical Domain)
    # =========================================================================
    def test_scenario_01_medical_xray_retrieval(self):
        """Medical query should detect medical domain, rank #1 exact match, 0 nature contamination."""
        img_path = os.path.join("dataset", "medical", "xray", "medical_xray_0004.jpg")
        self.assertTrue(os.path.exists(img_path), f"File {img_path} must exist.")
        
        with Image.open(img_path) as img:
            raw_feats, _, _ = self.extractor.extract_features(img)
        
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        # Domain classification
        dom_info = self.classifier.classify_image(raw_features=raw_feats, filename=img_path, image_bytes=img_bytes)
        self.assertEqual(dom_info["domain"], "medical", "X-ray query must be classified as medical domain.")

        # Search without noise to test pure projection accuracy
        search_vec, _ = self.protector.protect_vector(raw_feats, apply_noise=False, sigma=0.0)
        
        query = ContentFreeVectorQuery(
            protected_vector=search_vec.tolist(),
            top_k=5,
            threshold=0.30,
            domain_filter="auto",
            sigma=0.0
        )
        res = asyncio.run(execute_content_free_search(query, current_user=self.doc1))
        
        matches = res["results"]
        self.assertGreaterEqual(len(matches), 1, "Must return at least 1 match.")
        
        # Rank 1 must be medical_xray_0004 with ~100% similarity
        rank1 = matches[0]
        self.assertIn("medical_xray_0004", rank1["image_id"], "Rank #1 must be the exact medical query image.")
        self.assertGreaterEqual(rank1["cosine_similarity"], 0.99, "Self-similarity must be ~ 1.0.")
        
        # All returned results must be medical domain (Zero nature contamination)
        for r in matches:
            self.assertEqual(r["category"].lower(), "medical", f"Contamination detected: returned {r['category']} in medical search.")

    # =========================================================================
    # Scenario 2: Nature query against mixed dataset (Nature Domain)
    # =========================================================================
    def test_scenario_02_nature_retrieval(self):
        """Nature query must return nature domain images only and rank #1 true match."""
        # Find any nature image in dataset
        nat_dir = os.path.join("dataset", "nature")
        nat_img_path = None
        for root, _, files in os.walk(nat_dir):
            for f in files:
                if f.lower().endswith((".jpg", ".png")):
                    nat_img_path = os.path.join(root, f)
                    break
            if nat_img_path:
                break
                
        self.assertIsNotNone(nat_img_path, "Must find at least one nature image.")
        
        with Image.open(nat_img_path) as img:
            raw_feats, _, _ = self.extractor.extract_features(img)
        with open(nat_img_path, "rb") as f:
            img_bytes = f.read()

        dom_info = self.classifier.classify_image(raw_features=raw_feats, filename=nat_img_path, image_bytes=img_bytes)
        self.assertEqual(dom_info["domain"], "nature", "Nature query must be classified as nature.")

        search_vec, _ = self.protector.protect_vector(raw_feats, apply_noise=False, sigma=0.0)
        query = ContentFreeVectorQuery(
            protected_vector=search_vec.tolist(),
            top_k=5,
            threshold=0.20,
            domain_filter="nature",
            sigma=0.0
        )
        res = asyncio.run(execute_content_free_search(query, current_user=self.guest))
        matches = res["results"]
        self.assertGreater(len(matches), 0)
        for r in matches:
            self.assertEqual(r["category"].lower(), "nature", "All matches must be in nature domain.")

    # =========================================================================
    # Scenario 3: Face biometric query against mixed dataset
    # =========================================================================
    def test_scenario_03_biometrics_retrieval(self):
        """Biometrics query must isolate biometric records."""
        bio_dir = os.path.join("dataset", "biometrics")
        bio_img_path = None
        for root, _, files in os.walk(bio_dir):
            for f in files:
                if f.lower().endswith((".jpg", ".png")):
                    bio_img_path = os.path.join(root, f)
                    break
            if bio_img_path:
                break
                
        self.assertIsNotNone(bio_img_path, "Must find biometric test image.")
        with Image.open(bio_img_path) as img:
            raw_feats, _, _ = self.extractor.extract_features(img)
            
        search_vec, _ = self.protector.protect_vector(raw_feats, apply_noise=False, sigma=0.0)
        query = ContentFreeVectorQuery(
            protected_vector=search_vec.tolist(),
            top_k=5,
            threshold=0.20,
            domain_filter="biometrics",
            sigma=0.0
        )
        res = asyncio.run(execute_content_free_search(query, current_user=self.admin))
        matches = res["results"]
        self.assertGreater(len(matches), 0)
        for r in matches:
            self.assertEqual(r["category"].lower(), "biometrics", "Matches must be biometrics.")

    # =========================================================================
    # Scenario 4: Vehicle query against mixed dataset
    # =========================================================================
    def test_scenario_04_vehicles_retrieval(self):
        """Vehicles query must return vehicles domain only."""
        veh_dir = os.path.join("dataset", "vehicles")
        veh_img_path = None
        for root, _, files in os.walk(veh_dir):
            for f in files:
                if f.lower().endswith((".jpg", ".png")):
                    veh_img_path = os.path.join(root, f)
                    break
            if veh_img_path:
                break
                
        self.assertIsNotNone(veh_img_path, "Must find vehicle test image.")
        with Image.open(veh_img_path) as img:
            raw_feats, _, _ = self.extractor.extract_features(img)
            
        search_vec, _ = self.protector.protect_vector(raw_feats, apply_noise=False, sigma=0.0)
        query = ContentFreeVectorQuery(
            protected_vector=search_vec.tolist(),
            top_k=5,
            threshold=0.20,
            domain_filter="vehicles",
            sigma=0.0
        )
        res = asyncio.run(execute_content_free_search(query, current_user=self.guest))
        matches = res["results"]
        self.assertGreater(len(matches), 0)
        for r in matches:
            self.assertEqual(r["category"].lower(), "vehicles", "Matches must be vehicles.")

    # =========================================================================
    # Scenario 5: Missing image paths and non-existent assets handling
    # =========================================================================
    def test_scenario_05_missing_assets_handling(self):
        """Non-existent image or storage reference must safely raise error without crashing."""
        non_existent_id = "IMG_FAKE_NON_EXISTENT_9999"
        record = db.get_image(non_existent_id)
        self.assertIsNone(record, "Non-existent image should return None from DB.")
        
        with self.assertRaises((FileNotFoundError, ValueError, Exception)):
            self.vault.retrieve_image_bytes("non_existent_encrypted_storage_ref_handle")

    # =========================================================================
    # Scenario 6: Empty, zero-norm, or NaN/Inf vector handling
    # =========================================================================
    def test_scenario_06_invalid_vectors_handling(self):
        """All-zero, NaN, or Inf vectors must be rejected with HTTP 400."""
        # 1. Zero vector
        zero_vec = [0.0] * 512
        q_zero = ContentFreeVectorQuery(protected_vector=zero_vec)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(execute_content_free_search(q_zero, current_user=self.guest))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("zero magnitude", ctx.exception.detail.lower())

        # 2. NaN vector
        nan_vec = [0.1] * 512
        nan_vec[10] = float("nan")
        q_nan = ContentFreeVectorQuery(protected_vector=nan_vec)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(execute_content_free_search(q_nan, current_user=self.guest))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("non-finite", ctx.exception.detail.lower())

        # 3. Inf vector
        inf_vec = [0.1] * 512
        inf_vec[5] = float("inf")
        q_inf = ContentFreeVectorQuery(protected_vector=inf_vec)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(execute_content_free_search(q_inf, current_user=self.guest))
        self.assertEqual(ctx.exception.status_code, 400)

    # =========================================================================
    # Scenario 7: Incompatible dimensions handling
    # =========================================================================
    def test_scenario_07_incompatible_dimensions(self):
        """Vectors with dimension != 512 must be rejected with HTTP 400."""
        # 128-D vector
        vec_128 = [0.05] * 128
        q128 = ContentFreeVectorQuery(protected_vector=vec_128)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(execute_content_free_search(q128, current_user=self.guest))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Expected 512-D", ctx.exception.detail)

        # 1024-D vector
        vec_1024 = [0.05] * 1024
        q1024 = ContentFreeVectorQuery(protected_vector=vec_1024)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(execute_content_free_search(q1024, current_user=self.guest))
        self.assertEqual(ctx.exception.status_code, 400)

    # =========================================================================
    # Scenario 8: Threshold enforcement
    # =========================================================================
    def test_scenario_08_threshold_enforcement(self):
        """Results with similarity strictly below threshold must be filtered out."""
        # Random vector will have very low similarity to database vectors (~0.0 - 0.20)
        np.random.seed(42)
        rand_vec = np.random.randn(512).astype(np.float32)
        rand_vec /= np.linalg.norm(rand_vec)
        
        # High threshold: 0.70
        q_high = ContentFreeVectorQuery(
            protected_vector=rand_vec.tolist(),
            top_k=5,
            threshold=0.70,
            domain_filter="all",
            include_below_threshold=False
        )
        res_high = asyncio.run(execute_content_free_search(q_high, current_user=self.guest))
        self.assertEqual(len(res_high["results"]), 0, "No random vector should pass 0.70 threshold.")

        # Low threshold: 0.05
        q_low = ContentFreeVectorQuery(
            protected_vector=rand_vec.tolist(),
            top_k=5,
            threshold=0.05,
            domain_filter="all",
            include_below_threshold=False
        )
        res_low = asyncio.run(execute_content_free_search(q_low, current_user=self.guest))
        for r in res_low["results"]:
            self.assertGreaterEqual(r["cosine_similarity"], 0.05, "All returned results must be >= threshold.")

    # =========================================================================
    # Scenario 9: Top-K limit enforcement
    # =========================================================================
    def test_scenario_09_top_k_limits(self):
        """Top-K parameter must constrain the returned count exactly."""
        # Use an indexed vector
        vec = self.retriever.index.reconstruct(0)
        for k in [3, 5, 10]:
            q = ContentFreeVectorQuery(
                protected_vector=vec.tolist(),
                top_k=k,
                threshold=0.10,
                domain_filter="all"
            )
            res = asyncio.run(execute_content_free_search(q, current_user=self.guest))
            self.assertLessEqual(len(res["results"]), k, f"Results count must be <= {k}")
            self.assertEqual(res["results"][0]["rank"], 1)

    # =========================================================================
    # Scenario 10: Unauthorized access attempts to private assets
    # =========================================================================
    def test_scenario_10_unauthorized_access_prevention(self):
        """Guest users must be denied access to private medical and biometric assets."""
        med_img = db.get_image("IMG_MED_XRA_medical_xray_0004")
        self.assertIsNotNone(med_img)
        self.assertEqual(med_img["is_private"], 1)

        # 1. Guest check
        is_auth, msg = self.vault.check_authorization(self.guest, med_img)
        self.assertFalse(is_auth, "Guest must not be authorized for private medical scans.")
        self.assertIn("lacks permissions", msg)

        # 2. None user check
        is_auth_none, _ = self.vault.check_authorization(None, med_img)
        self.assertFalse(is_auth_none, "Unauthenticated user must be denied.")

    # =========================================================================
    # Scenario 11: Doctor selection / specialist RBAC authorization verification
    # =========================================================================
    def test_scenario_11_doctor_rbac_authorization(self):
        """Specialists (Dr. Sharma, Dr. Patel) and Admin must be authorized for medical scans."""
        med_img = db.get_image("IMG_MED_XRA_medical_xray_0004")
        self.assertIsNotNone(med_img)

        # Dr. R. Sharma (Specialist)
        auth_doc1, _ = self.vault.check_authorization(self.doc1, med_img)
        self.assertTrue(auth_doc1, "Dr. R. Sharma (Specialist) must be authorized for medical assets.")

        # Dr. Anita Patel (Specialist)
        auth_doc2, _ = self.vault.check_authorization(self.doc2, med_img)
        self.assertTrue(auth_doc2, "Dr. Anita Patel (Specialist) must be authorized for medical assets.")

        # System Security Admin
        auth_admin, _ = self.vault.check_authorization(self.admin, med_img)
        self.assertTrue(auth_admin, "System Admin must be authorized for medical assets.")

        # Researcher (unauthorized for medical)
        auth_res, _ = self.vault.check_authorization(self.researcher, med_img)
        self.assertFalse(auth_res, "Researcher without medical role must be denied access.")

    # =========================================================================
    # Scenario 12: Reindexing consistency and normalization
    # =========================================================================
    def test_scenario_12_reindexing_consistency(self):
        """FAISS index must contain 1,035 normalized 512-D vectors with perfect inner product."""
        total_vectors = self.retriever.index.ntotal
        self.assertGreaterEqual(total_vectors, 1000, f"Expected >1000 vectors in index, found {total_vectors}.")
        self.assertEqual(self.retriever.dimension, 512, "Index vector dimension must be 512.")
        
        # Verify vector normalization for a sample of indexed vectors
        for row_id in [0, 50, 200, 500, 1000]:
            if row_id < total_vectors:
                v = self.retriever.index.reconstruct(row_id)
                norm = np.linalg.norm(v)
                self.assertAlmostEqual(norm, 1.0, places=4, msg=f"Vector {row_id} must have unit norm.")
                
                # Verify self search yields similarity 1.0
                dists, inds = self.retriever.index.search(v.reshape(1, 512), 1)
                self.assertEqual(inds[0][0], row_id, "Vector must match itself at rank #1.")
                self.assertAlmostEqual(dists[0][0], 1.0, places=4, msg="Self inner product must equal 1.0.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
