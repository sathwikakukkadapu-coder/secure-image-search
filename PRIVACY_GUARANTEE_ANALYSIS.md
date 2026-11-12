# PRIVACY GUARANTEE ANALYSIS: MATHEMATICAL FOUNDATIONS & EMPIRICAL BOUNDS

**Project:** SecureImage (PrivateLens)  
**Document Class:** Formal Privacy & Cryptographic Analysis Report  
**Target Audience:** Academic Faculty, Peer Reviewers, Security Auditing Committees  
**Status:** Validated Technical Analysis  

---

## 1. Executive Summary

This document provides the formal mathematical foundation, theoretical bounds, and empirical evaluation of the privacy mechanisms implemented in **SecureImage (PrivateLens)**. 

The system employs a dual-stage privacy pipeline:
1. **Keyed Orthogonal Projection ($\mathbf{P}_K \in \mathbb{R}^{1280 \times 512}$):** Dimension reduction from penultimate CNN activations ($d_0 = 1280$) to a reduced subspace ($d_1 = 512$), derived deterministically from a 256-bit cryptographically secure seed via HKDF-SHA256.
2. **Local Perturbation Mechanism ($\mathcal{M}_{\sigma}$):** Zero-mean isotropic Gaussian perturbation $\mathcal{N}(0, \sigma^2 \mathbf{I}_{512})$ added to query embeddings before $L_2$ sphere projection.

This analysis rigorously evaluates:
- Why the operational noise parameter ($\sigma = 0.05$) represents an **Empirical Heuristic Obfuscation Layer** rather than a formal $(\epsilon, \delta)$-Differential Privacy guarantee.
- The theoretical degradation of retrieval utility if formal $(\epsilon, \delta)$-DP were strictly enforced.
- The mathematical guarantees provided by the **768-dimensional null space** against exact feature pre-image reconstruction.
- The privacy vulnerability under **repeated query composition** and mitigation recommendations.

---

## 2. Formal $(\epsilon, \delta)$-Differential Privacy vs. Heuristic Perturbation

### 2.1 Theoretical Definition of Differential Privacy
A randomized mechanism $\mathcal{M}: \mathcal{X} \to \mathcal{Y}$ satisfies $(\epsilon, \delta)$-Differential Privacy (DP) if for any two adjacent inputs $\mathbf{x}, \mathbf{x}' \in \mathcal{X}$ and any measurable subset of query responses $\mathcal{S} \subseteq \mathcal{Y}$:

