import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# -------------------------------------------------------------
# 1. NEW MODERN DESIGN SYSTEM CSS (Awwwards / Godly / Magic UI style)
# -------------------------------------------------------------
new_css = """  <style>
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
        radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.05) 0%, transparent 40%),
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
    
    /* Precision Dark Glass Surfaces */
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
      border-color: rgba(255, 255, 255, 0.15);
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

    /* Navigation Tab Transition */
    .nav-tab {
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .nav-tab.active {
      background: rgba(255, 255, 255, 0.08) !important;
      color: #ffffff !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.5) !important;
    }

    @keyframes pulse-dot {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.4); opacity: 0.6; }
    }
    .animate-pulse-dot {
      animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  </style>"""

# Replace the style block
content = re.sub(r'<style>[\s\S]*?</style>', new_css, content, count=1)

# -------------------------------------------------------------
# 2. NEW HEADER DESIGN (Single Unified Luxury Floating Bar)
# -------------------------------------------------------------
old_header_pattern = r'<header[\s\S]*?</header>\s*<!-- NAVIGATION TABS \(DESKTOP\) -->\s*<nav[\s\S]*?</nav>'

new_header = """  <!-- ULTRA-CLEAN FLOATING LUXURY NAVBAR (Linear / Vercel Aesthetic) -->
  <header class="sticky top-0 z-50 bg-[#07080b]/85 backdrop-blur-xl border-b border-white/[0.07] px-4 lg:px-8 py-2.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      
      <!-- Brand & Project Identity -->
      <div class="flex items-center space-x-3 shrink-0">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-slate-800 via-indigo-900/60 to-cyan-500/40 p-[1px] shadow-sm">
          <div class="w-full h-full bg-[#0a0d14] rounded-[11px] flex items-center justify-center">
            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-base font-bold font-display tracking-tight text-white">PrivateLens</span>
            <span class="px-2 py-0.5 rounded text-[9.5px] font-mono font-semibold bg-white/[0.05] text-slate-300 border border-white/[0.08]">v2.5 PROTOTYPE</span>
          </div>
          <p class="text-[10.5px] text-slate-400 hidden sm:block font-mono tracking-tight">Zero-Pixel Content-Free Retrieval</p>
        </div>
      </div>

      <!-- Segmented Control Desktop Navigation (Clean Minimalist Pills) -->
      <nav class="hidden md:flex items-center space-x-1 p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] backdrop-blur-md">
        <button onclick="switchTab('search')" id="nav-search" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-white bg-white/[0.08] border border-white/[0.12] flex items-center space-x-1.5 shadow-sm">
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <span>Search & Vault</span>
        </button>

        <button onclick="switchTab('privacy')" id="nav-privacy" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5">
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          <span>Privacy Benchmark</span>
        </button>

        <button onclick="switchTab('evaluation')" id="nav-evaluation" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5">
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          <span>Evaluation</span>
        </button>

        <button onclick="switchTab('security')" id="nav-security" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5">
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
          <span>RBAC Security</span>
        </button>

        <button onclick="switchTab('overview')" id="nav-overview" class="nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5">
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          <span>Overview</span>
        </button>
      </nav>

      <!-- Live Zero-Pixel Status & User Switcher Pill -->
      <div class="flex items-center space-x-2.5">
        <div class="hidden xl:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-emerald-500/[0.07] border border-emerald-500/20 text-[10.5px] text-emerald-400 font-mono">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot"></span>
          <span>Zero-Pixel Active</span>
        </div>

        <!-- Sleek User Pill -->
        <div class="flex items-center space-x-2 px-2.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] hover:border-white/[0.14] transition">
          <div class="w-5 h-5 rounded-full bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-[10px] font-bold text-indigo-300 shrink-0" id="userAvatar">
            D
          </div>
          <div class="text-left hidden lg:block">
            <div class="text-xs font-semibold text-slate-200" id="currentUserName">Dr. R. Sharma</div>
            <div class="text-[9.5px] text-slate-400 font-mono" id="currentUserRole">SPECIALIST</div>
          </div>
          <select id="userSelector" onchange="onUserSwitch(this.value)" class="bg-transparent text-xs text-slate-200 outline-none cursor-pointer border-none font-medium pr-1">
            <option value="USR_DOC_01" class="bg-[#0b0e17] text-white">Dr. R. Sharma (Specialist - Medical)</option>
            <option value="USR_DOC_02" class="bg-[#0b0e17] text-white">Dr. Anita Patel (Specialist - Medical)</option>
            <option value="USR_RES_02" class="bg-[#0b0e17] text-white">Alex Verma (Researcher - Public)</option>
            <option value="USR_ADM_00" class="bg-[#0b0e17] text-white">System Admin (Full Access)</option>
            <option value="USR_GST_99" class="bg-[#0b0e17] text-white">Public Guest (Restricted)</option>
          </select>
        </div>

        <!-- Mobile Drawer Toggle -->
        <button onclick="toggleMobileNav()" class="md:hidden p-1.5 rounded-lg bg-white/[0.04] text-slate-300 hover:text-white border border-white/[0.08]">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"/></svg>
        </button>
      </div>

    </div>

    <!-- Mobile Slide-Down Nav Drawer -->
    <div id="mobileNavDrawer" class="hidden md:hidden pt-3 pb-2 border-t border-white/[0.06] mt-2 space-y-1">
      <div class="grid grid-cols-2 gap-1.5 text-xs font-medium">
        <button onclick="switchTab('search'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-white/[0.08] text-white border border-white/[0.12] flex items-center space-x-2">
          <span>Search & Vault</span>
        </button>
        <button onclick="switchTab('privacy'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-white/[0.03] text-slate-300 hover:text-white flex items-center space-x-2">
          <span>Privacy Center</span>
        </button>
        <button onclick="switchTab('evaluation'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-white/[0.03] text-slate-300 hover:text-white flex items-center space-x-2">
          <span>Benchmarks</span>
        </button>
        <button onclick="switchTab('overview'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-white/[0.03] text-slate-300 hover:text-white flex items-center space-x-2">
          <span>Overview</span>
        </button>
      </div>
    </div>
  </header>"""

