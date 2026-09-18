HTML_PART_4 = """
  <!-- FOOTER -->
  <footer class="bg-[#050811] border-t border-slate-800/80 py-8 text-xs text-slate-500 mt-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        <span class="font-bold text-slate-300 font-mono">Private Image Search // Decoupled Retrieval Engine</span>
        <p class="text-[11px] text-slate-500 mt-0.5">AIML Engineering Project • Protected Visual Representations & Decoupled AES Vault</p>
      </div>
      <div class="text-center sm:text-right font-mono text-[11px]">
        <span class="text-cyan-400 italic">“Retrieve what you need, without unnecessarily exposing what you store.”</span>
      </div>
    </div>
  </footer>

  <!-- JAVASCRIPT APPLICATION LOGIC -->
  <script>
    let activeUser = {
      user_id: "USR_DOC_01",
      name: "Dr. R. Sharma",
      role: "specialist"
    };
    let currentSelectedFile = null;

    function switchTab(tabId) {
      ['search', 'privacy', 'eval', 'admin'].forEach(t => {
        document.getElementById(`tab-${t}`).classList.add('hidden');
        document.getElementById(`tabBtn-${t}`).className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition cursor-pointer";
      });
      document.getElementById(`tab-${tabId}`).classList.remove('hidden');
      document.getElementById(`tabBtn-${tabId}`).className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-semibold transition cursor-pointer";

      if (tabId === 'eval') fetchEvaluationBenchmark();
      if (tabId === 'admin') fetchAdminStats();
    }

    function onUserChange() {
      const sel = document.getElementById('userSelector');
      const val = sel.value;
      const text = sel.options[sel.selectedIndex].text;
      
      let role = "guest";
      if (val === "USR_DOC_01") role = "specialist";
      else if (val === "USR_RES_02") role = "researcher";
      else if (val === "USR_ADM_00") role = "admin";

      activeUser = { user_id: val, name: text.split(' (')[0], role: role };
      console.log("Active User Switched:", activeUser);

      if (currentSelectedFile) {
        runSearch();
      }
    }

    function handleDragOver(e) {
      e.preventDefault();
      document.getElementById('dropzone').classList.add('border-cyan-400', 'bg-blue-950/30');
    }
    function handleDragLeave(e) {
      e.preventDefault();
      document.getElementById('dropzone').classList.remove('border-cyan-400', 'bg-blue-950/30');
    }
    function handleDrop(e) {
      e.preventDefault();
      document.getElementById('dropzone').classList.remove('border-cyan-400', 'bg-blue-950/30');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processFile(e.dataTransfer.files[0]);
      }
    }
    function handleFileSelect(e) {
      if (e.target.files && e.target.files[0]) {
        processFile(e.target.files[0]);
      }
    }

    function processFile(file) {
      if (!file.type.startsWith('image/')) {
        alert("Please upload a valid image file (JPG, PNG, WebP).");
        return;
      }
      currentSelectedFile = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('previewName').innerText = file.name;
        document.getElementById('dropzonePrompt').classList.add('hidden');
        document.getElementById('dropzonePreview').classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    }

    function clearImage(e) {
      if (e) e.stopPropagation();
      currentSelectedFile = null;
      document.getElementById('fileInput').value = "";
      document.getElementById('dropzonePreview').classList.add('hidden');
      document.getElementById('dropzonePrompt').classList.remove('hidden');
      document.getElementById('resultsContainer').innerHTML = `
        <div class="text-center py-12 text-slate-500 text-xs font-mono">
          Upload an image above and click "Execute Private Image Search" to view results.
        </div>
      `;
      document.getElementById('summaryCard').classList.add('hidden');
      resetPipeline();
    }

    async function loadSamplePreset(cat) {
      // Direct sample base64 or fetch from backend API
      const presetUrls = {
        medical: "/api/storage/image/IMG_MED_ct_pulmonary_101",
        biometrics: "/api/storage/image/IMG_BIO_face_biometric_201",
        vehicles: "/api/storage/image/IMG_VEH_car_sedan_301",
        nature: "/api/storage/image/IMG_NAT_nature_mountain_401"
      };
      const url = presetUrls[cat];
      try {
        const res = await fetch(url, {
          headers: { "Authorization": `Bearer ${activeUser.user_id}` }
        });
        if (!res.ok) {
          // If current user is restricted, fetch with admin header for preset loading
          const fallbackRes = await fetch(url, { headers: { "Authorization": "Bearer USR_ADM_00" } });
          const blob = await fallbackRes.blob();
          const file = new File([blob], `${cat}_sample.jpg`, { type: "image/jpeg" });
          processFile(file);
        } else {
          const blob = await res.blob();
          const file = new File([blob], `${cat}_sample.jpg`, { type: "image/jpeg" });
          processFile(file);
        }
        setTimeout(() => runSearch(), 200);
      } catch (err) {
        console.error("Error loading sample preset:", err);
      }
    }

    function resetPipeline() {
      ['upload', 'prep', 'infer', 'protect', 'faiss', 'auth'].forEach(st => {
        const el = document.getElementById(`pipe-${st}`);
        el.className = "p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400";
        el.querySelector('.step-status').innerText = "Waiting";
      });
      document.getElementById('pipelineStatusBadge').innerText = "IDLE";
      document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800";
    }

    async function runSearch() {
      if (!currentSelectedFile) {
        alert("Please upload an image or select a preset query first.");
        return;
      }

      const searchBtn = document.getElementById('searchBtn');
      searchBtn.disabled = true;
      searchBtn.innerHTML = `<span>Processing Pipeline...</span>`;

      resetPipeline();
      document.getElementById('pipelineStatusBadge').innerText = "PROCESSING";
      document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700 animate-pulse";

      const markStep = (id, timeText) => {
        const el = document.getElementById(`pipe-${id}`);
        el.className = "p-2 rounded-lg bg-emerald-950/40 border border-emerald-600 text-emerald-300";
        el.querySelector('.step-status').innerText = timeText;
      };

      markStep('upload', 'In progress');

      const formData = new FormData();
      formData.append("file", currentSelectedFile);
      formData.append("top_k", document.getElementById('topKSelect').value);
      formData.append("protected", document.getElementById('privacyToggle').checked ? "true" : "false");
      formData.append("sigma", "0.05");

      try {
        const res = await fetch("/api/search/query", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${activeUser.user_id}`
          },
          body: formData
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Search request failed");
        }

        const data = await res.json();
        console.log("Search API Result:", data);

        data.pipeline_steps.forEach(s => {
          const stepKey = {
            "Upload": "upload",
            "Preprocessing": "prep",
            "Feature Extraction": "infer",
            "Privacy Protection": "protect",
            "Vector Search": "faiss",
            "Authorization": "auth"
          }[s.step];
          if (stepKey) {
            markStep(stepKey, `${s.time_ms.toFixed(1)}ms`);
          }
        });

        document.getElementById('pipelineStatusBadge').innerText = "COMPLETED";
        document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700";

        document.getElementById('summaryCard').classList.remove('hidden');
        document.getElementById('resultsCountText').innerText = `${data.results.length} similar images found`;
        document.getElementById('searchLatencyText').innerText = `Search time: ${data.query_summary.search_time_sec}`;

        renderResultsCards(data.results);

      } catch (err) {
        alert("Search error: " + err.message);
        document.getElementById('pipelineStatusBadge').innerText = "FAILED";
        document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-700";
      } finally {
        searchBtn.disabled = false;
        searchBtn.innerHTML = `
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <span>Execute Private Image Search</span>
        `;
      }
    }

    function renderResultsCards(results) {
      const container = document.getElementById('resultsContainer');
      container.innerHTML = "";

      if (results.length === 0) {
        container.innerHTML = `<div class="p-4 rounded-xl bg-slate-900 text-center text-slate-400 text-xs">No similar vectors found in FAISS index.</div>`;
        return;
      }

      results.forEach(item => {
        const card = document.createElement('div');
        card.className = "p-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4 transition";

        card.innerHTML = `
          <div class="flex items-center space-x-3.5 w-full sm:w-auto">
            <div class="w-16 h-16 rounded-lg bg-slate-950 border ${item.authorized ? 'border-emerald-500/60' : 'border-red-900/60'} flex items-center justify-center shrink-0 overflow-hidden relative">
              ${item.authorized 
                ? `<img src="${item.image_url}" class="w-full h-full object-cover">`
                : `<div class="text-center p-1">
                     <svg class="w-5 h-5 mx-auto text-red-400 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                     <span class="text-[8px] font-mono text-red-300 block">LOCKED</span>
                   </div>`
              }
            </div>

            <div>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-mono font-bold px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">#${item.rank}</span>
                <span class="font-mono text-xs font-bold text-white">${item.image_id}</span>
                <span class="text-xs font-bold text-cyan-400 font-mono">Similarity: ${item.similarity_percent}</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Category: <span class="text-slate-200 capitalize">${item.category}</span> • Owner: <span class="font-mono text-slate-400">${item.owner_id}</span></p>
              <div class="mt-1">
                ${item.authorized
                  ? `<span class="inline-flex items-center text-[10px] font-mono text-emerald-400"><svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Authorized — Decrypted from Private Vault</span>`
                  : `<span class="inline-flex items-center text-[10px] font-mono text-red-400"><svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg> ${item.auth_message}</span>`
                }
              </div>
            </div>
          </div>

          <div class="shrink-0 text-right w-full sm:w-auto">
            ${item.authorized
              ? `<a href="${item.image_url}" target="_blank" class="px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-600 text-emerald-300 text-xs font-mono inline-block transition">Inspect Full Asset</a>`
              : `<span class="px-3 py-1.5 rounded-lg bg-red-950/40 border border-red-800 text-red-300 text-[11px] font-mono block sm:inline-block">Permission Denied</span>`
            }
          </div>
        `;

        container.appendChild(card);
      });
    }

    async function fetchEvaluationBenchmark() {
      const loading = document.getElementById('evalLoading');
      const content = document.getElementById('evalContent');
      loading.classList.remove('hidden');
      content.innerHTML = "";

      try {
        const res = await fetch("/api/evaluation/benchmark");
        const data = await res.json();
        loading.classList.add('hidden');

        if (data.status !== 'completed') {
          content.innerHTML = `<div class="lg:col-span-12 p-6 glass-card rounded-xl text-center text-amber-300 font-mono text-xs">${data.message}</div>`;
          return;
        }

        const rm = data.retrieval_metrics;
        const pe = data.privacy_experiment;

        content.innerHTML = `
          <div class="lg:col-span-5 glass-card rounded-2xl p-5 space-y-4">
            <h3 class="text-xs font-bold text-white uppercase font-mono tracking-wider">Retrieval Accuracy Metrics</h3>
            <div class="space-y-3 font-mono text-xs">
              <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span class="text-slate-400">Precision@1 (Top-1 Match):</span>
                <span class="text-emerald-400 font-bold text-sm">${rm.precision_at_1}</span>
              </div>
              <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span class="text-slate-400">Precision@3 (Top-3 Matches):</span>
                <span class="text-emerald-400 font-bold text-sm">${rm.precision_at_3}</span>
              </div>
              <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span class="text-slate-400">Precision@5 (Top-5 Matches):</span>
                <span class="text-emerald-400 font-bold text-sm">${rm.precision_at_5}</span>
              </div>
              <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span class="text-slate-400">Average Query Latency:</span>
                <span class="text-cyan-400 font-bold">${rm.average_search_time_ms}</span>
              </div>
              <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                <span class="text-slate-400">Search Throughput:</span>
                <span class="text-purple-400 font-bold">${rm.search_throughput_qps}</span>
              </div>
            </div>
          </div>

          <div class="lg:col-span-7 glass-card rounded-2xl p-5 space-y-4">
            <h3 class="text-xs font-bold text-white uppercase font-mono tracking-wider">Baseline vs Protected Experiment</h3>
            <div class="overflow-x-auto border border-slate-800 rounded-lg">
              <table class="w-full text-left text-xs font-mono">
                <thead class="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th class="p-2.5 text-blue-400">Parameter</th>
                    <th class="p-2.5">Baseline (Raw CNN)</th>
                    <th class="p-2.5 text-emerald-400">Proposed Protected</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800 text-slate-300">
                  <tr>
                    <td class="p-2.5 text-white font-semibold">Precision@5</td>
                    <td class="p-2.5">${pe.baseline_representation.precision_at_5}</td>
                    <td class="p-2.5 text-emerald-400 font-bold">${pe.protected_representation.precision_at_5}</td>
                  </tr>
                  <tr>
                    <td class="p-2.5 text-white font-semibold">Reconstruction SSIM</td>
                    <td class="p-2.5 text-red-400">${pe.baseline_representation.inversion_ssim} (High Leakage)</td>
                    <td class="p-2.5 text-emerald-400 font-bold">${pe.protected_representation.inversion_ssim} (Suppressed)</td>
                  </tr>
                  <tr>
                    <td class="p-2.5 text-white font-semibold">Inversion Attack Risk</td>
                    <td class="p-2.5 text-red-400">${pe.baseline_representation.reconstruction_risk}</td>
                    <td class="p-2.5 text-emerald-400 font-bold">${pe.protected_representation.reconstruction_risk}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-[11px] text-slate-400 leading-relaxed font-mono bg-blue-950/20 p-3 rounded-lg border border-blue-900/40">
              <strong>Analysis:</strong> ${pe.tradeoff_analysis}
            </p>
          </div>
        `;
      } catch (err) {
        loading.classList.add('hidden');
        content.innerHTML = `<div class="lg:col-span-12 p-4 text-red-400 text-xs font-mono">Error: ${err.message}</div>`;
      }
    }

    async function fetchAdminStats() {
      try {
        const res = await fetch("/api/admin/stats");
        const data = await res.json();

        const grid = document.getElementById('adminStatsGrid');
        grid.innerHTML = `
          <div class="glass-card rounded-xl p-4 text-center">
            <span class="block text-2xl font-bold text-white font-mono">${data.dataset.total_images}</span>
            <span class="text-[11px] text-slate-400 mt-1 block">Total Indexed Images</span>
          </div>
          <div class="glass-card rounded-xl p-4 text-center">
            <span class="block text-2xl font-bold text-cyan-400 font-mono">${data.dataset.faiss_indexed_vectors}</span>
            <span class="text-[11px] text-slate-400 mt-1 block">FAISS Vectors (0 Pixels)</span>
          </div>
          <div class="glass-card rounded-xl p-4 text-center">
            <span class="block text-2xl font-bold text-emerald-400 font-mono">${data.security.total_searches_logged}</span>
            <span class="text-[11px] text-slate-400 mt-1 block">Searches Executed</span>
          </div>
          <div class="glass-card rounded-xl p-4 text-center">
            <span class="block text-2xl font-bold text-amber-400 font-mono">${data.security.unauthorized_attempts_blocked}</span>
            <span class="text-[11px] text-slate-400 mt-1 block">Blocked Intrusion Attempts</span>
          </div>
        `;

        const tbody = document.getElementById('auditTableBody');
        tbody.innerHTML = "";
        data.recent_audit_trail.forEach(log => {
          const tr = document.createElement('tr');
          const isAllowed = log.status === 'ALLOWED' || log.status === 'PROCESSED';
          tr.innerHTML = `
            <td class="p-2 text-slate-400">${log.timestamp.split('T')[1].split('.')[0]}</td>
            <td class="p-2 text-cyan-300">${log.user_id}</td>
            <td class="p-2 text-white">${log.action}</td>
            <td class="p-2"><span class="px-1.5 py-0.5 rounded text-[10px] ${isAllowed ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-red-950 text-red-300 border border-red-800'}">${log.status}</span></td>
            <td class="p-2 text-slate-400 text-[11px]">${log.details}</td>
          `;
          tbody.appendChild(tr);
        });

      } catch (err) {
        console.error("Admin stats error:", err);
      }
    }
  </script>
</body>
</html>
"""
with open("frontend/index.html", "a", encoding="utf-8") as f:
    f.write(HTML_PART_4)
print("Frontend successfully written!")
