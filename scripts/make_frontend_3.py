HTML_PART_3 = """
    <!-- TAB 2: PRIVACY ARCHITECTURE & COMPARISON -->
    <section id="tab-privacy" class="hidden space-y-6">
      <div class="text-center max-w-3xl mx-auto mb-6">
        <span class="text-xs font-mono font-semibold text-cyan-400 tracking-wider uppercase">Architectural Comparison</span>
        <h2 class="text-2xl sm:text-3xl font-bold text-white mt-1">Conventional vs Proposed Private Retrieval</h2>
        <p class="text-xs text-slate-400 mt-2">
          Comparing vulnerable centralized image processing against our decoupled, protected representation pipeline.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Conventional Model -->
        <div class="glass-card rounded-2xl p-6 border-l-4 border-l-red-500">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-base font-bold text-red-400">1. Conventional Image Retrieval (High Risk)</h3>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">Vulnerable</span>
          </div>
          <p class="text-xs text-slate-300 mb-4 leading-relaxed">
            In traditional CBIR, client images are transmitted and stored unencrypted on central cloud databases. If the database is compromised, all sensitive visual records are exposed.
          </p>
          <div class="space-y-2 text-xs font-mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-300">
            <div class="p-2 rounded bg-red-950/30 border border-red-900 text-red-200">Original Images Uploaded</div>
            <div class="text-center text-red-400">↓</div>
            <div class="p-2 rounded bg-red-950/30 border border-red-900 text-red-200">Centralized Cloud Storage (Holds 100% of Raw Pixels)</div>
            <div class="text-center text-red-400">↓</div>
            <div class="p-2 rounded bg-red-950/30 border border-red-900 text-red-200">Unencrypted Search Server</div>
          </div>
          <div class="mt-4 text-[11px] text-red-300/80">
            ⚠ Single Point of Breach: Database leaks reveal full-resolution personal or medical pictures.
          </div>
        </div>

        <!-- Proposed Decoupled Model -->
        <div class="glass-card rounded-2xl p-6 border-l-4 border-l-emerald-500">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-base font-bold text-emerald-400">2. Proposed Private Retrieval (Protected)</h3>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">Zero-Pixel Index</span>
          </div>
          <p class="text-xs text-slate-300 mb-4 leading-relaxed">
            Physical images remain isolated in an encrypted private vault. The vector database stores only protected mathematical representations mapped to anonymized Image IDs.
          </p>
          <div class="space-y-2 text-xs font-mono bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-300">
            <div class="p-2 rounded bg-emerald-950/30 border border-emerald-900 text-emerald-200">Original Images ➔ AES-256 Private Storage</div>
            <div class="text-center text-cyan-400">↓ (Decoupled)</div>
            <div class="p-2 rounded bg-blue-950/40 border border-blue-900 text-cyan-200">Protected Representations (Orthogonal Projection + Noise)</div>
            <div class="text-center text-cyan-400">↓</div>
            <div class="p-2 rounded bg-emerald-950/30 border border-emerald-900 text-emerald-200">FAISS Search Engine (Returns Image IDs Only)</div>
            <div class="text-center text-cyan-400">↓</div>
            <div class="p-2 rounded bg-purple-950/40 border border-purple-900 text-purple-200">Authorization Gate (Decrypts for verified owners only)</div>
          </div>
          <div class="mt-4 text-[11px] text-emerald-300 font-bold">
            ✔ Core Highlight: “The vector database does not contain the original images.”
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: EVALUATION & BENCHMARKS -->
    <section id="tab-eval" class="hidden space-y-6">
      <div class="text-center max-w-3xl mx-auto mb-6">
        <span class="text-xs font-mono font-semibold text-amber-400 tracking-wider uppercase">Empirical Evaluation</span>
        <h2 class="text-2xl sm:text-3xl font-bold text-white mt-1">Automated Benchmark & Privacy Metrics</h2>
        <p class="text-xs text-slate-400 mt-2">
          Real metrics measured dynamically across indexed images on this system (no synthetic numbers).
        </p>
      </div>

      <div class="flex justify-end">
        <button onclick="fetchEvaluationBenchmark()" class="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 font-mono text-xs transition flex items-center space-x-1.5 cursor-pointer">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Re-run Evaluation Benchmark</span>
        </button>
      </div>

      <div id="evalLoading" class="hidden text-center py-8 font-mono text-xs text-slate-400">
        Computing benchmark over FAISS index...
      </div>

      <div id="evalContent" class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Dynamically filled via JS -->
      </div>
    </section>

    <!-- TAB 4: SYSTEM ADMIN & AUDIT TRAIL -->
    <section id="tab-admin" class="hidden space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-lg font-bold text-white">System Diagnostics & Security Audit</h2>
          <p class="text-xs text-slate-400">Live telemetry directly queried from SQLite database and FAISS index</p>
        </div>
        <button onclick="fetchAdminStats()" class="px-3 py-1 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:text-white cursor-pointer">Refresh</button>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4" id="adminStatsGrid">
        <!-- Dynamically populated -->
      </div>

      <!-- Live Audit Trail Table -->
      <div class="glass-card rounded-2xl p-5">
        <h3 class="text-xs font-bold text-white uppercase font-mono tracking-wider mb-3">Cryptographic Access Audit Trail</h3>
        <div class="overflow-x-auto border border-slate-800 rounded-lg">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-900/90 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="p-2.5 text-blue-400">Timestamp</th>
                <th class="p-2.5">User</th>
                <th class="p-2.5">Action</th>
                <th class="p-2.5">Status</th>
                <th class="p-2.5">Audit Detail</th>
              </tr>
            </thead>
            <tbody id="auditTableBody" class="divide-y divide-slate-800/60 bg-slate-950/40 text-slate-300">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </main>
"""
with open("frontend/index.html", "a", encoding="utf-8") as f:
    f.write(HTML_PART_3)
print("Part 3 written")
