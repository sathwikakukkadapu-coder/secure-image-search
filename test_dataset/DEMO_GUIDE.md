# FACULTY DEMO & TEST DATASET PRESENTATION GUIDE

**Project:** SecureImage (PrivateLens)  
**Target:** Live Demonstration to Faculty Advisor / Committee  
**Dataset Directory:** `test_dataset/`  

---

## 1. Test Dataset Structure

The `test_dataset/` directory contains **48 curated, held-out test query images** across all 4 operational domains, derived strictly from the official test split (`secureimage_dataset/splits/test.csv`).

```text
test_dataset/
├── 01_Medical/                  # Medical Imaging (Private Domain)
│   ├── test_medical_xray_05.jpg         (Chest Radiograph - Thoracic)
│   ├── test_medical_xray_10.jpg         (Chest Radiograph - Pulmonary)
│   ├── test_medical_mri_03.jpg          (Brain Magnetic Resonance)
│   ├── test_medical_mri_08.jpg          (Spine Magnetic Resonance)
│   ├── test_medical_ct_02.jpg           (Computed Tomography - Axial)
│   ├── test_medical_ct_07.jpg           (Computed Tomography - Coronal)
│   └── ... (12 images total)
├── 02_Biometrics/               # Biometric Data (Strict Private Domain)
│   ├── test_biometrics_faces_01.jpg     (Facial Biometric Portrait)
│   ├── test_biometrics_faces_05.jpg     (Facial Biometric Portrait)
│   ├── test_biometrics_iris_03.jpg      (High-Resolution Iris Scan)
│   ├── test_biometrics_iris_07.jpg      (Iris Texture Pattern)
│   ├── test_biometrics_fingerprints_02.jpg (Dactyloscopic Whorl)
│   ├── test_biometrics_fingerprints_06.jpg (Dactyloscopic Loop)
│   └── ... (12 images total)
├── 03_Vehicles/                 # Vehicles (Public Domain)
│   ├── test_vehicles_cars_01.jpg        (Passenger Automobile)
│   ├── test_vehicles_commercial_02.jpg  (Cargo Transport Truck)
│   ├── test_vehicles_two_wheelers_...   (Motorcycles & Scooters)
│   └── ... (12 images total)
├── 04_Nature/                   # Natural Environments (Public Domain)
│   ├── test_nature_landscapes_02.jpg    (Mountain / Wilderness)
│   ├── test_nature_general_01.jpg       (Aurora / Night Sky)
│   ├── test_nature_water_...            (Coastlines & Lakes)
│   └── ... (12 images total)
├── all_test_split/              # Complete 259-image research test split
└── curated_demo_catalog.csv     # Metadata index (SHA256, category, IDs)
```

---

## 2. Live Demo Script (Step-by-Step for Your Faculty / Mam)

### Step 1: Open the Application
1. Start the server (if not already running):
   ```powershell
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. Open your web browser to:
   ```text
   http://localhost:8000
   ```

### Step 2: Open File Explorer Side-by-Side
1. In Windows File Explorer, navigate to:
   ```text
   secureimage\test_dataset\01_Medical
   ```
2. Place the browser and File Explorer side-by-side on your laptop screen.

### Step 3: Demonstrate Medical Query (The Primary Privacy Use Case)
1. Drag and drop **`test_medical_xray_05.jpg`** into the **Query Representation Input** box on the web page.
2. **Key Point to Explain to Mam:**
   > *"Mam, notice that the raw image is **NOT displayed** in the query input box. Instead, our system enforces a strict **Zero-Pixel Privacy Invariant**. The image pixels are buffered exclusively in client RAM, passed through MobileNetV3 to extract a 1280-D activation vector, projected via a secret 256-bit orthonormal matrix into 512 dimensions, and perturbed with calibrated noise ($\sigma = 0.05$). **Zero raw pixels ever reach the server or leave the client memory buffer.**"*
3. Click **Execute Content-Free Search** (or observe the instant search result).
4. Point out the results in **Retrieved Image Matches**:
   - The top match displays high cosine proximity (e.g. $54.5\% - 82\%$ noise-calibrated proximity).
   - Highlight the **`[Authorized]`** badge: Original catalog images are AES-256 encrypted at rest in the storage vault (`private_storage/vault/`). Because we are logged in as an authorized user (`Dr. Evelyn Reed, Chief Radiologist`), our RBAC clearance decrypts the matching vault asset for diagnostic inspection.

### Step 4: Demonstrate Biometric Query (Strict Sensitive Domain)
1. Open `test_dataset\02_Biometrics\`.
2. Drag and drop **`test_biometrics_faces_01.jpg`** or **`test_biometrics_fingerprints_02.jpg`**.
3. Point out that the 512-D float32 vector barcode is immediately computed in the client buffer.
4. Show how the FAISS vector database retrieves biometric matches without ever having received the query person's actual face photo.

### Step 5: Demonstrate Cross-Domain Capability
1. Try a vehicle (`test_dataset\03_Vehicles\test_vehicles_cars_01.jpg`) or nature image.
2. Show that domain filtering works seamlessly (Auto-Detect vs. Explicit Domain Filter).

---

## 3. Anticipated Faculty Questions & Scientifically Defensible Answers

### Q1: "Why doesn't the query image preview show up in the upload box?"
> **Answer:**  
> *"That is intentional, Mam. In a true Content-Free Privacy-Preserving Image Retrieval system, the client does not display or expose raw query pixels in the search pipeline. The query image exists strictly as an ephemeral array in client memory during feature extraction. Displaying raw pixels or sending them violates the zero-pixel boundary. The server and search pipeline operate exclusively on the 512-D protected vector."*

### Q2: "If an attacker captures the 512-D vector from FAISS or the network, can't they reconstruct the original image?"
> **Answer:**  
> *"No, Mam. We mathematically proved and experimentally verified this:
> 1. **Dimensionality Loss (768-D Null Space):** The projection reduces 1280 deep features to 512, which creates an underdetermined linear system with an unconstrained 768-dimensional kernel ($\dim(\ker(\mathbf{P}_K^T)) = 768$). An infinite family of 1280-D vectors maps to the exact same 512-D representation.
> 2. **Empirical Inversion Benchmark:** Even under white-box conditions where an attacker uses an Adam gradient-based inversion with access to the neural network weights and projection matrix, the reconstruction achieves an **SSIM of only 0.0099** and **PSNR of 3.77 dB**, which is indistinguishable from random static noise."*

### Q3: "Is your noise addition formally Differentially Private?"
> **Answer:**  
> *"Our system implements local calibrated Gaussian perturbation ($\sigma = 0.05$). Under the worst-case global sensitivity of antipodal unit vectors ($\Delta_2 = 2.0$), formal $(\epsilon, \delta)$-DP at $\epsilon = 2.0$ would require $\sigma \ge 4.84$, which produces an SNR of $-40.8\text{ dB}$ and collapses retrieval accuracy to $3.1\%$ (random guessing). Therefore, we honestly and scientifically classify our $\sigma = 0.05$ as an **Empirical Calibrated Noise Obfuscation Mechanism** that preserves $89.6\%$ retrieval precision while preventing inversion and suppressing membership inference."*

---

*Prepared for student academic project presentation and faculty defense.*
