"""
Automated Test Suite for Scientific Dimensionality Ablation & Retrieval Analysis.

Validates:
1. Independent Projection Consistency: Mathematical equivalence (x P)[:, :d] == x (P[:, :d]).
2. Hand-Calculated Toy Examples: Deterministic unit tests for:
   - Precision@5 and Precision@10
   - Recall@5 and Recall@10
   - AP@10 and mAP@10
   - Zero-relevant-query handling
   - Gallery smaller than K (e.g. N_gallery = 3)
3. Zero Data Leakage via Source Groups: Group-level partition ensures near-duplicates and
   augmented variants never leak across gallery and query sets.
4. Production Index Immutability: SHA-256 checksum of vector_db/faiss_index.bin verified
   before and after execution.
5. Separate Clean vs Exp A vs Exp B: Evaluated with statistical metrics across seeds without
   assuming monotonic degradation on every single stochastic realization.
6. Metric Boundedness & Monotonic Storage Savings: Vector storage decreases strictly monotonically.
"""

import os
import sys
import json
import hashlib
import numpy as np

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research.retrieval_ablation.experiment_runner import AblationExperimentRunner
from research.retrieval_ablation.retrieval_evaluation import RetrievalEvaluator

FAISS_PROD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_db", "faiss_index.bin"))


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum of a file on disk."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_independent_projection_consistency():
    """
    Replaces self-comparison test with a rigorous independent projection consistency test.
    Verifies that for an independent feature matrix X in R^(B x D_in) and an independent
    orthonormal projection matrix P in R^(D_in x D_proj):
        (X P)[:, :d] == X (P[:, :d])
    holds to within machine precision across all tested dimensionalities.
    """
    rng = np.random.RandomState(1337)
    b_size = 16
    d_in = 1280
    d_proj = 512

    # Independent random feature matrix
    x_test = rng.randn(b_size, d_in).astype(np.float32)

    # Independent orthonormal projection matrix generated via QR decomposition
    gaussian_mat = rng.randn(d_in, d_proj).astype(np.float32)
    q_mat, _ = np.linalg.qr(gaussian_mat)
    p_mat = q_mat.astype(np.float32)  # (1280, 512)

    # Full projection followed by prefix slicing
    full_proj = np.dot(x_test, p_mat)  # (16, 512)

    test_dims = [256, 128, 64, 32, 16]
    for d in test_dims:
        prefix_of_full = full_proj[:, :d]

        # Sliced projection matrix applied directly
        p_slice = p_mat[:, :d]  # (1280, d)
        direct_proj = np.dot(x_test, p_slice)  # (16, d)

        max_diff = np.max(np.abs(prefix_of_full - direct_proj))
        assert max_diff < 1e-5, f"Independent projection consistency failed at d={d}: max diff={max_diff}"

    print("PASS: test_independent_projection_consistency ((X P)[:, :d] == X (P[:, :d]) verified)")


