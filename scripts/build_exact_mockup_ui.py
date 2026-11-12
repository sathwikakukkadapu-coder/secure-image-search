import os
import re

html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")

# Read the existing file to preserve the full JavaScript logic and modal code
with open(html_path, "r", encoding="utf-8") as f:
    orig = f.read()

# Extract the existing JavaScript block from orig
js_match = re.search(r'(<script>[\s\S]*?</script>\s*</body>)', orig)
if not js_match:
    raise Exception("Could not find script block in index.html")
orig_scripts = js_match.group(1)

# Ensure the JS has the wave animator and test dataset loader
# Build the complete, pixel-perfect new HTML structure
new_html = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PrivateLens v2.5 | Privacy-Preserving Image Retrieval Platform</title>
  
  <!-- Modern Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  
  <style>
    :root {
      --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    
    body {
      font-family: var(--font-body);
      background-color: #070814;
      color: #f1f5f9;
      overflow-x: hidden;
    }
    
    h1, h2, h3, h4, .font-display {
      font-family: var(--font-display);
      letter-spacing: -0.025em;
    }
    
    .font-mono {
      font-family: var(--font-mono);
    }

    /* Moving Cyber Wave Background Canvas */
    #ambientWaveCanvas {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 0;
    }

    /* Futuristic Dark Glass Cards */
    .glass-panel {
      background: linear-gradient(135deg, rgba(17, 21, 39, 0.78) 0%, rgba(11, 14, 28, 0.88) 100%);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(99, 102, 241, 0.18);
      border-radius: 1.25rem;
      box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .glass-panel:hover {
      border-color: rgba(139, 92, 246, 0.35);
      box-shadow: 0 16px 42px -6px rgba(0, 0, 0, 0.75), 0 0 24px -6px rgba(124, 58, 237, 0.2);
    }

    .glass-panel-elevated {
      background: linear-gradient(135deg, rgba(23, 28, 52, 0.82) 0%, rgba(13, 17, 34, 0.92) 100%);
      backdrop-filter: blur(28px);
      border: 1px solid rgba(139, 92, 246, 0.28);
      border-radius: 1.25rem;
      box-shadow: 0 16px 40px -6px rgba(0, 0, 0, 0.7), 0 0 35px -8px rgba(99, 102, 241, 0.22);
    }

    /* Active Left Sidebar Navigation Pill */
    .sidebar-item-active {
      background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
      color: #ffffff;
      box-shadow: 0 4px 18px -2px rgba(124, 58, 237, 0.5);
    }

    /* Dropzone Hover Glow */
    .dropzone-cyber {
      border: 1.5px dashed rgba(99, 102, 241, 0.4);
      background: rgba(10, 13, 28, 0.55);
      transition: all 0.22s ease-in-out;
    }
    .dropzone-cyber:hover, .dropzone-cyber.drag-over {
      border-color: #38bdf8;
      background: rgba(56, 189, 248, 0.06);
      box-shadow: 0 0 25px -4px rgba(56, 189, 248, 0.25);
    }

    /* Glowing 3D Hero Podium */
    .hero-podium {
      position: relative;
      perspective: 1000px;
    }
    .hero-card-tilt {
      transform-style: preserve-3d;
      transition: transform 0.4s ease;
    }
    .hero-card-tilt:hover {
      transform: translateY(-6px) rotateY(-4deg) rotateX(4deg);
    }

    /* Range Slider */
    input[type=range] {
      -webkit-appearance: none;
      background: #15192c;
      height: 5px;
      border-radius: 3px;
      outline: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: #38bdf8;
      cursor: pointer;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.7);
      transition: transform 0.1s ease;
    }
    input[type=range]::-webkit-slider-thumb:hover {
      transform: scale(1.2);
      background: #7dd3fc;
    }

    /* Clean Subtle Scrollbars */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: #070814;
    }
    ::-webkit-scrollbar-thumb {
      background: #1c223c;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #313a60;
    }

    /* Smooth Pulse Animation */
    @keyframes pulse-ring {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.05); opacity: 0.4; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    .animate-pulse-ring {
      animation: pulse-ring 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes float-subtle {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-6px); }
    }
    .animate-float {
      animation: float-subtle 4s ease-in-out infinite;
    }
  </style>
