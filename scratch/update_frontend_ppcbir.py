import os

with open("frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add CKKS & Attack Evaluation Sections into tab-privacy
privacy_extra = """
      <!-- 4B. TEN-SEAL CKKS HOMOMORPHIC ENCRYPTION CONSOLE -->
      <div class="card-surface p-6 space-y-4 border-t-2 border-t-cyan-500">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="badge-cyan text-[10px] px-2 py-0.5 rounded w-max font-mono font-bold mb-1">RLWE HOMOMORPHIC ENCRYPTION</div>
            <h4 class="text-sm font-bold text-white font-display">TenSEAL CKKS Encrypted Similarity Engine</h4>
            <p class="text-xs text-slate-400">Evaluates inner products directly on ciphertext polynomials. Server receives ZERO plaintext bits.</p>
          </div>
          <button onclick="runCKKSBenchmarkUI()" id="runCKKSBtn" class="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold font-display shadow-lg shadow-cyan-900/40 transition flex items-center space-x-2 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            <span id="runCKKSBtnText">Execute CKKS Benchmark</span>
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
            <div class="text-[10px] text-slate-400 uppercase font-mono">Poly Modulus Degree</div>
            <div class="text-base font-bold text-cyan-400 font-mono mt-1" id="ckksDegree">N = 8,192</div>
            <div class="text-[10px] text-slate-500 mt-0.5">128-bit RLWE Security</div>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
            <div class="text-[10px] text-slate-400 uppercase font-mono">Client Encrypt Time</div>
            <div class="text-base font-bold text-emerald-400 font-mono mt-1" id="ckksEncTime">~24 ms</div>
            <div class="text-[10px] text-slate-500 mt-0.5" id="ckksCipherSize">323 KB Ciphertext</div>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
            <div class="text-[10px] text-slate-400 uppercase font-mono">Server Inner Product</div>
            <div class="text-base font-bold text-purple-400 font-mono mt-1" id="ckksServerTime">~47 ms/item</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Encrypted Dot Product</div>
          </div>
          <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
            <div class="text-[10px] text-slate-400 uppercase font-mono">Precision Error</div>
            <div class="text-base font-bold text-amber-400 font-mono mt-1" id="ckksError">&lt; 3 &times; 10&#8315;&#8310;</div>
            <div class="text-[10px] text-slate-500 mt-0.5">Scale = 2&#8308;&#8304;</div>
          </div>
        </div>
      </div>

      <!-- 4C. EMPIRICAL SECURITY ATTACK BENCHMARK CONSOLE -->
      <div class="card-surface p-6 space-y-4 border-t-2 border-t-rose-500">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="badge-rose text-[10px] px-2 py-0.5 rounded w-max font-mono font-bold mb-1">EMPIRICAL ATTACK BENCHMARK</div>
            <h4 class="text-sm font-bold text-white font-display">Adversarial Reconstruction & Re-Identification Evaluation</h4>
            <p class="text-xs text-slate-400">Evaluates linear pre-image feature inversion and known-gallery re-identification attack success rates.</p>
          </div>
          <button onclick="runSecurityAttacksUI()" id="runAttackBtn" class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold font-display shadow-lg shadow-rose-900/40 transition flex items-center space-x-2 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <span id="runAttackBtnText">Run Empirical Attacks</span>
          </button>
        </div>

        <div class="overflow-x-auto pt-2">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Representation Scheme</th>
                <th class="py-2.5 px-3">Inversion MSE</th>
                <th class="py-2.5 px-3">Cosine Drift</th>
                <th class="py-2.5 px-3">Top-1 Re-ID</th>
                <th class="py-2.5 px-3">Top-5 Re-ID</th>
                <th class="py-2.5 px-3">Security Verdict</th>
              </tr>
            </thead>
            <tbody id="attackEvaluationTable" class="divide-y divide-slate-800/60 font-sans">
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-semibold text-rose-400">Plaintext Raw Embeddings</td>
                <td class="py-2.5 px-3 font-mono">0.0000</td>
                <td class="py-2.5 px-3 font-mono">0.0000</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold font-mono">100.0%</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold font-mono">100.0%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-rose font-semibold">Vulnerable (Deterministic)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-semibold text-slate-300">Baseline Orthogonal (512-D)</td>
                <td class="py-2.5 px-3 font-mono text-amber-400">0.0025</td>
                <td class="py-2.5 px-3 font-mono">0.0487</td>
                <td class="py-2.5 px-3 text-amber-400 font-bold font-mono">86.7%</td>
                <td class="py-2.5 px-3 text-amber-400 font-bold font-mono">93.3%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-amber font-semibold">Partially Resistant</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-semibold text-purple-400">LDP Gaussian (&epsilon;=2.0)</td>
                <td class="py-2.5 px-3 font-mono text-emerald-400">0.0098</td>
                <td class="py-2.5 px-3 font-mono">0.0964</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">20.0%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">40.0%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-emerald font-semibold">Strong LDP Defense</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-semibold text-blue-400">Non-Invertible RFF</td>
                <td class="py-2.5 px-3 font-mono text-emerald-400">0.0382</td>
                <td class="py-2.5 px-3 font-mono">0.2410</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">13.3%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">33.3%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-blue font-semibold">High Non-Linear Barrier</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40 bg-cyan-950/20">
                <td class="py-2.5 px-3 font-semibold text-cyan-300">CKKS Homomorphic Ciphertext</td>
                <td class="py-2.5 px-3 font-mono text-cyan-400">&infin; (1.000)</td>
                <td class="py-2.5 px-3 font-mono">1.0000</td>
                <td class="py-2.5 px-3 text-cyan-300 font-bold font-mono">0.0%</td>
                <td class="py-2.5 px-3 text-cyan-300 font-bold font-mono">0.0%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-cyan font-semibold">Cryptographically Secure (IND-CPA)</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
"""

target_sec_anchor = "    <!-- ==========================================\n    <!-- 5. SECURITY CENTER & AUDIT TRAIL TAB       -->"
if target_sec_anchor not in html:
    target_sec_anchor = "    <!-- 5. SECURITY CENTER & AUDIT TRAIL TAB       -->"

if target_sec_anchor in html and "runCKKSBenchmarkUI" not in html:
    html = html.replace(target_sec_anchor, privacy_extra + "\n\n" + target_sec_anchor)
    print("Added CKKS and Attack Evaluation sections.")

# 2. Add Privacy Representation Scheme selector to tab-search
scheme_selector_html = """
              <!-- Privacy Representation Scheme Selector -->
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-semibold">Privacy Scheme:</span>
                <select id="privacySchemeSelect" class="bg-[#192338] text-xs text-purple-300 border border-purple-700/60 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer font-semibold shadow-sm">
                  <option value="baseline_orthogonal">Baseline: Orthogonal Projection (512-D)</option>
                  <option value="ldp_gaussian">LDP: Gaussian Mechanism (&epsilon;=2.0, &delta;=10&#8315;&#8309;)</option>
                  <option value="ldp_laplace">LDP: Laplace Mechanism (&epsilon;=2.0)</option>
                  <option value="non_invertible_rff">Non-Invertible: Random Fourier Features (RFF)</option>
                  <option value="non_invertible_sign">Non-Invertible: 1-Bit Sign Projection (SimHash)</option>
                </select>
              </div>
"""

min_anchor = "              <!-- Minimization Toggle -->"
if min_anchor in html and "privacySchemeSelect" not in html:
    html = html.replace(min_anchor, scheme_selector_html + "\n" + min_anchor)
    print("Added Privacy Scheme selector to Search controls.")

# 3. Add JavaScript Handler Functions
js_handlers = """
    async function runCKKSBenchmarkUI() {
      const btn = document.getElementById('runCKKSBtn');
      const btnText = document.getElementById('runCKKSBtnText');
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = "Evaluating Homomorphic Math...";
      try {
        const res = await fetch("/api/privacy/ckks-benchmark?candidates=8");
        if (!res.ok) throw new Error("CKKS benchmark failed.");
        const data = await res.json();
        const dEl = document.getElementById('ckksDegree');
        const eEl = document.getElementById('ckksEncTime');
        const cEl = document.getElementById('ckksCipherSize');
        const sEl = document.getElementById('ckksServerTime');
        const errEl = document.getElementById('ckksError');
        
        if (dEl) dEl.innerText = `N = ${data.poly_modulus_degree.toLocaleString()}`;
        if (eEl) eEl.innerText = `${data.client_encryption_time_ms} ms`;
        if (cEl) cEl.innerText = `${data.ciphertext_size_kb} KB Ciphertext`;
        if (sEl) sEl.innerText = `${data.server_per_vector_latency_ms} ms/item`;
        if (errEl) errEl.innerText = `< ${data.max_numerical_precision_error.toExponential(2)}`;
        showToast("TenSEAL CKKS Homomorphic benchmark executed!");
      } catch (err) {
        alert("CKKS error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = "Execute CKKS Benchmark";
      }
    }

    async function runSecurityAttacksUI() {
      const btn = document.getElementById('runAttackBtn');
      const btnText = document.getElementById('runAttackBtnText');
      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = "Executing Adversarial Inversion...";
      try {
        const res = await fetch("/api/privacy/security-attacks");
        if (!res.ok) throw new Error("Security attacks evaluation failed.");
        const data = await res.json();
        const inv = data.inversion_attack_benchmark.schemes_evaluated;
        const gallery = data.known_gallery_identification.results;
        const tbody = document.getElementById('attackEvaluationTable');

        if (tbody) {
          const rows = [
            {
              name: "Plaintext Raw Embeddings",
              inv: inv.raw_embedding,
              gal: gallery.raw_embeddings,
              cls: "text-rose-400",
              badge: "badge-rose",
              verdict: "Vulnerable (Deterministic)"
            },
            {
              name: "Baseline Orthogonal (512-D)",
              inv: inv.baseline_orthogonal,
              gal: gallery.baseline_orthogonal,
              cls: "text-slate-300",
              badge: "badge-amber",
              verdict: "Partially Resistant"
            },
            {
              name: "LDP Gaussian (ε=2.0)",
              inv: inv.ldp_gaussian,
              gal: gallery.ldp_gaussian_eps_1_5,
              cls: "text-purple-400",
              badge: "badge-emerald",
              verdict: "Strong LDP Defense"
            },
            {
              name: "Non-Invertible RFF",
              inv: inv.non_invertible_rff,
              gal: gallery.non_invertible_rff,
              cls: "text-blue-400",
              badge: "badge-blue",
              verdict: "High Non-Linear Barrier"
            },
            {
              name: "CKKS Homomorphic Ciphertext",
              inv: inv.ckks_homomorphic,
              gal: gallery.ckks_homomorphic,
              cls: "text-cyan-300",
              badge: "badge-cyan",
              verdict: "Cryptographically Secure (IND-CPA)"
            }
          ];

          tbody.innerHTML = rows.map(r => `
            <tr class="hover:bg-slate-900/40">
              <td class="py-2.5 px-3 font-semibold ${r.cls}">${r.name}</td>
              <td class="py-2.5 px-3 font-mono">${r.inv.mean_squared_error.toFixed(4)}</td>
              <td class="py-2.5 px-3 font-mono">${r.inv.cosine_recovery_drift.toFixed(4)}</td>
              <td class="py-2.5 px-3 font-mono font-bold">${r.gal.top_1_identification_accuracy.toFixed(1)}%</td>
              <td class="py-2.5 px-3 font-mono font-bold">${r.gal.top_5_identification_accuracy.toFixed(1)}%</td>
              <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] ${r.badge} font-semibold">${r.verdict}</span></td>
            </tr>
          `).join('');
        }

        showToast("Adversarial attack evaluations completed!");
      } catch (err) {
        alert("Attack benchmark error: " + err.message);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = "Run Empirical Attacks";
      }
    }
"""

export_anchor = "    function exportPrivacy(fmt) {\n      window.open(`/api/privacy/export?format=${fmt}`, '_blank');\n    }"
if export_anchor not in html:
    export_anchor = "function exportPrivacy(fmt)"

if export_anchor in html and "runCKKSBenchmarkUI" not in html:
    html = html.replace(export_anchor, js_handlers + "\n\n" + export_anchor)
    print("Added JavaScript handlers for CKKS and Attack benchmarks.")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: frontend/index.html updated with PP-CBIR enhancements!")
