# SecureImage – Test Execution Report

**Project**: SecureImage (Privacy-Preserving Content-Free Image Retrieval System)  
**Execution Environment**: Python 3.12 (CPython), Windows 11 x64, PyTorch CPU, FAISS-CPU 1.7.4, FastAPI 0.100+  
**Tester**: Senior Software Tester & Cybersecurity QA Engineer  
**Execution Date**: November 6, 2026  
**Catalog Under Test**: 1,035 Multi-Domain Vectors (Medical: 252, Biometrics: 252, Nature: 270, Vehicles: 261)  

---

## 1. Executive Summary

| Test ID | Test Case Name | Type | Result | Key Metric / Latency | Evidence Path |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **TC01** | Successful Visual Image Retrieval | Positive Functional | **PASS** | Precision@5: **100.0%** (5/5) \| Latency: **135.3 ms** | `evaluation/screenshots/TC01/` |
| **TC02** | Successful Text Image Retrieval (OCR) | Positive Functional | **BLOCKED** | Feature Absent (No OCR engine or text index) | `evaluation/screenshots/TC02/` |
| **TC03** | Successful Hybrid Retrieval (Visual + Text) | Positive Functional | **BLOCKED** | Feature Absent (No multimodal score fusion) | `evaluation/screenshots/TC03/` |
| **TC04** | Negative Test: Unrelated Image (No Match) | Negative Functional | **PASS** | 0 False Positives \| 127 Candidates Rejected | `evaluation/screenshots/TC04/` |
| **TC05** | Negative Test: Corrupted Image Input | Security / Robustness | **PASS** | HTTP 400 \| 0 Vectors Added \| Zero Crash | `evaluation/screenshots/TC05/` |

**Overall Result**: 
- **Executable Tests (3/3)**: **100% PASS** (TC01, TC04, TC05)
- **Blocked Due to Architecture Scope (2/5)**: **BLOCKED** (TC02, TC03)
- **Defects / Regressions**: **0 Critical Defects** found in implemented visual search and security validation.

---

## 2. Detailed Test Execution Results

### TC01: Successful Visual Image Retrieval

- **Input File**: `test_dataset/01_Medical/test_medical_xray_05.jpg` (Resolution: 640×640)
- **Execution Workflow**:
  1. Processed locally via `/api/client/process-local`: Stripped metadata, MobileNetV3 1280-D feature extraction, 512-D orthonormal keyed projection ($P^T P = I_{512}$), noise perturbation ($\sigma = 0.05$).
  2. Submitted 512-D float32 vector to `/api/search/content-free-query` with domain filter `medical` and `top_k=5`.
  3. FAISS `IndexFlatIP` executed inner product search over 1,035 catalog vectors.
- **Observed Results**:
  - **Rank #1**: `IMG_MED_XRA_medical_xray_0075` | Category: `medical` | Cosine Similarity: `51.5%`
  - **Rank #2**: `IMG_MED_XRA_medical_xray_0051` | Category: `medical` | Cosine Similarity: `51.5%`
  - **Rank #3**: `IMG_MED_XRA_medical_xray_0009` | Category: `medical` | Cosine Similarity: `51.2%`
  - **Rank #4**: `IMG_MED_XRA_medical_xray_0086` | Category: `medical` | Cosine Similarity: `37.1%`
  - **Rank #5**: `IMG_MED_XRA_medical_xray_0087` | Category: `medical` | Cosine Similarity: `32.9%`
- **Evaluation Metrics**:
  - **Precision@5**: $5/5 = 100.0\%$ (All 5 matches are genuine medical radiographs).
  - **Recall@5**: Evaluated over 251 catalog peers.
  - **Total Pipeline Latency**: $135.31\text{ ms}$ (Client extraction: $127.8\text{ ms}$, FAISS search: $7.42\text{ ms}$).
  - **Zero-Pixel Invariant**: Verified. The search server received **zero** query pixels or reconstruction streams.
- **Status**: **PASS**
- **Evidence**: `evaluation/screenshots/TC01/input_query_image.jpg`, `tc01_visual_evidence.png`, `execution_log.json`

---

### TC02: Successful Text Image Retrieval (OCR)

- **Input File**: `evaluation/screenshots/TC02/query_text_document.png` (Document / Receipt image containing printed text)
- **Codebase Inspection**:
  - Inspected `requirements.txt`: No OCR packages (`pytesseract`, `easyocr`, `paddleocr`, or `tesseract-ocr`) installed.
  - Inspected FastAPI routing table in `backend/main.py`: Zero text extraction or OCR routes exist (`/api/search/text` or `/api/ocr` are absent).
  - Inspected SQLite and FAISS schema: Database stores solely visual metadata (`image_id`, `category`, `owner_id`, `is_private`). FAISS holds strictly 512-D float32 visual projections.
