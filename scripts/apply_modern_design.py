import os

index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. NEW ELEVATED MODERN CSS (Linear + Vercel + Magic UI + Raycast)
css_start = text.find("<style>")
css_end = text.find("</style>") + len("</style>")

modern_css = """<style>
    :root {
      --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    
    body {
      font-family: var(--font-body);
      background-color: #07080b;
      color: #f1f5f9;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 50% -5%, rgba(56, 189, 248, 0.10) 0%, transparent 50%),
        radial-gradient(circle at 90% 15%, rgba(99, 102, 241, 0.05) 0%, transparent 40%),
        linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
      background-attachment: fixed;
    }
    
    h1, h2, h3, h4, .font-display {
      font-family: var(--font-display);
      letter-spacing: -0.025em;
    }
    
    .font-mono {
      font-family: var(--font-mono);
    }
    
    /* Precision Dark Glass Surfaces (Linear / Vercel style) */
    .card-surface {
      background: rgba(13, 16, 24, 0.72);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 1rem;
      box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.04);
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .card-surface:hover {
      border-color: rgba(255, 255, 255, 0.14);
      box-shadow: 0 12px 36px -6px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .card-surface-elevated {
      background: rgba(18, 22, 34, 0.85);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(255, 255, 255, 0.10);
      border-radius: 1.125rem;
      box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.6);
    }

    .card-surface-interactive {
      background: rgba(13, 16, 24, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 0.875rem;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .card-surface-interactive:hover {
      background: rgba(22, 27, 40, 0.85);
      border-color: rgba(99, 102, 241, 0.45);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    }

    /* Refined Monochromatic & Semantic Badges */
    .badge-cyan {
      background: rgba(6, 182, 212, 0.09);
      color: #38bdf8;
      border: 1px solid rgba(6, 182, 212, 0.22);
    }
    .badge-blue {
      background: rgba(59, 130, 246, 0.09);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.22);
    }
    .badge-emerald {
      background: rgba(16, 185, 129, 0.09);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.22);
    }
    .badge-amber {
      background: rgba(245, 158, 11, 0.09);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.22);
    }
    .badge-rose {
      background: rgba(244, 63, 94, 0.09);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.22);
    }
    .badge-purple {
      background: rgba(168, 85, 247, 0.09);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.22);
    }

    /* Dropzone Micro-Grid & Hover */
    .dropzone-glow {
      border: 1.5px dashed rgba(255, 255, 255, 0.14);
      background: rgba(10, 13, 20, 0.5);
      transition: all 0.22s ease-in-out;
    }
    .dropzone-glow:hover, .dropzone-glow.drag-over {
      border-color: #38bdf8;
      background: rgba(56, 189, 248, 0.04);
      box-shadow: 0 0 25px -4px rgba(56, 189, 248, 0.15);
    }

    /* Range Slider */
    input[type=range] {
      -webkit-appearance: none;
      background: #171b26;
      height: 5px;
      border-radius: 3px;
      outline: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #38bdf8;
      cursor: pointer;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
      transition: transform 0.1s ease;
    }
    input[type=range]::-webkit-slider-thumb:hover {
      transform: scale(1.15);
      background: #7dd3fc;
    }

    /* Clean Subtle Scrollbars */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: #07080b;
    }
    ::-webkit-scrollbar-thumb {
      background: #1e2433;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #334155;
    }

    .nav-tab {
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes pulse-dot {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.4); opacity: 0.6; }
    }
    .animate-pulse-dot {
      animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  </style>"""

text = text[:css_start] + modern_css + text[css_end:]

# 2. Make SEARCH the default tab on initial load
text = text.replace(
    '<section id="tab-overview" class="space-y-8">',
    '<section id="tab-overview" class="hidden space-y-8">'
)
text = text.replace(
    '<section id="tab-search" class="hidden space-y-8">',
    '<section id="tab-search" class="space-y-8">'
)

# Also update the desktop nav initial active tab styling
text = text.replace(
    'id="nav-overview" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600/20 text-blue-400 border border-blue-500/40 flex items-center space-x-2 transition"',
    'id="nav-overview" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition"'
)
text = text.replace(
    'id="nav-search" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition"',
    'id="nav-search" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-white bg-white/[0.08] border border-white/[0.12] flex items-center space-x-1.5 shadow-sm transition"'
)

# Update other nav buttons to clean styling
for tab in ['evaluation', 'privacy', 'security', 'index', 'settings']:
    text = text.replace(
        f'id="nav-{tab}" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition"',
        f'id="nav-{tab}" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition"'
    )

# 3. Add Canvas Spectrum Visualizer inside dropzoneSelected
canvas_markup = """                <!-- Live Vector Spectrum Visualizer (DARPA/Apple Cybersecurity style) -->
                <div class="p-3 rounded-xl bg-[#090b10] border border-white/[0.06] space-y-2">
                  <div class="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span class="flex items-center space-x-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse-dot"></span>
                      <span>512-D Coordinate Spectrum Amplitude:</span>
                    </span>
                    <span class="text-cyan-400 font-semibold font-mono">||z|| = 1.0 (Unit L2)</span>
                  </div>

                  <canvas id="vectorSpectrumCanvas" width="340" height="38" class="w-full rounded bg-[#06070a] border border-white/[0.04] block"></canvas>

                  <div class="flex items-center justify-between pt-0.5">
                    <div class="font-mono text-[9.5px] text-slate-400 truncate max-w-[230px]" id="selectedVectorSample">
                      [+0.0421, -0.0115, +0.0764, -0.0857, -0.0137...]
                    </div>
                    <span class="text-[9px] font-mono text-indigo-300 font-bold tracking-wider" id="selectedVectorBarcode">
                      ██▓▒░░▓█▒░█
                    </span>
                  </div>
                </div>"""

