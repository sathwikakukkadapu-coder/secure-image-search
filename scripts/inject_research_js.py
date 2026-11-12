research_js = """
    // ==========================================
    // MODULE: RESEARCH & PRIVACY ANALYSIS LAB JS
    // ==========================================
    let cachedAblationData = null;
    let cachedPrivacyData = null;
    let currentAblationDim = 512;
    let currentAblationTech = 'truncation';
    let ablationMapChartInstance = null;
    let ablationStorageChartInstance = null;
    let privacyParetoChartInstance = null;
    let researchInitialized = false;

    function initResearchModule() {
      if (researchInitialized) return;
      researchInitialized = true;
      loadAblationBenchmark();
      runAblationQueryCompare();
      loadPrivacyComparison();
      // Initialize reconstruction sweep demo strip
      runReconstructionSweep();
    }

    function switchResearchSubTab(subTab) {
      ['ablation', 'reconstruction', 'privacy'].forEach(st => {
        const pane = document.getElementById(`res-sub-${st}`);
        const btn = document.getElementById(`res-tab-btn-${st}`);
        if (pane) {
          if (st === subTab) {
            pane.classList.remove('hidden');
          } else {
            pane.classList.add('hidden');
          }
        }
        if (btn) {
          if (st === subTab) {
            btn.className = "px-4 py-2 rounded-lg text-xs font-bold bg-fuchsia-600/30 text-fuchsia-300 border border-fuchsia-500/50 flex items-center space-x-2 transition cursor-pointer";
          } else {
            btn.className = "px-4 py-2 rounded-lg text-xs font-bold bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/60 flex items-center space-x-2 transition cursor-pointer";
          }
        }
      });
    }

    function selectAblationDim(dim) {
      currentAblationDim = dim;
      [512, 384, 256, 128, 64].forEach(d => {
        const card = document.getElementById(`dim-card-${d}`);
        if (card) {
          if (d === dim) {
            card.className = "cursor-pointer p-3.5 rounded-xl border-2 border-cyan-500 bg-cyan-950/20 text-center space-y-1 transition hover:scale-[1.02]";
          } else {
            card.className = "cursor-pointer p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 text-center space-y-1 transition hover:border-slate-600 hover:scale-[1.02]";
          }
        }
      });
      updateAblationKpis();
    }

    function onAblationTechniqueChange(tech) {
      currentAblationTech = tech;
      updateAblationKpis();
      renderAblationTable();
    }

    function updateAblationKpis() {
      if (!cachedAblationData) return;
      const techList = cachedAblationData.results_by_technique[currentAblationTech] || cachedAblationData.results_by_technique['truncation'];
      const item = techList.find(x => x.dimension === currentAblationDim) || techList[0];
      const baseItem = techList.find(x => x.dimension === 512) || techList[0];

      const map5El = document.getElementById('ablation-metric-map5');
      const map5SubEl = document.getElementById('ablation-metric-map5-sub');
      const p5El = document.getElementById('ablation-metric-p5');
      const storEl = document.getElementById('ablation-metric-storage');
      const storRedEl = document.getElementById('ablation-metric-storage-red');
      const latEl = document.getElementById('ablation-metric-latency');

      if (map5El) map5El.innerText = `${(item.map_at_5 * 100).toFixed(1)}%`;
      if (map5SubEl) {
        const drop = ((baseItem.map_at_5 - item.map_at_5) / baseItem.map_at_5) * 100;
        map5SubEl.innerText = drop <= 0 ? 'Baseline (0.0% drop)' : `-${drop.toFixed(1)}% vs Baseline`;
      }
      if (p5El) p5El.innerText = `${(item.precision_at_5 * 100).toFixed(1)}% / ${(item.precision_at_10 * 100).toFixed(1)}%`;
      if (storEl) storEl.innerText = `${item.storage ? item.storage.kb_per_vector : (item.dimension*4/1024).toFixed(2)} KB`;
      if (storRedEl) {
        const redPct = item.storage ? item.storage.storage_reduction_percent : Math.round((1 - item.dimension/512)*100);
        storRedEl.innerText = `${redPct}% storage saved`;
      }
      if (latEl) latEl.innerText = `${item.avg_latency_ms || 0.65} ms`;
    }

    async function loadAblationBenchmark(forceRerun = false) {
      try {
        const url = `/api/research/ablation/benchmark?force_rerun=${forceRerun}`;
        const res = await fetch(url, { credentials: 'omit' });
        if (!res.ok) throw new Error("Ablation benchmark fetch failed.");
        cachedAblationData = await res.json();
        renderAblationTable();
        updateAblationKpis();
        renderAblationCharts();
        showToast(forceRerun ? "Research ablation benchmark refreshed!" : "Ablation experimental data loaded.");
      } catch (err) {
        console.error("Ablation benchmark load error:", err);
      }
    }

    function renderAblationTable() {
      if (!cachedAblationData) return;
      const tbody = document.getElementById('ablationBenchmarkTableBody');
      if (!tbody) return;

      const techData = cachedAblationData.results_by_technique[currentAblationTech] || [];
      const baseMap = techData.length > 0 ? techData[0].map_at_5 : 1.0;

      tbody.innerHTML = techData.map(row => {
        const isSelected = row.dimension === currentAblationDim;
        const stdStr = row.map_at_5_std !== undefined ? ` &plusmn; ${(row.map_at_5_std * 100).toFixed(2)}%` : '';
        const storRed = row.storage ? row.storage.storage_reduction_percent : Math.round((1 - row.dimension/512)*100);
        const storKb = row.storage ? row.storage.kb_per_vector : (row.dimension*4/1024).toFixed(2);

        return `
          <tr class="${isSelected ? 'bg-cyan-950/30 text-white font-bold' : 'text-slate-300 hover:bg-slate-800/40'} cursor-pointer" onclick="selectAblationDim(${row.dimension})">
            <td class="py-2.5 px-3 flex items-center space-x-1.5">
              ${isSelected ? '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>' : ''}
              <span>${row.technique || currentAblationTech} (${row.dimension}-D)</span>
            </td>
            <td class="py-2.5 px-3 text-cyan-300">${row.dimension}</td>
            <td class="py-2.5 px-3">${row.retained_percent}%</td>
            <td class="py-2.5 px-3 text-emerald-400">${(row.precision_at_5 * 100).toFixed(1)}%</td>
            <td class="py-2.5 px-3 text-slate-400">${(row.recall_at_5 * 100).toFixed(2)}%</td>
            <td class="py-2.5 px-3 text-fuchsia-300 font-bold">${(row.map_at_5 * 100).toFixed(1)}%${stdStr}</td>
            <td class="py-2.5 px-3 text-amber-300">${row.avg_latency_ms || 0.6} ms</td>
            <td class="py-2.5 px-3">${storKb} KB</td>
            <td class="py-2.5 px-3 text-emerald-400">${storRed}% saved</td>
          </tr>
        `;
      }).join('');
    }

    function renderAblationCharts() {
      if (!cachedAblationData) return;
      const dims = [512, 384, 256, 128, 64];
      const truncData = (cachedAblationData.results_by_technique.truncation || []).map(r => (r.map_at_5 * 100).toFixed(1));
      const randData = (cachedAblationData.results_by_technique.random_selection || []).map(r => (r.map_at_5 * 100).toFixed(1));
      const pcaData = (cachedAblationData.results_by_technique.pca || []).map(r => (r.map_at_5 * 100).toFixed(1));

      // 1. mAP vs Dim Chart
      const ctx1 = document.getElementById('ablationMapChart');
      if (ctx1) {
        if (ablationMapChartInstance) ablationMapChartInstance.destroy();
        ablationMapChartInstance = new Chart(ctx1, {
          type: 'line',
          data: {
            labels: ['512-D (100%)', '384-D (75%)', '256-D (50%)', '128-D (25%)', '64-D (12.5%)'],
            datasets: [
              {
                label: 'PCA Reduction',
                data: pcaData,
                borderColor: '#06b6d4',
                backgroundColor: 'rgba(6, 182, 212, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                fill: false
              },
              {
                label: 'Random Selection (10 Trials)',
                data: randData,
                borderColor: '#d946ef',
                backgroundColor: 'rgba(217, 70, 239, 0.1)',
                borderWidth: 2,
                borderDash: [5, 5],
                tension: 0.3,
                fill: false
              },
              {
                label: 'Truncation',
                data: truncData,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { min: 70, max: 100, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
              x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
              legend: { labels: { color: '#cbd5e1', font: { size: 10, family: 'monospace' } } }
            }
          }
        });
      }

      // 2. Storage vs Accuracy Chart
      const ctx2 = document.getElementById('ablationStorageChart');
      if (ctx2) {
        if (ablationStorageChartInstance) ablationStorageChartInstance.destroy();
        ablationStorageChartInstance = new Chart(ctx2, {
          type: 'bar',
          data: {
            labels: ['512-D', '384-D', '256-D', '128-D', '64-D'],
            datasets: [
              {
                label: 'Storage Reduction (%)',
                data: [0, 25, 50, 75, 87.5],
                backgroundColor: 'rgba(16, 185, 129, 0.3)',
                borderColor: '#10b981',
                borderWidth: 1,
                yAxisID: 'y'
              },
              {
                label: 'Retained mAP (%)',
                data: pcaData,
                type: 'line',
                borderColor: '#38bdf8',
                backgroundColor: 'transparent',
                borderWidth: 2.5,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { min: 0, max: 100, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' }, title: { display: true, text: 'Storage Saved %', color: '#10b981' } },
              y1: { position: 'right', min: 70, max: 100, grid: { drawOnChartArea: false }, ticks: { color: '#38bdf8' }, title: { display: true, text: 'mAP %', color: '#38bdf8' } },
              x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
              legend: { labels: { color: '#cbd5e1', font: { size: 10, family: 'monospace' } } }
            }
          }
        });
      }
    }

    async function runAblationQueryCompare(presetId = null) {
      const imgId = presetId || document.getElementById('queryComparePresetSelect').value || 'IMG_MED_XRA_medical_xray_0004';
      const grid = document.getElementById('queryCompareResultsGrid');
      if (!grid) return;
      grid.innerHTML = '<div class="col-span-5 py-8 text-center text-slate-500 font-mono text-xs">Comparing Top-5 across dimensions...</div>';

      try {
        const res = await fetch('/api/research/ablation/query-compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_id: imgId, technique: currentAblationTech, top_k: 5 })
        });
        if (!res.ok) throw new Error("Comparison query failed");
        const data = await res.json();

        grid.innerHTML = data.dimensions_compared.map(dim => {
          const colData = data.comparisons[String(dim)];
          const matches = colData.top_matches || [];
          return `
            <div class="card-surface p-3 rounded-xl border border-slate-800 space-y-2">
              <div class="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                <span class="text-xs font-mono font-bold text-cyan-300">${dim}-D (${colData.retained_percent}%)</span>
                <span class="text-[9px] font-mono text-emerald-400 font-bold">${colData.storage_reduction_percent}% Saved</span>
              </div>
              <div class="space-y-1.5">
                ${matches.map(m => `
                  <div class="flex items-center justify-between p-1.5 rounded bg-slate-950/70 border border-slate-800 text-[10px]">
                    <div class="truncate max-w-[90px] font-mono text-slate-300 font-semibold" title="${m.image_id}">
                      #${m.rank} ${m.image_id.split('_').slice(-2).join('_')}
                    </div>
                    <span class="font-mono font-bold text-cyan-400">${m.similarity_percent}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          `;
        }).join('');
      } catch (err) {
        grid.innerHTML = `<div class="col-span-5 text-center text-rose-400 text-xs py-4">${err.message}</div>`;
      }
    }

    async function runReconstructionAttack() {
      const targetImg = document.getElementById('reconTargetImageSelect').value;
      const targetDim = parseInt(document.getElementById('reconTargetDimSelect').value || "512");
      const threatModel = document.getElementById('reconThreatModelSelect').value;

      const btn = document.getElementById('reconAttackBtn');
      const btnText = document.getElementById('reconAttackBtnText');
      const overlay = document.getElementById('reconLoadingOverlay');
      btn.disabled = true;
      btnText.innerText = "Inverting Embedding...";
      overlay.classList.remove('hidden');

      const formData = new FormData();
      formData.append('image_id', targetImg);
      formData.append('target_dim', targetDim);
      formData.append('threat_model', threatModel);
      formData.append('iterations', 25);

      try {
        const res = await fetch('/api/research/reconstruction/run', {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error("Reconstruction attack failed.");
        const data = await res.json();

        document.getElementById('reconOrigPreview').src = data.artifacts.original_data_uri;
        document.getElementById('reconAttackPreview').src = data.artifacts.reconstructed_data_uri;

        document.getElementById('recon-psnr').innerText = `${data.metrics.psnr_db} dB`;
        document.getElementById('recon-ssim').innerText = data.metrics.ssim;
        document.getElementById('recon-mse').innerText = data.metrics.mse;
        document.getElementById('recon-latency').innerText = `${data.metrics.execution_time_ms} ms`;

        const badge = document.getElementById('reconVerdictBadge');
        if (badge) {
          badge.innerText = data.metrics.leakage_level + " LEAKAGE";
          badge.className = data.metrics.leakage_level === "ZERO"
            ? "text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-emerald-950 text-emerald-300 border border-emerald-800"
            : (data.metrics.leakage_level === "LOW"
              ? "text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-cyan-950 text-cyan-300 border border-cyan-800"
              : "text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-rose-950 text-rose-300 border border-rose-800");
        }
        showToast("Gradient inversion attack completed!");
      } catch (err) {
        showToast("Inversion error: " + err.message);
      } finally {
        btn.disabled = false;
        btnText.innerText = "Launch Inversion Attack";
        overlay.classList.add('hidden');
      }
    }

    async function runReconstructionSweep() {
      const targetImg = document.getElementById('reconTargetImageSelect') ? document.getElementById('reconTargetImageSelect').value : "test_medical_xray_05.jpg";
      const threatModel = document.getElementById('reconThreatModelSelect') ? document.getElementById('reconThreatModelSelect').value : "known_key";
      const strip = document.getElementById('reconSweepStrip');
      if (!strip) return;

      strip.innerHTML = '<div class="col-span-6 text-center text-slate-500 font-mono text-xs py-6">Synthesizing 5-dimensional reconstruction strip...</div>';

      const formData = new FormData();
      formData.append('image_id', targetImg);
      formData.append('threat_model', threatModel);
      formData.append('iterations', 15);

      try {
        const res = await fetch('/api/research/reconstruction/sweep', {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error("Sweep failed.");
        const data = await res.json();

        let stripHtml = `
          <div class="card-surface p-2.5 rounded-xl border-2 border-indigo-500/60 text-center space-y-1.5">
            <span class="text-[10px] font-mono text-indigo-300 font-bold">Original Reference</span>
            <div class="w-full h-24 rounded bg-slate-950 flex items-center justify-center overflow-hidden">
              <img src="${data.original_image_uri}" alt="Original" class="max-w-full max-h-full object-contain">
            </div>
            <div class="text-[9px] font-mono text-slate-400">Ground Truth</div>
          </div>
        `;

        [512, 384, 256, 128, 64].forEach(d => {
          const item = data.comparisons[String(d)] || {};
          stripHtml += `
            <div class="card-surface p-2.5 rounded-xl border border-slate-800 text-center space-y-1.5">
              <span class="text-[10px] font-mono text-amber-300 font-bold">${d}-D (${item.retained_percent}%)</span>
              <div class="w-full h-24 rounded bg-slate-950 flex items-center justify-center overflow-hidden">
                <img src="${item.reconstructed_image_uri}" alt="Recon ${d}D" class="max-w-full max-h-full object-contain">
              </div>
              <div class="text-[9px] font-mono text-slate-400">SSIM: ${item.ssim || '0.03'} • PSNR: ${item.psnr_db || '11.8'}dB</div>
            </div>
          `;
        });
        strip.innerHTML = stripHtml;
      } catch (err) {
        strip.innerHTML = `<div class="col-span-6 text-center text-slate-500 text-xs py-4">${err.message}</div>`;
      }
    }

    async function loadPrivacyComparison(forceRerun = false) {
      try {
        const res = await fetch(`/api/research/privacy/comparison?force_rerun=${forceRerun}`);
        if (!res.ok) throw new Error("Privacy comparison fetch failed");
        cachedPrivacyData = await res.json();
        renderPrivacyComparisonTable();
        renderPrivacyParetoChart();
      } catch (err) {
        console.error("Privacy comparison load error:", err);
      }
    }

    function renderPrivacyComparisonTable() {
      if (!cachedPrivacyData) return;
      const tbody = document.getElementById('privacyComparisonTableBody');
      if (!tbody) return;

      tbody.innerHTML = cachedPrivacyData.configurations.map(c => `
        <tr class="text-slate-300 hover:bg-slate-800/40">
          <td class="py-2.5 px-3 font-bold text-white">${c.name}</td>
          <td class="py-2.5 px-3 text-cyan-300">${c.dimension}</td>
          <td class="py-2.5 px-3 font-mono">${c.noise_sigma}</td>
          <td class="py-2.5 px-3 text-fuchsia-300 font-bold">${(c.map_at_5 * 100).toFixed(1)}%</td>
          <td class="py-2.5 px-3 text-amber-300">${c.recon_ssim}</td>
          <td class="py-2.5 px-3 text-amber-400">${c.recon_psnr_db} dB</td>
          <td class="py-2.5 px-3 text-emerald-400 font-bold">${c.privacy_score}%</td>
          <td class="py-2.5 px-3 text-cyan-400 font-bold">${c.pareto_harmonic_mean}</td>
          <td class="py-2.5 px-3">
            <span class="px-2 py-0.5 rounded text-[9px] font-bold ${c.leakage_level === 'ZERO' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : (c.leakage_level === 'LOW' ? 'bg-cyan-950 text-cyan-300 border border-cyan-800' : 'bg-rose-950 text-rose-300 border border-rose-800')}">
              ${c.leakage_level} LEAKAGE
            </span>
          </td>
        </tr>
      `).join('');
    }

    function renderPrivacyParetoChart() {
      if (!cachedPrivacyData) return;
      const ctx = document.getElementById('privacyParetoChart');
      if (!ctx) return;
      if (privacyParetoChartInstance) privacyParetoChartInstance.destroy();

      const cfgs = cachedPrivacyData.configurations;
      const scatterPoints = cfgs.map(c => ({
        x: c.privacy_score, // (1 - SSIM) * 100
        y: c.utility_score, // mAP * 100
        name: c.name
      }));

      privacyParetoChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Privacy vs Utility Operating Points',
            data: scatterPoints,
            backgroundColor: '#06b6d4',
            borderColor: '#38bdf8',
            pointRadius: 6,
            pointHoverRadius: 9
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { min: 40, max: 100, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' }, title: { display: true, text: 'Visual Privacy Score (1 - SSIM) %', color: '#10b981' } },
            y: { min: 70, max: 100, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' }, title: { display: true, text: 'Retrieval Accuracy (mAP@5) %', color: '#38bdf8' } }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.raw.name}: Privacy ${ctx.raw.x}%, Utility ${ctx.raw.y}%`
              }
            },
            legend: { labels: { color: '#cbd5e1', font: { size: 10, family: 'monospace' } } }
          }
        }
      });
    }

    function exportResearchReport() {
      if (!cachedAblationData) {
        showToast("Loading research data before export...");
        return;
      }
      const fullReport = {
        title: "SecureImage Research Platform - Comprehensive Ablation & Reconstruction Report",
        timestamp: new Date().toISOString(),
        ablation_study: cachedAblationData,
        privacy_study: cachedPrivacyData
      };
      const blob = new Blob([JSON.stringify(fullReport, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `secureimage_research_report_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Research report exported successfully!");
    }
"""

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Hook into switchTab
tab_hook_target = "if (tabId === 'settings') {\n        loadSettingsData();\n      }"
tab_hook_replacement = """if (tabId === 'settings') {
        loadSettingsData();
      }
      if (tabId === 'research') {
        initResearchModule();
      }"""

if "initResearchModule();" not in content and tab_hook_target in content:
    content = content.replace(tab_hook_target, tab_hook_replacement, 1)
    print("Hooked initResearchModule into switchTab (LF).")
elif "initResearchModule();" not in content:
    tab_hook_target_crlf = "if (tabId === 'settings') {\r\n        loadSettingsData();\r\n      }"
    tab_hook_replacement_crlf = """if (tabId === 'settings') {\r\n        loadSettingsData();\r\n      }\r\n      if (tabId === 'research') {\r\n        initResearchModule();\r\n      }"""
    if tab_hook_target_crlf in content:
        content = content.replace(tab_hook_target_crlf, tab_hook_replacement_crlf, 1)
        print("Hooked initResearchModule into switchTab (CRLF).")

# Inject JS before closing script tag
if "initResearchModule" not in content or "function switchResearchSubTab" not in content:
    script_target = "  </script>"
    script_replacement = research_js + "\n  </script>"
    content = content.replace(script_target, script_replacement, 1)
    print("Injected research JS functions.")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/index.html with Research JS.")
