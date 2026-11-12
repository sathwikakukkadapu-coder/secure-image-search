# SecureImage – Test Case Specifications (5 Target Test Cases)

**Project**: SecureImage (Privacy-Preserving Content-Free Image Retrieval System)  
**Evaluation Target**: Current Implementation Workspace  
**QA Role**: Senior Software Tester & Cybersecurity QA Engineer  
**Date**: November 6, 2026  

---

## Overview

This document specifies the exact **Five Test Cases** evaluated against the SecureImage system:
- **3 Positive / Functional Test Cases**:
  - `TC01`: Successful Visual Image Retrieval
  - `TC02`: Successful Text Image Retrieval (OCR)
  - `TC03`: Successful Hybrid Retrieval (Visual + Text)
- **2 Negative / Security Test Cases**:
  - `TC04`: Negative Test: Unrelated Image / No Relevant Match
  - `TC05`: Negative Test: Invalid or Corrupted Image

In accordance with strict QA standards:
- Missing components (such as OCR or hybrid ranking) are explicitly audited and reported as **BLOCKED** rather than falsely simulated.
- Real images and actual FAISS vector search outputs are used without synthetic fabrication.

---

## Test Case 1: TC01 – Successful Visual Image Retrieval

| Attribute | Details |
| :--- | :--- |
| **Test Case ID** | `TC01` |
| **Test Name** | Successful Visual Image Retrieval |
| **Category** | Functional / Core Retrieval |
| **Priority** | High (Critical Path) |
| **Objective** | Verify that the application retrieves visually relevant images from the indexed gallery using MobileNetV3 deep features and 512-D keyed projection while maintaining the zero-pixel retrieval invariant. |
| **Preconditions** | 1. FAISS index loaded with 1,035 catalog vectors (`faiss_index.bin`).<br>2. SQLite database initialized with image metadata (`images` table).<br>3. Orthonormal projection matrix $P \in \mathbb{R}^{1280 \times 512}$ derived and active. |
| **Input Data** | `test_dataset/01_Medical/test_medical_xray_05.jpg` (Curated held-out chest radiograph, 640×640). |
| **Execution Steps** | 1. Upload `test_medical_xray_05.jpg` via `/api/client/process-local`.<br>2. Extract 1280-D raw feature vector via MobileNetV3.<br>3. Apply secret keyed projection $v_{proj} = P^T v_{raw}$ and calibrate noise ($\sigma = 0.05$).<br>4. Submit 512-D float32 vector to `/api/search/content-free-query` with `top_k=5`.<br>5. Query FAISS `IndexFlatIP` using inner product (cosine similarity).<br>6. Measure similarity scores, ranking, and retrieval latency. |
| **Expected Result** | 1. System extracts 1280-D vector and maps to 512-D protected space.<br>2. Server receives **zero** image pixels.<br>3. Top 5 retrieved matches belong to the Medical domain (`P@5 >= 80%`).<br>4. Cosine similarity scores and rank pills are properly displayed.<br>5. Latency is sub-second ($< 300\text{ ms}$). |
| **Pass Criteria** | Top 5 returned results contain at least 4 relevant medical radiographs ($\text{P@5} \ge 80\%$) and total latency $< 500\text{ ms}$. |

---

## Test Case 2: TC02 – Successful Text Image Retrieval (OCR)

| Attribute | Details |
| :--- | :--- |
| **Test Case ID** | `TC02` |
| **Test Name** | Successful Text Image Retrieval (OCR) |
| **Category** | Functional / Multimodal Retrieval |
| **Priority** | Medium |
| **Objective** | Verify OCR-based text extraction and lexical/semantic gallery retrieval using an image containing readable printed text (e.g., document/receipt). |
| **Preconditions** | 1. OCR library (e.g., Tesseract or EasyOCR) installed.<br>2. Text extraction endpoint available in FastAPI.<br>3. Gallery images indexed with text transcriptions or OCR token embeddings. |
| **Input Data** | `evaluation/screenshots/TC02/query_text_document.png` (Printed receipt/invoice text sample). |
| **Execution Steps** | 1. Inspect codebase for OCR dependencies in `requirements.txt`.<br>2. Inspect backend router for text search endpoints (`/api/search/text` or `/ocr`).<br>3. Attempt to upload text document query for OCR extraction.<br>4. Search gallery using extracted text tokens. |
| **Expected Result** | System extracts optical character tokens and performs lexical retrieval against text-indexed gallery assets. |
| **QA Evaluation Rule** | If OCR engine or text indexing pipeline is not implemented, the test must be marked **BLOCKED**. Do not pretend or simulate success. |