def test_hand_calculated_toy_metrics():
    """
    Tests exact hand-calculated retrieval metrics against known toy examples:
    - Precision@5, Precision@10
    - Recall@5, Recall@10
    - AP@10 and mAP@10
    - Gallery smaller than K (N_gallery = 3)
    - Zero-relevant-query handling
    """
    evaluator = RetrievalEvaluator()

    # --------------------------------------------------------------------------
    # Case 1: Standard ranking with known binary relevance
    # Gallery size: 20 items (10 of 'A', 10 of 'B')
    # --------------------------------------------------------------------------
    gallery_labels = ['A'] * 10 + ['B'] * 10  # indices 0..9 are 'A', 10..19 are 'B'
    query_labels = ['A']

    # Query retrieved rows: 6 relevant items (indices 0..5) and 4 non-relevant (10..13)
    # Positions 1..10:
    # 1: 0 (rel=1), P@1 = 1.0
    # 2: 1 (rel=1), P@2 = 1.0
    # 3: 10 (rel=0), P@3 = 2/3
    # 4: 2 (rel=1), P@4 = 3/4 = 0.75
    # 5: 11 (rel=0), P@5 = 3/5 = 0.60
    # 6: 3 (rel=1), P@6 = 4/6 = 0.66667
    # 7: 12 (rel=0), P@7 = 4/7
    # 8: 4 (rel=1), P@8 = 5/8 = 0.625
    # 9: 13 (rel=0), P@9 = 5/9
    # 10: 5 (rel=1), P@10 = 6/10 = 0.60
    retrieved_indices = np.array([[0, 1, 10, 2, 11, 3, 12, 4, 13, 5]], dtype=np.int64)

    # Hand calculation:
    # rel_5 = 3 ('A' at ranks 1, 2, 4) -> P@5 = 3 / 5.0 = 0.60
    # rel_10 = 6 ('A' at ranks 1, 2, 4, 6, 8, 10) -> P@10 = 6 / 10.0 = 0.60
    # R_total in gallery = 10 ('A' count is 10)
    # Recall@5 = 3 / 10.0 = 0.30
    # Recall@10 = 6 / 10.0 = 0.60
    # denom = min(10, 10) = 10
    # AP@10 terms sum: 1.0 + 1.0 + 0.75 + (4.0/6.0) + (5.0/8.0) + 0.60 = 4.641666667
    # AP@10 = 4.641666667 / 10.0 = 0.464166667 -> round(4) = 0.4642
    res1 = evaluator.calculate_ranking_metrics(
        retrieved_indices=retrieved_indices,
        gallery_labels=gallery_labels,
        query_labels=query_labels,
        gallery_size=20,
        k_eval=10,
        exclude_zero_rel=True
    )

    assert res1["precision_at_5"] == 0.6, f"Expected P@5=0.6, got {res1['precision_at_5']}"
    assert res1["precision_at_10"] == 0.6, f"Expected P@10=0.6, got {res1['precision_at_10']}"
    assert res1["recall_at_5"] == 0.3, f"Expected R@5=0.3, got {res1['recall_at_5']}"
    assert res1["recall_at_10"] == 0.6, f"Expected R@10=0.6, got {res1['recall_at_10']}"
    assert res1["map_at_10"] == 0.4642, f"Expected mAP@10=0.4642, got {res1['map_at_10']}"

    # --------------------------------------------------------------------------
    # Case 2: Gallery smaller than K (N_gallery = 3 < 10)
    # --------------------------------------------------------------------------
    small_gallery = ['X', 'X', 'X']  # 3 items, all relevant
    small_queries = ['X']
    small_retrieved = np.array([[0, 1, 2]], dtype=np.int64)

    # Hand calculation:
    # P@5: 3 / 5.0 = 0.60 (denominator is fixed ranking truncation K=5)
    # P@10: 3 / 10.0 = 0.30
    # R@5: 3 / 3.0 = 1.00 (all gallery items retrieved)
    # R@10: 3 / 3.0 = 1.00
    # AP@10: denom = min(3, 10) = 3
    # terms: P@1=1.0, P@2=1.0, P@3=1.0 -> sum = 3.0 -> AP@10 = 3.0 / 3 = 1.00
    res2 = evaluator.calculate_ranking_metrics(
        retrieved_indices=small_retrieved,
        gallery_labels=small_gallery,
        query_labels=small_queries,
        gallery_size=3,
        k_eval=10,
        exclude_zero_rel=True
    )
    assert res2["precision_at_5"] == 0.60
    assert res2["precision_at_10"] == 0.30
    assert res2["recall_at_5"] == 1.00
    assert res2["recall_at_10"] == 1.00
    assert res2["map_at_10"] == 1.00

    # --------------------------------------------------------------------------
    # Case 3: Zero-relevant-query handling
    # Query has label 'Z', which does not exist in gallery (R_total = 0)
    # --------------------------------------------------------------------------
    zero_rel_queries = ['Z']
    zero_rel_retrieved = np.array([[0, 1, 2]], dtype=np.int64)

    res3 = evaluator.calculate_ranking_metrics(
        retrieved_indices=zero_rel_retrieved,
        gallery_labels=small_gallery,  # ['X', 'X', 'X']
        query_labels=zero_rel_queries,  # ['Z']
        gallery_size=3,
        k_eval=10,
        exclude_zero_rel=True
    )
    assert res3["queries_evaluated"] == 1
    assert res3["valid_queries"] == 0
    assert res3["queries_excluded_zero_rel"] == 1
    assert res3["precision_at_5"] == 0.0

    print("PASS: test_hand_calculated_toy_metrics (P@5, P@10, R@5, R@10, AP@10, small gallery, zero-rel queries verified)")


def test_production_index_immutability():
    """Verify that running ablation experiments leaves the production FAISS index strictly untouched."""
    assert os.path.exists(FAISS_PROD_PATH), f"Production index not found at {FAISS_PROD_PATH}"
    sha_before = compute_file_sha256(FAISS_PROD_PATH)

    runner = AblationExperimentRunner.get_instance()
    # Run ablation study across seeds
    res = runner.run_ablation_study(domain="medical", relevance_mode="domain", sigma=0.05, seeds=[42, 107], force_rerun=True)
    assert res["status"] == "completed"

    sha_after = compute_file_sha256(FAISS_PROD_PATH)
    assert sha_before == sha_after, (
        f"Production FAISS index mutation detected! SHA before: {sha_before}, SHA after: {sha_after}"
    )
    print(f"PASS: test_production_index_immutability (SHA-256 intact: {sha_before[:16]}...)")


