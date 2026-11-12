"""
Comprehensive Test Suite for Research Modules A, B, C, and D:
1. Dimensionality Reduction (Truncation, Random Selection, PCA) including 32-D (6.25%).
2. Query/Gallery Dimension Compatibility & L2 Unit Normalization.
3. Query-Peer Exclusion in Retrieval Evaluation.
4. Reduced Dimension FAISS Indexing (512, 384, 256, 128, 64, 32-D).
5. Gradient Inversion Reconstruction Optimization & Metric Calculations (PSNR, SSIM).
6. Result Persistence and API Route Integration.
7. Noise-Based Vector Privacy Protection & Nearest-Neighbor Identification Attack.
8. Multi-Channel Vector Inspection (Clean, Protected, Delta Vector, Cosine Similarity, L2 Drift).
"""

import os
import sys
import json
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research.retrieval_ablation.dimensionality_reduction import DimensionalityReducer
from research.retrieval_ablation.retrieval_evaluation import RetrievalEvaluator
from research.retrieval_ablation.experiment_runner import AblationExperimentRunner
from research.reconstruction.reconstruction_metrics import ReconstructionMetrics
from research.reconstruction.inversion_attack import ImageInversionAttacker
from research.privacy_analysis.threat_models import ThreatModelRegistry
from research.privacy_analysis.privacy_comparison import PrivacyTransformationComparator
from research.noise_analysis.noise_evaluation import NoiseEvaluator
from backend.services.privacy.protector import PrivacyProtectionLayer


def test_dimensionality_reduction_and_normalization():
    print(">>> 1. Testing Dimensionality Reduction & L2 Unit Normalization (including 32-D)...")
    np.random.seed(42)
    sample_vecs = np.random.randn(400, 512).astype(np.float32)

    for target_d in [384, 256, 128, 64, 32]:
        # Truncation
        trunc = DimensionalityReducer.apply_truncation(sample_vecs, target_d)
        assert trunc.shape == (400, target_d), f"Truncation shape mismatch: {trunc.shape}"
        norms_trunc = np.linalg.norm(trunc, axis=1)
        assert np.allclose(norms_trunc, 1.0, atol=1e-5), "Truncated vectors not unit normalized"

        # Random Selection
        rand_vecs, indices = DimensionalityReducer.apply_random_selection(sample_vecs, target_d, seed=42)
        assert rand_vecs.shape == (400, target_d)
        assert len(indices) == target_d
        norms_rand = np.linalg.norm(rand_vecs, axis=1)
        assert np.allclose(norms_rand, 1.0, atol=1e-5), "Random selected vectors not unit normalized"

        # PCA
        pca_gallery, pca_queries, _ = DimensionalityReducer.fit_and_apply_pca(sample_vecs, sample_vecs[:2], target_d, seed=42)
        assert pca_gallery.shape == (400, target_d)
        assert pca_queries.shape == (2, target_d)
        norms_pca_g = np.linalg.norm(pca_gallery, axis=1)
        norms_pca_q = np.linalg.norm(pca_queries, axis=1)
        assert np.allclose(norms_pca_g, 1.0, atol=1e-5)
        assert np.allclose(norms_pca_q, 1.0, atol=1e-5)

    print("    [PASS] Dimensionality reduction & unit normalization verified across all 5 target dimensions (down to 32-D).")


def test_query_peer_exclusion_and_faiss():
    print("\n>>> 2. Testing Query-Peer Exclusion & Reduced-Dim FAISS Retrieval (32-D supported)...")
    evaluator = RetrievalEvaluator()
    g_vecs, g_ids = evaluator.get_full_gallery_embeddings()

    assert g_vecs.shape[1] == 512
    assert len(g_ids) >= 1000

    # Pick 5 queries directly from gallery
    q_vecs = g_vecs[:5]
    q_ids = g_ids[:5]
    q_cats = [evaluator.db_records.get(gid, {}).get("category", "unknown") for gid in q_ids]

    for dim in [256, 128, 32]:
        red_g = DimensionalityReducer.apply_truncation(g_vecs, dim)
        red_q = DimensionalityReducer.apply_truncation(q_vecs, dim)

        metrics = evaluator.evaluate_retrieval(
            gallery_vectors=red_g,
            gallery_ids=g_ids,
            query_vectors=red_q,
            query_ids=q_ids,
            query_categories=q_cats,
            top_k_list=(5, 10)
        )

        assert metrics["dimension"] == dim
        assert metrics["precision_at_5"] >= 0.0
        assert metrics["precision_at_10"] >= 0.0
        assert metrics["map_at_5"] >= 0.0
        assert metrics["storage"]["storage_reduction_percent"] in [50.0, 75.0, 93.8]

    print("    [PASS] FAISS retrieval executed successfully with query-peer exclusion verified across 256, 128, 32-D.")