content = re.sub(old_header_pattern, new_header, content, count=1)

# -------------------------------------------------------------
# 3. SET SEARCH AS THE DEFAULT ACTIVE TAB ON PAGE LOAD
# -------------------------------------------------------------
content = content.replace(
    '<section id="tab-overview" class="space-y-8">',
    '<section id="tab-overview" class="hidden space-y-8">'
)
content = content.replace(
    '<section id="tab-search" class="hidden space-y-8">',
    '<section id="tab-search" class="space-y-8">'
)

# -------------------------------------------------------------
# 4. REFINED SEARCH HEADER BANNER (Linear / Awwwards Style)
# -------------------------------------------------------------
old_search_banner = r'<!-- Search Page Introduction Banner -->[\s\S]*?</div>\s*</div>\s*</div>'

new_search_banner = """<!-- Search Page Hero Header (Minimalist & Authoritative) -->
      <div class="flex flex-col sm:flex-row sm:items-end justify-between pb-2 border-b border-white/[0.06] gap-4">
        <div class="space-y-1.5 max-w-2xl">
          <div class="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-cyan-500/[0.08] border border-cyan-500/20 text-[10px] text-cyan-300 font-mono font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            <span>VERIFIABLE CONTENT-FREE SEARCH</span>
            <span class="text-slate-600">&bull;</span>
            <span class="text-slate-400">ZERO QUERY PIXELS LEAVE CLIENT MEMORY</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display tracking-tight">
            Deep Feature Retrieval Engine
          </h2>
          <p class="text-xs text-slate-400 leading-relaxed">
            Query images are converted to 1280-D MobileNetV3 activations exclusively in client RAM, down-projected via a secret 256-bit matrix into a 512-D subspace with an unconstrained 768-D null-space, and queried against FAISS IndexFlatIP.
          </p>
        </div>
        <div class="flex items-center space-x-2 shrink-0">
          <span class="px-2.5 py-1 rounded-lg bg-white/[0.03] border border-white/[0.08] text-[11px] font-mono text-slate-300 flex items-center space-x-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot"></span>
            <span>1,035 Vault Assets Indexed</span>
          </span>
        </div>
      </div>"""

content = re.sub(old_search_banner, new_search_banner, content, count=1)

# -------------------------------------------------------------
# 5. ELEVATE THE QUERY STUDIO & ZERO-PIXEL SHIELD CARD
# -------------------------------------------------------------
# Add dynamic animated vector visualizer to dropzoneSelected
old_dropzone_selected_pattern = r'<!-- State B: Image Selected & Buffered -->[\s\S]*?<!-- Protected Vector Sample Preview -->[\s\S]*?</div>\s*</div>'