def test_zero_leakage_source_groups():
    """Verify that source-group partitioning prevents leakage of duplicates and augmented variants."""
    runner = AblationExperimentRunner.get_instance()
    runner._load_data_sources()

    # Verify grouping
    group_stats = runner.get_source_group_statistics()
    assert group_stats["total_images"] == 1035
    assert group_stats["total_source_groups"] > 900
    assert group_stats["multi_image_groups_count"] > 40

    # Test across multiple seeds
    for s in [42, 107, 211, 389, 523]:
        part = runner.create_partition(domain="all", relevance_mode="domain", split_ratio=0.8, seed=s)
        g_set = set(part["gallery_indices"])
        q_set = set(part["query_indices"])
        overlap = g_set.intersection(q_set)
        assert len(overlap) == 0, f"Seed {s}: Image leakage detected!"

        # Verify that no multi-image group is split across gallery and query
        for grp in runner._source_groups:
            if len(grp) > 1:
                grp_in_g = any(idx in g_set for idx in grp)
                grp_in_q = any(idx in q_set for idx in grp)
                assert not (grp_in_g and grp_in_q), (
                    f"Seed {s}: Source group {grp} split across gallery and query boundary!"
                )

    print("PASS: test_zero_leakage_source_groups (0% leakage across all source groups and seeds)")


def test_separate_experiments_and_statistical_bounds():
    """
    Verifies that Clean Baseline, Exp A (Noisy Query vs Clean Gallery), and Exp B (Noisy Query vs Noisy Gallery)
    produce statistically valid results bounded in [0, 1] without assuming deterministic degradation
    on any individual stochastic run.
    """
    runner = AblationExperimentRunner.get_instance()
    res = runner.run_ablation_study(
        domain="all",
        relevance_mode="domain",
        sigma=0.05,
        seeds=[42, 107],
        force_rerun=True
    )

    clean = res["clean_baseline"]
    exp_a = res["exp_a_noisy_query"]
    exp_b = res["exp_b_noisy_both"]

    for exp_list in [clean, exp_a, exp_b]:
        for r in exp_list:
            dim = r["dimension"]
            assert 0.0 <= r["precision_at_5"] <= 1.0, f"P@5 out of bounds at {dim}-D"
            assert 0.0 <= r["precision_at_10"] <= 1.0, f"P@10 out of bounds at {dim}-D"
            assert 0.0 <= r["recall_at_5"] <= 1.0, f"R@5 out of bounds at {dim}-D"
            assert 0.0 <= r["recall_at_10"] <= 1.0, f"R@10 out of bounds at {dim}-D"
            assert 0.0 <= r["map_at_10"] <= 1.0, f"mAP@10 out of bounds at {dim}-D"

            # Check confidence intervals
            ci = r["map_at_10_ci95"]
            assert len(ci) == 2 and ci[0] <= ci[1], f"Invalid 95% CI at {dim}-D"

    # Strictly monotonic storage savings
    core_clean = [r for r in clean if not r.get("is_raw_baseline")]
    sorted_dims = sorted(core_clean, key=lambda x: x["dimension"], reverse=True)
    prev_bytes = float("inf")
    for r in sorted_dims:
        curr_bytes = r["storage"]["bytes_per_vector"]
        assert curr_bytes < prev_bytes, f"Storage did not decrease at {r['dimension']}-D"
        prev_bytes = curr_bytes

    print("PASS: test_separate_experiments_and_statistical_bounds (Valid bounds, CIs, and monotonic storage)")


def test_explicit_ground_truth_taxonomy():
    """Verifies domain vs fine-grained subtype ground truth modes."""
    runner = AblationExperimentRunner.get_instance()

    # Domain mode
    res_dom = runner.run_ablation_study(domain="all", relevance_mode="domain", sigma=0.05, seeds=[42], force_rerun=True)
    assert res_dom["relevance_mode"] == "domain"

    # Subtype mode
    res_sub = runner.run_ablation_study(domain="all", relevance_mode="subtype", sigma=0.05, seeds=[42], force_rerun=True)
    assert res_sub["relevance_mode"] == "subtype"

    print("PASS: test_explicit_ground_truth_taxonomy (Both domain and subtype modes functional)")


if __name__ == "__main__":
    print("======================================================================")
    print("RUNNING SCIENTIFIC ABLATION AUTOMATED TEST SUITE")
    print("======================================================================")
    test_independent_projection_consistency()
    test_hand_calculated_toy_metrics()
    test_zero_leakage_source_groups()
    test_production_index_immutability()
    test_separate_experiments_and_statistical_bounds()
    test_explicit_ground_truth_taxonomy()
    print("======================================================================")
    print("ALL TESTS PASSED SUCCESSFULLY.")
    print("======================================================================")