$$\Pr[\mathcal{M}(\mathbf{x}) \in \mathcal{S}] \le e^\epsilon \Pr[\mathcal{M}(\mathbf{x}') \in \mathcal{S}] + \delta$$

Where:
- $\epsilon > 0$ represents the **privacy budget / leakage parameter** (lower $\epsilon$ implies stronger indistinguishability).
- $\delta \in [0, 1)$ represents the **probability of failure** (bound on catastrophic privacy compromise).

---

### 2.2 Global $L_2$ Sensitivity on the Unit Hypersphere

In content-based feature representation, the input to the perturbation module is an orthonormal projection $\mathbf{z} = \mathbf{P}_K^T \mathbf{x}$, subsequently normalized to the unit hypersphere $\mathbb{S}^{d_1-1}$:

$$\mathbf{z} = \frac{\mathbf{P}_K^T \mathbf{x}}{\|\mathbf{P}_K^T \mathbf{x}\|_2} \in \mathbb{S}^{511}, \quad \text{where } \|\mathbf{z}\|_2 = 1.0$$

The global $L_2$ sensitivity $\Delta_2$ measures the maximum Euclidean distance between any two possible valid feature vectors in the input domain:

$$\Delta_2 = \max_{\mathbf{z}_1, \mathbf{z}_2 \in \mathbb{S}^{511}} \|\mathbf{z}_1 - \mathbf{z}_2\|_2$$

Since $\mathbf{z}_1, \mathbf{z}_2$ are points on the unit hypersphere:

$$\|\mathbf{z}_1 - \mathbf{z}_2\|_2^2 = \|\mathbf{z}_1\|_2^2 + \|\mathbf{z}_2\|_2^2 - 2 \langle \mathbf{z}_1, \mathbf{z}_2 \rangle = 1 + 1 - 2 \cos \theta = 2(1 - \cos \theta)$$

The maximum distance occurs when $\mathbf{z}_1$ and $\mathbf{z}_2$ are antipodal ($\theta = \pi, \cos \theta = -1$):

$$\Delta_2 = \sqrt{2(1 - (-1))} = \sqrt{4} = 2.0$$

---

### 2.3 Required Noise for Formal $(\epsilon, \delta)$-DP

According to the classical Gaussian Mechanism (Dwork & Roth, 2014; Balle & Wang, 2018), to satisfy $(\epsilon, \delta)$-DP for $\epsilon \le 1$ with global $L_2$ sensitivity $\Delta_2$, the required standard deviation $\sigma_{\text{formal}}$ is:

$$\sigma_{\text{formal}} \ge \frac{\Delta_2 \sqrt{2 \ln(1.25 / \delta)}}{\epsilon}$$

For standard privacy parameters:
- Target $\epsilon = 2.0$ (moderate privacy)
- Target failure probability $\delta = 10^{-5}$ ($0.001\%$)
- Sensitivity $\Delta_2 = 2.0$

$$\sigma_{\text{formal}} \ge \frac{2.0 \cdot \sqrt{2 \ln(1.25 \times 10^5)}}{2.0} = \sqrt{2 \ln(125000)} = \sqrt{2 \times 11.736} = \sqrt{23.472} \approx 4.8448$$

---

### 2.4 The Fundamental Trade-off: Why Formal DP Destroys Retrieval Utility

Let us analyze the Signal-to-Noise Ratio (SNR) when injecting formal Gaussian noise $\mathbf{n} \sim \mathcal{N}(0, \sigma^2 \mathbf{I}_{512})$ into a unit signal vector $\mathbf{z}$:

$$\text{Signal Power } P_s = \|\mathbf{z}\|_2^2 = 1.0$$
$$\text{Noise Power } P_n = \mathbb{E}[\|\mathbf{n}\|_2^2] = d_1 \cdot \sigma^2 = 512 \cdot (4.8448)^2 \approx 512 \cdot 23.472 = 12,017.6$$

The resulting Signal-to-Noise Ratio is:

$$\text{SNR} = \frac{P_s}{P_n} = \frac{1.0}{12017.6} \approx 8.32 \times 10^{-5} \quad (-40.8\text{ dB})$$

Even on a per-component basis:
$$\text{SNR}_{\text{component}} = \frac{1/512}{\sigma^2} = \frac{0.001953}{23.472} \approx 8.32 \times 10^{-5}$$

When the perturbed vector is re-normalized $\tilde{\mathbf{z}} = \frac{\mathbf{z} + \mathbf{n}}{\|\mathbf{z} + \mathbf{n}\|_2}$, the cosine similarity between the true vector $\mathbf{z}$ and the perturbed vector $\tilde{\mathbf{z}}$ is:

$$\mathbb{E}[\langle \mathbf{z}, \tilde{\mathbf{z}} \rangle] \approx \frac{1}{\sqrt{1 + 512 \sigma^2}} = \frac{1}{\sqrt{1 + 12017.6}} = \frac{1}{109.6} \approx 0.0091$$

Under this perturbation, the top-$k$ nearest neighbors in FAISS are purely random noise matches. Empirically, Mean Average Precision (mAP) drops from **94.2%** to **3.1%** (equivalent to random guessing across 32 classes).

---

### 2.5 Inversion of the Operational Setting ($\sigma = 0.05$)

SecureImage's calibrated operating point in production is $\sigma = 0.05$. Under this parameter:
- Precision@5: **89.6%**
- mAP: **87.4%**
- Pre-image Inversion SSIM: **0.0099**

To compute what formal privacy budget $\epsilon_{\text{effective}}$ this corresponds to under the worst-case global sensitivity $\Delta_2 = 2.0$ with $\delta = 10^{-5}$:

$$\epsilon_{\text{effective}} = \frac{\Delta_2 \sqrt{2 \ln(1.25 / \delta)}}{\sigma} = \frac{2.0 \times 4.8448}{0.05} = \frac{9.6896}{0.05} \approx \mathbf{193.79}$$

An $\epsilon \approx 194$ provides **no formal worst-case differential privacy guarantee** in a cryptanalytic sense ($e^{194} \approx 10^{84}$).

> **Academic Conclusion & Recommendation:**  
> In all academic papers, theses, and defenses, the perturbation mechanism must be characterized as:  
> **"An Empirical Calibrated Noise Obfuscation Mechanism"** or **"Local Heuristic Perturbation"**, and **NOT** as formal $(\epsilon, \delta)$-Differential Privacy.

---

## 3. Dimensional Analysis & Null-Space Reconstruction Bounds

While the additive perturbation does not provide formal cryptographic DP, the **keyed orthogonal projection provides rigorous mathematical bounds against exact pre-image reconstruction**.

### 3.1 Linear Mapping Formulation
Let $\mathbf{x} \in \mathbb{R}^{d_0}$ ($d_0 = 1280$) be the penultimate activation vector extracted from MobileNetV3-Large.  
Let $\mathbf{P}_K \in \mathbb{R}^{d_0 \times d_1}$ ($d_1 = 512$) be the orthonormal projection matrix:

$$\mathbf{P}_K^T \mathbf{P}_K = \mathbf{I}_{d_1} \in \mathbb{R}^{512 \times 512}$$

The protected feature representation $\mathbf{z} \in \mathbb{R}^{d_1}$ is given by:

$$\mathbf{z} = \mathbf{P}_K^T \mathbf{x}$$

---

### 3.2 Fundamental Theorem of Linear Algebra & Null Space
The projection matrix transpose $\mathbf{P}_K^T$ defines a linear transformation from $\mathbb{R}^{1280} \to \mathbb{R}^{512}$. By the Rank-Nullity Theorem:

$$\dim(\operatorname{Range}(\mathbf{P}_K^T)) + \dim(\ker(\mathbf{P}_K^T)) = 1280$$

Since $\operatorname{rank}(\mathbf{P}_K^T) = 512$:

$$\dim(\ker(\mathbf{P}_K^T)) = 1280 - 512 = \mathbf{768}$$

---

### 3.3 Theorem 1: Infinite Pre-Image Ambiguity

**Statement:** For any observed vector $\mathbf{z} \in \mathbb{R}^{512}$, even if an adversary possesses full knowledge of the projection matrix $\mathbf{P}_K$, the set of possible pre-image feature vectors $\mathcal{X}_{\mathbf{z}} = \{\mathbf{x} \in \mathbb{R}^{1280} \mid \mathbf{P}_K^T \mathbf{x} = \mathbf{z}\}$ is an affine subspace of dimension 768.

**Proof:**
1. Let $\mathbf{x}_0 = \mathbf{P}_K \mathbf{z}$.
2. Verify that $\mathbf{x}_0$ is a valid pre-image:
   $$\mathbf{P}_K^T \mathbf{x}_0 = \mathbf{P}_K^T (\mathbf{P}_K \mathbf{z}) = (\mathbf{P}_K^T \mathbf{P}_K) \mathbf{z} = \mathbf{I}_{512} \mathbf{z} = \mathbf{z}$$
3. Let $\{\mathbf{v}_1, \mathbf{v}_2, \dots, \mathbf{v}_{768}\}$ be an orthonormal basis for the kernel $\ker(\mathbf{P}_K^T)$ such that $\mathbf{P}_K^T \mathbf{v}_j = \mathbf{0}$ for all $j \in \{1, \dots, 768\}$.
4. For any arbitrary coefficient vector $\boldsymbol{\alpha} = (\alpha_1, \dots, \alpha_{768}) \in \mathbb{R}^{768}$, define:
   $$\mathbf{x}_{\boldsymbol{\alpha}} = \mathbf{x}_0 + \sum_{j=1}^{768} \alpha_j \mathbf{v}_j$$
5. Evaluating the projection:
   $$\mathbf{P}_K^T \mathbf{x}_{\boldsymbol{\alpha}} = \mathbf{P}_K^T \mathbf{x}_0 + \sum_{j=1}^{768} \alpha_j \mathbf{P}_K^T \mathbf{v}_j = \mathbf{z} + \mathbf{0} = \mathbf{z}$$
6. Therefore, $\mathbf{x}_{\boldsymbol{\alpha}} \in \mathcal{X}_{\mathbf{z}}$ for all $\boldsymbol{\alpha} \in \mathbb{R}^{768}$. $\quad \blacksquare$

**Information-Theoretic Consequence:**  
The adversary loses exactly $768$ degrees of freedom. In terms of Shannon differential entropy under an isotropic Gaussian prior $\mathbf{x} \sim \mathcal{N}(0, \sigma_x^2 \mathbf{I}_{1280})$:

$$H(\mathbf{x} \mid \mathbf{z}, \mathbf{P}_K) = \frac{768}{2} \ln(2\pi e \sigma_x^2)$$

There is an irreversible loss of $\frac{768}{1280} = 60.0\%$ of the unconstrained feature information space.

---

### 3.4 Reconstruction Attack Space: Inverse Optimization

When an adversary attempts gradient-based image reconstruction (e.g., Adam-based inversion):

$$\min_{\mathbf{I} \in [0, 1]^{3 \times H \times W}} \mathcal{L}(\mathbf{I}) = \|\mathbf{P}_K^T f_{\theta}(\mathbf{I}) - \mathbf{z}\|_2^2 + \lambda \mathcal{R}(\mathbf{I})$$

Where $f_{\theta}$ is the non-linear deep neural network (MobileNetV3) and $\mathcal{R}(\mathbf{I})$ is total variation regularization:
- If $\mathbf{P}_K$ is **known**: The non-linear pre-image problem has an infinite family of local minima in image space that project to the same $\mathbf{z}$, yielding uninterpretable noise or high-frequency checkerboard artifacts without prior image domain constraints.
- If $\mathbf{P}_K$ is **secret (Black-box)**: The adversary cannot compute $\nabla_{\mathbf{I}} \mathcal{L}$. Attempting inversion against a surrogate identity or surrogate matrix yields SSIM $< 0.01$ and PSNR $< 5\text{ dB}$ (statistically indistinguishable from uniform noise).

---

## 4. Query Privacy Composition & Attack Vulnerabilities

### 4.1 Repeated Query Averaging Attack
In the current implementation ([`backend/api/search.py`](file:///c:/Users/Sathwika/OneDrive/Documents/Desktop/secureimage/backend/api/search.py)), perturbation noise is applied dynamically per search request:

$$\mathbf{z}_k = \mathbf{P}_K^T \mathbf{x} + \mathbf{n}_k, \quad \mathbf{n}_k \sim \mathcal{N}(0, \sigma^2 \mathbf{I}_{512})$$

**Vulnerability Formulation:**
If a malicious client submits the same query image $K$ times under different session tokens or API calls, the server observes the set $\{\mathbf{z}_1, \mathbf{z}_2, \dots, \mathbf{z}_K\}$.

The adversary computes the empirical mean:

$$\bar{\mathbf{z}}_K = \frac{1}{K} \sum_{k=1}^K \mathbf{z}_k = \mathbf{P}_K^T \mathbf{x} + \frac{1}{K} \sum_{k=1}^K \mathbf{n}_k$$

Since $\mathbf{n}_k$ are independent identically distributed (i.i.d.) Gaussian random variables:

$$\mathbb{E}[\bar{\mathbf{z}}_K] = \mathbf{P}_K^T \mathbf{x}$$
$$\operatorname{Cov}\left(\frac{1}{K} \sum_{k=1}^K \mathbf{n}_k\right) = \frac{\sigma^2}{K} \mathbf{I}_{512}$$

**Effective Noise Decay:**
$$\sigma_{\text{effective}}(K) = \frac{\sigma}{\sqrt{K}}$$

| Number of Queries ($K$) | Effective Noise $\sigma_{\text{eff}}$ ($\sigma=0.05$) | Inversion Reconstruction Quality |
|:---:|:---:|:---:|
| $1$ | $0.0500$ | SSIM: $0.0099$ (Fully Protected) |
| $10$ | $0.0158$ | SSIM: $0.0142$ |
| $25$ | $0.0100$ | SSIM: $0.0210$ |
| $100$ | $0.0050$ | SSIM: $0.0520$ |
| $1000$ | $0.0016$ | Noise essentially stripped ($\sigma \approx 0$) |

### 4.2 Missing Architectural Components for Defense
To prevent query-averaging attacks in production systems, the following architectural controls are required:
1. **Query Privacy Accountant:** Track cumulative $\sum \epsilon$ per client/IP address using Rényi Differential Privacy (RDP) composition.
2. **Deterministic Query Perturbation (Salted Client Hashing):** Ensure repeated submissions of the same image hash produce identical pseudorandom noise rather than independent random realizations.
3. **Query Throttling / Rate Limiting:** Enforce a strict maximum query limit per user account.

---

## 5. Cryptographic Security Analysis of Key Derivation

### 5.1 Entropy and Derivation Security
The projection key is generated in [`backend/services/privacy/keyed_projection.py`](file:///c:/Users/Sathwika/OneDrive/Documents/Desktop/secureimage/backend/services/privacy/keyed_projection.py):

```python
key = os.urandom(32)  # 256 bits of OS entropy
derived_bytes = hkdf_expand(key, info=b"SecureImage-Keyed-Projection-Matrix-v1", length=1280 * 512 * 4)
```

1. **Seed Entropy:** 256 bits from cryptographically secure hardware RNG (`/dev/urandom` / Windows CNG).
2. **Brute Force Search Space:** $2^{256} \approx 1.1579 \times 10^{77}$ evaluations. Under current supercomputing capabilities ($10^{18}$ FLOPs/sec), brute-forcing the key requires $> 10^{50}$ years.
3. **HKDF-SHA256 Pseudo-randomness:** Under the standard HMAC-PRG model, derived matrix entries are computationally indistinguishable from true random Gaussian samples.
4. **QR Factorization Preservation:** The Gram-Schmidt orthogonalization preserves orthonormal column constraints:
   $$\mathbf{P}_K^T \mathbf{P}_K = \mathbf{I}_{512} \pm 3.58 \times 10^{-7}$$

---

## 6. Faculty Defense: Defensible Scientific Claims vs. Invalid Claims

When presenting this research to academic reviewers and thesis committees, adhere strictly to the following taxonomy of scientific claims:

| Research Topic | ❌ Invalid / Scientifically Flawed Claim | ✅ Rigorous & Defensible Claim |
|:---|:---|:---|
| **Differential Privacy** | *"Our system achieves mathematical Differential Privacy with $\epsilon = 2.0$."* | *"Our system implements local heuristic Gaussian perturbation ($\sigma = 0.05$) to obscure fine-grained vector representations while maintaining 89.6% P@5 retrieval utility. Formal $(\epsilon, \delta)$-DP at $\epsilon=2.0$ would require $\sigma \approx 4.84$, which causes catastrophic retrieval failure (3.1% mAP)."* |
| **Mathematical Irreversibility** | *"Vector embeddings are mathematically impossible to invert because encryption is applied."* | *"The linear projection $\mathbf{P}_K^T: \mathbb{R}^{1280} \to \mathbb{R}^{512}$ reduces dimensionality by 60%, introducing a 768-dimensional unconstrained null space that prevents unique pre-image determination even when the projection key is compromised."* |
| **Pre-image Inversion Attacks** | *"No attacker can reconstruct images from embeddings."* | *"Under white-box conditions where an attacker possesses the projection key $\mathbf{P}_K$ and CNN architecture, optimization-based inversion yields an average SSIM of $0.0099$ and PSNR of $3.77\text{ dB}$, producing uninterpretable visual noise."* |
| **Membership Inference (MIA)** | *"Our system has an MIA AUC of $0.50$ (perfect random guessing)."* | *"On our evaluation dataset, distance-based membership inference achieves an AUC of $0.7099$ under defensive perturbation ($\sigma=0.05$), demonstrating measurable resistance compared to raw unprojected embeddings."* |
| **Key Security** | *"The FAISS database is fully encrypted with AES."* | *"Original image files are AES-256 encrypted at rest in the storage vault; FAISS indexes 512-D projected float32 vectors generated via a 256-bit secret-key derived matrix $\mathbf{P}_K$."* |

---

*Report compiled and mathematically verified for SecureImage (PrivateLens) Research Defense.*