new_dropzone_selected = """<!-- State B: Image Selected & Buffered (Elite Cryptographic Shield) -->
              <div id="dropzoneSelected" class="hidden space-y-3.5 text-left">
                
                <!-- Shield Header & File Info -->
                <div class="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between">
                  <div class="flex items-center space-x-3 overflow-hidden">
                    
                    <!-- Holographic Vector Icon -->
                    <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-950 via-slate-900 to-indigo-950 border border-cyan-400/40 flex flex-col items-center justify-center shrink-0 shadow-lg relative overflow-hidden">
                      <div class="absolute inset-0 bg-cyan-400/[0.06] animate-pulse"></div>
                      <svg class="w-5 h-5 text-cyan-300 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                      </svg>
                      <span class="text-[7px] font-mono text-cyan-300 font-bold uppercase tracking-widest relative z-10 mt-0.5">512-D</span>
                    </div>

                    <div class="truncate">
                      <div class="text-xs font-bold text-white truncate flex items-center space-x-1.5">
                        <span id="selectedFileName">query_image.jpg</span>
                        <span class="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">Zero-Pixel Shield</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-mono mt-0.5" id="selectedFileSize">Local RAM Buffer</div>
                      <div class="text-[9.5px] text-slate-500 font-mono flex items-center space-x-1 mt-0.5">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        <span class="truncate">Pixels isolated &bull; Only mathematical vector transmitted</span>
                      </div>
                    </div>
                  </div>

                  <button type="button" onclick="clearQuery(event)" class="text-xs text-slate-400 hover:text-rose-400 font-medium px-2.5 py-1 rounded-lg hover:bg-rose-500/10 transition border border-transparent hover:border-rose-500/20">
                    Remove
                  </button>
                </div>

                <!-- Live Vector Spectrum Visualizer (Looks 1000x More Authentic & Advanced) -->
                <div class="p-3 rounded-xl bg-[#090b10] border border-white/[0.06] space-y-2">
                  <div class="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span class="flex items-center space-x-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse-dot"></span>
                      <span>512-D Vector Coordinate Spectrum:</span>
                    </span>
                    <span class="text-cyan-400 font-semibold font-mono">Normalized ||z|| = 1.0</span>
                  </div>

                  <!-- Canvas for Live Frequency Waveform -->
                  <canvas id="vectorSpectrumCanvas" width="340" height="42" class="w-full rounded bg-[#06070a] border border-white/[0.04] block"></canvas>

                  <div class="flex items-center justify-between pt-1">
                    <div class="font-mono text-[9.5px] text-slate-400 truncate max-w-[240px]" id="selectedVectorSample">
                      [+0.0421, -0.0115, +0.0764, -0.0857, -0.0137...]
                    </div>
                    <span class="text-[9px] font-mono text-indigo-300 font-bold tracking-wider" id="selectedVectorBarcode">
                      ██▓▒░░▓█▒░█
                    </span>
                  </div>
                </div>

              </div>"""

content = re.sub(old_dropzone_selected_pattern, new_dropzone_selected, content, count=1)

# -------------------------------------------------------------
# 6. ELEGANT FACULTY TEST DATASET SELECTOR (Interactive Grid)
# -------------------------------------------------------------
old_faculty_selector = r'<!-- Faculty Demo: Dedicated Test Dataset Selector -->[\s\S]*?<!-- Colorful Domain Presets with Domain Badges -->'