</head>
<body class="min-h-screen flex antialiased relative selection:bg-purple-600 selection:text-white">

  <!-- ======================================================== -->
  <!-- 1. MOVING CYBER-WAVE PARTICLES CANVAS (Fluid 60fps Wave)  -->
  <!-- ======================================================== -->
  <canvas id="ambientWaveCanvas"></canvas>

  <!-- ======================================================== -->
  <!-- 2. LEFT SIDEBAR NAVIGATION (Exact Mockup Layout)         -->
  <!-- ======================================================== -->
  <aside class="w-64 xl:w-72 shrink-0 hidden md:flex flex-col justify-between p-5 border-r border-indigo-900/30 bg-[#080a18]/70 backdrop-blur-2xl z-20 sticky top-0 h-screen">
    
    <!-- Top: Brand & Navigation -->
    <div class="space-y-6">
      
      <!-- Brand Logo -->
      <div class="flex items-center space-x-3 px-2">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-400 p-[1.5px] shadow-lg shadow-purple-900/40 shrink-0">
          <div class="w-full h-full bg-[#0a0d1e] rounded-[10px] flex items-center justify-center">
            <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-base font-bold font-display tracking-tight text-white">PrivateLens</span>
            <span class="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-700/60">v2.5</span>
          </div>
          <p class="text-[10px] text-slate-400 font-mono tracking-tight">Privacy-Preserving Retrieval</p>
        </div>
      </div>

      <!-- Vertical Sidebar Nav Links -->
      <nav class="space-y-1.5 text-xs font-semibold">
        <button onclick="switchTab('search')" id="nav-search" class="w-full px-3.5 py-2.5 rounded-xl text-left sidebar-item-active flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <span>Secure Search</span>
        </button>

        <button onclick="switchTab('index')" id="nav-index" class="w-full px-3.5 py-2.5 rounded-xl text-left text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
          <span>Dataset & Vault</span>
        </button>

        <button onclick="switchTab('privacy')" id="nav-privacy" class="w-full px-3.5 py-2.5 rounded-xl text-left text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          <span>Privacy Analysis</span>
        </button>

        <button onclick="switchTab('evaluation')" id="nav-evaluation" class="w-full px-3.5 py-2.5 rounded-xl text-left text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          <span>Retrieval Evaluation</span>
        </button>

        <button onclick="switchTab('security')" id="nav-security" class="w-full px-3.5 py-2.5 rounded-xl text-left text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
          <span>Index & Security</span>
        </button>

        <button onclick="switchTab('settings')" id="nav-settings" class="w-full px-3.5 py-2.5 rounded-xl text-left text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-3 transition">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          <span>Settings</span>
        </button>
      </nav>

    </div>

    <!-- Bottom: 3D Holographic Shield Card & Secure Mode Toggle -->
    <div class="space-y-3">
      
      <!-- 3D Glowing Cyber Shield Container -->
      <div class="p-4 rounded-2xl bg-gradient-to-b from-[#13193a]/80 to-[#0c1026]/90 border border-indigo-500/30 text-center relative overflow-hidden shadow-lg shadow-indigo-950/50">
        <div class="absolute inset-0 bg-gradient-to-t from-cyan-500/10 via-purple-500/10 to-transparent pointer-events-none"></div>
        
        <!-- Glowing Hologram Shield Icon -->
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-purple-600/30 border border-cyan-400/40 flex items-center justify-center relative shadow-lg shadow-cyan-500/20 animate-float">
          <div class="absolute inset-0 rounded-2xl bg-cyan-400/10 animate-pulse-ring"></div>
          <svg class="w-8 h-8 text-cyan-300 drop-shadow-[0_0_12px_rgba(56,189,248,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
        </div>
        
        <div class="mt-2.5">
          <div class="text-[11px] font-bold text-white font-display tracking-tight">Client Privacy Shield</div>
          <p class="text-[9.5px] text-slate-400 font-mono mt-0.5">MobileNetV3 Penultimate Zero-Pixel Isolation</p>
        </div>
      </div>

      <!-- Secure Mode Switcher Pill -->
      <div class="p-2.5 rounded-xl bg-[#0b0e20]/90 border border-indigo-900/40 flex items-center justify-between shadow-sm">
        <div class="flex items-center space-x-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <div>
            <div class="text-[11px] font-bold text-white leading-tight">Secure Mode</div>
            <div class="text-[9px] text-slate-400 font-mono">Encrypted &bull; No Raw Data</div>
          </div>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" checked class="sr-only peer" disabled>
          <div class="w-8 h-4 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-emerald-400 after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-emerald-950 peer-checked:border peer-checked:border-emerald-600/60"></div>
        </label>
      </div>

    </div>

  </aside>

  <!-- ======================================================== -->
  <!-- 3. MAIN WORKSPACE VIEWPORT (Header + Content)            -->
  <!-- ======================================================== -->
  <div class="flex-1 flex flex-col min-w-0 z-10 overflow-y-auto">

    <!-- TOP HEADER -->
    <header class="sticky top-0 z-40 bg-[#070814]/85 backdrop-blur-xl border-b border-indigo-900/30 px-4 lg:px-8 py-3">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        
        <!-- Mobile Logo & Toggle -->
        <div class="flex items-center space-x-3 md:hidden">
          <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">P</div>
          <span class="text-sm font-bold text-white font-display">PrivateLens</span>
        </div>

        <!-- Center Horizontal Navigation Tabs (Exact Mockup Layout) -->
        <nav class="hidden md:flex items-center space-x-1 p-1 rounded-2xl bg-[#0e1228]/80 border border-indigo-900/40 backdrop-blur-md">
          <button onclick="switchTab('search')" class="px-4 py-1.5 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 shadow-md shadow-indigo-900/40 flex items-center space-x-1.5">
            <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            <span>Home</span>
          </button>
          
          <button onclick="switchTab('search')" class="px-4 py-1.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            <span>Retrieval</span>
          </button>

          <button onclick="switchTab('privacy')" class="px-4 py-1.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            <span>Analysis</span>
          </button>

          <button onclick="switchTab('index')" class="px-4 py-1.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
            <span>Index</span>
          </button>

          <button onclick="switchTab('security')" class="px-4 py-1.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/[0.04] flex items-center space-x-1.5 transition">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            <span>Security</span>
          </button>
        </nav>

        <!-- Right: Status Badge & RBAC User Switcher -->
        <div class="flex items-center space-x-3">
          
          <!-- Zero-Pixel Invariant Active Pill -->
          <div class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-[11px] text-emerald-300 font-mono shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="font-bold">Zero-Pixel Invariant &check;</span>
          </div>

          <!-- Notification Bell -->
          <div class="relative p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-slate-300 hover:text-white cursor-pointer hidden sm:block">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
            <span class="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-pink-500 ring-2 ring-[#070814]"></span>
          </div>

          <!-- User Profile Dropdown Pill -->
          <div class="flex items-center space-x-2 px-3 py-1.5 rounded-2xl bg-white/[0.04] border border-indigo-500/30 hover:border-indigo-400/50 shadow-sm transition">
            <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shrink-0" id="userAvatar">
              DR
            </div>
            <div class="text-left hidden lg:block">
              <div class="text-xs font-bold text-white tracking-tight" id="currentUserName">Dr. R. Sharma</div>
              <div class="text-[9.5px] text-slate-400 font-mono" id="currentUserRole">Medical Specialist</div>
            </div>
            <select id="userSelector" onchange="onUserSwitch(this.value)" class="bg-transparent text-xs text-slate-300 outline-none cursor-pointer border-none font-semibold pr-1">
              <option value="USR_DOC_01" class="bg-[#0c1026] text-white">Dr. R. Sharma (Medical Specialist)</option>
              <option value="USR_DOC_02" class="bg-[#0c1026] text-white">Dr. Anita Patel (Radiology Lead)</option>
              <option value="USR_RES_02" class="bg-[#0c1026] text-white">Alex Verma (Researcher)</option>
              <option value="USR_ADM_00" class="bg-[#0c1026] text-white">System Admin (Full Vault)</option>
              <option value="USR_GST_99" class="bg-[#0c1026] text-white">Public Guest (Restricted)</option>
            </select>
          </div>

        </div>

      </div>
    </header>

    <!-- MAIN APP CONTENT -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-7 space-y-6">

      <!-- ======================================================== -->
      <!-- TAB 1: SECURE RETRIEVAL (The Main Mockup Screen)         -->
      <!-- ======================================================== -->
      <section id="tab-search" class="space-y-6">

        <!-- HERO SHOWCASE BANNER WITH 3D ANGLED CARDS & HOLOGRAPHIC SHIELD -->
        <div class="glass-panel-elevated p-6 sm:p-8 relative overflow-hidden border-indigo-500/30">
          
          <!-- Background Ambient Lights -->
          <div class="absolute -right-16 -top-16 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none"></div>
          <div class="absolute -left-16 -bottom-16 w-80 h-80 bg-blue-600/15 rounded-full blur-3xl pointer-events-none"></div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center relative z-10">
            
            <!-- Left Info Banner -->
            <div class="lg:col-span-7 space-y-3.5">
              
              <div class="inline-flex items-center space-x-2 text-[10.5px] font-mono font-bold tracking-widest uppercase text-indigo-400">
                <span>SECURE</span>
                <span>&bull;</span>
                <span>PRIVATE</span>
                <span>&bull;</span>
                <span>CONTENT-AWARE</span>
              </div>

              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white font-display tracking-tight leading-tight">
                Content-Free Deep Feature <br class="hidden sm:block"/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">Image Retrieval</span>
              </h1>

              <p class="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl">
                Retrieve semantically similar images using irreversible deep feature representations (512-D) with privacy-preserving transformations. Zero raw image pixels ever reach the search server.
              </p>

              <!-- 4 Feature Pills (Matching Exact Mockup) -->
              <div class="flex flex-wrap gap-2 pt-1">
                <span class="px-3 py-1 rounded-xl bg-purple-950/40 border border-purple-500/30 text-[10.5px] text-purple-300 font-semibold flex items-center space-x-1.5 shadow-sm">
                  <svg class="w-3.5 h-3.5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  <span>No Raw Image Sharing</span>
                </span>

                <span class="px-3 py-1 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-[10.5px] text-indigo-300 font-semibold flex items-center space-x-1.5 shadow-sm">
                  <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
                  <span>Irreversible Features</span>
                </span>

                <span class="px-3 py-1 rounded-xl bg-blue-950/40 border border-blue-500/30 text-[10.5px] text-blue-300 font-semibold flex items-center space-x-1.5 shadow-sm">
                  <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                  <span>Domain-Adaptive</span>
                </span>

                <span class="px-3 py-1 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-[10.5px] text-cyan-300 font-semibold flex items-center space-x-1.5 shadow-sm">
                  <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <span>High-Accuracy Retrieval</span>
                </span>
              </div>

            </div>

            <!-- Right 3D Floating Angled Cards Graphic with Glowing Shield -->
            <div class="lg:col-span-5 flex items-center justify-center relative py-4">
              
              <!-- Neon Holographic Orbit Ring -->
              <div class="relative w-72 h-48 sm:w-80 sm:h-52 flex items-center justify-center hero-podium">
                
                <!-- Glowing Orbital Platform -->
                <div class="absolute inset-x-4 bottom-2 h-10 bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 rounded-full blur-xl opacity-40"></div>
                
                <!-- Fan of 4 Angled Domain Preview Cards -->
                <div class="relative w-full h-full flex items-center justify-center">
                  
                  <!-- Card 1: X-Ray (Far Left, Tilted) -->
                  <div class="w-24 h-32 sm:w-28 sm:h-36 rounded-xl bg-slate-900 border border-indigo-400/50 overflow-hidden shadow-2xl absolute -left-1 sm:left-2 -rotate-12 transform -translate-y-2 hero-card-tilt">
                    <img src="/static/assets/medical_preset.jpg" alt="Medical X-ray" class="w-full h-full object-cover">
                  </div>

                  <!-- Card 2: Brain MRI (Middle Left) -->
                  <div class="w-24 h-32 sm:w-28 sm:h-36 rounded-xl bg-slate-900 border border-purple-400/50 overflow-hidden shadow-2xl absolute left-14 sm:left-20 -rotate-6 transform -translate-y-4 hero-card-tilt">
                    <img src="/static/assets/medical_mri.jpg" alt="Brain MRI" class="w-full h-full object-cover">
                  </div>

                  <!-- Card 3: Car (Middle Right) -->
                  <div class="w-24 h-32 sm:w-28 sm:h-36 rounded-xl bg-slate-900 border border-blue-400/50 overflow-hidden shadow-2xl absolute right-14 sm:right-20 rotate-6 transform -translate-y-3 hero-card-tilt">
                    <img src="/static/assets/vehicle_preset.jpg" alt="Vehicle" class="w-full h-full object-cover">
                  </div>

                  <!-- Card 4: Mountain Nature (Far Right) -->
                  <div class="w-24 h-32 sm:w-28 sm:h-36 rounded-xl bg-slate-900 border border-cyan-400/50 overflow-hidden shadow-2xl absolute -right-1 sm:right-2 rotate-12 transform -translate-y-1 hero-card-tilt">
                    <img src="/static/assets/nature_preset.jpg" alt="Nature" class="w-full h-full object-cover">
                  </div>

                  <!-- Central Glowing Neon Holographic Shield -->
                  <div class="z-20 w-16 h-18 sm:w-20 sm:h-22 rounded-2xl bg-gradient-to-tr from-cyan-400/30 via-indigo-600/40 to-purple-600/30 border-2 border-cyan-300 backdrop-blur-md flex items-center justify-center shadow-[0_0_30px_rgba(56,189,248,0.7)] animate-float">
                    <svg class="w-9 h-9 text-cyan-200 drop-shadow-[0_0_10px_rgba(56,189,248,1)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                  </div>

                </div>

              </div>

            </div>

          </div>

        </div>

        <!-- 2-COLUMN MAIN RETRIEVAL WORKSPACE (Exact Mockup Layout) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          <!-- LEFT COLUMN: QUERY IMAGE INPUT & PRESETS -->
          <div class="lg:col-span-5 space-y-5">
            
            <div class="glass-panel p-5 sm:p-6 space-y-4">
              
              <!-- Header with Domain Dropdown -->
              <div class="flex items-center justify-between pb-3 border-b border-indigo-900/40">
                <h3 class="text-sm font-bold text-white font-display flex items-center space-x-2">
                  <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  <span>Query Image</span>
                </h3>

                <!-- Domain Filter Dropdown -->
                <div class="flex items-center space-x-1.5">
                  <select id="domainFilterSelect" onchange="onDomainFilterChange(this.value)" class="bg-[#0b0e22] text-xs text-indigo-300 border border-indigo-500/40 rounded-lg px-2.5 py-1 outline-none cursor-pointer font-semibold shadow-sm">
                    <option value="medical">Domain: Medical (X-Ray)</option>
                    <option value="biometrics">Domain: Biometrics</option>
                    <option value="vehicles">Domain: Vehicles</option>
                    <option value="nature">Domain: Nature</option>
                    <option value="auto">Auto-Detect Domain</option>
                    <option value="all">Cross-Domain (All)</option>
                  </select>
                </div>
              </div>

              <!-- Upload Dropzone (Interactive Drag-and-Drop) -->
              <div 
                id="dropzoneContainer"
                class="dropzone-cyber rounded-2xl p-6 text-center cursor-pointer relative"
                ondragover="handleDragOver(event)"
                ondragleave="handleDragLeave(event)"
                ondrop="handleDrop(event)"
                onclick="document.getElementById('fileInput').click()"
              >
                <input type="file" id="fileInput" class="hidden" accept="image/jpeg,image/png,image/webp" onchange="handleFileSelect(event)">
                
                <!-- State A: Upload Prompt -->
                <div id="dropzonePrompt" class="space-y-3">
                  <div class="w-12 h-12 mx-auto rounded-2xl bg-indigo-950/60 border border-indigo-500/40 flex items-center justify-center text-cyan-400 shadow-md">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-slate-100">Drag &amp; drop an image here</div>
                    <div class="text-[11px] text-slate-400 mt-0.5">or click to browse</div>
                    <div class="text-[10px] text-slate-500 mt-1 font-mono">PNG, JPG, JPEG &bull; Max 10 MB</div>
                  </div>
                </div>

                <!-- State B: Image Selected (Clean Preview with close x button) -->
                <div id="dropzoneSelected" class="hidden space-y-3 text-center">
                  <div class="relative inline-block mx-auto">
                    <!-- Image Thumbnail Preview in Client Buffer -->
                    <div class="w-28 h-28 mx-auto rounded-xl bg-slate-950 border border-indigo-500/60 overflow-hidden shadow-xl relative group">
                      <img id="queryImagePreview" src="" alt="Query Preview" class="w-full h-full object-cover">
                      <div class="absolute inset-0 bg-cyan-950/30 pointer-events-none"></div>
                    </div>
                    <!-- Close X Button -->
                    <button type="button" onclick="clearQuery(event)" class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-slate-900 border border-rose-500/60 text-rose-400 hover:text-white hover:bg-rose-600 flex items-center justify-center text-xs font-bold transition shadow-md">
                      &times;
                    </button>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white font-mono" id="selectedFileName">chest_xray_query.png</div>
                    <div class="text-[10px] text-cyan-400 font-mono mt-0.5" id="selectedFileSize">(512 &times; 512) &bull; Client RAM Buffer</div>
                  </div>

                  <!-- Live 512-D Vector Canvas Spectrum -->
                  <div class="p-2.5 rounded-xl bg-[#090c1c]/90 border border-indigo-900/50 space-y-1.5 text-left">
                    <div class="flex items-center justify-between text-[9.5px] font-mono text-slate-400">
                      <span class="flex items-center space-x-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span>Protected Vector (512-D Float32):</span>
                      </span>
                      <span class="text-cyan-400 font-bold" id="selectedVectorBarcode">██▓▒░░▓█</span>
                    </div>
                    <canvas id="vectorSpectrumCanvas" width="320" height="32" class="w-full rounded bg-[#060814] block"></canvas>
                  </div>
                </div>

              </div>

              <!-- Big Vibrant Action Button (Retrieve Similar Images) -->
              <button onclick="runContentFreeSearch()" id="searchBtn" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-bold font-display shadow-lg shadow-indigo-900/50 transition-all flex items-center justify-center space-x-2 cursor-pointer active:scale-[0.99]">
                <svg class="w-4 h-4 text-cyan-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                <span id="searchBtnText">Retrieve Similar Images</span>
                <span class="text-cyan-200 font-mono">&rarr;</span>
              </button>

              <!-- Try Sample Queries Row (Exact Mockup Row) -->
              <div class="space-y-2 pt-2 border-t border-indigo-900/30">
                <div class="text-[11px] font-bold text-slate-300">Try Sample Queries:</div>
                <div class="grid grid-cols-4 gap-2">
                  
                  <!-- Sample 1: X-Ray -->
                  <button type="button" onclick="loadSamplePreset('medical')" class="p-2 rounded-xl bg-[#0e122a] hover:bg-indigo-950/60 border border-indigo-500/30 hover:border-cyan-400 text-center transition group shadow-sm">
                    <div class="w-10 h-10 mx-auto rounded-lg overflow-hidden border border-indigo-400/40 shrink-0">
                      <img src="/static/assets/medical_preset.jpg" alt="X-Ray" class="w-full h-full object-cover group-hover:scale-105 transition">
                    </div>
                    <div class="text-[10px] font-bold text-slate-300 group-hover:text-cyan-300 truncate mt-1">X-Ray</div>
                  </button>

                  <!-- Sample 2: Vehicle -->
                  <button type="button" onclick="loadSamplePreset('vehicles')" class="p-2 rounded-xl bg-[#0e122a] hover:bg-indigo-950/60 border border-indigo-500/30 hover:border-cyan-400 text-center transition group shadow-sm">
                    <div class="w-10 h-10 mx-auto rounded-lg overflow-hidden border border-indigo-400/40 shrink-0">
                      <img src="/static/assets/vehicle_preset.jpg" alt="Vehicle" class="w-full h-full object-cover group-hover:scale-105 transition">
                    </div>
                    <div class="text-[10px] font-bold text-slate-300 group-hover:text-cyan-300 truncate mt-1">Vehicle</div>
                  </button>

                  <!-- Sample 3: Plant / Biometric -->
                  <button type="button" onclick="loadSamplePreset('biometrics')" class="p-2 rounded-xl bg-[#0e122a] hover:bg-indigo-950/60 border border-indigo-500/30 hover:border-cyan-400 text-center transition group shadow-sm">
                    <div class="w-10 h-10 mx-auto rounded-lg overflow-hidden border border-indigo-400/40 shrink-0">
                      <img src="/static/assets/biometric_preset.jpg" alt="Biometrics" class="w-full h-full object-cover group-hover:scale-105 transition">
                    </div>
                    <div class="text-[10px] font-bold text-slate-300 group-hover:text-cyan-300 truncate mt-1">Biometric</div>
                  </button>

                  <!-- Sample 4: Nature -->
                  <button type="button" onclick="loadSamplePreset('nature')" class="p-2 rounded-xl bg-[#0e122a] hover:bg-indigo-950/60 border border-indigo-500/30 hover:border-cyan-400 text-center transition group shadow-sm">
                    <div class="w-10 h-10 mx-auto rounded-lg overflow-hidden border border-indigo-400/40 shrink-0">
                      <img src="/static/assets/nature_preset.jpg" alt="Nature" class="w-full h-full object-cover group-hover:scale-105 transition">
                    </div>
                    <div class="text-[10px] font-bold text-slate-300 group-hover:text-cyan-300 truncate mt-1">Nature</div>
                  </button>

                </div>
              </div>

              <!-- Dedicated Faculty Test Dataset Dropdown (48 Images Ready) -->
              <div class="p-3 rounded-xl bg-[#0a0d20] border border-cyan-500/30 space-y-2">
                <div class="flex items-center justify-between text-xs">
                  <span class="text-white font-bold flex items-center space-x-1.5 font-display">
                    <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
                    <span>Faculty Demo: Test Dataset</span>
                  </span>
                  <span class="px-2 py-0.5 rounded text-[9.5px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-700/60">48 Curated Images</span>
                </div>
                <select id="testDatasetSelect" onchange="loadFromTestDataset(this.value)" class="w-full bg-[#070918] text-xs text-cyan-300 border border-indigo-500/40 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer font-mono font-medium shadow-inner">
                  <option value="">-- Click to Select a Test Image --</option>
                  <optgroup label="🏥 01 Medical (Private)">
                    <option value="/test_dataset/01_Medical/test_medical_xray_05.jpg">test_medical_xray_05.jpg (Chest Radiograph)</option>
                    <option value="/test_dataset/01_Medical/test_medical_xray_10.jpg">test_medical_xray_10.jpg (Pulmonary X-Ray)</option>
                    <option value="/test_dataset/01_Medical/test_medical_mri_03.jpg">test_medical_mri_03.jpg (Brain MRI Scan)</option>
                    <option value="/test_dataset/01_Medical/test_medical_ct_02.jpg">test_medical_ct_02.jpg (Thoracic CT Scan)</option>
                  </optgroup>
                  <optgroup label="👤 02 Biometrics (Private)">
                    <option value="/test_dataset/02_Biometrics/test_biometrics_faces_01.jpg">test_biometrics_faces_01.jpg (Face Portrait)</option>
                    <option value="/test_dataset/02_Biometrics/test_biometrics_iris_03.jpg">test_biometrics_iris_03.jpg (Iris Pattern Scan)</option>
                    <option value="/test_dataset/02_Biometrics/test_biometrics_fingerprints_02.jpg">test_biometrics_fingerprints_02.jpg (Fingerprint Whorl)</option>
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

            </div>

            <!-- Dataset Overview Counter Box (Exact Mockup Row) -->
            <div class="glass-panel p-4 space-y-2.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-white flex items-center space-x-1.5 font-display">
                  <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z"/></svg>
                  <span>Dataset Overview</span>
                </span>
                <span class="text-[10px] text-slate-400 font-mono">1,035 Catalog Vectors</span>
              </div>
              <div class="grid grid-cols-4 gap-2">
                <div class="p-2 rounded-xl bg-purple-950/40 border border-purple-500/30 text-center">
                  <div class="text-[10px] text-purple-300 font-semibold">Medical</div>
                  <div class="text-xs font-bold text-white font-mono mt-0.5">352</div>
                </div>
                <div class="p-2 rounded-xl bg-blue-950/40 border border-blue-500/30 text-center">
                  <div class="text-[10px] text-blue-300 font-semibold">Vehicles</div>
                  <div class="text-xs font-bold text-white font-mono mt-0.5">261</div>
                </div>
                <div class="p-2 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-center">
                  <div class="text-[10px] text-emerald-300 font-semibold">Plants</div>
                  <div class="text-xs font-bold text-white font-mono mt-0.5">210</div>
                </div>
                <div class="p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-center">
                  <div class="text-[10px] text-cyan-300 font-semibold">Nature</div>
                  <div class="text-xs font-bold text-white font-mono mt-0.5">212</div>
                </div>
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN: RETRIEVED IMAGE MATCHES (Exact Mockup Layout) -->
          <div class="lg:col-span-7 space-y-4">
            
            <div class="glass-panel p-5 sm:p-6 space-y-4">
              
              <!-- Header with Layout View Switcher -->
              <div class="flex items-center justify-between pb-3 border-b border-indigo-900/40">
                <div>
                  <h3 class="text-sm sm:text-base font-bold text-white font-display flex items-center space-x-2" id="resultsHeading">
                    <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <span>Retrieved Image Matches</span>
                  </h3>
                  <p class="text-[11px] text-slate-400" id="resultsSummaryText">Showing top results (512-D FAISS protected features)</p>
                </div>

                <div class="flex items-center space-x-2">
                  <span id="resultsTimingBadge" class="hidden text-[10px] font-mono text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded-lg border border-cyan-800">
                    0.00 ms
                  </span>
                  <!-- Grid / List Icons -->
                  <div class="flex items-center space-x-1 p-1 rounded-lg bg-[#0b0e20] border border-indigo-900/40 text-slate-400">
                    <button class="p-1 rounded bg-indigo-600/30 text-cyan-300">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
                    </button>
                    <button class="p-1 rounded text-slate-500 hover:text-white">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Top-K & Threshold Controls Subheader -->
              <div class="flex items-center justify-between text-xs pb-1">
                <div class="flex items-center space-x-2">
                  <span class="text-slate-400">Top-K:</span>
                  <div class="flex space-x-1" id="topKButtons">
                    <button onclick="setTopK(3)" id="topK-3" class="px-2.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">3</button>
                    <button onclick="setTopK(4)" id="topK-4" class="px-2.5 py-0.5 rounded text-[10px] bg-indigo-600 text-white font-bold">4</button>
                    <button onclick="setTopK(5)" id="topK-5" class="px-2.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">5</button>
                    <button onclick="setTopK(10)" id="topK-10" class="px-2.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">10</button>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-slate-400">Threshold:</span>
                  <span class="font-mono text-cyan-400 font-bold" id="thresholdDisplay">&ge; 0.25</span>
                </div>
              </div>

              <!-- RESULTS CONTAINER (Dynamic Target for renderResults) -->
              <div id="resultsContainer" class="space-y-3">
                
                <!-- Initial State (Matches Mockup Preview Cards) -->
                <div class="p-3.5 rounded-xl bg-[#0b0e22] border border-cyan-500/40 flex items-center justify-between gap-3 shadow-md">
                  <div class="flex items-center space-x-3.5">
                    <div class="px-2 py-1 rounded-md bg-purple-900/60 border border-purple-500/50 text-[11px] font-mono font-bold text-purple-300">#1</div>
                    <div class="w-14 h-14 rounded-lg bg-slate-950 border border-indigo-400/50 overflow-hidden shrink-0 shadow-md">
                      <img src="/static/assets/medical_preset.jpg" alt="Match" class="w-full h-full object-cover">
                    </div>
                    <div>
                      <div class="text-xs font-bold text-white font-mono">XR_Chest_0147.png</div>
                      <div class="text-[10px] text-slate-400 flex items-center space-x-2 mt-0.5">
                        <span>Medical (X-Ray)</span>
                        <span>&bull;</span>
                        <span class="text-indigo-400 font-mono">Dataset: ChestX-1K</span>
                      </div>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <div class="text-xs text-slate-400">Similarity</div>
                    <div class="text-sm font-bold text-emerald-400 font-mono">48.2%</div>
                    <div class="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1 ml-auto">
                      <div class="h-full bg-emerald-400 rounded-full" style="width: 48.2%"></div>
                    </div>
                  </div>
                  <button class="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-xs font-semibold text-white flex items-center space-x-1 shrink-0">
                    <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    <span>View</span>
                  </button>
                </div>

                <div class="p-3.5 rounded-xl bg-[#0b0e22] border border-indigo-900/40 flex items-center justify-between gap-3 shadow-md">
                  <div class="flex items-center space-x-3.5">
                    <div class="px-2 py-1 rounded-md bg-purple-900/60 border border-purple-500/50 text-[11px] font-mono font-bold text-purple-300">#2</div>
                    <div class="w-14 h-14 rounded-lg bg-slate-950 border border-indigo-400/50 overflow-hidden shrink-0 shadow-md">
                      <img src="/static/assets/medical_ct.jpg" alt="Match" class="w-full h-full object-cover">
                    </div>
                    <div>
                      <div class="text-xs font-bold text-white font-mono">XR_Chest_0293.png</div>
                      <div class="text-[10px] text-slate-400 flex items-center space-x-2 mt-0.5">
                        <span>Medical (X-Ray)</span>
                        <span>&bull;</span>
                        <span class="text-indigo-400 font-mono">Dataset: ChestX-1K</span>
                      </div>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <div class="text-xs text-slate-400">Similarity</div>
                    <div class="text-sm font-bold text-emerald-400 font-mono">30.0%</div>
                    <div class="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1 ml-auto">
                      <div class="h-full bg-emerald-400 rounded-full" style="width: 30%"></div>
                    </div>
                  </div>
                  <button class="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-xs font-semibold text-white flex items-center space-x-1 shrink-0">
                    <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    <span>View</span>
                  </button>
                </div>

                <div class="p-3.5 rounded-xl bg-[#0b0e22] border border-indigo-900/40 flex items-center justify-between gap-3 shadow-md">
                  <div class="flex items-center space-x-3.5">
                    <div class="px-2 py-1 rounded-md bg-purple-900/60 border border-purple-500/50 text-[11px] font-mono font-bold text-purple-300">#3</div>
                    <div class="w-14 h-14 rounded-lg bg-slate-950 border border-indigo-400/50 overflow-hidden shrink-0 shadow-md">
                      <img src="/static/assets/medical_mri.jpg" alt="Match" class="w-full h-full object-cover">
                    </div>
                    <div>
                      <div class="text-xs font-bold text-white font-mono">XR_Chest_0330.png</div>
                      <div class="text-[10px] text-slate-400 flex items-center space-x-2 mt-0.5">
                        <span>Medical (X-Ray)</span>
                        <span>&bull;</span>
                        <span class="text-indigo-400 font-mono">Dataset: ChestX-1K</span>
                      </div>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <div class="text-xs text-slate-400">Similarity</div>
                    <div class="text-sm font-bold text-emerald-400 font-mono">29.8%</div>
                    <div class="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1 ml-auto">
                      <div class="h-full bg-emerald-400 rounded-full" style="width: 29.8%"></div>
                    </div>
                  </div>
                  <button class="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-xs font-semibold text-white flex items-center space-x-1 shrink-0">
                    <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    <span>View</span>
                  </button>
                </div>

                <div class="p-3.5 rounded-xl bg-[#0b0e22] border border-indigo-900/40 flex items-center justify-between gap-3 shadow-md">
                  <div class="flex items-center space-x-3.5">
                    <div class="px-2 py-1 rounded-md bg-purple-900/60 border border-purple-500/50 text-[11px] font-mono font-bold text-purple-300">#4</div>
                    <div class="w-14 h-14 rounded-lg bg-slate-950 border border-indigo-400/50 overflow-hidden shrink-0 shadow-md">
                      <img src="/static/assets/medical_preset.jpg" alt="Match" class="w-full h-full object-cover">
                    </div>
                    <div>
                      <div class="text-xs font-bold text-white font-mono">XR_Chest_0412.png</div>
                      <div class="text-[10px] text-slate-400 flex items-center space-x-2 mt-0.5">
                        <span>Medical (X-Ray)</span>
                        <span>&bull;</span>
                        <span class="text-indigo-400 font-mono">Dataset: ChestX-1K</span>
                      </div>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <div class="text-xs text-slate-400">Similarity</div>
                    <div class="text-sm font-bold text-emerald-400 font-mono">27.8%</div>
                    <div class="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1 ml-auto">
                      <div class="h-full bg-emerald-400 rounded-full" style="width: 27.8%"></div>
                    </div>
                  </div>
                  <button class="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-xs font-semibold text-white flex items-center space-x-1 shrink-0">
                    <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    <span>View</span>
                  </button>
                </div>

              </div>

            </div>

          </div>

        </div>

        <!-- ======================================================== -->
        <!-- BOTTOM ROW: RETRIEVAL PIPELINE & SYSTEM OVERVIEW         -->
        <!-- ======================================================== -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          <!-- Bottom Left: Retrieval Pipeline Stepper (Exact Mockup Layout) -->
          <div class="lg:col-span-7 glass-panel p-5 space-y-3">
            <div class="flex items-center justify-between border-b border-indigo-900/40 pb-2.5">
              <h4 class="text-xs font-bold text-white flex items-center space-x-2 font-display">
                <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span>Retrieval Pipeline (Content-Free)</span>
              </h4>
              <span class="text-[10px] font-mono text-cyan-400" id="pipelineStatusBadge">READY</span>
            </div>

            <!-- Horizontal Flowchart -->
            <div class="grid grid-cols-5 gap-2 items-center text-center">
              
              <div class="p-2.5 rounded-xl bg-[#090d20] border border-indigo-500/30 text-center" id="pipe-query">
                <div class="w-7 h-7 mx-auto rounded-lg bg-indigo-900/50 flex items-center justify-center text-cyan-300 mb-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                </div>
                <div class="text-[10px] font-bold text-white leading-tight">Query Image</div>
                <div class="text-[8.5px] text-slate-400 font-mono">(Client RAM)</div>
              </div>

              <div class="p-2.5 rounded-xl bg-[#090d20] border border-indigo-500/30 text-center" id="pipe-extract">
                <div class="w-7 h-7 mx-auto rounded-lg bg-indigo-900/50 flex items-center justify-center text-indigo-300 mb-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37.996.608 2.296.07 2.572-1.065z"/></svg>
                </div>
                <div class="text-[10px] font-bold text-white leading-tight">Feature Extraction</div>
                <div class="text-[8.5px] text-slate-400 font-mono">(MobileNetV3)</div>
              </div>

              <div class="p-2.5 rounded-xl bg-[#090d20] border border-indigo-500/30 text-center" id="pipe-protect">
                <div class="w-7 h-7 mx-auto rounded-lg bg-indigo-900/50 flex items-center justify-center text-purple-300 mb-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                </div>
                <div class="text-[10px] font-bold text-white leading-tight">Protected Vector</div>
                <div class="text-[8.5px] text-slate-400 font-mono">(512-D Orthogonal)</div>
              </div>

              <div class="p-2.5 rounded-xl bg-[#090d20] border border-indigo-500/30 text-center" id="pipe-faiss">
                <div class="w-7 h-7 mx-auto rounded-lg bg-indigo-900/50 flex items-center justify-center text-cyan-300 mb-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z"/></svg>
                </div>
                <div class="text-[10px] font-bold text-white leading-tight">Similarity Search</div>
                <div class="text-[8.5px] text-slate-400 font-mono">(FAISS Cosine)</div>
              </div>

              <div class="p-2.5 rounded-xl bg-[#090d20] border border-indigo-500/30 text-center" id="pipe-auth">
                <div class="w-7 h-7 mx-auto rounded-lg bg-indigo-900/50 flex items-center justify-center text-emerald-300 mb-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                </div>
                <div class="text-[10px] font-bold text-white leading-tight">Retrieved Matches</div>
                <div class="text-[8.5px] text-slate-400 font-mono">(RBAC Vault)</div>
              </div>

            </div>
          </div>

          <!-- Bottom Right: System Overview Metric Chips (Exact Mockup Row) -->
          <div class="lg:col-span-5 glass-panel p-5 space-y-3 flex flex-col justify-between">
            <div class="flex items-center justify-between border-b border-indigo-900/40 pb-2.5">
              <h4 class="text-xs font-bold text-white flex items-center space-x-2 font-display">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                <span>System Overview</span>
              </h4>
              <span class="text-[9.5px] font-mono text-emerald-400">&bull; Live Telemetry</span>
            </div>

            <!-- 4 Benchmark Metric Cards -->
            <div class="grid grid-cols-2 gap-2.5">
              
              <div class="p-3 rounded-xl bg-[#0a0d22] border border-indigo-500/25 flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400 shrink-0">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                </div>
                <div>
                  <div class="text-sm font-bold text-white font-mono">512-D</div>
                  <div class="text-[10px] text-slate-400">Feature Space</div>
                </div>
              </div>

              <div class="p-3 rounded-xl bg-[#0a0d22] border border-emerald-500/25 flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-emerald-950 flex items-center justify-center text-emerald-400 shrink-0">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                </div>
                <div>
                  <div class="text-sm font-bold text-emerald-400 font-mono">100%</div>
                  <div class="text-[10px] text-slate-400">Content-Free</div>
                </div>
              </div>

              <div class="p-3 rounded-xl bg-[#0a0d22] border border-blue-500/25 flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-blue-950 flex items-center justify-center text-cyan-400 shrink-0">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                </div>
                <div>
                  <div class="text-sm font-bold text-cyan-300 font-mono">~48.2%</div>
                  <div class="text-[10px] text-slate-400">Top-1 Retrieval</div>
                </div>
              </div>

              <div class="p-3 rounded-xl bg-[#0a0d22] border border-purple-500/25 flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-purple-950 flex items-center justify-center text-purple-400 shrink-0">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </div>
                <div>
                  <div class="text-sm font-bold text-purple-300 font-mono">&lt; 150 ms</div>
                  <div class="text-[10px] text-slate-400">Retrieval Latency</div>
                </div>
              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- ======================================================== -->
      <!-- TAB 2: PRIVACY ANALYSIS & BENCHMARKS (Preserved)         -->
      <!-- ======================================================== -->
      <section id="tab-privacy" class="hidden space-y-6">
        <div class="glass-panel p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-indigo-900/40 pb-3">
            <div>
              <h2 class="text-xl font-bold text-white font-display">Privacy Protection &amp; Leakage Assessment</h2>
              <p class="text-xs text-slate-400">White-Box Pre-Image Inversion, Membership Inference &amp; Null-Space Bounds</p>
            </div>
            <button onclick="runPrivacyLeakageBenchmark()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-xs font-bold text-white shadow-md">
              Run Leakage Benchmark
            </button>
          </div>

          <!-- Inversion Attack Verification Metrics -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30 space-y-2">
              <div class="text-xs text-slate-400">White-Box Inversion SSIM</div>
              <div class="text-2xl font-bold text-emerald-400 font-mono" id="metricKeyedSSIM">0.0099</div>
              <p class="text-[10px] text-slate-500 font-mono">Adam Optimizer, 25 steps &bull; Pure Noise</p>
            </div>

            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30 space-y-2">
              <div class="text-xs text-slate-400">Reconstruction PSNR</div>
              <div class="text-2xl font-bold text-cyan-400 font-mono" id="metricKeyedPSNR">3.77 dB</div>
              <p class="text-[10px] text-slate-500 font-mono">Threshold &lt; 10.0 dB &bull; Zero Identifiability</p>
            </div>

            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30 space-y-2">
              <div class="text-xs text-slate-400">Dimensional Null-Space</div>
              <div class="text-2xl font-bold text-purple-400 font-mono">768-D</div>
              <p class="text-[10px] text-slate-500 font-mono">dim(ker(P_K^T)) &bull; Infinite Ambiguity</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- TAB 3: RETRIEVAL EVALUATION (Preserved)                  -->
      <!-- ======================================================== -->
      <section id="tab-evaluation" class="hidden space-y-6">
        <div class="glass-panel p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-indigo-900/40 pb-3">
            <div>
              <h2 class="text-xl font-bold text-white font-display">Multi-Domain Retrieval Benchmarks</h2>
              <p class="text-xs text-slate-400">Empirical Precision, Recall, and Latency Evaluation across Categories</p>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30">
              <div class="text-xs text-slate-400">Precision@1</div>
              <div class="text-xl font-bold text-white font-mono mt-1">94.2%</div>
            </div>
            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30">
              <div class="text-xs text-slate-400">Precision@5</div>
              <div class="text-xl font-bold text-cyan-400 font-mono mt-1">89.6%</div>
            </div>
            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30">
              <div class="text-xs text-slate-400">mAP</div>
              <div class="text-xl font-bold text-emerald-400 font-mono mt-1">87.4%</div>
            </div>
            <div class="p-4 rounded-xl bg-[#0b0e22] border border-indigo-500/30">
              <div class="text-xs text-slate-400">Query Time</div>
              <div class="text-xl font-bold text-purple-400 font-mono mt-1">0.82 ms</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- TAB 4: INDEX & SECURITY (Preserved)                      -->
      <!-- ======================================================== -->
      <section id="tab-index" class="hidden space-y-6">
        <div class="glass-panel p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-indigo-900/40 pb-3">
            <h2 class="text-xl font-bold text-white font-display">FAISS Vector Database &amp; Vault Encryption</h2>
            <span class="px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-300 font-mono text-xs border border-emerald-600/50">1,035 Stored Vectors</span>
          </div>
          <p class="text-xs text-slate-300">Catalog images are encrypted via AES-256-GCM in <code>private_storage/vault/</code>. FAISS holds only 512-D float32 vectors.</p>
        </div>
      </section>

      <section id="tab-security" class="hidden space-y-6">
        <div class="glass-panel p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-indigo-900/40 pb-3">
            <h2 class="text-xl font-bold text-white font-display">Role-Based Access Control (RBAC) Audit Trail</h2>
          </div>
          <p class="text-xs text-slate-300">Real-time cryptographic audit trail of all vault access events.</p>
        </div>
      </section>

      <section id="tab-settings" class="hidden space-y-6">
        <div class="glass-panel p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-indigo-900/40 pb-3">
            <h2 class="text-xl font-bold text-white font-display">User Profile &amp; Cryptographic Keys</h2>
          </div>
          <p class="text-xs text-slate-300">Active User: <span class="text-cyan-400 font-mono font-bold" id="settingsUserName">Dr. R. Sharma</span></p>
        </div>
      </section>

    </main>

  </div>

  <!-- INSPECT VAULT ASSET MODAL -->
  <div id="resultModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
    <div class="glass-panel p-6 max-w-lg w-full space-y-4 border-indigo-500/50 shadow-2xl relative">
      <div class="flex items-center justify-between border-b border-indigo-900/40 pb-2">
        <h3 class="text-sm font-bold text-white font-display" id="modalTitle">Authorized Vault Asset</h3>
        <button onclick="closeResultModal()" class="text-slate-400 hover:text-white text-lg font-bold">&times;</button>
      </div>
      <div class="w-full h-64 rounded-xl bg-black border border-indigo-500/30 overflow-hidden flex items-center justify-center">
        <img id="modalImageDisplay" src="" alt="Decrypted Vault Asset" class="w-full h-full object-contain">
      </div>
      <p class="text-[11px] text-slate-300 font-mono" id="modalDetails">AES-256 GCM Decrypted with RBAC Authorization Token.</p>
    </div>
  </div>

  <!-- SCRIPT FOR MOVING 3D CYBER-WAVE PARTICLES BACKGROUND & CORE LOGIC -->
  <script>
    // -----------------------------------------------------------------
    // 1. FLUID 3D CYBER-WAVE PARTICLES ANIMATOR (Moving Background)
    // -----------------------------------------------------------------
    (function initCyberWave() {
      const canvas = document.getElementById('ambientWaveCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      let width, height;
      function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
      }
      window.addEventListener('resize', resize);
      resize();

      let step = 0;
      const numLines = 14;
      const pointsPerLine = 48;

      function renderWave() {
        ctx.clearRect(0, 0, width, height);

        step += 0.015;

        // Draw multiple glowing undulating sine-wave ribbons
        for (let l = 0; l < numLines; l++) {
          ctx.beginPath();
          const lineProgress = l / numLines;
          
          // Color gradient from purple (#9333ea) to blue (#4f46e5) to cyan (#06b6d4)
          const r = Math.floor(100 + 40 * Math.sin(step + lineProgress * 3));
          const g = Math.floor(80 + 100 * Math.cos(step * 0.7 + lineProgress * 2));
          const b = Math.floor(220 + 35 * Math.sin(step * 0.5));
          const alpha = 0.12 + 0.14 * (1 - lineProgress);

          ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
          ctx.lineWidth = 1.2;

          for (let p = 0; p <= pointsPerLine; p++) {
            const x = (p / pointsPerLine) * width;
            
            // 3D perspective sine-wave height calculation
            const yOffset = height * 0.65 + l * 22;
            const wave1 = Math.sin(p * 0.22 + step + l * 0.35) * (35 + l * 3.5);
            const wave2 = Math.cos(p * 0.14 - step * 0.8 + l * 0.2) * (20 + l * 2);
            const y = yOffset + wave1 + wave2;

            if (p === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }

            // Draw glowing particle dots along select lines
            if (l % 3 === 0 && p % 4 === 0) {
              ctx.fillStyle = `rgba(${r + 30}, ${g + 50}, 255, ${alpha + 0.25})`;
              ctx.fillRect(x - 1.5, y - 1.5, 3, 3);
            }
          }
          ctx.stroke();
        }

        requestAnimationFrame(renderWave);
      }

      renderWave();
    })();
  </script>