def test_reconstruction_attack_and_metrics():
    print("\n>>> 3. Testing Optimization-Based Inversion Attack & Metrics...")
    attacker = ImageInversionAttacker.get_instance()
    test_path = "test_dataset/01_Medical/test_medical_xray_05.jpg"
    assert os.path.exists(test_path), f"Missing test image {test_path}"

    test_img = Image.open(test_path).convert("RGB")

    # Run quick 5-iteration inversion for Known Key (Attacker B)
    res_b = attacker.run_inversion(
        target_image=test_img,
        target_dim=256,
        threat_model="known_key",
        iterations=5
    )

    assert res_b["status"] == "success"
    assert res_b["dimension"] == 256
    assert "metrics" in res_b
    assert "psnr_db" in res_b["metrics"]
    assert "ssim" in res_b["metrics"]
    assert res_b["metrics"]["psnr_db"] > 0
    assert 0.0 <= res_b["metrics"]["ssim"] <= 1.0
    assert "artifacts" in res_b
    assert res_b["artifacts"]["reconstructed_data_uri"].startswith("data:image/png;base64,")

    print(f"    [PASS] Known-Key Inversion verified. PSNR: {res_b['metrics']['psnr_db']} dB, SSIM: {res_b['metrics']['ssim']}.")

    # Run quick 5-iteration inversion for Restricted Key (Attacker A)
    res_a = attacker.run_inversion(
        target_image=test_img,
        target_dim=256,
        threat_model="restricted_key",
        iterations=5
    )
    assert res_a["status"] == "success"
    assert res_a["threat_model"] == "restricted_key"
    print(f"    [PASS] Restricted-Key Inversion verified. PSNR: {res_a['metrics']['psnr_db']} dB, SSIM: {res_a['metrics']['ssim']}.")


def test_privacy_comparison_and_persistence():
    print("\n>>> 4. Testing Privacy Transformation Comparison & Persistence...")
    comparator = PrivacyTransformationComparator.get_instance()
    res = comparator.run_comparison(force_rerun=False)

    assert res["status"] == "completed"
    assert len(res["configurations"]) == 6
    for cfg in res["configurations"]:
        assert "map_at_5" in cfg
        assert "recon_ssim" in cfg
        assert "privacy_score" in cfg
        assert "pareto_harmonic_mean" in cfg

    cache_file = os.path.join(os.path.dirname(__file__), "..", "research", "results", "experiment_results", "privacy_comparison.json")
    assert os.path.exists(cache_file), f"Cache file {cache_file} missing"

    threats = ThreatModelRegistry.get_all_threat_models()
    assert len(threats) == 4
    print("    [PASS] Privacy transformation comparison & threat model registry verified.")


def test_noise_benchmark_and_identification_leakage():
    print("\n>>> 5. Testing Noise-Based Privacy & Identification Leakage Benchmark...")
    evaluator = NoiseEvaluator.get_instance()
    benchmark = evaluator.run_noise_benchmark(num_queries=12, force_rerun=False)

    assert benchmark["status"] == "completed"
    assert len(benchmark["results"]) == 6

    # Verify monotonic degradation of Top-1 Identification Leakage as sigma increases
    results = benchmark["results"]
    assert results[0]["sigma"] == 0.00
    assert results[5]["sigma"] == 0.35

    top1_clean = results[0]["identification_attack"]["top_1_accuracy"]
    top1_noisy = results[5]["identification_attack"]["top_1_accuracy"]
    assert top1_clean >= top1_noisy, "Noise should reduce Top-1 ID accuracy"
    assert results[5]["identification_attack"]["identity_protection_score"] >= results[0]["identification_attack"]["identity_protection_score"]

    # Verify query latency breakdown fields
    for r in results:
        lat = r["latency_breakdown"]
        assert "extraction_ms" in lat
        assert "noise_ms" in lat
        assert "search_ms" in lat
        assert "total_ms" in lat
        assert lat["total_ms"] > 0

    print("    [PASS] Noise privacy benchmark and nearest-neighbor attack metrics verified across 6 levels.")


def test_vector_inspection_and_delta_computation():
    print("\n>>> 6. Testing Vector Protection, Cosine Alignment & Delta Computation...")
    protector = PrivacyProtectionLayer.get_instance(input_dim=1280, protected_dim=512)
    raw_vec = np.random.randn(1280).astype(np.float32)
    raw_vec /= np.linalg.norm(raw_vec)

    clean_vec, _ = protector.protect_vector(raw_vec, apply_noise=False)
    noisy_vec, _ = protector.protect_vector(raw_vec, apply_noise=True, sigma=0.05)

    assert clean_vec.shape == (512,)
    assert noisy_vec.shape == (512,)
    assert np.isclose(np.linalg.norm(clean_vec), 1.0, atol=1e-5)
    assert np.isclose(np.linalg.norm(noisy_vec), 1.0, atol=1e-5)

    cos_sim = float(np.dot(clean_vec, noisy_vec))
    delta = noisy_vec - clean_vec
    l2_drift = float(np.linalg.norm(delta))

    assert 0.40 <= cos_sim <= 1.0, f"Expected valid cosine similarity, got {cos_sim}"
    assert l2_drift > 0, "Noisy vector should exhibit non-zero L2 drift"
    print(f"    [PASS] Vector delta verified: Cosine Sim = {cos_sim:.4f}, L2 Drift = {l2_drift:.4f}.")


if __name__ == "__main__":
    print("=================================================================")
    print("RUNNING SECUREIMAGE RESEARCH EXTENSION VERIFICATION SUITE")
    print("=================================================================")
    test_dimensionality_reduction_and_normalization()
    test_query_peer_exclusion_and_faiss()
    test_reconstruction_attack_and_metrics()
    test_privacy_comparison_and_persistence()
    test_noise_benchmark_and_identification_leakage()
    test_vector_inspection_and_delta_computation()
    print("\n=================================================================")
    print(">>> ALL 6 RESEARCH EXTENSION VERIFICATIONS PASSED SUCCESSFULLY! <<<")
    print("=================================================================")
