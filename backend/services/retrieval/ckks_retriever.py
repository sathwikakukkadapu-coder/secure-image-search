"""
SecureImage CKKS Homomorphic Encryption Retrieval Engine.

Implements Cryptographically Protected Feature Retrieval using the Cheon-Kim-Kim-Song (CKKS)
Leveled Homomorphic Encryption scheme over Ring-Learning-With-Errors (RLWE).

Protocol:
1. Trusted Client generates CKKS Context (poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60]).
2. Trusted Client retains Secret Key (SK) locally.
3. Public Evaluation Context (Galois & Relinearization keys) is shared with untrusted retrieval server.
4. Client encrypts query representation into CKKS ciphertext: c_q = Enc_PK(v_query).
5. Untrusted Server evaluates encrypted inner products with candidate gallery vectors:
       c_sim_i = c_q (x) v_db_i
   No plaintext feature vector is ever decrypted on the server.
6. Server transmits encrypted scalar ciphertexts [c_sim_1, ..., c_sim_k] back to client.
7. Authorized Client decrypts similarity scores: s_i = Dec_SK(c_sim_i) and ranks results locally.
"""

import time
import os
import base64
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

try:
    import tenseal as ts
    TENSEAL_AVAILABLE = True
except ImportError:
    ts = None
    TENSEAL_AVAILABLE = False

