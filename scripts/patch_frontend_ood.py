with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """      const badge = document.getElementById('diagStatusBadge');
      if (badge && diag.detected_domain) {
        badge.innerText = `Domain: ${diag.detected_domain.toUpperCase()} (Protected)`;
      }
    }

    function renderResults(results) {
      const container = document.getElementById('resultsContainer');
      const filtered = results.slice(0, currentTopK);

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="card-surface p-10 text-center space-y-2 border border-slate-800">
            <div class="w-10 h-10 mx-auto rounded-full bg-slate-900 flex items-center justify-center text-slate-500 mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            <p class="text-sm font-bold text-slate-300">No matches found meeting threshold (${currentThreshold.toFixed(2)})</p>
            <p class="text-xs text-slate-500">Try lowering similarity threshold or changing domain filter.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(r => {
        const isAuth = r.authorized;
        return `
          <div class="card-surface p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border ${isAuth ? 'border-slate-800 hover:border-indigo-500/60' : 'border-rose-950/70 bg-rose-950/10'} transition">
            <div class="flex items-center space-x-4">
              <!-- Thumbnail of Database Asset (AUTHORIZED ONLY, OR LOCKED) -->
              <div class="w-20 h-20 rounded-xl bg-slate-950 border ${isAuth ? 'border-indigo-500/40' : 'border-rose-900/60'} flex items-center justify-center shrink-0 overflow-hidden shadow-md">
                ${isAuth && r.image_url 
                  ? `<img src="${r.image_url}" alt="${r.image_id}" class="w-full h-full object-cover cursor-pointer hover:scale-110 transition duration-300" onclick="openResultModal('${r.image_id}', '${r.image_url}')" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'text-center p-1 text-slate-500 text-[10px]\\'>Locked</div>'">`
                  : `<div class="text-center p-2 text-rose-400">
                      <svg class="w-6 h-6 mx-auto mb-0.5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                      <div class="text-[9px] font-mono text-rose-300 font-bold">LOCKED</div>
                    </div>`
                }
              </div>

              <div class="space-y-1.5">
                <div class="flex items-center space-x-2">
                  <span class="text-xs font-mono font-bold text-white">${r.image_id}</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono ${isAuth ? 'badge-emerald' : 'badge-rose'} font-bold">
                    ${isAuth ? '✓ Authorized' : '🔒 Access Denied'}
                  </span>
                  <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700 uppercase font-bold font-mono">
                    ${r.category}
                  </span>
                </div>
                <p class="text-xs text-slate-300">${r.match_explanation}</p>
                <!-- Barcode of Stored Vector -->
                <div class="font-mono text-[10px] text-indigo-300">
                  Vector Signature: <span class="tracking-wider text-cyan-400 font-bold">${r.vector_barcode || '░░░░░░░░'}</span>
                </div>
              </div>
            </div>

            <!-- Similarity Metric & Action -->
            <div class="text-right shrink-0">
              <div class="text-lg font-extrabold font-mono text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">${r.similarity_percent}</div>
              <div class="text-[10px] text-slate-400 font-mono">Rank #${r.rank} Cosine Proximity</div>
              ${isAuth && r.image_url 
                ? `<button onclick="openResultModal('${r.image_id}', '${r.image_url}')" class="mt-2 text-[11px] text-cyan-400 hover:text-cyan-300 font-semibold underline block ml-auto">Inspect Vault Asset</button>`
                : `<div class="mt-2 text-[10px] text-rose-400 font-mono font-semibold">Specialist Auth Required</div>`
              }
            </div>
          </div>
        `;
      }).join('');
    }"""

