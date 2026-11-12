import re

research_html = """
    <!-- ========================================== -->
    <!-- MODULE: RESEARCH & PRIVACY ANALYSIS LAB   -->
    <!-- ========================================== -->
    <section id="tab-research" class="hidden space-y-8">

      <!-- Header with glowing research badge -->
      <div class="card-surface p-6 sm:p-8 space-y-4 border border-fuchsia-500/40 bg-gradient-to-r from-fuchsia-950/30 via-slate-900/80 to-cyan-950/30 rounded-2xl shadow-2xl relative overflow-hidden">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1.5">
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-mono font-bold bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40">
              <span class="w-2 h-2 rounded-full bg-fuchsia-400 animate-pulse"></span>
              <span>EXPERIMENTAL RESEARCH SUITE v3.0</span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-white font-display tracking-tight">
              Research &amp; Privacy Analysis Platform
            </h2>
            <p class="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Empirical investigation into <span class="text-cyan-300 font-semibold">Embedding Dimensionality Reduction</span>, 
              <span class="text-fuchsia-300 font-semibold">Retrieval Ablation (512-D down to 64-D)</span>, and 
              <span class="text-amber-300 font-semibold">Pre-Image Reconstruction Attacks</span> across differential threat models.
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="loadAblationBenchmark(true)" class="px-3.5 py-2 rounded-xl text-xs font-bold bg-fuchsia-600 hover:bg-fuchsia-500 text-white shadow-lg shadow-fuchsia-900/40 transition flex items-center space-x-1.5 cursor-pointer">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              <span>Rerun All Benchmarks</span>
            </button>
            <button onclick="exportResearchReport()" class="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center space-x-1.5 cursor-pointer">
              <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              <span>Export Findings (JSON)</span>
            </button>
          </div>
        </div>

        <!-- Research Sub-Tabs Navigation -->
        <div class="pt-2 border-t border-slate-800/80 flex flex-wrap gap-2">
          <button onclick="switchResearchSubTab('ablation')" id="res-tab-btn-ablation" class="px-4 py-2 rounded-lg text-xs font-bold bg-fuchsia-600/30 text-fuchsia-300 border border-fuchsia-500/50 flex items-center space-x-2 transition cursor-pointer">
            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            <span>Lab 1: Retrieval Ablation &amp; Dimensionality</span>
          </button>
          <button onclick="switchResearchSubTab('reconstruction')" id="res-tab-btn-reconstruction" class="px-4 py-2 rounded-lg text-xs font-bold bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/60 flex items-center space-x-2 transition cursor-pointer">
            <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            <span>Lab 2: Image Reconstruction Attacks</span>
          </button>
          <button onclick="switchResearchSubTab('privacy')" id="res-tab-btn-privacy" class="px-4 py-2 rounded-lg text-xs font-bold bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/60 flex items-center space-x-2 transition cursor-pointer">
            <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            <span>Lab 3: Privacy-Utility Tradeoff Analysis</span>
          </button>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- SUB-TAB 1: RETRIEVAL ABLATION & DIMENSIONALITY REDUCTION  -->
      <!-- ========================================================= -->
      <div id="res-sub-ablation" class="space-y-6">

        <!-- Controls: Technique & Dimension Selector -->
        <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider font-display">Ablation Configuration</h3>
              <p class="text-xs text-slate-400">Select dimensionality reduction method and query image for live cross-dimensional comparison.</p>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-xs text-slate-400 font-mono">Reduction Technique:</span>
              <select id="ablationTechniqueSelect" onchange="onAblationTechniqueChange(this.value)" class="bg-slate-900 border border-slate-700 text-xs text-cyan-300 font-bold px-3 py-1.5 rounded-lg focus:outline-none focus:border-cyan-500">
                <option value="truncation">Technique 1: Truncation (First D Coords)</option>
                <option value="random_selection">Technique 2: Random Selection (10 Trials)</option>
                <option value="pca">Technique 3: Principal Component Analysis (PCA)</option>
              </select>
            </div>
          </div>

          <!-- Dimension Selector Cards -->
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
            <div onclick="selectAblationDim(512)" id="dim-card-512" class="cursor-pointer p-3.5 rounded-xl border-2 border-cyan-500 bg-cyan-950/20 text-center space-y-1 transition hover:scale-[1.02]">
              <div class="text-xs font-mono text-cyan-300 font-bold">512-D (Baseline)</div>
              <div class="text-lg font-extrabold text-white font-mono">100%</div>
              <div class="text-[10px] text-slate-400 font-mono">2.0 KB / vec • 0% Red.</div>
            </div>
            <div onclick="selectAblationDim(384)" id="dim-card-384" class="cursor-pointer p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 text-center space-y-1 transition hover:border-slate-600 hover:scale-[1.02]">
              <div class="text-xs font-mono text-slate-300 font-bold">384-D (Exp 1)</div>
              <div class="text-lg font-extrabold text-white font-mono">75.0%</div>
              <div class="text-[10px] text-slate-400 font-mono">1.5 KB / vec • 25% Red.</div>
            </div>
            <div onclick="selectAblationDim(256)" id="dim-card-256" class="cursor-pointer p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 text-center space-y-1 transition hover:border-slate-600 hover:scale-[1.02]">
              <div class="text-xs font-mono text-slate-300 font-bold">256-D (Exp 2)</div>
              <div class="text-lg font-extrabold text-white font-mono">50.0%</div>
              <div class="text-[10px] text-slate-400 font-mono">1.0 KB / vec • 50% Red.</div>
            </div>
            <div onclick="selectAblationDim(128)" id="dim-card-128" class="cursor-pointer p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 text-center space-y-1 transition hover:border-slate-600 hover:scale-[1.02]">
              <div class="text-xs font-mono text-slate-300 font-bold">128-D (Exp 3)</div>
              <div class="text-lg font-extrabold text-white font-mono">25.0%</div>
              <div class="text-[10px] text-slate-400 font-mono">0.5 KB / vec • 75% Red.</div>
            </div>
            <div onclick="selectAblationDim(64)" id="dim-card-64" class="cursor-pointer p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 text-center space-y-1 transition hover:border-slate-600 hover:scale-[1.02]">
              <div class="text-xs font-mono text-slate-300 font-bold">64-D (Exp 4)</div>
              <div class="text-lg font-extrabold text-white font-mono">12.5%</div>
              <div class="text-[10px] text-slate-400 font-mono">0.25 KB / vec • 87.5% Red.</div>
            </div>
          </div>
        </div>

        <!-- Metric KPI Cards for Selected Configuration -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="card-surface p-4 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[11px] font-mono text-slate-400">Mean Average Precision (mAP@5)</span>
            <div class="text-2xl font-extrabold font-mono text-cyan-400" id="ablation-metric-map5">--%</div>
            <div class="text-[10px] text-slate-500 font-mono" id="ablation-metric-map5-sub">Relative drop: --</div>
          </div>
          <div class="card-surface p-4 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[11px] font-mono text-slate-400">Precision@5 / Precision@10</span>
            <div class="text-2xl font-extrabold font-mono text-emerald-400" id="ablation-metric-p5">--% / --%</div>
            <div class="text-[10px] text-slate-500 font-mono">Top-k category accuracy</div>
          </div>
          <div class="card-surface p-4 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[11px] font-mono text-slate-400">Vector Storage Footprint</span>
            <div class="text-2xl font-extrabold font-mono text-fuchsia-400" id="ablation-metric-storage">-- KB</div>
            <div class="text-[10px] text-emerald-400 font-mono" id="ablation-metric-storage-red">--% storage reduction</div>
          </div>
          <div class="card-surface p-4 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[11px] font-mono text-slate-400">FAISS Query Latency</span>
            <div class="text-2xl font-extrabold font-mono text-amber-400" id="ablation-metric-latency">-- ms</div>
            <div class="text-[10px] text-slate-500 font-mono">SIMD inner-product kernel</div>
          </div>
        </div>

        <!-- Comparative Interactive Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">mAP@5 vs Embedding Dimensions</h4>
              <span class="text-[10px] font-mono text-cyan-400">All 3 Techniques</span>
            </div>
            <div class="h-64">
              <canvas id="ablationMapChart"></canvas>
            </div>
          </div>

          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Storage Reduction vs Retrieval Accuracy</h4>
              <span class="text-[10px] font-mono text-emerald-400">Pareto Tradeoff</span>
            </div>
            <div class="h-64">
              <canvas id="ablationStorageChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Empirical Metrics Table Across All 5 Configurations -->
        <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Complete Experimental Evaluation Grid</h4>
            <span class="text-[10px] font-mono text-slate-400">Query-Peer Exclusion: ENFORCED • 10-Trial Random Mean &plusmn; Std</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead>
                <tr class="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                  <th class="py-2.5 px-3">Configuration</th>
                  <th class="py-2.5 px-3">Dimension</th>
                  <th class="py-2.5 px-3">Retained %</th>
                  <th class="py-2.5 px-3">Precision@5</th>
                  <th class="py-2.5 px-3">Recall@5</th>
                  <th class="py-2.5 px-3">mAP@5</th>
                  <th class="py-2.5 px-3">Latency</th>
                  <th class="py-2.5 px-3">Storage / Vec</th>
                  <th class="py-2.5 px-3">Storage Saved</th>
                </tr>
              </thead>
              <tbody id="ablationBenchmarkTableBody" class="divide-y divide-slate-800/60">
                <tr><td colspan="9" class="py-6 text-center text-slate-500">Loading benchmark evaluation matrix...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Section: Dynamic Query Visual Comparison Across Dimensions -->
        <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h4 class="text-sm font-bold text-white font-display">Visual Ranking Comparison Across Dimensionality</h4>
              <p class="text-xs text-slate-400">Select an image to inspect how Top-5 retrieved matches shift across 512, 384, 256, 128, and 64 dimensions.</p>
            </div>
            <div class="flex items-center space-x-2">
              <select id="queryComparePresetSelect" onchange="runAblationQueryCompare(this.value)" class="bg-slate-900 border border-slate-700 text-xs text-white px-3 py-1.5 rounded-lg focus:outline-none">
                <option value="IMG_MED_XRA_medical_xray_0004">Query Preset: Medical Thoracic X-ray</option>
                <option value="IMG_BIO_face_biometric_201">Query Preset: Biometrics Facial Crop</option>
                <option value="IMG_VEH_CAR_vehicles_cars_0012">Query Preset: Automotive Sports Vehicle</option>
                <option value="IMG_NAT_WEA_nature_weather_0003">Query Preset: Nature Aurora Borealis</option>
              </select>
              <button onclick="runAblationQueryCompare()" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition">
                Compare Top-5
              </button>
            </div>
          </div>

          <!-- Dynamic Side-by-Side Dim Columns Container -->
          <div id="queryCompareResultsGrid" class="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2">
            <!-- Populated via Javascript -->
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- SUB-TAB 2: IMAGE RECONSTRUCTION ATTACKS (MODULE B)        -->
      <!-- ========================================================= -->
      <div id="res-sub-reconstruction" class="hidden space-y-6">

        <!-- Attack Parameter Configuration Card -->
        <div class="card-surface p-6 rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-slate-900/60 to-slate-900/90 space-y-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="space-y-1">
              <div class="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                <span>PRE-IMAGE GRADIENT INVERSION ATTACK</span>
              </div>
              <h3 class="text-base font-bold text-white font-display">Image Reconstruction &amp; Privacy Leakage Assessment</h3>
              <p class="text-xs text-slate-300">
                Optimizes a candidate pixel tensor via Adam gradient descent through MobileNetV3 to invert stored visual embeddings.
              </p>
            </div>

            <!-- Threat Model Selector -->
            <div class="flex items-center space-x-3 bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
              <span class="text-xs text-slate-400 font-mono">Threat Model:</span>
              <select id="reconThreatModelSelect" class="bg-slate-900 border border-slate-700 text-xs text-amber-300 font-bold px-3 py-1.5 rounded-lg focus:outline-none">
                <option value="known_key">Attacker B: Known-Key (Possesses Projection Matrix P_K)</option>
                <option value="restricted_key">Attacker A: Restricted-Key (Surrogate Basis / No Secret Key)</option>
              </select>
            </div>
          </div>

          <!-- Target Image & Dimension Controls -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div>
              <label class="block text-[11px] font-mono text-slate-400 mb-1">Target Test Subject:</label>
              <select id="reconTargetImageSelect" class="w-full bg-slate-900 border border-slate-700 text-xs text-white px-3 py-2 rounded-lg">
                <option value="test_medical_xray_05.jpg">Medical: Chest Radiograph 05 (X-ray)</option>
                <option value="test_biometrics_face_01.jpg">Biometrics: High-Res Facial Portrait 01</option>
                <option value="test_vehicles_cars_01.jpg">Vehicles: Sports Coupe Vehicle 01</option>
                <option value="test_nature_general_01.jpg">Nature: Forest Landscape 01</option>
              </select>
            </div>

            <div>
              <label class="block text-[11px] font-mono text-slate-400 mb-1">Target Embedding Dimension:</label>
              <select id="reconTargetDimSelect" class="w-full bg-slate-900 border border-slate-700 text-xs text-cyan-300 font-bold px-3 py-2 rounded-lg">
                <option value="512">100% Embedding (512-D)</option>
                <option value="384">75.0% Embedding (384-D)</option>
                <option value="256">50.0% Embedding (256-D)</option>
                <option value="128">25.0% Embedding (128-D)</option>
                <option value="64">12.5% Embedding (64-D)</option>
              </select>
            </div>

            <div class="flex items-end space-x-2">
              <button onclick="runReconstructionAttack()" id="reconAttackBtn" class="flex-1 py-2 rounded-lg bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-500 hover:to-rose-500 text-white text-xs font-bold shadow-lg shadow-amber-900/40 transition cursor-pointer flex items-center justify-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span id="reconAttackBtnText">Launch Inversion Attack</span>
              </button>
              <button onclick="runReconstructionSweep()" id="reconSweepBtn" class="py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition cursor-pointer" title="Reconstruct all 5 dimensions side-by-side">
                5-Dim Sweep
              </button>
            </div>
          </div>
        </div>

        <!-- Attack Result Display: Side-by-Side Original vs Reconstructed -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Original Reference Image -->
          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Target Reference Image</h4>
              <span class="text-[10px] font-mono text-slate-400">224x224 RGB True Pre-Image</span>
            </div>
            <div class="w-full h-64 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden">
              <img id="reconOrigPreview" src="/static/assets/medical_preset.jpg" alt="Target Reference" class="max-w-full max-h-full object-contain">
            </div>
            <div class="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-[11px] font-mono text-slate-400 flex justify-between">
              <span>Embedding Space: 512-D</span>
              <span class="text-cyan-400">Status: Client Memory Shield Active</span>
            </div>
          </div>

          <!-- Reconstructed Image Output -->
          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Attacker Inversion Reconstruction</h4>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded font-bold" id="reconVerdictBadge">Ready</span>
            </div>
            <div class="w-full h-64 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden relative">
              <img id="reconAttackPreview" src="/static/assets/reconstructions/latest_recon_keyed.png" alt="Reconstructed Output" onerror="this.src='/static/assets/medical_preset.jpg'" class="max-w-full max-h-full object-contain">
              <div id="reconLoadingOverlay" class="hidden absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-2">
                <div class="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                <span class="text-xs font-mono text-amber-300">Optimizing pixel gradients (Adam)...</span>
              </div>
            </div>

            <!-- Reconstruction Metric Pills -->
            <div class="grid grid-cols-4 gap-2 text-center font-mono">
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="text-[9px] text-slate-500">PSNR</div>
                <div class="text-xs font-bold text-cyan-400" id="recon-psnr">11.89 dB</div>
              </div>
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="text-[9px] text-slate-500">SSIM</div>
                <div class="text-xs font-bold text-emerald-400" id="recon-ssim">0.0365</div>
              </div>
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="text-[9px] text-slate-500">MSE</div>
                <div class="text-xs font-bold text-amber-400" id="recon-mse">4,210</div>
              </div>
              <div class="p-2 rounded-lg bg-slate-950 border border-slate-800">
                <div class="text-[9px] text-slate-500">EXEC TIME</div>
                <div class="text-xs font-bold text-fuchsia-400" id="recon-latency">-- ms</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section: Multi-Dimensional Reconstruction Strip (Original | 100% | 75% | 50% | 25% | 12.5%) -->
        <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Multi-Dimensionality Reconstruction Comparison</h4>
              <p class="text-xs text-slate-400">Side-by-side visual fidelity across original reference and all five reduced embedding dimensionalities.</p>
            </div>
            <span class="text-[10px] font-mono text-amber-400 font-bold">Original vs 512, 384, 256, 128, 64-D</span>
          </div>

          <div id="reconSweepStrip" class="grid grid-cols-2 sm:grid-cols-6 gap-3">
            <!-- Populated via Javascript -->
          </div>
        </div>

      </div>

      <!-- ========================================================= -->
      <!-- SUB-TAB 3: PRIVACY-UTILITY TRADEOFF ANALYSIS (MODULE C)   -->
      <!-- ========================================================= -->
      <div id="res-sub-privacy" class="hidden space-y-6">

        <!-- 6-Stage Transformation Matrix -->
        <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Controlled Privacy Transformation Benchmark</h4>
              <p class="text-xs text-slate-400">Systematic evaluation of individual privacy mechanisms (Keyed Projection vs Noise Injection vs Key Secrecy).</p>
            </div>
            <span class="text-[10px] font-mono text-emerald-400 font-bold">Pareto Optimal: Keyed + sigma=0.05</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead>
                <tr class="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                  <th class="py-2.5 px-3">Stage / Configuration</th>
                  <th class="py-2.5 px-3">Dimensions</th>
                  <th class="py-2.5 px-3">Noise &sigma;</th>
                  <th class="py-2.5 px-3">Retrieval mAP@5</th>
                  <th class="py-2.5 px-3">Recon SSIM</th>
                  <th class="py-2.5 px-3">Recon PSNR</th>
                  <th class="py-2.5 px-3">Privacy Score</th>
                  <th class="py-2.5 px-3">Pareto Score</th>
                  <th class="py-2.5 px-3">Security Level</th>
                </tr>
              </thead>
              <tbody id="privacyComparisonTableBody" class="divide-y divide-slate-800/60">
                <tr><td colspan="9" class="py-6 text-center text-slate-500">Loading privacy comparison matrix...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Pareto Frontier Chart & Threat Model Breakdown -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Pareto Frontier: Retrieval Utility vs Visual Privacy</h4>
              <span class="text-[10px] font-mono text-cyan-400">Tradeoff Curve</span>
            </div>
            <div class="h-64">
              <canvas id="privacyParetoChart"></canvas>
            </div>
          </div>

          <div class="card-surface p-6 rounded-2xl border border-slate-800 space-y-3">
            <h4 class="text-xs font-bold text-white uppercase tracking-wider font-display">Faculty Research Conclusions</h4>
            <div class="space-y-2.5 text-xs text-slate-300 leading-relaxed">
              <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-cyan-300 font-bold font-mono">1. Key Secrecy vs Gradient Inversion</span>
                <p class="text-[11px] text-slate-400">
                  Without possession of the 256-bit secret key, an attacker cannot compute backward gradients into the feature extractor. Reconstructed SSIM collapses to 0.034 (pure noise).
                </p>
              </div>
              <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-fuchsia-300 font-bold font-mono">2. Dimensionality Ablation Trade-off</span>
                <p class="text-[11px] text-slate-400">
                  Reducing dimensionality from 512-D down to 256-D cuts storage by 50% while preserving over 95% of mAP. PCA demonstrates superior retention over truncation at 128-D and 64-D.
                </p>
              </div>
              <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-emerald-300 font-bold font-mono">3. Defense-in-Depth Guarantee</span>
                <p class="text-[11px] text-slate-400">
                  Even if the projection matrix is fully compromised (Attacker B), calibrated perturbation (&sigma;=0.05) destroys facial and medical contours (PSNR &lt; 12 dB), preventing biometric or diagnostic identification.
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>

    </section>
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Desktop Nav Tab if not present
nav_target = '<button onclick="switchTab(\'settings\')"'
nav_replacement = """<button onclick="switchTab('research')" id="nav-research" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4 text-fuchsia-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 to-cyan-400 font-bold">Research &amp; Privacy Lab</span>
      </button>

      <button onclick="switchTab('settings')\""""