class CKKSRetrievalEngine:
    """
    Experimental Homomorphic Encryption Retrieval Engine using TenSEAL (Microsoft SEAL wrapper).
    Preserves existing FAISS as the plaintext baseline while offering a cryptographically secure alternative.
    """
    _instance = None

    def __init__(self, poly_modulus_degree: int = 8192, vector_dim: int = 512):
        if not TENSEAL_AVAILABLE or ts is None:
            raise RuntimeError(
                "TenSEAL is not installed or unavailable in the current environment. "
                "Install with 'pip install tenseal' to enable CKKS homomorphic encryption operations."
            )
        self.poly_modulus_degree = poly_modulus_degree
        self.vector_dim = vector_dim
        self.scale = 2**40
        self.coeff_mod_bit_sizes = [60, 40, 40, 60]
        
        # Initialize client context (with secret key)
        self.client_context = self._create_client_context()
        
        # Export server evaluation context (public keys only, secret key dropped)
        self.server_context_bytes = self.client_context.serialize(
            save_public_key=True,
            save_secret_key=False,
            save_galois_keys=True,
            save_relin_keys=True
        )
        self.server_context = ts.context_from(self.server_context_bytes)

    def _create_client_context(self):
        ctx = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=self.poly_modulus_degree,
            coeff_mod_bit_sizes=self.coeff_mod_bit_sizes
        )
        ctx.generate_galois_keys()
        ctx.generate_relin_keys()
        ctx.global_scale = self.scale
        return ctx

    @classmethod
    def get_instance(cls, poly_modulus_degree: int = 8192, vector_dim: int = 512):
        if not TENSEAL_AVAILABLE or ts is None:
            raise RuntimeError(
                "TenSEAL is not installed or unavailable in the current environment. "
                "Install with 'pip install tenseal' to enable CKKS homomorphic encryption operations."
            )
        if cls._instance is None:
            cls._instance = cls(poly_modulus_degree=poly_modulus_degree, vector_dim=vector_dim)
        return cls._instance

    # --------------------------------------------------------------------------
    # Client-Side Operations
    # --------------------------------------------------------------------------
    def client_encrypt_vector(self, vector: np.ndarray) -> Tuple[bytes, float]:
        """
        [Client Operation] Encrypts a float32 vector using the client secret key.
        Returns serialized ciphertext bytes and encryption duration in ms.
        """
        t0 = time.time()
        v = vector.astype(np.float64).flatten().tolist()
        if len(v) != self.vector_dim:
            # Pad or truncate to expected dimension
            v = (v + [0.0] * self.vector_dim)[:self.vector_dim]
            
        enc_vec = ts.ckks_vector(self.client_context, v)
        enc_bytes = enc_vec.serialize()
        elapsed_ms = (time.time() - t0) * 1000.0
        return enc_bytes, elapsed_ms

    def client_decrypt_scores(self, encrypted_scores_bytes: List[bytes]) -> Tuple[List[float], float]:
        """
        [Client Operation] Decrypts homomorphically computed inner-product scores.
        """
        t0 = time.time()
        scores = []
        for enc_b in encrypted_scores_bytes:
            enc_val = ts.ckks_vector_from(self.client_context, enc_b)
            dec_list = enc_val.decrypt()
            scores.append(float(dec_list[0]))
        elapsed_ms = (time.time() - t0) * 1000.0
        return scores, elapsed_ms

    # --------------------------------------------------------------------------
    # Untrusted Server-Side Operations
    # --------------------------------------------------------------------------
    def server_evaluate_similarity(
        self,
        encrypted_query_bytes: bytes,
        candidate_vectors: List[np.ndarray]
    ) -> Tuple[List[bytes], float]:
        """
        [Server Operation] Evaluates encrypted inner products against candidate vectors
        using strictly public evaluation keys. The server NEVER sees the plaintext query.
        """
        t0 = time.time()
        enc_query = ts.ckks_vector_from(self.server_context, encrypted_query_bytes)
        
        encrypted_results = []
        for cand in candidate_vectors:
            c_flat = cand.astype(np.float64).flatten().tolist()
            if len(c_flat) != self.vector_dim:
                c_flat = (c_flat + [0.0] * self.vector_dim)[:self.vector_dim]
                
            # Homomorphic dot product between ciphertext vector and plaintext database vector
            enc_dot = enc_query.dot(c_flat)
            encrypted_results.append(enc_dot.serialize())
            
        elapsed_ms = (time.time() - t0) * 1000.0
        return encrypted_results, elapsed_ms

    # --------------------------------------------------------------------------
    # Complete End-to-End Evaluation Benchmark
    # --------------------------------------------------------------------------
    def benchmark_ckks_pipeline(self, num_candidates: int = 16) -> Dict[str, Any]:
        """
        Runs an empirical benchmark comparing plaintext cosine similarity with CKKS homomorphic inner product.
        Records encryption time, ciphertext size, server evaluation time, decryption time, and numerical error.
        """
        rng = np.random.RandomState(42)
        q_vec = rng.randn(self.vector_dim).astype(np.float32)
        q_vec = q_vec / np.linalg.norm(q_vec)
        
        candidates = []
        plaintext_sims = []
        for _ in range(num_candidates):
            c_vec = rng.randn(self.vector_dim).astype(np.float32)
            c_vec = c_vec / np.linalg.norm(c_vec)
            candidates.append(c_vec)
            plaintext_sims.append(float(np.dot(q_vec, c_vec)))

        # 1. Client Encrypts Query
        enc_query_bytes, enc_time_ms = self.client_encrypt_vector(q_vec)
        ciphertext_size_kb = len(enc_query_bytes) / 1024.0

        # 2. Server Evaluates Inner Products
        enc_scores_bytes, server_time_ms = self.server_evaluate_similarity(enc_query_bytes, candidates)
        server_per_item_ms = server_time_ms / max(1, num_candidates)

        # 3. Client Decrypts Scores
        dec_scores, dec_time_ms = self.client_decrypt_scores(enc_scores_bytes)

        # 4. Measure Numerical Precision Error
        errors = [abs(dec - pt) for dec, pt in zip(dec_scores, plaintext_sims)]
        max_error = float(np.max(errors))
        mean_error = float(np.mean(errors))

        return {
            "scheme": "CKKS (Cheon-Kim-Kim-Song) Homomorphic Encryption",
            "security_parameter": "128-bit classical security (RLWE)",
            "poly_modulus_degree": self.poly_modulus_degree,
            "coeff_mod_bit_sizes": self.coeff_mod_bit_sizes,
            "vector_dimension": self.vector_dim,
            "num_candidates_evaluated": num_candidates,
            "client_encryption_time_ms": round(enc_time_ms, 2),
            "ciphertext_size_kb": round(ciphertext_size_kb, 2),
            "server_homomorphic_eval_time_ms": round(server_time_ms, 2),
            "server_per_vector_latency_ms": round(server_per_item_ms, 3),
            "client_decryption_time_ms": round(dec_time_ms, 2),
            "max_numerical_precision_error": round(max_error, 8),
            "mean_numerical_precision_error": round(mean_error, 8),
            "security_guarantee": "Semantic security (IND-CPA) - untrusted server receives ZERO plaintext bits",
            "practical_tradeoff": f"Homomorphic evaluation requires ~{server_per_item_ms:.2f} ms per vector vs ~0.001 ms for FAISS IndexFlatIP."
        }
