import os

index_html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
with open(index_html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace the query preview thumbnail with the zero-pixel shielded buffer
old_preview_block = """                  <div class="flex items-center space-x-3 overflow-hidden">
                    <!-- Image Preview Thumbnail in Client Memory -->
                    <div class="w-12 h-12 rounded-lg bg-slate-950 border border-indigo-500/50 overflow-hidden shrink-0 shadow-sm">
                      <img id="queryImagePreview" src="" alt="Query Preview" class="w-full h-full object-cover">
                    </div>
                    <div class="truncate">
                      <div class="text-xs font-bold text-white truncate" id="selectedFileName">medical_xray_0004.jpg</div>
                      <div class="text-[10px] text-emerald-400 font-mono font-semibold" id="selectedFileSize">49.5 KB | Local Memory Buffer</div>
                    </div>
                  </div>"""

new_shield_block = """                  <div class="flex items-center space-x-3 overflow-hidden">
                    <!-- Zero-Pixel Shield: Raw Query Pixels Withheld from Display & Network -->
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-950 via-slate-900 to-indigo-950 border border-cyan-500/60 flex flex-col items-center justify-center shrink-0 shadow-lg relative overflow-hidden group">
                      <div class="absolute inset-0 bg-cyan-400/10 animate-pulse pointer-events-none"></div>
                      <svg class="w-6 h-6 text-cyan-400 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                      </svg>
                      <span class="text-[7.5px] font-mono text-cyan-300 font-bold uppercase tracking-wider relative z-10 mt-0.5">SHIELDED</span>
                    </div>
                    <div class="truncate">
                      <div class="text-xs font-bold text-white truncate flex items-center space-x-1.5">
                        <span id="selectedFileName">medical_xray_0004.jpg</span>
                        <span class="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-600/60 font-bold">Zero-Pixel Shield</span>
                      </div>
                      <div class="text-[10px] text-cyan-400 font-mono font-semibold" id="selectedFileSize">49.5 KB | Protected in Local RAM</div>
                      <div class="text-[9.5px] text-slate-400 font-mono flex items-center space-x-1 mt-0.5">
                        <svg class="w-3 h-3 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                        <span class="truncate">Raw pixels withheld &bull; Only 512-D vector extracted</span>
                      </div>
                    </div>
                  </div>"""

# 2. Add Faculty Demo Test Dataset Selector above presets
old_presets_header = """            <!-- Colorful Domain Presets with Rich Thumbnail Images -->
            <div class="space-y-2.5 pt-1">
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-bold">Quick Test Query Presets:</span>
                <span class="text-[10px] text-cyan-400 font-mono font-semibold">1-Click Test & Search</span>
              </div>"""

new_presets_header = """            <!-- Faculty Demo: Dedicated Test Dataset Selector -->
            <div class="p-3.5 rounded-xl bg-gradient-to-r from-slate-900/95 via-indigo-950/40 to-slate-900/95 border border-cyan-500/40 space-y-2 shadow-lg">
              <div class="flex items-center justify-between text-xs">
                <span class="text-white font-bold flex items-center space-x-1.5 font-display">
                  <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                  <span>Faculty Demo Test Dataset</span>
                </span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-600/60 shadow-sm">48 Curated Images</span>
              </div>
              <div class="text-[11px] text-slate-300">
                Choose any pre-segregated test image from <span class="font-mono text-cyan-300 bg-slate-950 px-1 py-0.5 rounded border border-slate-800">test_dataset/</span> to demo live search to Mam:
              </div>
              <select id="testDatasetSelect" onchange="loadFromTestDataset(this.value)" class="w-full bg-[#050811] text-xs text-cyan-300 border border-cyan-600/70 rounded-lg px-2.5 py-2 outline-none cursor-pointer font-mono font-semibold shadow-inner focus:border-cyan-400 transition">
                <option value="">-- Click to Select a Demo Test Image --</option>
                <optgroup label="🏥 01 Medical (Private Domain)">
                  <option value="/test_dataset/01_Medical/test_medical_xray_05.jpg">test_medical_xray_05.jpg (Chest Radiograph - Thoracic)</option>
                  <option value="/test_dataset/01_Medical/test_medical_xray_10.jpg">test_medical_xray_10.jpg (Pulmonary Radiograph)</option>
                  <option value="/test_dataset/01_Medical/test_medical_mri_03.jpg">test_medical_mri_03.jpg (Brain Magnetic Resonance MRI)</option>
                  <option value="/test_dataset/01_Medical/test_medical_ct_02.jpg">test_medical_ct_02.jpg (Thoracic Computed Tomography CT)</option>
                </optgroup>
                <optgroup label="👤 02 Biometrics (Strict Private Domain)">
                  <option value="/test_dataset/02_Biometrics/test_biometrics_faces_01.jpg">test_biometrics_faces_01.jpg (Facial Biometric Portrait)</option>
                  <option value="/test_dataset/02_Biometrics/test_biometrics_iris_03.jpg">test_biometrics_iris_03.jpg (High-Res Iris Texture Scan)</option>
                  <option value="/test_dataset/02_Biometrics/test_biometrics_fingerprints_02.jpg">test_biometrics_fingerprints_02.jpg (Dactyloscopic Fingerprint Whorl)</option>
                </optgroup>
                <optgroup label="🚗 03 Vehicles (Public Domain)">
                  <option value="/test_dataset/03_Vehicles/test_vehicles_cars_01.jpg">test_vehicles_cars_01.jpg (Passenger Automobile)</option>
                  <option value="/test_dataset/03_Vehicles/test_vehicles_commercial_02.jpg">test_vehicles_commercial_02.jpg (Commercial Transport Truck)</option>
                </optgroup>
                <optgroup label="🌲 04 Nature (Public Domain)">
                  <option value="/test_dataset/04_Nature/test_nature_general_01.jpg">test_nature_general_01.jpg (Aurora Borealis Night Sky)</option>
                  <option value="/test_dataset/04_Nature/test_nature_landscapes_02.jpg">test_nature_landscapes_02.jpg (Mountain Alpine Landscape)</option>
                </optgroup>
              </select>
            </div>

            <!-- Colorful Domain Presets with Domain Badges -->
            <div class="space-y-2.5 pt-1">
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-bold">Quick 1-Click Domain Presets:</span>
                <span class="text-[10px] text-cyan-400 font-mono font-semibold">Instant Search</span>
              </div>"""

# 3. JS FileReader removal (Zero pixel rendering)
old_js_reader = """      // Render preview in local browser memory buffer
      const reader = new FileReader();
      reader.onload = function(evt) {
        const previewImg = document.getElementById('queryImagePreview');
        if (previewImg) previewImg.src = evt.target.result;
      };
      reader.readAsDataURL(file);"""

new_js_reader = """      // ZERO-PIXEL INVARIANT: Raw query image pixels are NEVER converted to dataURL or rendered on screen!
      // The image binary is processed in local browser memory strictly for feature extraction."""

# 4. Add loadFromTestDataset function
old_sample_preset_fn = """    async function loadSamplePreset(cat) {"""

new_test_dataset_fn = """    async function loadFromTestDataset(url) {
      if (!url) return;
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("Could not load test image from " + url);
        const blob = await res.blob();
        const fileName = url.split('/').pop();
        const file = new File([blob], fileName, { type: blob.type || "image/jpeg" });
        processSelectedFile(file);
        setTimeout(() => runContentFreeSearch(), 300);
      } catch (err) {
        showToast("Test query load failed: " + err.message);
      }
    }

    async function loadSamplePreset(cat) {"""

# Replace in html
norm_html = html.replace("\r\n", "\n")

applied = 0
if old_preview_block.replace("\r\n", "\n") in norm_html:
    norm_html = norm_html.replace(old_preview_block.replace("\r\n", "\n"), new_shield_block.replace("\r\n", "\n"), 1)
    applied += 1
    print("1. Replaced preview thumbnail with zero-pixel shield.")
else:
    print("WARNING: Could not find old_preview_block")

if old_presets_header.replace("\r\n", "\n") in norm_html:
    norm_html = norm_html.replace(old_presets_header.replace("\r\n", "\n"), new_presets_header.replace("\r\n", "\n"), 1)
    applied += 1
    print("2. Added Faculty Demo test dataset selector.")
else:
    print("WARNING: Could not find old_presets_header")

if old_js_reader.replace("\r\n", "\n") in norm_html:
    norm_html = norm_html.replace(old_js_reader.replace("\r\n", "\n"), new_js_reader.replace("\r\n", "\n"), 1)
    applied += 1
    print("3. Removed JS FileReader pixel rendering.")
else:
    print("WARNING: Could not find old_js_reader")

if old_sample_preset_fn.replace("\r\n", "\n") in norm_html:
    norm_html = norm_html.replace(old_sample_preset_fn.replace("\r\n", "\n"), new_test_dataset_fn.replace("\r\n", "\n"), 1)
    applied += 1
    print("4. Added loadFromTestDataset JS function.")
else:
    print("WARNING: Could not find old_sample_preset_fn")

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(norm_html)

print(f"Update complete! {applied}/4 changes successfully applied to frontend/index.html")