---

## Test Case 3: TC03 – Successful Hybrid Retrieval (Visual + Text)

| Attribute | Details |
| :--- | :--- |
| **Test Case ID** | `TC03` |
| **Test Name** | Successful Hybrid Retrieval (Visual + Text Multimodal) |
| **Category** | Functional / Multimodal Fusion |
| **Priority** | Medium |
| **Objective** | Verify retrieval using joint visual deep features and OCR keyword matching with calibrated rank fusion. |
| **Preconditions** | 1. Visual feature extraction pipeline operational.<br>2. OCR engine operational.<br>3. Multimodal score fusion layer (e.g. $S_{final} = \alpha S_{vis} + (1-\alpha) S_{text}$) implemented. |
| **Input Data** | `evaluation/screenshots/TC03/query_multimodal_poster.png` (Poster containing visual landscape and typography). |
| **Execution Steps** | 1. Inspect backend for multimodal fusion endpoints (`/api/search/hybrid`).<br>2. Inspect code for visual-text ranking integration.<br>3. Attempt to submit multimodal query. |
| **Expected Result** | System computes both visual and textual similarity and produces an integrated ranked list of top-5 matches. |
| **QA Evaluation Rule** | If multimodal hybrid ranking is not implemented, mark test as **BLOCKED**. |

---

## Test Case 4: TC04 – Negative Test: Unrelated Image / No Relevant Match

| Attribute | Details |
| :--- | :--- |
| **Test Case ID** | `TC04` |
| **Test Name** | Negative Test: Unrelated Image / No Relevant Match |
| **Category** | Negative Functional / Boundary Testing |
| **Priority** | High |
| **Objective** | Verify that the application correctly handles an image that has no relevant match in the catalog, rejecting unrelated matches rather than falsely claiming high relevance. |
| **Preconditions** | 1. Catalog indexed with 4 specific categories (Medical, Biometrics, Vehicles, Nature).<br>2. Similarity threshold cut-off configured in search pipeline ($\ge 0.25$). |
| **Input Data** | `evaluation/screenshots/TC04/unrelated_noise_image.png` (High-entropy synthetic RGB noise array representing an out-of-distribution non-semantic query). |
| **Execution Steps** | 1. Submit `unrelated_noise_image.png` to `/api/client/process-local`.<br>2. Generate 512-D protected vector.<br>3. Execute content-free query with similarity threshold cut-off $\ge 0.25$ and `include_below_threshold=False`.<br>4. Inspect candidate filter diagnostics and returned results. |
| **Expected Result** | 1. System processes the query vector.<br>2. Nearest neighbor search detects that similarity scores fail the threshold.<br>3. System rejects low-similarity candidates and returns **0 false-positive matches**.<br>4. UI displays: *"No matches found meeting threshold (0.25)"*. |
| **Pass Criteria** | Zero false-positive matches returned to the user; diagnostics report candidates filtered out by threshold cut-off. |

---

## Test Case 5: TC05 – Negative Test: Invalid or Corrupted Image

| Attribute | Details |
| :--- | :--- |
| **Test Case ID** | `TC05` |
| **Test Name** | Negative Test: Invalid or Corrupted Image Input |
| **Category** | Security / Robustness / Input Validation |
| **Priority** | Critical |
| **Objective** | Verify that the system safely rejects corrupted image payloads, returning appropriate HTTP 400 errors without crashing the server or polluting FAISS and database state. |
| **Preconditions** | 1. Baseline database record count recorded ($N_{DB} = 1,035$).<br>2. Baseline FAISS vector count recorded ($N_{FAISS} = 1,035$). |
| **Input Data** | `evaluation/screenshots/TC05/corrupted_payload.jpg` (Arbitrary non-image byte stream: `b"CORRUPTED_NON_IMAGE_HEADER_0xDEADBEEF_TRUNCATED"`). |
| **Execution Steps** | 1. Submit corrupted payload to `/api/client/process-local`.<br>2. Observe server HTTP response status and error message.<br>3. Verify backend process remains running.<br>4. Re-query SQLite database image count.<br>5. Re-query FAISS index vector count. |
| **Expected Result** | 1. Server returns HTTP 400 Bad Request with clear detail: *"Unsupported or corrupted image file."*<br>2. Backend does not crash or raise unhandled 500 exceptions.<br>3. Zero invalid vectors added to FAISS index ($1,035 == 1,035$).<br>4. Zero corrupt metadata rows stored in SQLite ($1,035 == 1,035$). |
| **Pass Criteria** | HTTP 400 received, backend alive, zero index or database pollution. |
