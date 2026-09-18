# Private Image Search
### Privacy-Preserving Image Retrieval Using Protected Visual Representations

A production-grade, working privacy-preserving content-based image retrieval (CBIR) system developed for an AIML Engineering Mini-Project.

---

## 1. Key Architectural Principles

1. **Decoupled Physical Storage:** Original full-resolution image binaries are stored exclusively in an isolated private vault (`private_storage/`). The vector database holds **zero image pixels**.
2. **Protected Representations:** Feature vectors extracted via pretrained CNN backbones (MobileNetV3 / ResNet-50) are transformed through a mathematical privacy layer (random orthogonal projection + calibrated differential noise perturbation) to suppress deep feature inversion attacks.
3. **Sub-Second Vector Search:** Meta AI FAISS (`IndexFlatIP`) executes nearest-neighbor queries on L2-normalized protected vectors (cosine similarity) in under 15ms.
4. **Cryptographic Access Control:** Retrieved Image IDs are checked against an owner-based and role-based access control (RBAC) matrix in SQLite before any pixel data is decrypted and released.

---

## 2. Project Structure

```
private-image-search/
│
├── backend/
│   ├── api/
│   │   ├── auth.py            # User authentication & session management
│   │   ├── search.py          # Live query pipeline & storage streaming
│   │   ├── admin.py           # Real-time system telemetry & audit trail
│   │   └── evaluation.py      # Automated benchmark & accuracy metrics
│   ├── database/
│   │   ├── db.py              # SQLite database schema & queries
│   │   └── private_search.db  # SQLite database
│   ├── services/
│   │   ├── feature_extraction/# PyTorch pretrained CNN extractor
│   │   ├── privacy/           # Orthogonal projection & AES-256 cipher
│   │   ├── retrieval/         # FAISS IndexFlatIP vector engine
│   │   └── storage/           # Decoupled private image vault
│   └── main.py                # FastAPI server entrypoint
│
├── frontend/
│   └── index.html             # Modern dark-tech single-page application
│
├── dataset/                   # Multi-domain images (medical, biometrics, vehicles, nature)
├── vector_db/                 # FAISS index (float32 vectors only, NO pixels)
├── private_storage/           # Decoupled image files
├── scripts/
│   └── index_images.py        # Dataset indexing and vault population script
├── requirements.txt
└── README.md
```

---

## 3. Quickstart & Execution Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12
- `uv` (recommended) or standard `pip`

### Step 1: Install Dependencies
```bash
# Using uv (fastest)
uv venv .venv
uv pip install -r requirements.txt

# Or using standard pip
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Populate & Index the Dataset
```bash
python scripts/index_images.py
```
This will:
- Ingest sample confidential images across medical, biometric, vehicle, and nature categories.
- Store original images in the decoupled `private_storage/` vault.
- Extract CNN visual features and apply the privacy protection layer.
- Add protected representations into the FAISS vector index (`vector_db/faiss_index.bin`).
- Record metadata and access permissions in SQLite (`backend/database/private_search.db`).

### Step 3: Launch the Application
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at:
👉 **`http://localhost:8000/`**

---

## 4. Demonstration Walkthrough for Evaluation

1. **Upload / Drag & Drop:** Drop any image or click one of the quick preset buttons (e.g. *Chest CT* or *Biometric*).
2. **Observe Live Pipeline:** Watch the 6 stages dynamically transition with exact wall-clock millisecond timings:
   `Upload` ➔ `Preprocessing` ➔ `Feature Extraction` ➔ `Privacy Protection` ➔ `Vector Search` ➔ `Authorization`.
3. **Verify Zero Pixels:** Inspect the *Privacy Status* section confirming that original images never enter the FAISS database.
4. **Test Access Control (RBAC):**
   - Switch user in top-right to **Dr. R. Sharma (Specialist)**: Private medical CT scans are decrypted and viewable (`✓ Authorized`).
   - Switch user to **Alex Verma (Researcher)** or **Public Guest**: Private medical images display a lock icon with `🔒 Private Asset - Access Denied`, while public vehicle and nature images remain accessible.
5. **Inspect Live Telemetry & Evaluation:**
   - Click the **Evaluation** tab to view actual measured Precision@K and Baseline vs Protected comparison.
   - Click the **Admin & Audit** tab to inspect live intrusion logs and database stats.