replacement = """      const badge = document.getElementById('diagStatusBadge');
      if (badge) {
        if (diag.records_passed_threshold === 0) {
          badge.innerText = `Out-of-Domain Filtered (Cut-off ≥ ${(currentThreshold * 100).toFixed(0)}%)`;
          badge.className = "text-[10px] font-mono text-amber-300 bg-amber-950 px-2.5 py-0.5 rounded border border-amber-800 font-bold";
        } else {
          badge.innerText = `Domain: ${(diag.detected_domain || 'ALL').toUpperCase()} (Protected)`;
          badge.className = "text-[10px] font-mono text-emerald-300 bg-emerald-950 px-2.5 py-0.5 rounded border border-emerald-800 font-bold";
        }
      }
    }

    function renderResultCards(items, isSuppressed = false) {
      return items.map(r => {
        const isAuth = r.authorized;
        const borderClass = isSuppressed 
          ? 'border-amber-500/30 bg-amber-950/10' 
          : (isAuth ? 'border-slate-800 hover:border-indigo-500/60' : 'border-rose-950/70 bg-rose-950/10');
        const badgeBorder = isSuppressed
          ? 'border-amber-500/40'
          : (isAuth ? 'border-indigo-500/40' : 'border-rose-900/60');
          
        return `
          <div class="card-surface p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border ${borderClass} transition rounded-xl">
            <div class="flex items-center space-x-4">
              <!-- Thumbnail of Database Asset (AUTHORIZED ONLY, OR LOCKED) -->
              <div class="w-20 h-20 rounded-xl bg-slate-950 border ${badgeBorder} flex items-center justify-center shrink-0 overflow-hidden shadow-md">
                ${isAuth && r.image_url 
                  ? `<img src="${r.image_url}" alt="${r.image_id}" class="w-full h-full object-cover cursor-pointer hover:scale-110 transition duration-300" onclick="openResultModal('${r.image_id}', '${r.image_url}')" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'text-center p-1 text-slate-500 text-[10px]\\'>Locked</div>'">`
                  : `<div class="text-center p-2 text-rose-400">
                      <svg class="w-6 h-6 mx-auto mb-0.5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                      <div class="text-[9px] font-mono text-rose-300 font-bold">LOCKED</div>
                    </div>`
                }
              </div>

              <div class="space-y-1.5">
                <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                  <span class="text-xs font-mono font-bold text-white">${r.image_id}</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono ${isAuth ? 'badge-emerald' : 'badge-rose'} font-bold">
                    ${isAuth ? '✓ Authorized' : '🔒 Access Denied'}
                  </span>
                  <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700 uppercase font-bold font-mono">
                    ${r.category}
                  </span>
                  ${isSuppressed ? `
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold">
                      Below Cut-Off
                    </span>
                  ` : ''}
                </div>
                <p class="text-xs text-slate-300">${r.match_explanation}</p>
                <!-- Barcode of Stored Vector -->
                <div class="font-mono text-[10px] text-indigo-300">
                  Vector Signature: <span class="tracking-wider text-cyan-400 font-bold">${r.vector_barcode || '░░░░░░░░'}</span>
                </div>
              </div>
            </div>

            <!-- Similarity Metric & Action -->
            <div class="text-right shrink-0">
              <div class="text-lg font-extrabold font-mono text-transparent bg-clip-text ${isSuppressed ? 'bg-gradient-to-r from-amber-400 to-rose-400' : 'bg-gradient-to-r from-cyan-400 to-emerald-400'}">${r.similarity_percent}</div>
              <div class="text-[10px] text-slate-400 font-mono">${isSuppressed ? 'Suppressed Candidate' : `Rank #${r.rank} Cosine Proximity`}</div>
              ${isAuth && r.image_url 
                ? `<button onclick="openResultModal('${r.image_id}', '${r.image_url}')" class="mt-2 text-[11px] text-cyan-400 hover:text-cyan-300 font-semibold underline block ml-auto">Inspect Vault Asset</button>`
                : `<div class="mt-2 text-[10px] text-rose-400 font-mono font-semibold">Specialist Auth Required</div>`
              }
            </div>
          </div>
        `;
      }).join('');
    }

    function toggleLowConfidenceInspection() {
      const container = document.getElementById('lowConfidenceContainer');
      const btn = document.getElementById('btnToggleLowConf');
      if (!container) return;
      if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        if (btn) btn.innerText = "Hide Suppressed Candidates";
      } else {
        container.classList.add('hidden');
        if (btn) btn.innerText = `Inspect Suppressed Candidates (${(lastRetrievedResults || []).length})`;
      }
    }

    function renderResults(results) {
      const container = document.getElementById('resultsContainer');
      const allResults = results || [];
      // Filter candidates that meet the threshold
      const validMatches = allResults.filter(r => r.is_above_threshold !== false && (r.cosine_similarity === undefined || r.cosine_similarity >= currentThreshold));
      const filtered = validMatches.slice(0, currentTopK);

      if (filtered.length === 0) {
        // Find highest similarity candidate among all returned candidates for informative feedback
        const topCandidate = allResults.length > 0 ? allResults[0] : null;
        const topPct = topCandidate ? topCandidate.similarity_percent : '0.0%';
        const isOutOfDomain = !topCandidate || (topCandidate.cosine_similarity !== undefined && topCandidate.cosine_similarity < currentThreshold);

        container.innerHTML = `
          <div class="card-surface p-8 text-center space-y-4 border border-amber-500/40 bg-gradient-to-b from-amber-950/20 to-slate-900/60 rounded-2xl shadow-xl">
            <div class="w-14 h-14 mx-auto rounded-2xl bg-amber-950/60 border border-amber-500/50 flex items-center justify-center text-amber-400 shadow-lg shadow-amber-900/30">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            
            <div class="space-y-1">
              <div class="inline-flex items-center space-x-1.5 px-3 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                <span>${isOutOfDomain ? 'OUT-OF-DOMAIN QUERY DETECTED' : 'BELOW SIMILARITY THRESHOLD'}</span>
              </div>
              <h3 class="text-base font-bold text-white">No Relevant Matches Found</h3>
            </div>

            <p class="text-xs text-slate-300 max-w-lg mx-auto leading-relaxed">
              The query image does not match indexed catalog categories (<span class="text-cyan-300 font-semibold">Medical, Biometrics, Vehicles, Nature</span>). The closest visual feature similarity was only <span class="font-mono font-bold text-amber-400">${topPct}</span>, which is below the relevance threshold cut-off (<span class="font-mono font-bold text-cyan-300">≥ ${(currentThreshold * 100).toFixed(0)}%</span>).
            </p>

            <div class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl max-w-md mx-auto text-left space-y-1.5">
              <div class="flex items-center justify-between text-[11px] font-mono">
                <span class="text-slate-400">Relevance Cut-Off:</span>
                <span class="text-cyan-400 font-bold">≥ ${(currentThreshold * 100).toFixed(0)}% Similarity</span>
              </div>
              <div class="flex items-center justify-between text-[11px] font-mono">
                <span class="text-slate-400">Closest Candidate Similarity:</span>
                <span class="text-amber-400 font-bold">${topPct} (Suppressed)</span>
              </div>
              <div class="flex items-center justify-between text-[11px] font-mono">
                <span class="text-slate-400">Zero-Pixel Shield:</span>
                <span class="text-emerald-400 font-bold">0 Query Pixels Transmitted</span>
              </div>
            </div>

            <div class="pt-2 flex flex-wrap items-center justify-center gap-3">
              <button onclick="document.getElementById('facultyDemoSelect') && (document.getElementById('facultyDemoSelect').focus())" class="px-3.5 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-semibold shadow-md transition">
                Select From Demo Test Dataset
              </button>
              ${allResults.length > 0 ? `
                <button onclick="toggleLowConfidenceInspection()" id="btnToggleLowConf" class="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition">
                  Inspect Suppressed Candidates (${allResults.length})
                </button>
              ` : ''}
            </div>

            <!-- Optional collapsible container for low-confidence candidates -->
            <div id="lowConfidenceContainer" class="hidden text-left pt-4 space-y-2 border-t border-slate-800/80 mt-4">
              <div class="text-[11px] font-mono text-slate-400 mb-2">
                Diagnostic Inspection: Nearest catalog vectors in FAISS space. Suppressed to prevent false-positive retrieval:
              </div>
              ${renderResultCards(allResults.slice(0, currentTopK), true)}
            </div>
          </div>
        `;
        return;
      }

      container.innerHTML = renderResultCards(filtered, false);
    }"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched frontend/index.html (LF)")
else:
    target_crlf = target.replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\n', '\r\n')
    if target_crlf in content:
        content = content.replace(target_crlf, replacement_crlf, 1)
        with open('frontend/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully patched frontend/index.html (CRLF)")
    else:
        print("Target NOT FOUND in frontend/index.html")