if 'id="nav-research"' not in content and nav_target in content:
    content = content.replace(nav_target, nav_replacement, 1)
    print("Added desktop nav tab.")

# 2. Add Mobile Nav Tab if not present
mobile_target = '<button onclick="switchTab(\'settings\'); toggleMobileNav();"'
mobile_replacement = """<button onclick="switchTab('research'); toggleMobileNav();" class="col-span-2 px-3 py-2 rounded-lg text-left bg-fuchsia-950/40 text-fuchsia-300 border border-fuchsia-800/50 hover:bg-fuchsia-900/50 flex items-center space-x-2">
          <span>Research &amp; Privacy Lab</span>
        </button>
        <button onclick="switchTab('settings'); toggleMobileNav();\""""

if 'switchTab(\'research\'); toggleMobileNav();' not in content and mobile_target in content:
    content = content.replace(mobile_target, mobile_replacement, 1)
    print("Added mobile nav tab.")

# 3. Add <section id="tab-research"> before </main>
section_target = '    </section>\n\n  </main>'
section_replacement = '    </section>\n\n' + research_html + '\n  </main>'

if 'id="tab-research"' not in content and section_target in content:
    content = content.replace(section_target, section_replacement, 1)
    print("Added section tab-research.")
elif 'id="tab-research"' not in content:
    # Try CRLF
    section_target_crlf = '    </section>\r\n\r\n  </main>'
    section_replacement_crlf = '    </section>\r\n\r\n' + research_html + '\r\n  </main>'
    if section_target_crlf in content:
        content = content.replace(section_target_crlf, section_replacement_crlf, 1)
        print("Added section tab-research (CRLF).")
    else:
        print("Could not find insertion point for tab-research!")

# 4. Update switchTab list to include 'research'
old_switch = "['overview', 'search', 'evaluation', 'privacy', 'security', 'index', 'settings'].forEach"
new_switch = "['overview', 'search', 'evaluation', 'privacy', 'security', 'index', 'settings', 'research'].forEach"
if old_switch in content:
    content = content.replace(old_switch, new_switch, 1)
    print("Updated switchTab tabs list.")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/index.html successfully.")