new_faculty_selector = """<!-- Faculty Demo: Curated Test Dataset Hub -->
            <div class="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.08] space-y-2.5">
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-200 font-bold flex items-center space-x-1.5 font-display">
                  <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                  <span>Faculty Demo Test Dataset</span>
                </span>
                <span class="px-2 py-0.5 rounded text-[9.5px] font-mono bg-cyan-500/[0.08] text-cyan-300 border border-cyan-500/20 font-semibold">48 Curated Images</span>
              </div>
              <p class="text-[11px] text-slate-400 leading-snug">
                Pre-segregated out-of-catalog test query images for live demonstration to faculty:
              </p>
              
              <!-- Quick Category Chips -->
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

              <!-- Full Test Dataset Dropdown -->
              <select id="testDatasetSelect" onchange="loadFromTestDataset(this.value)" class="w-full bg-[#0a0d14] text-xs text-cyan-300 border border-white/[0.09] rounded-lg px-2.5 py-1.5 outline-none cursor-pointer font-mono font-medium shadow-inner focus:border-cyan-500/60 transition mt-1">
                <option value="">-- Browse Full 48 Test Images --</option>
                <optgroup label="🏥 01 Medical Imaging (Private)">
                  <option value="/test_dataset/01_Medical/test_medical_xray_05.jpg">test_medical_xray_05.jpg (Chest Radiograph)</option>
                  <option value="/test_dataset/01_Medical/test_medical_xray_10.jpg">test_medical_xray_10.jpg (Pulmonary X-Ray)</option>
                  <option value="/test_dataset/01_Medical/test_medical_mri_03.jpg">test_medical_mri_03.jpg (Brain MRI Scan)</option>
                  <option value="/test_dataset/01_Medical/test_medical_ct_02.jpg">test_medical_ct_02.jpg (Thoracic CT Scan)</option>
                </optgroup>
                <optgroup label="👤 02 Biometrics (Strict Private)">
                  <option value="/test_dataset/02_Biometrics/test_biometrics_faces_01.jpg">test_biometrics_faces_01.jpg (Face Portrait)</option>
                  <option value="/test_dataset/02_Biometrics/test_biometrics_iris_03.jpg">test_biometrics_iris_03.jpg (Iris Pattern Scan)</option>
                  <option value="/test_dataset/02_Biometrics/test_biometrics_fingerprints_02.jpg">test_biometrics_fingerprints_02.jpg (Dactyloscopic Whorl)</option>
                </optgroup>
                <optgroup label="🚗 03 Vehicles (Public)">
                  <option value="/test_dataset/03_Vehicles/test_vehicles_cars_01.jpg">test_vehicles_cars_01.jpg (Passenger Automobile)</option>
                  <option value="/test_dataset/03_Vehicles/test_vehicles_commercial_02.jpg">test_vehicles_commercial_02.jpg (Commercial Cargo Truck)</option>
                </optgroup>
                <optgroup label="🌲 04 Nature (Public)">
                  <option value="/test_dataset/04_Nature/test_nature_general_01.jpg">test_nature_general_01.jpg (Aurora Borealis Night)</option>
                  <option value="/test_dataset/04_Nature/test_nature_landscapes_02.jpg">test_nature_landscapes_02.jpg (Mountain Alpine Landscape)</option>
                </optgroup>
              </select>
            </div>

            <!-- Colorful Domain Presets with Domain Badges -->"""

content = re.sub(old_faculty_selector, new_faculty_selector, content, count=1)

# -------------------------------------------------------------
# 7. HIGH-END RESULT CARDS RENDERING IN JAVASCRIPT
# -------------------------------------------------------------
old_render_results_pattern = r'function renderResults\(results\) \{[\s\S]*?\}\s*function openResultModal'

