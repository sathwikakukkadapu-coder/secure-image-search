# AGENTS.md - Antigravity Project Configuration

## Project: Privacy-Preserving Content-Free Image Retrieval (PPIR)

### Overview
This project demonstrates genuine **Privacy-Preserving Content-Free Image Retrieval** using MobileNetV3 deep feature extraction, noise perturbation, FAISS vector indexing, and role-based access control.

- **Conversation Origin**: `07efd5e5-c5d5-4760-960e-d29a80aaf388`
- **Active Workspace Directory**: `C:\Users\Sathwika\Desktop\secureimage` (Mirrored at `C:\Users\Sathwika\.gemini\antigravity\scratch\private-image-search`)
- **Web Interface**: `http://localhost:8000`

---

### Core Architectural Invariants

1. **Zero-Pixel Retrieval Rule**:
   - Query image pixels are processed strictly on the client/local buffer.
   - The retrieval server receives **only** a 512-D float32 protected feature vector.
   - Zero raw query image pixels, JPEG/PNG streams, or reconstruction artifacts reach the search server.
2. **Decoupled Vault Storage**:
   - Original database catalog images are encrypted via AES-256 and stored in `private_storage/`.
   - Access to unencrypted database match images requires RBAC authorization tokens.
3. **High-Resolution Dataset (32 Images, 640x640)**:
   - 4 Categories: Medical (radiographs), Biometrics (facial/iris), Vehicles, and Nature.
   - Re-indexed into FAISS `IndexFlatIP` with normalized inner product (cosine similarity).

---

### Quick Commands

- **Activate Virtual Environment**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Start FastAPI & Web UI Server**:
  ```powershell
  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
- **Run Verification & Test Suite**:
  ```powershell
  python tests/test_system.py
  ```
- **Re-index Dataset**:
  ```powershell
  python scripts/index_images.py
  ```
