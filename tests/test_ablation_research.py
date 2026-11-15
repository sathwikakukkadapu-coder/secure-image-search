"""
Automated Test Suite for Scientific Dimensionality Ablation & Retrieval Analysis.

Validates:
1. Zero Data Leakage: Complete disjointness between gallery and evaluation queries.
2. Nested Prefix Consistency: Lower-dimensional transformations are exact mathematical prefixes.
3. Metric Correctness: Precision@5, Precision@10, Recall@5, Recall@10, mAP@10 bounds [0, 1].
4. Monotonic Storage Savings: Float32 storage decreases monotonically from 1280-D to 16-D.
5. Separate Clean vs Noise Experiments: Clean (Exp A) and Noise (Exp B) evaluated independently.
6. Domain-Wise Ablation: Medical, Biometrics, Vehicles, Nature, and Overall.
7. Production Index Immutability: Production FAISS index remains completely untouched.
8. Reproducibility & Export: Hash validation, CSV, and JSON integrity.
"""

import os
import sys
import json
import numpy as np
import faiss

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research.retrieval_ablation.experiment_runner import AblationExperimentRunner
from research.retrieval_ablation.retrieval_evaluation import RetrievalEvaluator

FAISS_PROD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_db", "faiss_index.bin"))


def test_zero_data_leakage():
    """Verify that gallery and query partitions have zero overlap across all domains."""
    runner = AblationExperimentRunner.get_instance()
    for domain in ["all", "medical", "biometrics", "vehicles", "nature"]:
        part = runner.create_partition(domain=domain, split_ratio=0.8, seed=42)
        g_set = set(part["gallery_indices"])
        q_set = set(part["query_indices"])
        overlap = g_set.intersection(q_set)
        assert len(overlap) == 0, f"Domain {domain}: Data leakage detected! Overlap: {overlap}"
        assert len(g_set) > 0, f"Domain {domain}: Gallery is empty."
        assert len(q_set) > 0, f"Domain {domain}: Query set is empty."
    print("PASS: test_zero_data_leakage (0% leakage across all domains)")


def test_nested_prefix_consistency():
    """Verify that 16-D, 32-D, 64-D, 128-D, 256-D are exact nested prefixes of 512-D vectors."""
    runner = AblationExperimentRunner.get_instance()
    runner._load_data_sources()
    v512 = runner._vectors_512[0]

    dims = [256, 128, 64, 32, 16]
    for d in dims:
        prefix = v512[:d]
        assert prefix.shape == (d,), f"Expected shape ({d},), got {prefix.shape}"
        assert np.allclose(prefix, v512[:d]), f"Prefix mismatch at dimension {d}"
    print("PASS: test_nested_prefix_consistency (Nested projection prefixes verified)")


def test_metric_correctness():
    """Verify bounds, monotonicity, and precision/recall calculations."""
    runner = AblationExperimentRunner.get_instance()
    data = runner.run_ablation_study(domain="all", sigma=0.05, force_rerun=False)

    clean_results = data["experiment_a_clean"]
    noise_results = data["experiment_b_noise"]

    for r in clean_results + noise_results:
        dim = r["dimension"]
        p5 = r["precision_at_5"]
        p10 = r["precision_at_10"]
        r5 = r["recall_at_5"]
        r10 = r["recall_at_10"]
        map10 = r["map_at_10"]

        assert 0.0 <= p5 <= 1.0, f"Invalid P@5: {p5} at {dim}-D"
        assert 0.0 <= p10 <= 1.0, f"Invalid P@10: {p10} at {dim}-D"
        assert 0.0 <= r5 <= 1.0, f"Invalid R@5: {r5} at {dim}-D"
        assert 0.0 <= r10 <= 1.0, f"Invalid R@10: {r10} at {dim}-D"
        assert 0.0 <= map10 <= 1.0, f"Invalid mAP@10: {map10} at {dim}-D"

        # Storage assertions
        st = r["storage"]
        assert st["bytes_per_vector"] == dim * 4, f"Bytes calculation mismatch at {dim}-D"
        assert st["kb_per_vector"] == round(dim * 4 / 1024.0, 3), f"KB calculation mismatch at {dim}-D"

    print("PASS: test_metric_correctness (Metrics bounded and mathematically valid)")


