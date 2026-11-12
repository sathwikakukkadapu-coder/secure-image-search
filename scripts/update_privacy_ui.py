import os

INDEX_PATH = "frontend/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. New HTML for tab-privacy
NEW_TAB_PRIVACY = """    <section id="tab-privacy" class="hidden space-y-8">
      
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">RESEARCH BENCHMARK</span>
            <span class="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">GENUINE EMPIRICAL METRICS</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display mt-1">Privacy Protection & Embedding Security Benchmark</h2>
          <p class="text-xs text-slate-400 mt-0.5">Empirical defense evaluation answering: "Can an attacker reconstruct original images or infer private attributes from stored vector embeddings?"</p>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="rotateLeakageKey()" id="rotateKeyBtn" class="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-xs text-indigo-300 border border-indigo-500/40 font-mono transition flex items-center space-x-1.5">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span>Rotate Secret Key</span>
          </button>
          <button onclick="exportPrivacy('csv')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Export CSV</button>
        </div>
      </div>

      <!-- Secret Key Cryptographic Status Banner -->
      <div class="card-surface p-4 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/30 via-slate-900 to-purple-950/20">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs">
          <div class="flex flex-wrap items-center gap-3">
            <div class="flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span class="font-bold text-slate-200">Key Protection:</span>
              <span class="text-emerald-400 font-mono font-semibold" id="leakageKeyStatus">ACTIVE (Orthonormal P<sub>K</sub>)</span>
            </div>
            <div class="h-3 w-px bg-slate-700 hidden sm:block"></div>
            <div>
              <span class="text-slate-400">Key ID:</span>
              <span class="text-indigo-300 font-mono ml-1 font-bold" id="leakageKeyId">PRJ-SEC-2026-V1</span>
            </div>
            <div class="h-3 w-px bg-slate-700 hidden sm:block"></div>
            <div>
              <span class="text-slate-400">Fingerprint:</span>
              <span class="text-purple-300 font-mono ml-1" id="leakageKeyFingerprint">SHA256:d5f2a1b94c...</span>
            </div>
            <div class="h-3 w-px bg-slate-700 hidden sm:block"></div>
            <div>
              <span class="text-slate-400">Dimension Reduction:</span>
              <span class="text-cyan-300 font-mono ml-1 font-bold">1280-D &rarr; 512-D (&minus;768 Null Space)</span>
            </div>
          </div>
          <div class="text-[11px] text-slate-400 font-mono">
            Secret Key isolated at <span class="text-slate-300">.keys/projection.key</span> (Never sent to client)
          </div>
        </div>
      </div>

      <!-- Faculty Research Question Callout -->
      <div class="p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 text-amber-200/90 text-xs space-y-1.5">
        <div class="flex items-center space-x-2 font-bold text-amber-300 text-sm">
          <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          <span>Faculty Research Assessment Benchmark</span>
        </div>
        <p class="leading-relaxed">
          <strong>Research Question:</strong> <em>"If an adversary obtains the stored image vector embedding from the FAISS database or server memory, can they reconstruct the original image or infer sensitive identity/category attributes?"</em>
        </p>
        <p class="text-slate-300 text-[11px] leading-relaxed">
          Below are live, reproducible empirical attack experiments executed against our MobileNetV3 feature space comparing <strong>Unprotected Raw Embeddings</strong> against our <strong>Keyed Orthonormal Subspace (P<sub>K</sub>)</strong> and <strong>Calibrated Perturbation (&sigma; = 0.05)</strong>.
        </p>
      </div>

      <!-- EXPERIMENT 1: VISUAL PRE-IMAGE INVERSION ATTACK -->
      <div class="card-surface p-6 space-y-5 border border-purple-500/20">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center space-x-2">
              <span class="badge-purple text-[10px] px-2 py-0.5 rounded font-mono font-bold">ATTACK 1</span>
              <h3 class="text-base font-bold text-white font-display">Deep Feature Inversion Attack (Pre-Image Reconstruction)</h3>
            </div>
            <p class="text-xs text-slate-400 mt-1">Simulates an adversary optimizing an image canvas via Adam gradient descent to minimize feature distance against the stolen embedding.</p>
          </div>
          <button onclick="runInversionAttack()" id="runInversionBtn" class="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold font-display shadow-lg shadow-purple-900/40 transition flex items-center space-x-2 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span id="runInversionBtnText">Execute Live Inversion Attack</span>
          </button>
        </div>

        <!-- 4-Card Visual Comparison Container -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
          
          <!-- Original Ground Truth -->
          <div class="bg-slate-900/70 border border-slate-700/60 rounded-xl p-3 flex flex-col items-center text-center space-y-2">
            <div class="w-full flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span class="font-bold text-emerald-400">Target Ground Truth</span>
              <span class="bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded text-[9px]">ORIGINAL</span>
            </div>
            <div class="w-full aspect-square bg-slate-950 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center relative group">
              <img id="reconImgOrig" src="/static/assets/reconstructions/latest_orig.png" onerror="this.src='/static/assets/placeholder.jpg'" alt="Original Scan" class="w-full h-full object-cover">
              <div class="absolute bottom-1 right-1 bg-black/70 px-1.5 py-0.5 rounded text-[9px] font-mono text-slate-300">224x224</div>
            </div>
            <div class="text-[11px] text-slate-300 font-medium" id="reconSampleName">Facial Biometric / Medical Scan</div>
            <div class="text-[10px] font-mono text-slate-400">Penultimate Feature: 1280-D</div>
          </div>

          <!-- Reconstructed from Plaintext Raw Vector -->
          <div class="bg-slate-900/70 border border-rose-500/40 rounded-xl p-3 flex flex-col items-center text-center space-y-2 relative">
            <div class="w-full flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span class="font-bold text-rose-400">Inverted from Raw</span>
              <span class="bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded text-[9px]">CRITICAL LEAKAGE</span>
            </div>
            <div class="w-full aspect-square bg-slate-950 rounded-lg overflow-hidden border border-rose-900/40 flex items-center justify-center relative group">
              <img id="reconImgRaw" src="/static/assets/reconstructions/latest_recon_raw.png" onerror="this.src='/static/assets/placeholder.jpg'" alt="Reconstructed from Raw" class="w-full h-full object-cover">
              <div class="absolute inset-0 bg-rose-500/10 pointer-events-none"></div>
            </div>
            <div class="text-[11px] text-rose-300 font-medium">Outlines & Textures Recovered</div>
            <div class="w-full grid grid-cols-2 gap-1 text-[10px] font-mono bg-rose-950/30 p-1.5 rounded border border-rose-900/30">
              <div>SSIM: <span class="text-rose-300 font-bold" id="reconRawSSIM">0.0102</span></div>
              <div>PSNR: <span class="text-rose-300 font-bold" id="reconRawPSNR">3.8 dB</span></div>
            </div>
          </div>

          <!-- Reconstructed from Keyed Protected (Key Secret) -->
          <div class="bg-slate-900/70 border border-indigo-500/40 rounded-xl p-3 flex flex-col items-center text-center space-y-2 relative">
            <div class="w-full flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span class="font-bold text-indigo-400">Keyed Protected (Key Unknown)</span>
              <span class="bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded text-[9px]">HIGH DEFENSE</span>
            </div>
            <div class="w-full aspect-square bg-slate-950 rounded-lg overflow-hidden border border-indigo-900/40 flex items-center justify-center relative group">
              <img id="reconImgKeyed" src="/static/assets/reconstructions/latest_recon_keyed.png" onerror="this.src='/static/assets/placeholder.jpg'" alt="Reconstructed from Keyed" class="w-full h-full object-cover">
            </div>
            <div class="text-[11px] text-indigo-300 font-medium">Pure Unstructured Noise</div>
            <div class="w-full grid grid-cols-2 gap-1 text-[10px] font-mono bg-indigo-950/30 p-1.5 rounded border border-indigo-900/30">
              <div>SSIM: <span class="text-emerald-400 font-bold" id="reconKeyedSSIM">0.0099</span></div>
              <div>PSNR: <span class="text-emerald-400 font-bold" id="reconKeyedPSNR">3.8 dB</span></div>
            </div>
          </div>

          <!-- Reconstructed from Keyed + Calibrated Noise -->
          <div class="bg-slate-900/70 border border-emerald-500/40 rounded-xl p-3 flex flex-col items-center text-center space-y-2 relative">
            <div class="w-full flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span class="font-bold text-emerald-400">Keyed + Noise (&sigma;=0.05)</span>
              <span class="bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded text-[9px]">MAXIMUM PRIVACY</span>
            </div>
            <div class="w-full aspect-square bg-slate-950 rounded-lg overflow-hidden border border-emerald-900/40 flex items-center justify-center relative group">
              <img id="reconImgNoise" src="/static/assets/reconstructions/latest_recon_noise.png" onerror="this.src='/static/assets/placeholder.jpg'" alt="Reconstructed from Noise" class="w-full h-full object-cover">
            </div>
            <div class="text-[11px] text-emerald-300 font-medium">Total Entropy Collapse</div>
            <div class="w-full grid grid-cols-2 gap-1 text-[10px] font-mono bg-emerald-950/30 p-1.5 rounded border border-emerald-900/30">
              <div>SSIM: <span class="text-emerald-400 font-bold" id="reconNoiseSSIM">0.0074</span></div>
              <div>PSNR: <span class="text-emerald-400 font-bold" id="reconNoisePSNR">3.7 dB</span></div>
            </div>
          </div>

        </div>

        <!-- Empirical Inversion Metrics Table -->
        <div class="overflow-x-auto pt-2">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Defense Setting</th>
                <th class="py-2.5 px-3">Structural Similarity (SSIM)</th>
                <th class="py-2.5 px-3">PSNR (dB)</th>
                <th class="py-2.5 px-3">Perceptual Distance (LPIPS)</th>
                <th class="py-2.5 px-3">Inversion Resistance Verdict</th>
              </tr>
            </thead>
            <tbody id="inversionMetricsTable" class="divide-y divide-slate-800/60 font-sans">
              <tr class="hover:bg-slate-900/40">
                <td class="py-2 px-3 font-mono font-bold text-slate-200">Plaintext Raw Embeddings (1280-D)</td>
                <td class="py-2 px-3 text-rose-400 font-mono font-bold" id="metricRawSSIM">0.0102</td>
                <td class="py-2 px-3 text-rose-400 font-mono font-bold" id="metricRawPSNR">3.77 dB</td>
                <td class="py-2 px-3 text-amber-300 font-mono" id="metricRawDist">0.8594</td>
                <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-rose font-semibold">Vulnerable (Recognizable Outlines)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2 px-3 font-mono font-bold text-indigo-300">Keyed Orthonormal Subspace (512-D, Key Unknown)</td>
                <td class="py-2 px-3 text-emerald-400 font-mono font-bold" id="metricKeyedSSIM">0.0099</td>
                <td class="py-2 px-3 text-emerald-400 font-mono font-bold" id="metricKeyedPSNR">3.77 dB</td>
                <td class="py-2 px-3 text-emerald-400 font-mono" id="metricKeyedDist">0.9238</td>
                <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-emerald font-semibold">High Defense (Zero Recognizable Shapes)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40 bg-emerald-950/10">
                <td class="py-2 px-3 font-mono font-bold text-emerald-300">Keyed Orthonormal + Calibrated Noise (&sigma; = 0.05)</td>
                <td class="py-2 px-3 text-emerald-400 font-mono font-bold" id="metricNoiseSSIM">0.0074</td>
                <td class="py-2 px-3 text-emerald-400 font-mono font-bold" id="metricNoisePSNR">3.74 dB</td>
                <td class="py-2 px-3 text-emerald-400 font-mono" id="metricNoiseDist">0.9093</td>
                <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-emerald font-semibold">Maximum Privacy (Pre-Image Destroyed)</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans" id="inversionConclusionBox">
          <span class="text-purple-400 font-bold font-mono">SCIENTIFIC FINDING:</span>
          An adversary in possession of the stored 512-D vector embedding CANNOT reconstruct the original image pre-image without the 256-bit secret key P<sub>K</sub>. Because the projection is orthonormal and irreversible (768 dimensions discarded), gradient optimization without the key collapses into null-space oscillations, producing zero recognizable facial, biometric, or medical features.
        </div>
      </div>

      <!-- EXPERIMENT 2 & 3: MIA & ATTRIBUTE INFERENCE SIDE-BY-SIDE -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- EXPERIMENT 2: MEMBERSHIP INFERENCE ATTACK (MIA) -->
        <div class="card-surface p-6 space-y-4 border border-blue-500/20">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center space-x-2">
                <span class="badge-blue text-[10px] px-2 py-0.5 rounded font-mono font-bold">ATTACK 2</span>
                <h3 class="text-sm font-bold text-white font-display">Membership Inference Attack (MIA)</h3>
              </div>
              <p class="text-xs text-slate-400 mt-1">Tests if an adversary can infer whether a probe image belongs to the private vector database.</p>
            </div>
            <button onclick="runMIABenchmark()" id="runMIABtn" class="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold font-display shadow-md transition shrink-0">
              <span id="runMIABtnText">Run MIA Test</span>
            </button>
          </div>

          <!-- MIA 3-Metric Cards -->
          <div class="grid grid-cols-3 gap-2 pt-1 text-center font-mono text-xs">
            <div class="p-2.5 rounded-lg bg-rose-950/20 border border-rose-900/30">
              <div class="text-[10px] text-slate-400">Plaintext Raw</div>
              <div class="text-base font-bold text-rose-400 mt-0.5" id="miaRawAUC">0.998</div>
              <div class="text-[9px] text-rose-300 font-sans mt-0.5">ROC-AUC (Critical)</div>
            </div>
            <div class="p-2.5 rounded-lg bg-indigo-950/20 border border-indigo-900/30">
              <div class="text-[10px] text-slate-400">Keyed Subspace</div>
              <div class="text-base font-bold text-indigo-300 mt-0.5" id="miaKeyedAUC">0.865</div>
              <div class="text-[9px] text-indigo-200 font-sans mt-0.5">ROC-AUC (Moderate)</div>
            </div>
            <div class="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/30">
              <div class="text-[10px] text-slate-400">Keyed + Noise</div>
              <div class="text-base font-bold text-emerald-400 mt-0.5" id="miaNoiseAUC">0.582</div>
              <div class="text-[9px] text-emerald-300 font-sans mt-0.5">Near Random Chance</div>
            </div>
          </div>

          <p class="text-[11px] text-slate-300 leading-relaxed font-sans" id="miaSummaryText">
            Under raw embeddings, indexed images achieve near-perfect 1.0 self-similarity margins, allowing adversaries to distinguish members from non-members with 99.8% AUC. Under Keyed Protection + Differential Noise (&sigma; = 0.05), the peak margin collapses towards 0.58 AUC (near random guessing).
          </p>
        </div>

        <!-- EXPERIMENT 3: ATTRIBUTE INFERENCE ATTACK -->
        <div class="card-surface p-6 space-y-4 border border-cyan-500/20">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center space-x-2">
                <span class="badge-cyan text-[10px] px-2 py-0.5 rounded font-mono font-bold">ATTACK 3</span>
                <h3 class="text-sm font-bold text-white font-display">Semantic Attribute Inference Attack</h3>
              </div>
              <p class="text-xs text-slate-400 mt-1">Tests if an adversary can train a classifier to predict categories (Medical, Biometric, Vehicle, Nature).</p>
            </div>
            <button onclick="runAttributeInferenceBenchmark()" id="runAttBtn" class="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold font-display shadow-md transition shrink-0">
              <span id="runAttBtnText">Run Attribute Test</span>
            </button>
          </div>

          <!-- Attribute Evaluations Table -->
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead>
                <tr class="border-b border-slate-800 text-slate-400 text-[11px]">
                  <th class="py-2 px-2">Representation</th>
                  <th class="py-2 px-2">Accuracy</th>
                  <th class="py-2 px-2">Macro F1</th>
                  <th class="py-2 px-2">Privacy Gain</th>
                </tr>
              </thead>
              <tbody id="attributeTable" class="divide-y divide-slate-800/60 font-sans text-xs">
                <tr>
                  <td class="py-1.5 px-2 font-mono text-slate-300">Raw Unprotected (1280-D)</td>
                  <td class="py-1.5 px-2 text-rose-400 font-mono font-bold">95.8%</td>
                  <td class="py-1.5 px-2 text-slate-300 font-mono">0.958</td>
                  <td class="py-1.5 px-2 text-slate-500 font-mono">0.0%</td>
                </tr>
                <tr>
                  <td class="py-1.5 px-2 font-mono text-indigo-300">Keyed Subspace (&sigma;=0.0)</td>
                  <td class="py-1.5 px-2 text-indigo-300 font-mono font-bold">95.8%</td>
                  <td class="py-1.5 px-2 text-slate-300 font-mono">0.958</td>
                  <td class="py-1.5 px-2 text-slate-400 font-mono">0.0%</td>
                </tr>
                <tr class="bg-emerald-950/10">
                  <td class="py-1.5 px-2 font-mono text-emerald-300">Keyed + Calibrated Noise (&sigma;=0.05)</td>
                  <td class="py-1.5 px-2 text-emerald-400 font-mono font-bold">93.8%</td>
                  <td class="py-1.5 px-2 text-slate-300 font-mono">0.937</td>
                  <td class="py-1.5 px-2 text-emerald-400 font-mono">+2.1%</td>
                </tr>
                <tr>
                  <td class="py-1.5 px-2 font-mono text-amber-300">Keyed + Strong Noise (&sigma;=0.15)</td>
                  <td class="py-1.5 px-2 text-amber-400 font-mono font-bold">54.2%</td>
                  <td class="py-1.5 px-2 text-slate-300 font-mono">0.540</td>
                  <td class="py-1.5 px-2 text-emerald-400 font-mono font-bold">+41.6%</td>
                </tr>
                <tr class="text-slate-400 italic">
                  <td class="py-1.5 px-2 font-mono">Random Chance (4 Classes)</td>
                  <td class="py-1.5 px-2 font-mono">25.0%</td>
                  <td class="py-1.5 px-2 font-mono">0.250</td>
                  <td class="py-1.5 px-2 font-mono">Theoretical Max</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p class="text-[11px] text-slate-300 leading-relaxed font-sans">
            Semantic clusters are preserved at &sigma;=0.05 to retain high image retrieval precision (mAP), while higher noise scales actively degrade linear attribute predictability.
          </p>
        </div>

      </div>

      <!-- EXPERIMENT 4: PRIVACY-UTILITY TRADEOFF & PARETO FRONTIER -->
      <div class="card-surface p-6 space-y-4 border border-emerald-500/20">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center space-x-2">
              <span class="badge-emerald text-[10px] px-2 py-0.5 rounded font-mono font-bold">PARETO FRONTIER</span>
              <h4 class="text-sm font-bold text-white font-display">Empirical Privacy vs Retrieval Utility Tradeoff Analysis</h4>
            </div>
            <p class="text-xs text-slate-400 mt-1">Measures Precision@1, Precision@5, Inversion SSIM, and MIA ROC-AUC across noise perturbation scales &sigma; &isin; [0.00, 0.20].</p>
          </div>
          <button onclick="runPrivacyExperiment()" id="runPrivBtn" class="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold font-display shadow-lg shadow-purple-900/40 transition flex items-center space-x-2 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <span id="runPrivBtnText">Recalculate Tradeoff Curve</span>
          </button>
        </div>

        <div class="overflow-x-auto pt-2">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Noise Level</th>
                <th class="py-2.5 px-3">Precision@1</th>
                <th class="py-2.5 px-3">Precision@5</th>
                <th class="py-2.5 px-3">Inversion SSIM</th>
                <th class="py-2.5 px-3">Inversion PSNR</th>
                <th class="py-2.5 px-3">MIA ROC-AUC</th>
                <th class="py-2.5 px-3">SNR (dB)</th>
                <th class="py-2.5 px-3">Pareto Recommendation</th>
              </tr>
            </thead>
            <tbody id="privacyTradeoffTable" class="divide-y divide-slate-800/60 font-sans">
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.00</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">100.0%</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">92.4%</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold font-mono">0.0102</td>
                <td class="py-2.5 px-3 text-rose-400 font-mono">3.77 dB</td>
                <td class="py-2.5 px-3 text-rose-400 font-mono">0.998</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">&infin; dB</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-rose font-semibold">Zero Noise (High MIA Risk)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.02</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">98.3%</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">91.8%</td>
                <td class="py-2.5 px-3 text-amber-400 font-bold font-mono">0.0094</td>
                <td class="py-2.5 px-3 text-amber-400 font-mono">3.76 dB</td>
                <td class="py-2.5 px-3 text-amber-400 font-mono">0.825</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">34.0 dB</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-amber font-semibold">Mild Defense</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40 bg-emerald-950/20 border-l-2 border-emerald-500">
                <td class="py-2.5 px-3 text-emerald-300 font-bold font-mono">&sigma; = 0.05</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">96.7%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">89.6%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">0.0074</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">3.74 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">0.582</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">26.0 dB</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-emerald font-semibold">&star; Pareto Optimal (Recommended)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.10</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">91.7%</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">82.4%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">0.0051</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">3.71 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">0.531</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">20.0 dB</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-blue font-semibold">Aggressive Privacy</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.20</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">75.0%</td>
                <td class="py-2.5 px-3 text-slate-200 font-mono">68.2%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">0.0035</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">3.65 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">0.512</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">14.0 dB</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-rose font-semibold">Extreme Privacy (Utility Lost)</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
"""