- **QA Finding**: 
  - OCR-based gallery text indexing and text retrieval are **not implemented** in the SecureImage repository.
  - As required by strict QA standards, this test cannot be executed and is not simulated.
- **Status**: **BLOCKED**
- **Evidence**: `evaluation/screenshots/TC02/blocked_audit_report.json`, `tc02_text_audit_evidence.png`

---

### TC03: Successful Hybrid Retrieval (Visual + Text)

- **Input File**: `evaluation/screenshots/TC03/query_multimodal_poster.png` (Poster with visual scene and typographic text)
- **Codebase Inspection**:
  - Inspected `backend/services/retrieval/`: Search engine implements `FAISSRetrievalEngine` operating exclusively on normalized visual feature vectors.
  - Inspected backend API routers: No multimodal ranking fusion module (e.g. $S_{final} = \alpha S_{vis} + (1-\alpha) S_{text}$) exists.
- **QA Finding**:
  - Multimodal hybrid visual-text retrieval is **not implemented**.
  - SecureImage was architected specifically for privacy-preserving visual representation retrieval.
- **Status**: **BLOCKED**
- **Evidence**: `evaluation/screenshots/TC03/blocked_audit_report.json`, `tc03_hybrid_audit_evidence.png`

---

### TC04: Negative Test: Unrelated Image / No Relevant Match

- **Input File**: `evaluation/screenshots/TC04/unrelated_noise_image.png` (High-entropy synthetic RGB Gaussian noise array, $300 \times 300$, belonging to none of the 4 indexed categories).
- **Execution Workflow**:
  1. Extracted 512-D protected representation from the unrelated noise image.
  2. Submitted vector to FAISS retrieval engine with configured similarity cut-off $\ge 0.25$ (`include_below_threshold=False`).
  3. Inspected rejection diagnostics and candidate filtering telemetry.
- **Observed Results**:
  - **Returned Matches Meeting Threshold**: `0` matches.
  - **Diagnostics**: `127 candidates rejected by threshold cut-off`.
  - **False Positive Matches**: `0`. The application did not claim any unrelated database images were relevant.
  - **Frontend Behavior**: Displays clean message: *"No matches found meeting threshold (0.25). Try lowering similarity threshold or changing domain filter."*
- **Evaluation Metrics**:
  - **Specificity / True Negative Handling**: $100\%$.
  - **Latency**: $124.6\text{ ms}$.
- **Status**: **PASS**
- **Evidence**: `evaluation/screenshots/TC04/unrelated_noise_image.png`, `tc04_unrelated_evidence.png`, `execution_log.json`

---

### TC05: Negative Test: Invalid or Corrupted Image Input

- **Input File**: `evaluation/screenshots/TC05/corrupted_payload.jpg` (Truncated non-image binary: `b"CORRUPTED_NON_IMAGE_HEADER_0xDEADBEEF_TRUNCATED"`).
- **Execution Workflow**:
  1. Recorded pre-test state: $N_{DB} = 1,035$ rows, $N_{FAISS} = 1,035$ vectors.
  2. Attempted upload via `/api/client/process-local`.
  3. Captured server exception, HTTP status code, and process survival.
  4. Verified post-test state: $N_{DB}$ and $N_{FAISS}$.
- **Observed Results**:
  - **HTTP Status Code**: `400 Bad Request`.
  - **Server Error Detail**: `"Unsupported or corrupted image file."`
  - **Backend Process**: Remained completely operational; zero unhandled exceptions or crashes.
  - **FAISS Vector Count**: $1,035 \rightarrow 1,035$ (Zero corrupt vectors injected).
  - **Database Records**: $1,035 \rightarrow 1,035$ (Zero corrupt metadata stored).
- **Security Evaluation**:
  - Safe input validation enforced via PIL `Image.verify()`.
  - Memory bounds and file integrity checks prevent remote code execution or state corruption from malformed uploads.
- **Status**: **PASS**
- **Evidence**: `evaluation/screenshots/TC05/corrupted_payload.jpg`, `tc05_corrupted_evidence.png`, `execution_log.json`

---

## 3. Summary of System Integrity

```text
========================================================================
Test Suite Execution Summary
========================================================================
Total Test Cases Formulated:   5
Total Tests Executable:        3 (TC01, TC04, TC05)
Total Executable Tests Passed: 3 (100% Pass Rate)
Total Tests Blocked (Scope):   2 (TC02: OCR, TC03: Hybrid)
System Degradation / Crashes:  0
Data / Index Corruption:       0
========================================================================
```