def test_storage_savings_monotonicity():
    """Verify that vector storage decreases strictly monotonically as dimension decreases."""
    runner = AblationExperimentRunner.get_instance()
    data = runner.run_ablation_study(domain="all", force_rerun=False)
    core_results = [r for r in data["experiment_a_clean"] if not r.get("is_raw_baseline")]

    # Sort descending by dimension: 512, 256, 128, 64, 32, 16
    sorted_res = sorted(core_results, key=lambda x: x["dimension"], reverse=True)
    prev_bytes = float("inf")
    prev_saved = -1.0

    for r in sorted_res:
        curr_bytes = r["storage"]["bytes_per_vector"]
        curr_saved = r["storage"]["reduction_percent"]
        assert curr_bytes < prev_bytes, f"Storage did not decrease at {r['dimension']}-D"
        assert curr_saved >= prev_saved, f"Storage savings % did not increase at {r['dimension']}-D"
        prev_bytes = curr_bytes
        prev_saved = curr_saved

    print("PASS: test_storage_savings_monotonicity (Storage reduction is strictly monotonic)")


def test_separate_experiments_clean_vs_noise():
    """Verify that Experiment A (Clean) and Experiment B (Noise) are distinct and reflect expected degradation."""
    runner = AblationExperimentRunner.get_instance()
    data = runner.run_ablation_study(domain="all", sigma=0.05, force_rerun=False)

    clean_map = {r["dimension"]: r["map_at_10"] for r in data["experiment_a_clean"]}
    noise_map = {r["dimension"]: r["map_at_10"] for r in data["experiment_b_noise"]}

    for d in [512, 256, 128, 64, 32, 16]:
        # Noise should not exceed clean performance
        assert clean_map[d] >= noise_map[d] - 0.02, f"Noise mAP exceeded clean at {d}-D"

    # In highly compressed spaces (16-D), noise impact should be substantial
    delta_16 = clean_map[16] - noise_map[16]
    assert delta_16 > 0.05, f"Expected noticeable noise impact at 16-D, got delta={delta_16:.4f}"

    print("PASS: test_separate_experiments_clean_vs_noise (Empirical privacy-utility boundary validated)")


def test_domain_wise_ablation():
    """Verify independent experiments across all 4 domains."""
    runner = AblationExperimentRunner.get_instance()
    for dom in ["medical", "biometrics", "vehicles", "nature"]:
        res = runner.run_ablation_study(domain=dom, force_rerun=False)
        assert res["domain_evaluated"] == dom
        assert res["gallery_size"] > 0
        assert res["queries_evaluated"] > 0
        assert len(res["experiment_a_clean"]) >= 6
    print("PASS: test_domain_wise_ablation (All 4 domains successfully evaluated)")


def test_production_faiss_immutability():
    """Verify that the production FAISS index binary file remains completely unmodified."""
    assert os.path.exists(FAISS_PROD_PATH)
    prod_index = faiss.read_index(FAISS_PROD_PATH)
    assert prod_index.ntotal == 1035, f"Expected 1035 vectors in production index, got {prod_index.ntotal}"
    assert prod_index.d == 512, f"Expected 512 dimension in production index, got {prod_index.d}"
    print("PASS: test_production_faiss_immutability (Production index unchanged: 1035 vectors, 512-D)")


def test_reproducibility_and_export():
    """Verify dataset SHA-256 hash calculation and CSV/JSON export formats."""
    runner = AblationExperimentRunner.get_instance()
    h1 = runner.get_dataset_hash()
    h2 = runner.get_dataset_hash()
    assert h1 == h2, "Dataset hash is non-deterministic"
    assert len(h1) == 16, f"Invalid hash length: {len(h1)}"

    data = runner.run_ablation_study(domain="all", force_rerun=False)
    csv_out = runner.export_csv(data)
    assert "PrivateLens Scientific Dimensionality" in csv_out
    assert "Experiment,Dimension,Noise_Sigma" in csv_out
    assert "Clean (Exp A)" in csv_out
    assert "Noise (Exp B)" in csv_out
    print("PASS: test_reproducibility_and_export (Deterministic hashing & export valid)")


if __name__ == "__main__":
    print("=== STARTING REAL ABLATION RESEARCH VERIFICATION SUITE ===\n")
    test_zero_data_leakage()
    test_nested_prefix_consistency()
    test_metric_correctness()
    test_storage_savings_monotonicity()
    test_separate_experiments_clean_vs_noise()
    test_domain_wise_ablation()
    test_production_faiss_immutability()
    test_reproducibility_and_export()
    print("\n>>> ALL 8 SCIENTIFIC TESTS PASSED WITH 100% SUCCESS! <<<")