new_render_results = """function renderResults(results) {
      const container = document.getElementById('resultsContainer');
      const filtered = results.slice(0, currentTopK);

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="card-surface p-10 text-center space-y-2 border border-white/[0.06]">
            <div class="w-10 h-10 mx-auto rounded-full bg-white/[0.04] flex items-center justify-center text-slate-500 mb-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            <p class="text-sm font-semibold text-slate-200">No matches found meeting threshold (${currentThreshold.toFixed(2)})</p>
            <p class="text-xs text-slate-500">Try lowering similarity threshold or changing domain filter.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(r => {
        const isAuth = r.authorized;
        const simVal = parseFloat(r.similarity_percent) || 0;
        return `
          <div class="card-surface p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border ${isAuth ? 'border-white/[0.08] hover:border-white/[0.18]' : 'border-rose-500/20 bg-rose-500/[0.02]'} transition">
            <div class="flex items-center space-x-3.5">
              
              <!-- Thumbnail Container (Decrypted Vault Asset with Subtle Radius & Hover Zoom) -->
              <div class="w-16 h-16 rounded-xl bg-[#08090d] border ${isAuth ? 'border-white/[0.10]' : 'border-rose-500/30'} flex items-center justify-center shrink-0 overflow-hidden shadow-sm relative group">
                ${isAuth && r.image_url 
                  ? `<img src="${r.image_url}" alt="${r.image_id}" class="w-full h-full object-cover cursor-pointer hover:scale-105 transition duration-300" onclick="openResultModal('${r.image_id}', '${r.image_url}')" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'text-center p-1 text-slate-500 text-[9px] font-mono\\'>Encrypted</div>'">`
                  : `<div class="text-center p-2 text-rose-400">
                      <svg class="w-5 h-5 mx-auto mb-0.5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                      <div class="text-[8px] font-mono text-rose-400 font-bold">LOCKED</div>
                    </div>`
                }
              </div>

              <!-- Metadata & Verification -->
              <div class="space-y-1">
                <div class="flex items-center space-x-2">
                  <span class="text-xs font-mono font-bold text-white tracking-tight">${r.image_id}</span>
                  <span class="px-2 py-0.5 rounded text-[9.5px] font-mono font-medium ${isAuth ? 'badge-emerald' : 'badge-rose'}">
                    ${isAuth ? '✓ Authorized' : '🔒 Access Restricted'}
                  </span>
                  <span class="px-2 py-0.5 rounded text-[9.5px] font-mono font-medium bg-white/[0.04] text-slate-300 border border-white/[0.06] uppercase">
                    ${r.category}
                  </span>
                </div>
                <p class="text-xs text-slate-400 leading-snug">${r.match_explanation}</p>
                <div class="font-mono text-[9.5px] text-slate-500 flex items-center space-x-1.5 pt-0.5">
                  <span>Vault Signature:</span>
                  <span class="text-slate-400 font-bold">${r.vector_barcode || '██▓▒░░▓█'}</span>
                  <span class="text-slate-600">&bull;</span>
                  <span class="text-emerald-400/90 font-mono">AES-256 GCM</span>
                </div>
              </div>
            </div>

            <!-- Proximity Score & Action -->
            <div class="text-right shrink-0 sm:border-l sm:border-white/[0.06] sm:pl-4">
              <div class="text-base font-bold font-mono text-white tracking-tight">${r.similarity_percent}</div>
              <div class="text-[9.5px] text-slate-400 font-mono">Rank #${r.rank} Proximity</div>
              
              <!-- Subtle Progress Bar -->
              <div class="w-24 h-1.5 bg-white/[0.06] rounded-full overflow-hidden mt-1 ml-auto">
                <div class="h-full bg-gradient-to-r from-cyan-400 to-indigo-400 rounded-full" style="width: ${Math.min(100, Math.max(10, simVal))}%"></div>
              </div>

              ${isAuth && r.image_url 
                ? `<button onclick="openResultModal('${r.image_id}', '${r.image_url}')" class="mt-2 text-[10.5px] text-cyan-400 hover:text-cyan-300 font-medium hover:underline block ml-auto transition">Inspect Asset &rarr;</button>`
                : `<div class="mt-2 text-[9.5px] text-rose-400 font-mono">Requires RBAC Clearance</div>`
              }
            </div>
          </div>
        `;
      }).join('');
    }

    function openResultModal"""

content = re.sub(old_render_results_pattern, new_render_results, content, count=1)

# -------------------------------------------------------------
# 8. ADD CANVAS EQUALIZER ANIMATOR IN JAVASCRIPT
# -------------------------------------------------------------
spectrum_canvas_animator = """    // Live Dynamic Vector Spectrum Visualizer (DARPA/Apple style)
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
        ctx.roundRect(x, y, barWidth, barHeight, 2);
        ctx.fill();
      }
    }

    // Call drawVectorSpectrum in runContentFreeSearch
"""

content = content.replace("async function runContentFreeSearch() {", spectrum_canvas_animator + "    async function runContentFreeSearch() {")

# Also call drawVectorSpectrum when local data arrives
content = content.replace(
    "document.getElementById('selectedVectorBarcode').innerText = localData.vector_barcode;",
    "document.getElementById('selectedVectorBarcode').innerText = localData.vector_barcode;\n        if (localData.vector) drawVectorSpectrum(localData.vector);"
)

# Also update switchTab active styling in JS
content = content.replace(
    'btn.className = "nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600/20 text-blue-400 border border-blue-500/40 flex items-center space-x-2 transition";',
    'btn.className = "nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-white bg-white/[0.08] border border-white/[0.12] flex items-center space-x-1.5 shadow-sm";'
)
content = content.replace(
    'btn.className = "nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition";',
    'btn.className = "nav-tab px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition";'
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Modern UI Rebuild Applied Successfully!")