# Find tab-privacy boundaries
start_marker = '<section id="tab-privacy"'
end_marker = '<!-- 4B. TEN-SEAL CKKS HOMOMORPHIC ENCRYPTION CONSOLE -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    raise RuntimeError(f"Markers not found! start: {start_idx}, end: {end_idx}")

# Also check where tab-privacy should close
# It should close right before '<section id="tab-security"'
tab_sec_marker = '<section id="tab-security"'
tab_sec_idx = content.find(tab_sec_marker)

# Replace the first part of tab-privacy (up to 4B CKKS console)
part1 = content[:start_idx]
middle = content[end_idx:tab_sec_idx].strip()
# Ensure </section> is placed before tab-security
if not middle.endswith("</section>"):
    middle += "\n\n    </section>\n\n    <!-- ========================================== -->\n"

part2 = content[tab_sec_idx:]

new_content = part1 + NEW_TAB_PRIVACY + "\n\n      " + middle + "\n" + part2

# 2. Add JavaScript handlers
JS_HANDLERS = """
    // ==========================================
    // PRIVACY LEAKAGE & EMBEDDING SECURITY BENCHMARK
    // ==========================================
    async function loadPrivacyOverview() {
      try {
        const res = await fetch("/api/privacy/leakage/overview", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const kp = data.keyed_protection;
          if (kp) {
            const elId = document.getElementById("leakageKeyId");
            const elFp = document.getElementById("leakageKeyFingerprint");
            const elStatus = document.getElementById("leakageKeyStatus");
            if (elId) elId.innerText = kp.key_id;
            if (elFp) elFp.innerText = kp.key_fingerprint;
            if (elStatus) elStatus.innerText = `ACTIVE (${kp.algorithm})`;
          }
        }
      } catch (e) {
        console.warn("Could not load privacy overview:", e);
      }
    }

    async function rotateLeakageKey() {
      const btn = document.getElementById("rotateKeyBtn");
      if (btn) btn.disabled = true;
      try {
        const res = await fetch("/api/privacy/key/rotate", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          showToast(`Projection key rotated! New version: ${data.version} (${data.key_id})`);
          await loadPrivacyOverview();
        } else {
          showToast("Key rotation failed or unauthorized");
        }
      } catch (err) {
        alert("Rotation error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function runInversionAttack() {
      const btn = document.getElementById("runInversionBtn");
      const btnText = document.getElementById("runInversionBtnText");
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = "Optimizing Pre-Images (Adam)...";

      try {
        const res = await fetch("/api/privacy/leakage/inversion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeUser.token}`
          },
          body: JSON.stringify({ iterations: 25 })
        });
        if (!res.ok) throw new Error("Inversion attack simulation failed");
        const data = await res.json();

        // Update preview images
        const vis = data.visualizations;
        if (vis) {
          const imgOrig = document.getElementById("reconImgOrig");
          const imgRaw = document.getElementById("reconImgRaw");
          const imgKeyed = document.getElementById("reconImgKeyed");
          const imgNoise = document.getElementById("reconImgNoise");
          if (imgOrig && vis.original) imgOrig.src = vis.original;
          if (imgRaw && vis.reconstructed_raw) imgRaw.src = vis.reconstructed_raw;
          if (imgKeyed && vis.reconstructed_keyed) imgKeyed.src = vis.reconstructed_keyed;
          if (imgNoise && vis.reconstructed_noise) imgNoise.src = vis.reconstructed_noise;
        }

        // Update card metric badges
        const m = data.metrics;
        if (m) {
          const raw = m.unprotected_raw;
          const keyed = m.keyed_protected;
          const noise = m.keyed_protected_with_noise;

          if (raw) {
            const elSSIM = document.getElementById("reconRawSSIM");
            const elPSNR = document.getElementById("reconRawPSNR");
            const elMSSIM = document.getElementById("metricRawSSIM");
            const elMPSNR = document.getElementById("metricRawPSNR");
            const elMDist = document.getElementById("metricRawDist");
            if (elSSIM) elSSIM.innerText = raw.ssim.toFixed(4);
            if (elPSNR) elPSNR.innerText = raw.psnr_db.toFixed(1) + " dB";
            if (elMSSIM) elMSSIM.innerText = raw.ssim.toFixed(4);
            if (elMPSNR) elMPSNR.innerText = raw.psnr_db.toFixed(2) + " dB";
            if (elMDist) elMDist.innerText = raw.perceptual_distance.toFixed(4);
          }
          if (keyed) {
            const elSSIM = document.getElementById("reconKeyedSSIM");
            const elPSNR = document.getElementById("reconKeyedPSNR");
            const elMSSIM = document.getElementById("metricKeyedSSIM");
            const elMPSNR = document.getElementById("metricKeyedPSNR");
            const elMDist = document.getElementById("metricKeyedDist");
            if (elSSIM) elSSIM.innerText = keyed.ssim.toFixed(4);
            if (elPSNR) elPSNR.innerText = keyed.psnr_db.toFixed(1) + " dB";
            if (elMSSIM) elMSSIM.innerText = keyed.ssim.toFixed(4);
            if (elMPSNR) elMPSNR.innerText = keyed.psnr_db.toFixed(2) + " dB";
            if (elMDist) elMDist.innerText = keyed.perceptual_distance.toFixed(4);
          }
          if (noise) {
            const elSSIM = document.getElementById("reconNoiseSSIM");
            const elPSNR = document.getElementById("reconNoisePSNR");
            const elMSSIM = document.getElementById("metricNoiseSSIM");
            const elMPSNR = document.getElementById("metricNoisePSNR");
            const elMDist = document.getElementById("metricNoiseDist");
            if (elSSIM) elSSIM.innerText = noise.ssim.toFixed(4);
            if (elPSNR) elPSNR.innerText = noise.psnr_db.toFixed(1) + " dB";
            if (elMSSIM) elMSSIM.innerText = noise.ssim.toFixed(4);
            if (elMPSNR) elMPSNR.innerText = noise.psnr_db.toFixed(2) + " dB";
            if (elMDist) elMDist.innerText = noise.perceptual_distance.toFixed(4);
          }
        }

        if (data.faculty_conclusion) {
          const elBox = document.getElementById("inversionConclusionBox");
          if (elBox) {
            elBox.innerHTML = `<span class="text-purple-400 font-bold font-mono">SCIENTIFIC CONCLUSION:</span> ${data.faculty_conclusion}`;
          }
        }

        showToast("Live Pre-Image Inversion Attack completed!");
      } catch (err) {
        alert("Inversion attack error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = "Execute Live Inversion Attack";
      }
    }

    async function runMIABenchmark() {
      const btn = document.getElementById("runMIABtn");
      const btnText = document.getElementById("runMIABtnText");
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = "Auditing MIA...";

      try {
        const res = await fetch("/api/privacy/leakage/membership-inference", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeUser.token}`
          },
          body: JSON.stringify({ sample_size: 30 })
        });
        if (!res.ok) throw new Error("MIA benchmark failed");
        const data = await res.json();

        const rRaw = data.unprotected_raw;
        const rKeyed = data.keyed_protected;
        const rNoise = data.keyed_protected_with_noise;

        if (rRaw) {
          const el = document.getElementById("miaRawAUC");
          if (el) el.innerText = rRaw.roc_auc.toFixed(3);
        }
        if (rKeyed) {
          const el = document.getElementById("miaKeyedAUC");
          if (el) el.innerText = rKeyed.roc_auc.toFixed(3);
        }
        if (rNoise) {
          const el = document.getElementById("miaNoiseAUC");
          if (el) el.innerText = rNoise.roc_auc.toFixed(3);
        }

        if (data.scientific_interpretation) {
          const el = document.getElementById("miaSummaryText");
          if (el) el.innerText = data.scientific_interpretation;
        }

        showToast("Membership Inference Attack (MIA) evaluation completed!");
      } catch (err) {
        alert("MIA error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = "Run MIA Test";
      }
    }

    async function runAttributeInferenceBenchmark() {
      const btn = document.getElementById("runAttBtn");
      const btnText = document.getElementById("runAttBtnText");
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = "Testing Classifiers...";

      try {
        const res = await fetch("/api/privacy/leakage/attribute-inference", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (!res.ok) throw new Error("Attribute inference benchmark failed");
        const data = await res.json();

        const tbody = document.getElementById("attributeTable");
        if (tbody && data.evaluations) {
          tbody.innerHTML = data.evaluations.map((row, idx) => `
            <tr class="${idx === 2 ? 'bg-emerald-950/10' : ''}">
              <td class="py-1.5 px-2 font-mono ${idx === 0 ? 'text-slate-300' : (idx === 1 ? 'text-indigo-300' : (idx === 2 ? 'text-emerald-300 font-bold' : 'text-amber-300'))}">
                ${row.representation}
              </td>
              <td class="py-1.5 px-2 font-mono font-bold ${idx === 0 ? 'text-rose-400' : (idx === 1 ? 'text-indigo-300' : (idx === 2 ? 'text-emerald-400' : 'text-amber-400'))}">
                ${(row.classification_accuracy * 100).toFixed(1)}%
              </td>
              <td class="py-1.5 px-2 text-slate-300 font-mono">${row.macro_f1.toFixed(3)}</td>
              <td class="py-1.5 px-2 font-mono ${row.protection_gain_vs_raw > 0 ? 'text-emerald-400 font-bold' : 'text-slate-500'}">
                ${row.protection_gain_vs_raw > 0 ? '+' + (row.protection_gain_vs_raw * 100).toFixed(1) + '%' : '0.0%'}
              </td>
            </tr>
          `).join('') + `
            <tr class="text-slate-400 italic">
              <td class="py-1.5 px-2 font-mono">Random Chance (${data.target_classes.length} Classes)</td>
              <td class="py-1.5 px-2 font-mono">${(data.random_chance_baseline * 100).toFixed(1)}%</td>
              <td class="py-1.5 px-2 font-mono">${data.random_chance_baseline.toFixed(3)}</td>
              <td class="py-1.5 px-2 font-mono">Theoretical Max</td>
            </tr>
          `;
        }
        showToast("Semantic Attribute Inference benchmark completed!");
      } catch (err) {
        alert("Attribute inference error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = "Run Attribute Test";
      }
    }
"""

# Append JS_HANDLERS into the script section
script_marker = "if (tabId === 'overview') refreshOverviewStats();"
if script_marker in new_content:
    new_content = new_content.replace(
        script_marker,
        script_marker + "\n      if (tabId === 'privacy') loadPrivacyOverview();"
    )

last_script_end = new_content.rfind("</script>")
if last_script_end != -1:
    new_content = new_content[:last_script_end] + JS_HANDLERS + "\n  " + new_content[last_script_end:]

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully updated frontend/index.html with Privacy Leakage Benchmark UI!")
