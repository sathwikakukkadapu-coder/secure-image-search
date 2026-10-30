# PrivateLens Open Research Dataset

## Privacy-Preserving Content-Free Visual Retrieval Benchmark Dataset

### 1. Overview & Architectural Principles
The **PrivateLens** dataset is an openly licensed, multi-domain benchmark specifically structured to evaluate **content-free, privacy-preserving visual search systems**.

In PrivateLens:
- **Zero Raw Query Pixels**: Query images are converted to 512-D protected embeddings locally. No raw pixels, uncompressed bitmaps, or reconstructible feature maps are stored in the search index.
- **Decoupled Vault Storage**: High-resolution catalog images are encrypted with AES-256-GCM and stored in the decoupled vault (`private_storage/`).
- **Cryptographic & Perceptual De-duplication**: The dataset is verified for zero duplicate files using both cryptographic hash (SHA-256) and perceptual difference hash (dHash with Hamming distance threshold $h_{dist} \le 2$).

---

### 2. Dataset Domains & Subcategory Breakdown

The catalog consists of four core domains with controlled subcategory quotas designed to evaluate cross-domain retrieval selectivity, domain clustering, and retrieval accuracy:

| Domain | Subcategories | Target Quota | Licensing | Primary Characteristics |
|---|---|---:|---|---|
| **Biometrics** | `fingerprints`, `iris`, `faces`, `other` (palmprints, vein patterns) | $\ge 250$ | CC-BY, CC-BY-SA, CC0, Public Domain | High-frequency ridge details, circular iris structures, facial contours. No identifiable PII. |
| **Medical** | `xray`, `ct`, `mri`, `other` (ultrasound, retinal fundus, histology) | $\ge 250$ | CC-BY, CC-BY-SA, CC0, Public Domain | De-identified clinical modalities; high contrast bone/tissue density distributions. |
| **Nature** | `landscapes`, `water`, `vegetation`, `weather`, `wildlife` | $\ge 250$ | CC-BY, CC-BY-SA, CC0, Public Domain | Varied terrain, natural textures, organic geometry, dynamic lighting conditions. |
| **Vehicles** | `cars`, `two_wheelers`, `commercial`, `other` (aviation, maritime, rail) | $\ge 250$ | CC-BY, CC-BY-SA, CC0, Public Domain | Rigid man-made geometry, specular reflections, diverse viewing angles. |
| **TOTAL** | **17 distinct subcategories** | $\ge \mathbf{1,000}$ | Open Research Licenses | Fully validated with SHA-256 and dHash integrity. |

---

### 3. Baseline Seed Images (Preserved)
The original 32 high-resolution seed images (640x640) reside directly in each domain root folder (`dataset/medical/ct_pulmonary_101.jpg`, etc.) and are indexed with permanent IDs (`IMG_MED_ct_pulmonary_101`, `IMG_BIO_face_biometric_201`, etc.) to guarantee continuous test harness compatibility.

---

### 4. Metadata Schema (`metadata.csv`)
All dataset images are indexed and tracked in `dataset/metadata.csv` with the following 19 fields:

1. `image_id`: Unique identifier (e.g. `IMG_MED_XRA_0001` or `IMG_MED_ct_pulmonary_101`).
2. `relative_path`: Relative filesystem path from `dataset/` (e.g. `medical/xray/medical_xray_0001.jpg`).
3. `domain`: Top-level domain (`biometrics`, `medical`, `nature`, `vehicles`).
4. `subcategory`: Fine-grained subcategory (`xray`, `ct`, `iris`, etc.).
5. `filename`: Standardized filename.
6. `source_url`: Provenance URL on Wikimedia Commons or PrivateLens Catalog.
7. `source_name`: Authoritative repository name.
8. `license`: Open license type (e.g. `CC-BY 4.0`, `CC-BY-SA 3.0`, `CC0`, `Public domain`).
9. `attribution`: Creator/photographer attribution string.
10. `image_width`: Image pixel width ($\le 640$).
11. `image_height`: Image pixel height ($\le 640$).
12. `file_format`: Format encoding (`JPEG`).
13. `file_size_bytes`: Raw byte size on disk.
14. `sha256`: Cryptographic SHA-256 hex digest.
15. `perceptual_hash`: 64-bit difference hash (dHash) hex string.
16. `is_synthetic`: Boolean indicating whether the image was synthetically generated.
17. `is_augmented`: Boolean indicating whether the image is a transformed test variant.
18. `original_image_id`: Reference to source image if augmented.
19. `collection_date`: Ingestion date (ISO format `YYYY-MM-DD`).

---

### 5. Robustness & Evaluation Augmentations (`dataset_augmented/`)
To test retrieval robustness under real-world visual distortions without contaminating the clean catalog, `scripts/augment_dataset.py` generates controlled test variations into `dataset_augmented/`:
- **Gaussian Blur** ($\sigma = 1.5$)
- **Contrast / Brightness Variation** (factor 1.25 / 0.85)
- **Gaussian Noise** ($\sigma = 15$)
- **Controlled Rotation** ($\pm 10^\circ$)
- **Central Cropping** ($85\%$ area crop)

Augmented images are tracked separately in `dataset_augmented/metadata_augmented.csv` and are evaluated via the Retrieval Benchmarking suite.

---

### 6. Verification & Index Rebuilding Commands

#### Run Dataset Validation Audit:
```powershell
python scripts/validate_dataset.py
```
Checks for:
- Corrupt / non-decodable images.
- Exact SHA-256 duplicate files.
- Perceptual near-duplicates ($h_{dist} \le 2$).
- Image dimensions and aspect ratio integrity.
- Metadata completeness and alignment.

#### Re-index Dataset into FAISS and AES-256 Vault:
```powershell
python scripts/index_images.py
```
Or via the authenticated REST API endpoint:
```http
POST /api/index/rebuild
Authorization: Bearer USR_ADM_00
```

#### Run Project Test Suite:
```powershell
python tests/test_system.py
```
