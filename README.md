# SecureImage (PrivateLens): Privacy-Preserving Content-Based Image Retrieval (PP-CBIR)

A research-grade prototype demonstrating **Privacy-Preserving Content-Based Image Retrieval (PP-CBIR)**. It enables searching high-dimensional image databases across sensitive domains (medical imaging, biometrics, vehicle telemetry, nature catalogs) while guaranteeing that **zero query image pixels reach the retrieval server**.

---

## 1. Core Architectural Pillars

1. **Zero-Pixel Query Invariant**:
   - Query image pixels are processed strictly inside the local/client edge memory buffer.
   - The untrusted retrieval server receives **only** a 512-D protected vector or homomorphically encrypted ciphertext.
2. **Three Privacy-Preserving Feature Representations**:
   - **Baseline Orthogonal**: Semi-orthogonal dimension reduction ($1280 \to 512$) + empirical Gaussian noise ($\sigma = 0.05$).
   - **Local Differential Privacy (LDP)**: Rigorously calibrated Gaussian ($(\epsilon, \delta)$-LDP) and Laplace ($\epsilon$-LDP) mechanisms with global $L_2$ sensitivity $\Delta_2 = 2.0$.
   - **Non-Invertible Feature Mappings**: Random Fourier Features (RFF) with sinusoidal projection ($W_{\text{rff}} x + b$) destroying closed-form linear pseudo-inverse reconstruction, and 1-bit Sign Random Projection (SimHash).
3. **Cryptographically Protected Retrieval (TenSEAL CKKS)**:
   - Microsoft SEAL-backed Cheon-Kim-Kim-Song (CKKS) Leveled Homomorphic Encryption over Ring-LWE.
   - Computes inner products on encrypted polynomial vectors ($N=8192$, scale $2^{40}$) with $< 3 \times 10^{-6}$ precision error.
4. **AES-256-GCM Envelope Encryption Storage**:
   - Decoupled Vault (`private_storage/`): Each catalog image is encrypted with a unique 256-bit Data Encryption Key (DEK).
   - DEKs are securely wrapped with the Master Key Encryption Key (KEK) and stored separately in SQLite.
5. **Argon2id Authentication & RBAC**:
   - Memory-hard Argon2id password hashing with constant-time verification.
   - HMAC-SHA256 signed session tokens with 24-hour expiration.
   - Strict Role-Based Access Control (`specialist`, `admin`, `officer`, `guest`).
6. **Empirical Security Evaluation Framework**:
   - Feature Inversion Attacks (Ridge regression and pseudo-inverse pre-image reconstruction).
   - Known-Gallery Image Re-Identification (Top-1 and Top-5 attack success rate).
   - Membership Inference Attack (MIA) evaluation.

---

## 2. Directory Structure