# Replace the old static text vector sample in dropzoneSelected
old_sample_box = text[text.find('<!-- Protected Vector Sample Preview -->'):text.find('</div>\n\n            </div>\n\n            <!-- Faculty Demo: Dedicated Test Dataset Selector -->')]
if old_sample_box:
    text = text.replace(old_sample_box, canvas_markup)

# 4. Add dynamic category pill buttons to Faculty Demo Test Dataset Selector
old_demo_select_area = """              <div class="text-[11px] text-slate-300">
                Choose any pre-segregated test image from <span class="font-mono text-cyan-300 bg-slate-950 px-1 py-0.5 rounded border border-slate-800">test_dataset/</span> to demo live search to Mam:
              </div>
              <select id="testDatasetSelect" """

new_demo_select_area = """              <p class="text-[11px] text-slate-400 leading-snug">
                Pre-segregated out-of-catalog test images from <code class="text-cyan-300 font-mono text-[10.5px]">test_dataset/</code> for presentation to faculty:
              </p>
              
              <!-- 1-Click Fast Category Pills -->
              <div class="grid grid-cols-4 gap-1.5 pt-0.5">
                <button type="button" onclick="loadFromTestDataset('/test_dataset/01_Medical/test_medical_xray_05.jpg')" class="p-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-cyan-500/40 text-center transition group">
                  <div class="text-[11px]">🩻</div>
                  <div class="text-[9.5px] font-semibold text-slate-300 group-hover:text-cyan-300 truncate mt-0.5">X-Ray 05</div>
                </button>
                <button type="button" onclick="loadFromTestDataset('/test_dataset/02_Biometrics/test_biometrics_faces_01.jpg')" class="p-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-fuchsia-500/40 text-center transition group">
                  <div class="text-[11px]">👤</div>
                  <div class="text-[9.5px] font-semibold text-slate-300 group-hover:text-fuchsia-300 truncate mt-0.5">Face 01</div>
                </button>
                <button type="button" onclick="loadFromTestDataset('/test_dataset/03_Vehicles/test_vehicles_cars_01.jpg')" class="p-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-amber-500/40 text-center transition group">
                  <div class="text-[11px]">🚗</div>
                  <div class="text-[9.5px] font-semibold text-slate-300 group-hover:text-amber-300 truncate mt-0.5">Car 01</div>
                </button>
                <button type="button" onclick="loadFromTestDataset('/test_dataset/04_Nature/test_nature_general_01.jpg')" class="p-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-emerald-500/40 text-center transition group">
                  <div class="text-[11px]">🌲</div>
                  <div class="text-[9.5px] font-semibold text-slate-300 group-hover:text-emerald-300 truncate mt-0.5">Aurora 01</div>
                </button>
              </div>

              <select id="testDatasetSelect" """

if old_demo_select_area in text:
    text = text.replace(old_demo_select_area, new_demo_select_area)

# 5. Add vector spectrum animator in JS
animator_js = """    // Live Dynamic Vector Spectrum Visualizer
    function drawVectorSpectrum(vectorData) {
      const canvas = document.getElementById('vectorSpectrumCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const numBars = 32;
      const barWidth = (w / numBars) - 2;
      const step = Math.floor(vectorData.length / numBars) || 1;

      for (let i = 0; i < numBars; i++) {
        const val = vectorData[i * step] || (Math.sin(i * 0.3) * 0.08);
        const absVal = Math.min(1.0, Math.abs(val) * 12);
        const barHeight = Math.max(3, absVal * (h - 6));
        const x = i * (barWidth + 2);
        const y = h - barHeight - 2;

        const grad = ctx.createLinearGradient(0, y, 0, h);
        if (val >= 0) {
          grad.addColorStop(0, '#38bdf8');
          grad.addColorStop(1, '#6366f1');
        } else {
          grad.addColorStop(0, '#818cf8');
          grad.addColorStop(1, '#a855f7');
        }
        ctx.fillStyle = grad;
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(x, y, barWidth, barHeight, 2);
        else ctx.rect(x, y, barWidth, barHeight);
        ctx.fill();
      }
    }
"""

if "function drawVectorSpectrum" not in text:
    text = text.replace("async function runContentFreeSearch() {", animator_js + "\n    async function runContentFreeSearch() {")

# Call drawVectorSpectrum when vectorData arrives
target_hook = "document.getElementById('selectedVectorBarcode').innerText = localData.vector_barcode;"
if target_hook in text and "drawVectorSpectrum(localData.vector)" not in text:
    text = text.replace(
        target_hook,
        target_hook + "\n        if (localData.vector) drawVectorSpectrum(localData.vector);"
    )

with open(index_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Modern UI Update Completed Successfully!")
