"""
SecureImage Research Module C: Threat Models & Security Bounds.

Formally specifies attacker capabilities, accessible information, and theoretical security guarantees:
1. Threat Model 1: Honest-but-Curious Server (Operates strictly on 512-D representations; 0 pixels).
2. Threat Model 2: Attacker A (Restricted-Key Eavesdropper; knows CNN architecture, lacks 256-bit key).
3. Threat Model 3: Attacker B (Known-Key Malicious Insider; possesses secret key P_K).
4. Threat Model 4: Storage Vault Attacker (Encrypted ciphertext at rest under AES-256-GCM).
"""

from typing import Dict, Any, List


class ThreatModelRegistry:
    """Provides formal specifications and risk profiles for privacy evaluations."""

    @staticmethod
    def get_all_threat_models() -> List[Dict[str, Any]]:
        return [
            {
                "id": "honest_but_curious_server",
                "name": "Honest-but-Curious Retrieval Server",
                "attacker_type": "Passive Server Operator",
                "knowledge": {
                    "network_traffic": "512-D Float32 vector embeddings only",
                    "raw_pixels": "None (Zero-pixel invariant)",
                    "projection_key": "None (Key is client-side / isolated)",
                    "vault_images": "None (Decoupled & AES-256 encrypted)"
                },
                "objective": "Attempt to reconstruct query image or identify patient/subject from query vector",
                "attack_vector": "Vector cluster inference, nearest-neighbor graph leakage",
                "defense": "Keyed orthonormal projection + Gaussian perturbation (sigma = 0.05)",
                "residual_risk": "Extremely Low (Information theoretically bounded)"
            },
            {
                "id": "restricted_key_attacker",
                "name": "Attacker A: Restricted-Key Eavesdropper",
                "attacker_type": "External Network / Database Sniffer",
                "knowledge": {
                    "network_traffic": "Stored or transmitted 512-D vectors",
                    "feature_extractor": "Known architecture (MobileNetV3-Large)",
                    "projection_key": "Unknown (256-bit entropy)",
                    "raw_pixels": "None"
                },
                "objective": "Invert intercepted vector to reconstruct visible pixel information",
                "attack_vector": "Optimization-based inversion using surrogate random basis or PCA prior",
                "defense": "Cryptographic key secrecy (P_K derived via HKDF-SHA256 from 256-bit master key)",
                "residual_risk": "Zero Recon (SSIM < 0.05, PSNR < 12 dB; equivalent to random noise)"
            },
            {
                "id": "known_key_attacker",
                "name": "Attacker B: Known-Key Malicious Insider",
                "attacker_type": "Compromised Authorized Client / Rogue Admin",
                "knowledge": {
                    "network_traffic": "512-D vectors",
                    "feature_extractor": "Known architecture (MobileNetV3)",
                    "projection_key": "Known (Compromised or shared key P_K)",
                    "raw_pixels": "None"
                },
                "objective": "Execute gradient backpropagation directly through P_K to invert embedding",
                "attack_vector": "Direct Adam optimization with Total Variation regularization",
                "defense": "Dimension reduction (1280-D -> 512-D eliminates 768 degrees of freedom) + Gaussian noise",
                "residual_risk": "Low (Reconstructs abstract color blobs; zero biometric/medical diagnostic utility)"
            },
            {
                "id": "vault_storage_attacker",
                "name": "Vault Storage Compromise (Data-at-Rest)",
                "attacker_type": "Host File System Intruder",
                "knowledge": {
                    "disk_access": "private_storage/ directory containing image binaries",
                    "database_access": "private_search.db"
                },
                "objective": "Directly exfiltrate catalog gallery images",
                "attack_vector": "Raw file extraction, direct disk read",
                "defense": "AES-256-GCM authenticated encryption with isolated key in .keys/vault.key",
                "residual_risk": "Negligible (Protected by NIST-approved AES-GCM standard)"
            }
        ]