```
secureimage/
├── backend/
│   ├── api/
│   │   ├── auth.py                  # Argon2id authentication & RBAC tokens
│   │   ├── search.py                # Zero-pixel vector search & storage streaming
│   │   ├── privacy.py               # LDP transforms, CKKS benchmarks, attack APIs
│   │   ├── admin.py                 # Telemetry & Merkle audit chain verification
│   │   ├── evaluation.py            # Retrieval accuracy & mAP benchmark engine
│   │   ├── security.py              # Security Center policy enforcement
│   │   └── index_mgmt.py            # FAISS index health & vector inspection
│   ├── database/
│   │   ├── db.py                    # SQLite schema, envelope DEK store, Argon2id
│   │   └── private_search.db        # SQLite database
│   ├── services/
│   │   ├── feature_extraction/      # Pretrained MobileNetV3-Large CNN backbone
│   │   ├── privacy/
│   │   │   ├── protector.py         # AES-256-GCM cipher & orthogonal projector
│   │   │   └── representation.py    # LDP Gaussian/Laplace & Non-Invertible RFF
│   │   ├── retrieval/
│   │   │   ├── faiss_index.py       # FAISS IndexFlatIP (cosine similarity)
│   │   │   ├── domain_classifier.py # Cosine centroid domain detector
│   │   │   └── ckks_retriever.py    # TenSEAL CKKS Homomorphic Encryption engine
│   │   ├── storage/
│   │   │   └── vault.py             # AES-256-GCM Envelope Encryption vault
│   │   └── evaluation/
│   │       └── security_evaluator.py# Inversion, Re-ID, and MIA attack evaluators
│   └── main.py                      # FastAPI server entrypoint
│
├── client/
│   └── secureimage_client.py        # Standalone trusted client CLI (0 query pixels sent)
│
├── secureimage_dataset/             # Research-standardized multi-domain dataset
│   ├── originals/                   # 1,035 genuine captures (Medical, Bio, Veh, Nat)
│   ├── augmented/                   # 500 controlled variants (rotation, blur, etc.)
│   ├── metadata/                    # SHA-256 & pHash manifests, duplicate reports
│   ├── splits/                      # Leakage-free 70/15/15 train/val/test splits
│   └── reports/                     # Markdown and interactive HTML audit reports
│
├── frontend/                        # Interactive dark-tech research SPA
│   ├── index.html                   # Research dashboard, search demo, and attack console
│   └── assets/                      # High-res authentic image previews
│
├── tests/
│   ├── test_pp_cbir_enhancements.py # LDP, RFF, CKKS, Envelope, and Attack unit tests
│   ├── test_retrieval_fixes.py      # Domain isolation & Top-K retrieval tests
│   └── test_system.py               # 15-suite end-to-end integration test
└── README.md
```

---

## 3. Quickstart & Execution

### Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Start the FastAPI Server
```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

### Run Verification Test Suites
```powershell
# 1. Test PP-CBIR Advanced Modules (LDP, CKKS, Envelope Encryption, Attacks)
python tests/test_pp_cbir_enhancements.py

# 2. Test Retrieval Fixes & Domain Filtering (12/12 PASS)
python tests/test_retrieval_fixes.py

# 3. Test Full System Integration (15/15 PASS)
python tests/test_system.py
```

### Run Trusted Client Query (Zero Pixels Transmitted)
```powershell
python client/secureimage_client.py --image dataset/medical/ct_pulmonary_101.jpg --scheme ldp_gaussian --epsilon 2.0
```

---

## 4. Empirical Security Benchmark Summary

| Scheme | Inversion MSE | Cosine Drift | Top-1 Re-ID | Top-5 Re-ID | Security Guarantee |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Plaintext Raw (1280-D)** | `0.0000` | `0.0000` | **100.0%** | **100.0%** | Vulnerable (Deterministic pre-image) |
| **Baseline Orthogonal (512-D)**| `0.0025` | `0.0487` | **86.7%** | **93.3%** | Partially Resistant (768 dims discarded) |
| **LDP Gaussian ($\epsilon=2.0$)** | `0.0098` | `0.0964` | **20.0%** | **40.0%** | Formally Bounded $(\epsilon, \delta)$-LDP |
| **Non-Invertible RFF** | `0.0382` | `0.2410` | **13.3%** | **33.3%** | Non-Linear Sinusoidal Kernel Barrier |
| **TenSEAL CKKS Homomorphic** | $\infty$ (`1.000`) | `1.0000` | **0.0%** | **0.0%** | Cryptographically Secure (IND-CPA) |

---

## 5. Pre-Seeded Test Credentials

| Role | Name | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Specialist** | Dr. R. Sharma | `doctor@hospital.org` | `doctor123` | Full access to Medical Scans & Public |
| **Specialist** | Dr. Anita Patel | `anita.patel@clinic.org` | `doctor456` | Full access to Medical Scans & Public |
| **Researcher** | Alex Verma | `researcher@lab.org` | `research123` | Benchmarking & Metrics (No Raw Scans) |
| **Administrator**| System Security Admin | `admin@security.org` | `admin123` | Unrestricted audit & asset management |
| **Guest** | Public Guest | `guest@demo.org` | `guest123` | Public domains only (Medical/Bio Locked) |
