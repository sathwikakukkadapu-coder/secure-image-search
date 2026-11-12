"""
Unit and Integration Test Suite for SecureImage Privacy Protection & Leakage Assessment Benchmark.

Verifies:
1. Secret-Keyed Projection Orthonormality (P_K^T P_K = I_512).
2. Key lifecycle management & rotation.
3. Embedding Inversion Attack (Pre-image reconstruction, SSIM, PSNR, Perceptual distance).
4. Membership Inference Attack (MIA) evaluation (ROC-AUC, curves).
5. Attribute Inference Attack (category reconstruction vs random chance).
6. Similarity Leakage & Cluster Reconstruction (NMI/ARI).
7. Privacy vs Retrieval Utility Trade-off curve & Pareto optimal sigma.
8. FastAPI leakage assessment endpoints.
"""

import os
import sys
import unittest
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import backend.database.db as db
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from backend.services.evaluation.privacy_leakage_benchmark import PrivacyLeakageBenchmark
from backend.api.privacy import (
    get_leakage_benchmark_overview,
    get_privacy_utility_tradeoff_curve,
    run_attribute_inference_benchmark,
    run_similarity_leakage_benchmark
)


class TestPrivacyLeakageBenchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.mgr = KeyedProjectionManager.get_instance(input_dim=1280, protected_dim=512)
        cls.bench = PrivacyLeakageBenchmark.get_instance()

    def test_01_keyed_projection_orthonormality(self):
        """Verifies that the derived projection matrix is orthonormal: P^T P = I_512."""
        P = self.mgr.projection_matrix
        self.assertEqual(P.shape, (1280, 512))
        
        # Check P^T P is approximately Identity matrix
        pt_p = np.dot(P.T, P)
        identity = np.eye(512, dtype=np.float32)
        diff = float(np.max(np.abs(pt_p - identity)))
        self.assertLess(diff, 1e-4, f"Matrix is not orthonormal! Max deviation: {diff}")

    def test_02_keyed_projection_preserves_unit_sphere(self):
        """Verifies that projected vectors lie on the unit hypersphere."""
        rng = np.random.RandomState(42)
        v = rng.randn(1280).astype(np.float32)
        
        # Project with 0 noise
        p0, t0 = self.mgr.project(v, sigma=0.0)
        self.assertEqual(p0.shape, (512,))
        self.assertAlmostEqual(float(np.linalg.norm(p0)), 1.0, places=4)
        self.assertGreater(t0, 0.0)

        # Project with calibrated noise
        p_noisy, _ = self.mgr.project(v, sigma=0.05)
        self.assertEqual(p_noisy.shape, (512,))
        self.assertAlmostEqual(float(np.linalg.norm(p_noisy)), 1.0, places=4)

    def test_03_key_rotation_and_metadata_safety(self):
        """Verifies key rotation generates a new version and never leaks raw key bytes."""
        initial_meta = self.mgr.get_public_metadata()
        self.assertIn("key_fingerprint", initial_meta)
        self.assertFalse(initial_meta["secret_key_exposed"])
        self.assertNotIn("secret_key", initial_meta)

        initial_version = initial_meta["version"]
        res = self.mgr.rotate_key()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["version"], initial_version + 1)
        
        new_meta = self.mgr.get_public_metadata()
        self.assertEqual(new_meta["version"], initial_version + 1)

    def test_04_inversion_attack_benchmark(self):
        """Verifies pre-image inversion attack metrics and visual artifacts generation."""
        res = self.bench.run_embedding_inversion_attack(iterations=10)
        
        self.assertEqual(res["status"], "completed")
        self.assertIn("metrics", res)
        m = res["metrics"]
        
        self.assertIn("unprotected_raw", m)
        self.assertIn("keyed_protected", m)
        self.assertIn("keyed_protected_with_noise", m)

        raw_metric = m["unprotected_raw"]
        keyed_metric = m["keyed_protected"]
        noise_metric = m["keyed_protected_with_noise"]

        self.assertGreaterEqual(raw_metric["ssim"], 0.0)
        self.assertLessEqual(raw_metric["ssim"], 1.0)
        self.assertGreaterEqual(keyed_metric["ssim"], 0.0)
        self.assertLessEqual(keyed_metric["ssim"], 1.0)
        self.assertGreaterEqual(noise_metric["ssim"], 0.0)
        self.assertLessEqual(noise_metric["ssim"], 1.0)
        
        # Visualizations present as base64 data URIs
        vis = res["visualizations"]
        self.assertTrue(vis["original"].startswith("data:image/png;base64,"))
        self.assertTrue(vis["reconstructed_raw"].startswith("data:image/png;base64,"))
        self.assertTrue(vis["reconstructed_keyed"].startswith("data:image/png;base64,"))
        self.assertTrue(vis["reconstructed_noise"].startswith("data:image/png;base64,"))

    def test_05_membership_inference_attack_benchmark(self):
        """Verifies Membership Inference Attack (MIA) evaluation across defenses."""
        res = self.bench.run_membership_inference_attack(sample_size=15)
        
        self.assertEqual(res["status"], "completed")
        self.assertIn("unprotected_raw", res)
        self.assertIn("keyed_protected", res)
        self.assertIn("keyed_protected_with_noise", res)

        raw_mia = res["unprotected_raw"]
        noise_mia = res["keyed_protected_with_noise"]

        self.assertGreaterEqual(raw_mia["roc_auc"], 0.0)
        self.assertLessEqual(raw_mia["roc_auc"], 1.0)
        self.assertGreaterEqual(noise_mia["roc_auc"], 0.0)
        self.assertLessEqual(noise_mia["roc_auc"], 1.0)
        self.assertGreater(len(raw_mia["roc_curve"]), 0)

    def test_06_attribute_inference_attack_benchmark(self):
        """Verifies semantic category attribute inference evaluation."""
        res = self.bench.run_attribute_inference_attack()
        
        self.assertEqual(res["status"], "completed")
        self.assertGreaterEqual(len(res["target_classes"]), 2)
        self.assertGreaterEqual(len(res["evaluations"]), 4)

        for ev in res["evaluations"]:
            self.assertGreaterEqual(ev["classification_accuracy"], 0.0)
            self.assertLessEqual(ev["classification_accuracy"], 1.0)
            self.assertGreaterEqual(ev["macro_f1"], 0.0)
            self.assertLessEqual(ev["macro_f1"], 1.0)

    def test_07_similarity_leakage_benchmark(self):
        """Verifies similarity clustering recovery assessment."""
        res = self.bench.run_similarity_leakage_attack()
        
        self.assertEqual(res["status"], "completed")
        self.assertGreaterEqual(len(res["evaluations"]), 4)
        for ev in res["evaluations"]:
            self.assertGreaterEqual(ev["nmi"], 0.0)
            self.assertLessEqual(ev["nmi"], 1.0)

    def test_08_privacy_utility_tradeoff_curve(self):
        """Verifies privacy-utility tradeoff curve generation and Pareto optimal sigma."""
        res = self.bench.compute_privacy_utility_tradeoff(sigmas=[0.0, 0.02, 0.05, 0.10, 0.20])
        
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["pareto_optimal_sigma"], 0.05)
        self.assertEqual(len(res["tradeoff_points"]), 5)
        for pt in res["tradeoff_points"]:
            self.assertGreaterEqual(pt["precision_at_5"], 0.0)
            self.assertLessEqual(pt["precision_at_5"], 1.0)
            self.assertGreaterEqual(pt["inversion_ssim"], 0.0)
            self.assertLessEqual(pt["inversion_ssim"], 1.0)

    def test_09_fastapi_leakage_endpoints(self):
        """Verifies that FastAPI leakage assessment route handlers execute successfully."""
        # 1. Overview
        data_ov = get_leakage_benchmark_overview(current_user={"user_id": "TEST_ADMIN", "role": "ADMIN"})
        self.assertEqual(data_ov["status"], "active")
        self.assertIn("keyed_protection", data_ov)

        # 2. Tradeoff curve
        data_to = get_privacy_utility_tradeoff_curve(current_user={"user_id": "TEST_ADMIN", "role": "ADMIN"})
        self.assertEqual(data_to["status"], "completed")
        self.assertGreaterEqual(len(data_to["tradeoff_points"]), 5)

        # 3. Attribute inference
        data_att = run_attribute_inference_benchmark(current_user={"user_id": "TEST_ADMIN", "role": "ADMIN"})
        self.assertEqual(data_att["status"], "completed")

        # 4. Similarity leakage
        data_sim = run_similarity_leakage_benchmark(current_user={"user_id": "TEST_ADMIN", "role": "ADMIN"})
        self.assertEqual(data_sim["status"], "completed")


if __name__ == "__main__":
    unittest.main()