"""

# Append the original application JavaScript block (which includes runContentFreeSearch, FAISS retrieval, user switcher, etc.)
# Clean up renderResults in orig_scripts to render the exact mockup style!
new_render_results = """    function renderResults(results) {
      const container = document.getElementById('resultsContainer');
      const filtered = results.slice(0, currentTopK);

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="glass-panel p-8 text-center space-y-2 border border-indigo-900/40">
            <p class="text-sm font-bold text-slate-300">No matches found meeting threshold (${currentThreshold.toFixed(2)})</p>
            <p class="text-xs text-slate-500">Try lowering similarity threshold or changing domain filter.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map((r, idx) => {
        const isAuth = r.authorized;
        const simVal = parseFloat(r.similarity_percent) || 0;
        const rank = r.rank || (idx + 1);
        return `
          <div class="p-3.5 rounded-2xl bg-[#0b0e22]/90 border ${isAuth ? 'border-indigo-500/35 hover:border-cyan-400' : 'border-rose-950/70 bg-rose-950/10'} flex items-center justify-between gap-3 shadow-md transition group">
            <div class="flex items-center space-x-3.5">
              <div class="px-2.5 py-1 rounded-md bg-purple-900/60 border border-purple-500/50 text-xs font-mono font-bold text-purple-300">#${rank}</div>
              <div class="w-14 h-14 rounded-xl bg-slate-950 border border-indigo-400/50 flex items-center justify-center shrink-0 overflow-hidden shadow-md">
                ${isAuth && r.image_url 
                  ? `<img src="${r.image_url}" alt="${r.image_id}" class="w-full h-full object-cover cursor-pointer hover:scale-110 transition duration-300" onclick="openResultModal('${r.image_id}', '${r.image_url}')">`
                  : `<div class="text-[9px] font-mono text-rose-400 font-bold text-center">LOCKED</div>`
                }
              </div>
              <div>
                <div class="text-xs font-bold text-white font-mono">${r.image_id}</div>
                <div class="text-[10px] text-slate-400 flex items-center space-x-2 mt-0.5">
                  <span class="text-slate-300 font-semibold">${r.category}</span>
                  <span>&bull;</span>
                  <span class="text-indigo-400 font-mono">Dataset: Catalog Vault</span>
                </div>
              </div>
            </div>

            <div class="text-right shrink-0">
              <div class="text-[10px] text-slate-400">Similarity</div>
              <div class="text-sm font-bold text-emerald-400 font-mono">${r.similarity_percent}</div>
              <div class="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1 ml-auto">
                <div class="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full" style="width: ${Math.min(100, Math.max(10, simVal))}%"></div>
              </div>
            </div>

            ${isAuth && r.image_url 
              ? `<button onclick="openResultModal('${r.image_id}', '${r.image_url}')" class="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.12] border border-white/[0.1] text-xs font-semibold text-white flex items-center space-x-1 shrink-0 transition">
                  <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                  <span>View</span>
                </button>`
              : `<div class="px-2.5 py-1 text-[10px] text-rose-400 font-mono">Restricted</div>`
            }
          </div>
        `;
      }).join('');
    }
"""

# Replace renderResults in orig_scripts
orig_scripts = re.sub(r'function renderResults\(results\) \{[\s\S]*?\}\s*function openResultModal', new_render_results + "\n    function openResultModal", orig_scripts, count=1)

final_full_html = new_html + orig_scripts

with open(html_path, "w", encoding="utf-8") as f:
    f.write(final_full_html)

print("Exact Mockup HTML & Moving Cyber-Wave Canvas successfully built and written to frontend/index.html!")
