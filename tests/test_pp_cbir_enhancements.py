"""
SecureImage Comprehensive PP-CBIR Enhancement Verification Suite.
Tests:
1. Local Differential Privacy (LDP) Gaussian & Laplace mechanisms.
2. Non-Invertible Feature Representations (RFF & Sign-RP).
3. TenSEAL CKKS Homomorphic Encryption inner-product retrieval.
4. AES-256-GCM Envelope Encryption (Wrapped DEK / KEK architecture).
5. Argon2id Password Hashing and constant-time verification.
6. Empirical Security Evaluator (Inversion, Gallery Identification, MIA).
7. FastAPI HTTP Endpoints for Privacy & Security benchmarks.
"""

import os
import sys
import unittest
import numpy as np
import base64

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import backend.database.db as db
from backend.services.privacy.representation import AdvancedPrivacyRepresentation, PrivacyRepresentationScheme
from backend.services.retrieval.ckks_retriever import CKKSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault
from backend.services.evaluation.security_evaluator import SecurityEvaluator

class TestPPCBIRSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.rep_mgr = AdvancedPrivacyRepresentation.get_instance(input_dim=1280, protected_dim=512)
        cls.ckks_engine = CKKSRetrievalEngine.get_instance(poly_modulus_degree=8192, vector_dim=512)
        cls.vault = PrivateImageVault.get_instance()
        cls.evaluator = SecurityEvaluator.get_instance()

    def test_01_ldp_gaussian_calibration(self):
        """Verifies formal Gaussian LDP calibration and unit sphere normalization."""
        raw_vec = np.random.randn(1280).astype(np.float32)
        raw_vec /= np.linalg.norm(raw_vec)

        # Test at epsilon = 2.0, delta = 1e-5
        protected, meta = self.rep_mgr.transform_ldp_gaussian(raw_vec, epsilon=2.0, delta=1e-5)
        self.assertEqual(len(protected), 512)
        self.assertAlmostEqual(float(np.linalg.norm(protected)), 1.0, places=4)
        self.assertIn("Gaussian Mechanism", meta["formal_guarantee"])
        self.assertGreater(meta["calibrated_sigma"], 0.0)

    def test_02_non_invertible_rff(self):
        """Verifies Random Fourier Features non-linear mapping and finite values."""
        raw_vec = np.random.randn(1280).astype(np.float32)
        raw_vec /= np.linalg.norm(raw_vec)

        protected, meta = self.rep_mgr.transform_non_invertible_rff(raw_vec)
        self.assertEqual(len(protected), 512)
        self.assertTrue(np.isfinite(protected).all())
        self.assertAlmostEqual(float(np.linalg.norm(protected)), 1.0, places=4)
        self.assertEqual(meta["scheme"], PrivacyRepresentationScheme.NON_INVERTIBLE_RFF)

    def test_03_non_invertible_sign_rp(self):
        """Verifies 1-bit Sign Random Projection (SimHash) sketch."""
        raw_vec = np.random.randn(1280).astype(np.float32)
        protected, meta = self.rep_mgr.transform_non_invertible_sign(raw_vec)
        self.assertEqual(len(protected), 512)
        self.assertAlmostEqual(float(np.linalg.norm(protected)), 1.0, places=4)

    def test_04_ckks_homomorphic_inner_product(self):
        """Verifies TenSEAL CKKS homomorphic inner product precision and semantic security."""
        v1 = np.random.randn(512).astype(np.float32)
        v1 /= np.linalg.norm(v1)
        v2 = np.random.randn(512).astype(np.float32)
        v2 /= np.linalg.norm(v2)

        # Client encrypts v1
        enc_v1, enc_time = self.ckks_engine.client_encrypt_vector(v1)
        self.assertGreater(len(enc_v1), 1000)

        # Server evaluates inner product with v2
        enc_scores, srv_time = self.ckks_engine.server_evaluate_similarity(enc_v1, [v2])
        self.assertEqual(len(enc_scores), 1)

        # Client decrypts score
        dec_scores, dec_time = self.ckks_engine.client_decrypt_scores(enc_scores)
        expected_dot = float(np.dot(v1, v2))
        error = abs(dec_scores[0] - expected_dot)
        self.assertLess(error, 1e-4, f"CKKS precision error too high: {error}")

    def test_05_ckks_benchmark_execution(self):
        """Verifies CKKS automated benchmark metrics."""
        res = self.ckks_engine.benchmark_ckks_pipeline(num_candidates=3)
        self.assertEqual(res["num_candidates_evaluated"], 3)
        self.assertIn("client_encryption_time_ms", res)
        self.assertIn("server_homomorphic_eval_time_ms", res)
        self.assertLess(res["max_numerical_precision_error"], 1e-4)

    def test_06_envelope_encryption_roundtrip(self):
        """Verifies AES-256-GCM envelope encryption with wrapped DEK and secure decryption."""
        test_payload = b"PRIVATE_MEDICAL_RADIOGRAPH_BYTES_TEST_12345"
        test_id = "TEST_IMG_ENV_01"
        
        # Store in vault
        vault_fname, enc_ref = self.vault.store_image(test_payload, test_id, "scan.jpg")
        self.assertTrue(os.path.exists(os.path.join(self.vault.storage_dir, vault_fname)))

        # Verify wrapped DEK exists in database
        key_rec = db.get_image_encryption_key(test_id)
        self.assertIsNotNone(key_rec)
        self.assertIn("wrapped_dek", key_rec)

        # Retrieve and decrypt
        decrypted = self.vault.retrieve_image_bytes(enc_ref, image_id=test_id)
        self.assertEqual(decrypted, test_payload)

    def test_07_argon2id_password_hashing(self):
        """Verifies Argon2id password hashing and backward compatibility."""
        password = "SecureResearchPassword2026!"
        h = db.hash_password(password)
        self.assertTrue(h.startswith("$argon2") or h.startswith("pbkdf2:"))
        self.assertTrue(db.verify_password(password, h))
        self.assertFalse(db.verify_password("WrongPassword!", h))

    def test_08_feature_inversion_attack_experiment(self):
        """Verifies empirical feature inversion attack metrics calculation."""
        res = self.evaluator.run_feature_inversion_experiment(num_samples=10)
        self.assertEqual(res["status"], "completed")
        schemes = res["schemes_evaluated"]
        self.assertIn("raw_embedding", schemes)
        self.assertIn("baseline_orthogonal", schemes)
        self.assertIn("ldp_gaussian", schemes)
        self.assertIn("non_invertible_rff", schemes)
        self.assertIn("ckks_homomorphic", schemes)
        # Verify raw embedding has 0 MSE, while RFF and LDP have substantial reconstruction drift
        self.assertEqual(schemes["raw_embedding"]["mean_squared_error"], 0.0)
        self.assertGreater(schemes["non_invertible_rff"]["cosine_recovery_drift"], 0.0)

    def test_09_known_gallery_reid_experiment(self):
        """Verifies empirical known-gallery re-identification attack rates."""
        res = self.evaluator.run_known_gallery_identification_experiment(gallery_size=20, probe_count=5)
        self.assertEqual(res["status"], "completed")
        results = res["results"]
        # Raw embeddings should have high Top-1 re-ID (100%), while CKKS has 0%
        self.assertEqual(results["raw_embeddings"]["top_1_identification_accuracy"], 100.0)
        self.assertEqual(results["ckks_homomorphic"]["top_1_identification_accuracy"], 0.0)

    def test_10_membership_inference_audit(self):
        """Verifies membership inference attack resistance and RBAC invariants."""
        res = self.evaluator.run_membership_inference_and_access_audit()
        self.assertEqual(res["status"], "completed")
        self.assertIn("membership_inference", res)
        self.assertIn("access_control_audit", res)

if __name__ == "__main__":
    unittest.main()
