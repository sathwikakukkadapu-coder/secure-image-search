HTML_PART_2 = """
  <!-- MAIN CONTAINER -->
  <main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full">

    <!-- TAB 1: SEARCH ENGINE (CORE RETRIEVAL) -->
    <section id="tab-search" class="space-y-6">
      
      <!-- Top Notice Banner -->
      <div class="p-3 rounded-xl bg-blue-950/40 border border-blue-800/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div class="flex items-center space-x-2.5 text-slate-300">
          <svg class="w-5 h-5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span><strong>Privacy Guarantee:</strong> Your query image is processed in volatile memory. <strong>Your original image is not added to the vector database.</strong></span>
        </div>
        <div class="flex items-center space-x-2 font-mono text-[11px] text-cyan-300">
          <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-700">AES-256 Vault Active</span>
          <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-700">FAISS Cosine Index</span>
        </div>
      </div>

      <!-- Main Search & Upload Area -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Upload & Settings Card (5 cols) -->
        <div class="lg:col-span-5 glass-card rounded-2xl p-5 space-y-4">
          <div class="flex justify-between items-center">
            <h2 class="text-sm font-bold text-white uppercase tracking-wider font-mono">Image Query Input</h2>
            <span class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">JPG • PNG • WebP (&lt;10MB)</span>
          </div>

          <!-- Drag and Drop Dropzone -->
          <div id="dropzone" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)" onclick="document.getElementById('fileInput').click()" class="border-2 border-dashed border-slate-700 hover:border-cyan-400 rounded-xl p-6 text-center cursor-pointer transition bg-slate-950/60 hover:bg-blue-950/20 group">
            <input type="file" id="fileInput" accept="image/*" onchange="handleFileSelect(event)" class="hidden">
            
            <div id="dropzonePrompt" class="space-y-2">
              <div class="w-12 h-12 mx-auto rounded-full bg-slate-900 border border-slate-700 group-hover:border-cyan-400 flex items-center justify-center text-slate-400 group-hover:text-cyan-300 transition">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              </div>
              <p class="text-xs font-semibold text-white">Upload an image to find similar images</p>
              <p class="text-[11px] text-slate-400">Drag and drop file here, or <span class="text-cyan-400 underline">browse files</span></p>
            </div>

            <!-- Active Image Preview -->
            <div id="dropzonePreview" class="hidden space-y-2">
              <img id="previewImg" src="" alt="Query Preview" class="max-h-44 mx-auto rounded-lg object-contain shadow-lg border border-slate-700">
              <div class="flex items-center justify-center space-x-3 text-xs pt-1">
                <span id="previewName" class="font-mono text-slate-300 truncate max-w-[180px]">image.jpg</span>
                <button type="button" onclick="clearImage(event)" class="text-red-400 hover:text-red-300 font-mono text-[11px] underline">Remove</button>
              </div>
            </div>
          </div>

          <!-- Quick Sample Presets -->
          <div>
            <span class="text-[11px] font-mono text-slate-400 block mb-1.5">Or test a confidential dataset sample:</span>
            <div class="grid grid-cols-4 gap-1.5 text-[10px] font-mono">
              <button onclick="loadSamplePreset('medical')" class="p-1.5 rounded bg-slate-900 hover:bg-blue-950 border border-slate-800 hover:border-blue-500 text-slate-300 hover:text-white transition truncate">Chest CT</button>
              <button onclick="loadSamplePreset('biometrics')" class="p-1.5 rounded bg-slate-900 hover:bg-blue-950 border border-slate-800 hover:border-blue-500 text-slate-300 hover:text-white transition truncate">Biometric</button>
              <button onclick="loadSamplePreset('vehicles')" class="p-1.5 rounded bg-slate-900 hover:bg-blue-950 border border-slate-800 hover:border-blue-500 text-slate-300 hover:text-white transition truncate">Sedan Car</button>
              <button onclick="loadSamplePreset('nature')" class="p-1.5 rounded bg-slate-900 hover:bg-blue-950 border border-slate-800 hover:border-blue-500 text-slate-300 hover:text-white transition truncate">Mountain</button>
            </div>
          </div>

          <!-- Controls: Top-K & Privacy Mode -->
          <div class="grid grid-cols-2 gap-3 pt-1 text-xs">
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
              <span class="text-slate-400 block mb-1 font-mono text-[10px]">Top-K Results:</span>
              <select id="topKSelect" class="w-full bg-slate-900 border border-slate-700 text-white rounded p-1.5 font-mono text-xs focus:ring-1 focus:ring-blue-500 cursor-pointer">
                <option value="3">Top 3 Results</option>
                <option value="5" selected>Top 5 Results</option>
                <option value="10">Top 10 Results</option>
              </select>
            </div>

            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
              <span class="text-slate-400 block mb-1 font-mono text-[10px]">Representation:</span>
              <label class="flex items-center space-x-2 mt-1 cursor-pointer">
                <input type="checkbox" id="privacyToggle" checked class="rounded text-blue-600 focus:ring-0 cursor-pointer">
                <span class="text-xs font-semibold text-cyan-300">Protected Mode</span>
              </label>
            </div>
          </div>

          <!-- Search Button -->
          <button id="searchBtn" onclick="runSearch()" class="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-400 font-bold text-white text-xs sm:text-sm tracking-wide shadow-lg shadow-blue-900/40 flex items-center justify-center space-x-2 transition cursor-pointer">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            <span>Execute Private Image Search</span>
          </button>
        </div>

        <!-- Pipeline Status & Results Gallery (7 cols) -->
        <div class="lg:col-span-7 space-y-4">
          
          <!-- Live Pipeline Visualizer -->
          <div class="glass-card rounded-2xl p-4">
            <div class="flex justify-between items-center mb-3">
              <span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider font-bold">Real-Time Processing Pipeline</span>
              <span id="pipelineStatusBadge" class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">IDLE</span>
            </div>

            <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 text-center text-[10px] font-mono">
              <div id="pipe-upload" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">1. Upload</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
              <div id="pipe-prep" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">2. Preprocess</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
              <div id="pipe-infer" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">3. Features</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
              <div id="pipe-protect" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">4. Protect</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
              <div id="pipe-faiss" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">5. FAISS</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
              <div id="pipe-auth" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400">
                <span class="block text-slate-500 mb-0.5">6. Auth Gate</span>
                <span class="step-status font-bold">Waiting</span>
              </div>
            </div>
          </div>

          <!-- Retrieval Summary Card -->
          <div id="summaryCard" class="hidden p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-2 font-mono">
            <div>
              <span id="resultsCountText" class="font-bold text-white text-sm">5 similar images found</span>
              <span class="text-slate-400 text-[11px] block">Model: MobileNetV3 (1280-D ➔ 512-D Protected)</span>
            </div>
            <div class="text-right">
              <span id="searchLatencyText" class="text-emerald-400 font-bold block">Latency: 0.28 sec</span>
              <span class="text-[10px] text-slate-500">Method: Cosine Vector Similarity</span>
            </div>
          </div>

          <!-- Results Grid -->
          <div id="resultsContainer" class="space-y-3">
            <div class="text-center py-12 text-slate-500 text-xs font-mono">
              Upload an image above and click "Execute Private Image Search" to view results.
            </div>
          </div>

        </div>

      </div>

      <!-- Privacy Status Checklist Section -->
      <div class="glass-card rounded-2xl p-5">
        <h3 class="text-xs font-bold text-white uppercase tracking-wider font-mono mb-3 flex items-center space-x-2">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>Privacy Status & Security Verification</span>
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-2">
            <span class="text-emerald-400 font-bold text-sm">✓</span>
            <div>
              <strong class="text-white block">Decoupled Storage</strong>
              <span class="text-slate-400 text-[11px]">Original images stored in isolated private storage, NOT in FAISS.</span>
            </div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-2">
            <span class="text-emerald-400 font-bold text-sm">✓</span>
            <div>
              <strong class="text-white block">Protected Vectors</strong>
              <span class="text-slate-400 text-[11px]">Orthogonal projection + differential perturbation applied before indexing.</span>
            </div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-2">
            <span class="text-emerald-400 font-bold text-sm">✓</span>
            <div>
              <strong class="text-white block">Access-Controlled</strong>
              <span class="text-slate-400 text-[11px]">Owner-based and role-based authorization required to release pictures.</span>
            </div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-2">
            <span class="text-emerald-400 font-bold text-sm">✓</span>
            <div>
              <strong class="text-white block">Encrypted References</strong>
              <span class="text-slate-400 text-[11px]">Storage paths protected with AES-256-GCM symmetric cipher at rest.</span>
            </div>
          </div>
        </div>
      </div>

    </section>
"""
with open("frontend/index.html", "a", encoding="utf-8") as f:
    f.write(HTML_PART_2)
print("Part 2 written")
