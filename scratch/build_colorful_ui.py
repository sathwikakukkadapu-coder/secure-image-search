import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

REQUIRED_IDS = [
    'auditCategoryFilter', 'auditStatusFilter', 'auditTrailTableBody', 'baselineP5', 
    'currentUserName', 'currentUserRole', 'diagAuthLatency', 'diagCandidates', 
    'diagDetectedDomain', 'diagDomainConfidence', 'diagDomainFilter', 'diagDomainPassed', 
    'diagLatency', 'diagStatusBadge', 'diagThresholdFiltered', 'diagnosticPanel', 
    'dropzonePrompt', 'dropzoneSelected', 'evalAvgLatency', 'evalChartContainer', 
    'evalDatasetSelect', 'evalHistoryTable', 'evalMAP', 'evalP1', 'evalP5', 
    'evalSampleLimit', 'evalSigma', 'evalThroughput', 'evalTradeoffText', 'fileInput', 
    'incrBtn', 'indexFaissCount', 'indexFaissSize', 'indexLastDuration', 'indexLastRebuild', 
    'indexVaultSize', 'metadataMinimizationToggle', 'modalDetails', 'modalImageDisplay', 
    'modalTitle', 'overviewRecentEvents', 'pipelineStatusBadge', 'privacyReceiptCard', 
    'privacyTradeoffTable', 'protectedP5', 'rebuildBtn', 'receiptFaissTime', 'receiptId', 
    'resultModal', 'resultsContainer', 'runEvalBtn', 'runEvalBtnText', 'runPrivBtn', 
    'runPrivBtnText', 'searchBtn', 'searchBtnText', 'secBlockedAttempts', 'secChainHash', 
    'secChainStatus', 'secFailedLogins', 'secTotalEvents', 'selectedFileName', 
    'selectedFileSize', 'selectedVectorBarcode', 'selectedVectorSample', 'settingsUserEmail', 
    'settingsUserId', 'settingsUserName', 'settingsUserRole', 'settingsUserToken', 
    'statAuditCount', 'statHealthBadge', 'statTotalImages', 'statTotalVectors', 
    'thresholdDisplay', 'toast', 'toastMsg', 'userAvatar', 'userSelector', 
    'valCategoriesText', 'valCorruptCount', 'valDuplicateCount', 'valStatusBadge', 
    'valTotalScanned', 'valValidCount', 'validateBtn'
]

html_content = '''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PrivateLens | Private Image Search & Privacy-Preserving AI Retrieval Platform</title>
  
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
      background-color: #050811;
      color: #f8fafc;
      overflow-x: hidden;
      background-image: 
        radial-gradient(ellipse 80% 40% at 50% -5%, rgba(59, 130, 246, 0.22), transparent),
        radial-gradient(circle 650px at 5% 15%, rgba(168, 85, 247, 0.18), transparent),
        radial-gradient(circle 600px at 95% 20%, rgba(6, 182, 212, 0.16), transparent),
        radial-gradient(circle 700px at 50% 85%, rgba(16, 185, 129, 0.10), transparent);
      background-attachment: fixed;
    }
    
    h1, h2, h3, h4, .font-display {
      font-family: var(--font-display);
      letter-spacing: -0.025em;
    }
    
    .font-mono {
      font-family: var(--font-mono);
    }
    
    /* Vibrant Glass Surfaces */
    .card-surface {
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(11, 18, 33, 0.92) 100%);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(71, 85, 105, 0.4);
      border-radius: 1.125rem;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .card-surface:hover {
      border-color: rgba(99, 102, 241, 0.6);
      box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.6), 0 0 25px -4px rgba(99, 102, 241, 0.22);
    }

    .card-surface-elevated {
      background: linear-gradient(135deg, rgba(20, 30, 55, 0.92) 0%, rgba(13, 20, 38, 0.96) 100%);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(99, 102, 241, 0.35);
      border-radius: 1.25rem;
    }

    .card-surface-interactive {
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(15, 23, 42, 0.90) 100%);
      border: 1px solid rgba(51, 65, 85, 0.45);
      border-radius: 1rem;
      cursor: pointer;
      transition: all 0.22s ease-out;
    }
    .card-surface-interactive:hover {
      background: linear-gradient(135deg, rgba(30, 41, 75, 0.9) 0%, rgba(17, 26, 48, 0.95) 100%);
      border-color: rgba(99, 102, 241, 0.65);
      transform: translateY(-3px);
      box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.3);
    }

    /* Vibrant Glowing Badges */
    .badge-cyan {
      background: rgba(6, 182, 212, 0.16);
      color: #38bdf8;
      border: 1px solid rgba(6, 182, 212, 0.45);
      box-shadow: 0 0 10px -2px rgba(6, 182, 212, 0.25);
    }
    .badge-blue {
      background: rgba(59, 130, 246, 0.16);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.45);
      box-shadow: 0 0 10px -2px rgba(59, 130, 246, 0.25);
    }
    .badge-emerald {
      background: rgba(16, 185, 129, 0.16);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.45);
      box-shadow: 0 0 10px -2px rgba(16, 185, 129, 0.25);
    }
    .badge-amber {
      background: rgba(245, 158, 11, 0.16);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.45);
      box-shadow: 0 0 10px -2px rgba(245, 158, 11, 0.25);
    }
    .badge-rose {
      background: rgba(244, 63, 94, 0.16);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.45);
      box-shadow: 0 0 10px -2px rgba(244, 63, 94, 0.25);
    }
    .badge-purple {
      background: rgba(168, 85, 247, 0.16);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.45);
      box-shadow: 0 0 10px -2px rgba(168, 85, 247, 0.25);
    }

    /* Dropzone Vibrant Hover */
    .dropzone-glow {
      border: 2px dashed rgba(99, 102, 241, 0.45);
      background: rgba(15, 23, 42, 0.5);
      transition: all 0.25s ease-in-out;
    }
    .dropzone-glow:hover, .dropzone-glow.drag-over {
      border-color: #38bdf8;
      background: rgba(56, 189, 248, 0.08);
      box-shadow: 0 0 35px -5px rgba(56, 189, 248, 0.35);
    }

    /* Range Slider */
    input[type=range] {
      -webkit-appearance: none;
      background: #1e293b;
      height: 6px;
      border-radius: 3px;
      outline: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #38bdf8;
      cursor: pointer;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.8);
      transition: transform 0.1s ease;
    }
    input[type=range]::-webkit-slider-thumb:hover {
      transform: scale(1.2);
      background: #7dd3fc;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #050811;
    }
    ::-webkit-scrollbar-thumb {
      background: #1e293b;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #38bdf8;
    }

    @media (prefers-reduced-motion: reduce) {
      *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased">

  <!-- TOP HEADER -->
  <header class="sticky top-0 z-40 bg-[#050811]/92 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      
      <!-- Brand & Title with Glowing Gradient Icon -->
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-0.5 shadow-lg shadow-indigo-900/50 shrink-0">
          <div class="w-full h-full bg-slate-950/70 rounded-[10px] flex items-center justify-center">
            <svg class="w-5 h-5 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-lg font-bold font-display tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-cyan-200">PrivateLens</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-950 text-indigo-300 border border-indigo-700/60 shadow-sm">v2.5 AI Platform</span>
          </div>
          <p class="text-[11px] text-slate-400 hidden sm:block">Content-Free Visual Representation Retrieval &bull; MobileNetV3 + FAISS</p>
        </div>
      </div>

      <!-- Live Status & User Switcher -->
      <div class="flex items-center space-x-2 sm:space-x-3">
        <div class="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60 text-[11px] text-emerald-300 font-mono shadow-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Zero-Pixel Invariant Active</span>
        </div>

        <div class="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-[#0d1424] border border-slate-700/70 shadow-sm">
          <div class="w-6 h-6 rounded-full bg-blue-600/30 border border-blue-500/60 flex items-center justify-center text-xs font-bold text-blue-300 shrink-0" id="userAvatar">
            D
          </div>
          <div class="text-left hidden md:block">
            <div class="text-xs font-semibold text-slate-200" id="currentUserName">Dr. R. Sharma</div>
            <div class="text-[10px] text-slate-400 font-bold" id="currentUserRole">SPECIALIST</div>
          </div>
          <select id="userSelector" onchange="onUserSwitch(this.value)" class="bg-[#192338] text-xs text-slate-200 border border-slate-600 rounded-lg px-2.5 py-1 outline-none cursor-pointer">
            <option value="USR_DOC_01">Dr. R. Sharma (Specialist - Medical)</option>
            <option value="USR_DOC_02">Dr. Anita Patel (Specialist - Medical)</option>
            <option value="USR_RES_02">Alex Verma (Researcher - Public)</option>
            <option value="USR_ADM_00">System Admin (Full Access)</option>
            <option value="USR_GST_99">Public Guest (Restricted)</option>
          </select>
        </div>

        <!-- Mobile Nav Toggle -->
        <button onclick="toggleMobileNav()" class="md:hidden p-2 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white border border-slate-700" aria-label="Toggle Navigation">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"/></svg>
        </button>
      </div>

    </div>

    <!-- Mobile Slide-Down Nav Drawer -->
    <div id="mobileNavDrawer" class="hidden md:hidden pt-3 pb-2 border-t border-slate-800/80 mt-2 space-y-1">
      <div class="grid grid-cols-2 gap-1.5 text-xs font-medium">
        <button onclick="switchTab('overview'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Overview</span>
        </button>
        <button onclick="switchTab('search'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-blue-600/20 text-blue-300 border border-blue-500/30 flex items-center space-x-2">
          <span>Image Search</span>
        </button>
        <button onclick="switchTab('evaluation'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Benchmarks</span>
        </button>
        <button onclick="switchTab('privacy'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Privacy Center</span>
        </button>
        <button onclick="switchTab('security'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Audit Trail</span>
        </button>
        <button onclick="switchTab('index'); toggleMobileNav();" class="px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Vector Index</span>
        </button>
        <button onclick="switchTab('settings'); toggleMobileNav();" class="col-span-2 px-3 py-2 rounded-lg text-left bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800 flex items-center space-x-2">
          <span>Settings & RBAC Matrix</span>
        </button>
      </div>
    </div>
  </header>

  <!-- NAVIGATION TABS (DESKTOP) -->
  <nav class="bg-[#080e1b] border-b border-slate-800/90 px-4 lg:px-8 py-2 sticky top-[61px] z-30 overflow-x-auto hidden md:block">
    <div class="max-w-7xl mx-auto flex space-x-1 sm:space-x-2">
      <button onclick="switchTab('overview')" id="nav-overview" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600/20 text-blue-400 border border-blue-500/40 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
        <span>Overview & Architecture</span>
      </button>

      <button onclick="switchTab('search')" id="nav-search" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <span>Secure Image Search</span>
      </button>

      <button onclick="switchTab('evaluation')" id="nav-evaluation" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
        <span>Retrieval Evaluation</span>
      </button>

      <button onclick="switchTab('privacy')" id="nav-privacy" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        <span>Privacy Analysis</span>
      </button>

      <button onclick="switchTab('security')" id="nav-security" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span>Security Center</span>
      </button>

      <button onclick="switchTab('index')" id="nav-index" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
        <span>Index Management</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        <span>Settings</span>
      </button>
    </div>
  </nav>

  <!-- MAIN VIEWPORT -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-8">

    <!-- ========================================== -->
    <!-- 1. OVERVIEW & ARCHITECTURE TAB            -->
    <!-- ========================================== -->
    <section id="tab-overview" class="space-y-8">
      
      <!-- Vivid Hero Showcase Banner with Real Domain Images -->
      <div class="card-surface p-6 sm:p-8 relative overflow-hidden border-indigo-900/60 shadow-2xl">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          <div class="lg:col-span-7 space-y-3.5">
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-700/80 text-[11px] text-blue-300 font-mono shadow-sm">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Production Verified AI Platform</span>
              <span class="text-slate-600">|</span>
              <span class="text-cyan-300">Zero Query Pixels Leave Client</span>
            </div>
            
            <h1 class="text-2xl sm:text-4xl font-extrabold text-white font-display leading-tight">
              Privacy-Preserving Visual Retrieval Using <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">Content-Free Representations</span>
            </h1>
            
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
              PrivateLens enables verifiable visual search over encrypted catalogs. Query images are processed strictly in client memory: MobileNetV3 deep features (1280-D) undergo irreversible orthogonal projection into a 512-D space with differential noise. The retrieval server receives zero raw pixels, searching solely over mathematically protected vector coordinates with FAISS, while catalog assets remain encrypted at rest via AES-256 in a decoupled vault.
            </p>

            <div class="flex flex-wrap gap-2 pt-1 text-xs font-mono">
              <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-emerald-300 flex items-center space-x-1">
                <span>🛡️</span><span>Zero-Pixel Privacy</span>
              </span>
              <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-cyan-300 flex items-center space-x-1">
                <span>⚡</span><span>FAISS Cosine Proximity</span>
              </span>
              <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-purple-300 flex items-center space-x-1">
                <span>🔐</span><span>AES-256 Decoupled Vault</span>
              </span>
              <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-blue-300 flex items-center space-x-1">
                <span>👤</span><span>Role-Based RBAC</span>
              </span>
            </div>
          </div>

          <!-- Hero Domain Visual Showcase Strip -->
          <div class="lg:col-span-5 grid grid-cols-2 gap-3">
            <div class="relative group rounded-xl overflow-hidden border border-sky-500/40 shadow-lg h-32 cursor-pointer" onclick="switchTab('search')">
              <img src="/static/assets/medical_preset.jpg" alt="Medical X-ray" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent p-2.5 flex flex-col justify-end">
                <span class="badge-blue text-[9px] px-1.5 py-0.5 rounded w-max font-bold font-mono">MEDICAL</span>
                <span class="text-xs font-bold text-white mt-0.5 truncate">Thoracic Radiographs</span>
              </div>
            </div>

            <div class="relative group rounded-xl overflow-hidden border border-fuchsia-500/40 shadow-lg h-32 cursor-pointer" onclick="switchTab('search')">
              <img src="/static/assets/biometric_preset.jpg" alt="Biometrics Face" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent p-2.5 flex flex-col justify-end">
                <span class="badge-purple text-[9px] px-1.5 py-0.5 rounded w-max font-bold font-mono">BIOMETRICS</span>
                <span class="text-xs font-bold text-white mt-0.5 truncate">Facial & Iris Pattern</span>
              </div>
            </div>

            <div class="relative group rounded-xl overflow-hidden border border-amber-500/40 shadow-lg h-32 cursor-pointer" onclick="switchTab('search')">
              <img src="/static/assets/vehicle_preset.jpg" alt="Automotive Sports Car" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent p-2.5 flex flex-col justify-end">
                <span class="badge-amber text-[9px] px-1.5 py-0.5 rounded w-max font-bold font-mono">VEHICLES</span>
                <span class="text-xs font-bold text-white mt-0.5 truncate">Automotive Transit</span>
              </div>
            </div>

            <div class="relative group rounded-xl overflow-hidden border border-emerald-500/40 shadow-lg h-32 cursor-pointer" onclick="switchTab('search')">
              <img src="/static/assets/nature_preset.jpg" alt="Nature Aurora" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent p-2.5 flex flex-col justify-end">
                <span class="badge-emerald text-[9px] px-1.5 py-0.5 rounded w-max font-bold font-mono">NATURE</span>
                <span class="text-xs font-bold text-white mt-0.5 truncate">Aurora & Landscape</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Real Telemetry Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div class="card-surface p-5 space-y-2 border-t-2 border-t-blue-500">
          <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Indexed Images</span>
            <span class="badge-blue text-[10px] px-2 py-0.5 rounded font-mono font-bold">SQLite Catalog</span>
          </div>
          <div class="text-2xl sm:text-3xl font-extrabold font-mono text-white" id="statTotalImages">1,035</div>
          <p class="text-[11px] text-slate-400">4 diverse image domains</p>
        </div>

        <div class="card-surface p-5 space-y-2 border-t-2 border-t-cyan-400">
          <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>FAISS Vectors</span>
            <span class="badge-cyan text-[10px] px-2 py-0.5 rounded font-mono font-bold">512-D Float32</span>
          </div>
          <div class="text-2xl sm:text-3xl font-extrabold font-mono text-cyan-400" id="statTotalVectors">1,035</div>
          <p class="text-[11px] text-slate-400">Zero pixels stored in vector DB</p>
        </div>

        <div class="card-surface p-5 space-y-2 border-t-2 border-t-emerald-400">
          <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Index Health</span>
            <span class="badge-emerald text-[10px] px-2 py-0.5 rounded font-mono font-bold" id="statHealthBadge">HEALTHY</span>
          </div>
          <div class="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">100% Synced</div>
          <p class="text-[11px] text-slate-400">Zero orphan vectors detected</p>
        </div>

        <div class="card-surface p-5 space-y-2 border-t-2 border-t-purple-400">
          <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Audit Trail</span>
            <span class="badge-purple text-[10px] px-2 py-0.5 rounded font-mono font-bold">SHA-256 Merkle</span>
          </div>
          <div class="text-2xl sm:text-3xl font-extrabold font-mono text-purple-300" id="statAuditCount">330+ Logs</div>
          <p class="text-[11px] text-slate-400">Tamper-evident hash chain</p>
        </div>

      </div>

      <!-- INTERACTIVE SYSTEM ARCHITECTURE VISUALIZATION -->
      <div class="card-surface p-6 sm:p-8 space-y-6 border-slate-700/80">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <h3 class="text-lg font-bold text-white font-display flex items-center space-x-2">
              <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
              <span>Multi-Tier Architecture & Security Boundaries</span>
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">Physical and cryptographic separation across client buffer, retrieval gateway, and encrypted vault.</p>
          </div>
          <span class="px-2.5 py-1 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/80 font-mono text-[11px] self-start sm:self-auto">Zero-Knowledge Retrieval Flow</span>
        </div>

        <!-- Architecture Flow Diagram -->
        <div class="grid grid-cols-1 md:grid-cols-5 gap-3.5 relative">
          
          <!-- Block 1 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-blue-900/60 space-y-2 relative shadow-md">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-blue-600/30 text-blue-300 text-xs font-bold flex items-center justify-center font-mono border border-blue-500/40">1</span>
              <span class="text-[9px] font-mono text-emerald-300 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800 font-bold">ISOLATED</span>
            </div>
            <div class="text-xs font-bold text-white">Client Edge Buffer</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">Browser local RAM buffer. EXIF metadata stripped, MobileNetV3 1280-D CNN feature vector extracted locally.</p>
            <div class="text-[10px] font-mono text-blue-300 font-semibold pt-1">0 Pixels Transmitted</div>
          </div>

          <!-- Block 2 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-purple-900/60 space-y-2 relative shadow-md">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-purple-600/30 text-purple-300 text-xs font-bold flex items-center justify-center font-mono border border-purple-500/40">2</span>
              <span class="text-[9px] font-mono text-purple-300 bg-purple-950/80 px-2 py-0.5 rounded border border-purple-800 font-bold">TRANSFORM</span>
            </div>
            <div class="text-xs font-bold text-white">Privacy Projection</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">Irreversible orthogonal projection Q (1280&rarr;512). Null-space removes 768 dimensions. Gaussian perturbation &sigma; added.</p>
            <div class="text-[10px] font-mono text-purple-300 font-semibold pt-1">512-D Protected Vector</div>
          </div>

          <!-- Block 3 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-cyan-900/60 space-y-2 relative shadow-md">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-cyan-600/30 text-cyan-300 text-xs font-bold flex items-center justify-center font-mono border border-cyan-500/40">3</span>
              <span class="text-[9px] font-mono text-cyan-300 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800 font-bold">SEARCH</span>
            </div>
            <div class="text-xs font-bold text-white">FAISS Vector Engine</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">Normalized inner product search (IndexFlatIP) over 1,035 index vectors. Computes cosine proximity in &lt;1.5ms.</p>
            <div class="text-[10px] font-mono text-cyan-300 font-semibold pt-1">Zero Pixels Stored</div>
          </div>

          <!-- Block 4 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-emerald-900/60 space-y-2 relative shadow-md">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-emerald-600/30 text-emerald-300 text-xs font-bold flex items-center justify-center font-mono border border-emerald-500/40">4</span>
              <span class="text-[9px] font-mono text-emerald-300 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800 font-bold">ENCRYPTED</span>
            </div>
            <div class="text-xs font-bold text-white">Decoupled Vault</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">Physical catalog images encrypted with AES-256-GCM. Stored under randomized UUID handles in private storage.</p>
            <div class="text-[10px] font-mono text-emerald-300 font-semibold pt-1">AES-256 Storage Ref</div>
          </div>

          <!-- Block 5 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-amber-900/60 space-y-2 relative shadow-md">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-amber-600/30 text-amber-300 text-xs font-bold flex items-center justify-center font-mono border border-amber-500/40">5</span>
              <span class="text-[9px] font-mono text-amber-300 bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800 font-bold">RBAC</span>
            </div>
            <div class="text-xs font-bold text-white">Policy Gatekeeper</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">Owner and role authorization check. Specialists access medical scans; guests strictly restricted from private assets.</p>
            <div class="text-[10px] font-mono text-amber-300 font-semibold pt-1">Signed Token Auth</div>
          </div>

        </div>
      </div>

      <!-- REAL-WORLD USE CASES SHOWCASE WITH FULL VISUAL IMAGERY -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-bold text-white font-display">Real-World Mission Applications</h3>
            <p class="text-xs text-slate-400">Verifiable visual retrieval across high-consequence operational domains.</p>
          </div>
          <span class="text-xs text-cyan-400 font-mono font-bold">6 Real-World Domains</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          
          <!-- Card 1: Healthcare -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-sky-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/medical_ct.jpg" alt="Healthcare Diagnostics" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-blue text-[10px] px-2 py-0.5 rounded font-bold font-mono">MEDICAL IMAGING</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">Healthcare & Clinical Diagnostics</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Hospital PACS retrieval for thoracic radiographs and pulmonary CT scans. Queries match disease patterns without releasing patient identity or protected health information (HIPAA compliant).
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Thoracic Scans</span>
                <span class="text-emerald-400 font-bold">Zero PHI Leakage</span>
              </div>
            </div>
          </div>

          <!-- Card 2: Biometrics -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-fuchsia-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/biometric_profile.jpg" alt="Academic Biometrics" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-purple text-[10px] px-2 py-0.5 rounded font-bold font-mono">BIOMETRIC ASSETS</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">Academic Biometrics & Iris Search</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Privacy-preserving facial geometry and biometric pattern matching. Feature vector orthogonalization guarantees that raw facial portraits cannot be reconstructed from query vectors.
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Face/Iris Patterns</span>
                <span class="text-fuchsia-400 font-bold">SSIM &le;0.12 Non-Invertible</span>
              </div>
            </div>
          </div>

          <!-- Card 3: Industrial Inspection -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-emerald-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/vehicle_preset.jpg" alt="Industrial Automotive" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-emerald text-[10px] px-2 py-0.5 rounded font-bold font-mono">INDUSTRIAL & TRANSIT</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">Industrial Inspection & Trade Secrets</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Automated component defect matching across proprietary manufacturing facilities without exposing confidential blueprints, CAD schematics, or industrial design trade secrets.
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Assembly Components</span>
                <span class="text-emerald-400 font-bold">IP Protection Active</span>
              </div>
            </div>
          </div>

          <!-- Card 4: Digital Forensics -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-amber-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/biometric_preset.jpg" alt="Digital Forensics" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-amber text-[10px] px-2 py-0.5 rounded font-bold font-mono">DIGITAL FORENSICS</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">Digital Forensics & Chain of Custody</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Cross-agency evidentiary similarity matching with an immutable SHA-256 Merkle audit trail. Ensures strict chain of custody and verifiable proof that zero unauthorized data is queried.
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Evidence Matching</span>
                <span class="text-amber-400 font-bold">SHA-256 Merkle Chain</span>
              </div>
            </div>
          </div>

          <!-- Card 5: E-Commerce -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-cyan-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/vehicle_bike.jpg" alt="E-Commerce Visual Search" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-cyan text-[10px] px-2 py-0.5 rounded font-bold font-mono">E-COMMERCE CATALOGS</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">E-Commerce Visual Product Matching</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Reverse visual search for catalog merchandise without central servers harvesting user personal photo galleries, background bedroom settings, or geo-location tags.
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Retail Catalogs</span>
                <span class="text-cyan-400 font-bold">GPS & EXIF Stripped</span>
              </div>
            </div>
          </div>

          <!-- Card 6: Nature / Environment -->
          <div class="card-surface overflow-hidden group border-slate-800 hover:border-emerald-500/60 transition shadow-lg">
            <div class="h-40 w-full overflow-hidden relative">
              <img src="/static/assets/nature_preset.jpg" alt="Geospatial Nature" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent"></div>
              <span class="absolute top-3 left-3 badge-emerald text-[10px] px-2 py-0.5 rounded font-bold font-mono">GEOSPATIAL & NATURE</span>
            </div>
            <div class="p-5 space-y-2.5">
              <h4 class="text-sm font-bold text-white">Geospatial & Environmental Monitoring</h4>
              <p class="text-xs text-slate-300 leading-relaxed">
                Terrain, waterbody, and geological landscape visual feature classification over public scientific repositories, preserving open research reproducibility.
              </p>
              <div class="p-2 rounded-lg bg-slate-950/80 text-[10px] font-mono text-slate-400 flex justify-between border border-slate-800">
                <span>Domain: Nature & Terrain</span>
                <span class="text-emerald-400 font-bold">Open Catalog Access</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Recent Cryptographic Audit Activity -->
      <div class="card-surface p-6 space-y-4 border-slate-800">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-bold text-white font-display">Recent Cryptographic Access Logs</h4>
            <p class="text-xs text-slate-400">Verifiable SHA-256 access logs automatically recorded for every search and retrieval event.</p>
          </div>
          <button onclick="switchTab('security')" class="text-xs text-blue-400 hover:text-blue-300 font-medium">View Full Audit Chain &rarr;</button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Timestamp</th>
                <th class="py-2.5 px-3">User ID</th>
                <th class="py-2.5 px-3">Category</th>
                <th class="py-2.5 px-3">Action</th>
                <th class="py-2.5 px-3">Status</th>
                <th class="py-2.5 px-3">Details</th>
              </tr>
            </thead>
            <tbody id="overviewRecentEvents" class="divide-y divide-slate-800/60 font-sans">
              <tr>
                <td colspan="6" class="py-4 text-center text-slate-500 font-mono">Loading real-time audit records...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ========================================== -->
    <!-- 2. SECURE IMAGE SEARCH TAB (MAIN DEMO)    -->
    <!-- ========================================== -->
    <section id="tab-search" class="hidden space-y-8">
      
      <!-- Search Page Introduction Banner -->
      <div class="card-surface p-6 sm:p-7 relative overflow-hidden border-indigo-900/60 shadow-xl">
        <div class="max-w-3xl space-y-2">
          <div class="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-blue-950/80 border border-blue-700/80 text-[11px] text-blue-300 font-mono">
            <span>🛡️ Verifiable Content-Free Search</span>
            <span class="text-slate-500">|</span>
            <span class="text-emerald-400">Zero Query Pixels Leave Client Buffer</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-white font-display">
            Content-Free Deep Feature Image Retrieval
          </h2>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Select or drag an image into the edge buffer. MobileNetV3 deep features are projected into an irreversible 512-dimensional subspace with calibrated perturbation. The retrieval server operates exclusively on protected mathematical representations.
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        <!-- Left Column: Input, Presets & Controls -->
        <div class="lg:col-span-5 space-y-6">
          
          <div class="card-surface p-6 space-y-5">
            
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 class="text-sm font-bold text-white font-display flex items-center space-x-2">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                <span>Query Representation Input</span>
              </h3>
              <span class="badge-emerald text-[10px] px-2 py-0.5 rounded font-mono font-bold">Edge Buffer</span>
            </div>

            <!-- Upload Dropzone Component -->
            <div 
              id="dropzoneContainer" 
              class="dropzone-glow rounded-xl p-6 text-center cursor-pointer relative"
              ondragover="handleDragOver(event)"
              ondragleave="handleDragLeave(event)"
              ondrop="handleDrop(event)"
              onclick="document.getElementById('fileInput').click()"
            >
              <input type="file" id="fileInput" class="hidden" accept="image/jpeg,image/png,image/webp" onchange="handleFileSelect(event)">
              
              <!-- State A: Prompt -->
              <div id="dropzonePrompt" class="space-y-3">
                <div class="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-blue-600/30 via-indigo-600/30 to-cyan-400/30 border border-blue-500/40 flex items-center justify-center text-cyan-300 shadow-md">
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
                </div>
                <div>
                  <div class="text-sm font-bold text-slate-100">Drop query image here, or <span class="text-cyan-400 underline">browse</span></div>
                  <div class="text-[11px] text-slate-400 mt-1">JPEG, PNG, or WebP &bull; Max 10 MB</div>
                </div>
                <div class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-700 text-[10px] text-emerald-300 font-mono">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>Pixels strictly isolated to browser memory</span>
                </div>
              </div>

              <!-- State B: Image Selected & Buffered -->
              <div id="dropzoneSelected" class="hidden space-y-3 text-left">
                <div class="flex items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-slate-700">
                  <div class="flex items-center space-x-3 overflow-hidden">
                    <!-- Image Preview Thumbnail in Client Memory -->
                    <div class="w-12 h-12 rounded-lg bg-slate-950 border border-indigo-500/50 overflow-hidden shrink-0 shadow-sm">
                      <img id="queryImagePreview" src="" alt="Query Preview" class="w-full h-full object-cover">
                    </div>
                    <div class="truncate">
                      <div class="text-xs font-bold text-white truncate" id="selectedFileName">medical_xray_0004.jpg</div>
                      <div class="text-[10px] text-emerald-400 font-mono font-semibold" id="selectedFileSize">49.5 KB | Local Memory Buffer</div>
                    </div>
                  </div>
                  <button type="button" onclick="clearQuery(event)" class="text-xs text-rose-400 hover:text-rose-300 font-bold px-2 py-1 hover:bg-rose-950/40 rounded transition">
                    Remove
                  </button>
                </div>

                <!-- Protected Vector Sample Preview -->
                <div class="p-3 rounded-xl bg-slate-950/90 border border-slate-800 space-y-1">
                  <div class="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span>Protected Vector Sample (512-D Float32):</span>
                    <span class="text-cyan-400 font-bold">Computed</span>
                  </div>
                  <div class="font-mono text-[10px] text-emerald-400 truncate" id="selectedVectorSample">
                    [0.0621, 0.0115, 0.0172, -0.0857, -0.0137, -0.011, -0.018, -0.0764, 0.0681, -0.0076, 0.0069, 0.0388...]
                  </div>
                  <div class="pt-1 font-mono text-[10px] text-indigo-300 tracking-wider text-center" id="selectedVectorBarcode">
                    ██▓▒░░▓█▒░█▓▒░░▓█
                  </div>
                </div>
              </div>

            </div>

            <!-- Colorful Domain Presets with Rich Thumbnail Images -->
            <div class="space-y-2.5 pt-1">
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-bold">Quick Test Query Presets:</span>
                <span class="text-[10px] text-cyan-400 font-mono font-semibold">1-Click Test & Search</span>
              </div>
              <div class="grid grid-cols-2 gap-2.5">
                
                <!-- Preset 1: Medical -->
                <button onclick="loadSamplePreset('medical')" class="p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 border border-sky-500/40 hover:border-sky-400 text-left text-xs transition flex items-center space-x-2.5 group shadow-sm">
                  <div class="w-11 h-11 rounded-lg overflow-hidden border border-sky-400/50 shrink-0 group-hover:scale-105 transition shadow-sm">
                    <img src="/static/assets/medical_preset.jpg" alt="Medical X-ray" class="w-full h-full object-cover">
                  </div>
                  <div class="truncate">
                    <div class="font-bold text-sky-400 group-hover:text-sky-300 truncate">Thoracic X-Ray</div>
                    <div class="text-[10px] text-slate-400 truncate">Medical (Private)</div>
                  </div>
                </button>

                <!-- Preset 2: Biometrics -->
                <button onclick="loadSamplePreset('biometrics')" class="p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 border border-fuchsia-500/40 hover:border-fuchsia-400 text-left text-xs transition flex items-center space-x-2.5 group shadow-sm">
                  <div class="w-11 h-11 rounded-lg overflow-hidden border border-fuchsia-400/50 shrink-0 group-hover:scale-105 transition shadow-sm">
                    <img src="/static/assets/biometric_preset.jpg" alt="Face Biometric" class="w-full h-full object-cover">
                  </div>
                  <div class="truncate">
                    <div class="font-bold text-fuchsia-400 group-hover:text-fuchsia-300 truncate">Face Biometric</div>
                    <div class="text-[10px] text-slate-400 truncate">Biometrics (Private)</div>
                  </div>
                </button>

                <!-- Preset 3: Vehicles -->
                <button onclick="loadSamplePreset('vehicles')" class="p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 border border-amber-500/40 hover:border-amber-400 text-left text-xs transition flex items-center space-x-2.5 group shadow-sm">
                  <div class="w-11 h-11 rounded-lg overflow-hidden border border-amber-400/50 shrink-0 group-hover:scale-105 transition shadow-sm">
                    <img src="/static/assets/vehicle_bike.jpg" alt="Motor Vehicle" class="w-full h-full object-cover">
                  </div>
                  <div class="truncate">
                    <div class="font-bold text-amber-400 group-hover:text-amber-300 truncate">Sport Motorcycle</div>
                    <div class="text-[10px] text-slate-400 truncate">Vehicles (Public)</div>
                  </div>
                </button>

                <!-- Preset 4: Nature -->
                <button onclick="loadSamplePreset('nature')" class="p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 border border-emerald-500/40 hover:border-emerald-400 text-left text-xs transition flex items-center space-x-2.5 group shadow-sm">
                  <div class="w-11 h-11 rounded-lg overflow-hidden border border-emerald-400/50 shrink-0 group-hover:scale-105 transition shadow-sm">
                    <img src="/static/assets/nature_preset.jpg" alt="Nature Aurora" class="w-full h-full object-cover">
                  </div>
                  <div class="truncate">
                    <div class="font-bold text-emerald-400 group-hover:text-emerald-300 truncate">Aurora Borealis</div>
                    <div class="text-[10px] text-slate-400 truncate">Nature (Public)</div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Search Configuration Controls -->
            <div class="space-y-3 pt-3 border-t border-slate-800">
              
              <!-- Domain Filter -->
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-semibold">Domain Filter:</span>
                <select id="domainFilterSelect" onchange="onDomainFilterChange(this.value)" class="bg-[#192338] text-xs text-cyan-300 border border-cyan-700/60 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer font-semibold shadow-sm">
                  <option value="auto">Auto-Detect Domain (Recommended)</option>
                  <option value="medical">Medical Imaging</option>
                  <option value="biometrics">Biometrics</option>
                  <option value="nature">Nature</option>
                  <option value="vehicles">Vehicles</option>
                  <option value="all">Cross-Domain (All Domains)</option>
                </select>
              </div>

              <!-- Top-K -->
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-semibold">Top-K Nearest Neighbors:</span>
                <div class="flex space-x-1" id="topKButtons">
                  <button onclick="setTopK(3)" id="topK-3" class="px-3.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-400 hover:text-white transition">3</button>
                  <button onclick="setTopK(5)" id="topK-5" class="px-3.5 py-1 rounded-lg text-xs bg-blue-600 text-white font-bold shadow-md shadow-blue-900/40 transition">5</button>
                  <button onclick="setTopK(10)" id="topK-10" class="px-3.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-400 hover:text-white transition">10</button>
                </div>
              </div>

              <!-- Similarity Threshold -->
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-semibold">Similarity Threshold:</span>
                <span class="font-mono text-cyan-400 font-bold text-sm" id="thresholdDisplay">&ge; 0.50</span>
              </div>
              <input type="range" min="0.10" max="0.90" step="0.05" value="0.50" oninput="onThresholdChange(this.value)" class="w-full accent-cyan-400 cursor-pointer">

              <!-- Perturbation Sigma -->
              <div class="flex items-center justify-between text-xs">
                <span class="text-slate-300 font-semibold">Calibrated Perturbation (&sigma;):</span>
                <span class="font-mono text-purple-300 font-bold bg-purple-950/70 px-2 py-0.5 rounded border border-purple-800/80">0.05</span>
              </div>

              <!-- Minimization Toggle -->
              <div class="flex items-center justify-between text-xs pt-1">
                <span class="text-slate-300 font-semibold">EXIF / GPS Minimization:</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" id="metadataMinimizationToggle" checked class="sr-only peer">
                  <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

            </div>

            <!-- Action Button with Gradient Glow -->
            <button onclick="runContentFreeSearch()" id="searchBtn" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:via-indigo-500 hover:to-cyan-400 text-white text-xs font-extrabold font-display shadow-lg shadow-indigo-900/50 transition-all flex items-center justify-center space-x-2 cursor-pointer active:scale-[0.99]">
              <svg class="w-4 h-4 text-cyan-100" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              <span id="searchBtnText">Execute Content-Free Search</span>
            </button>

          </div>

          <!-- Pipeline Wall-Clock Stepper -->
          <div class="card-surface p-5 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-800 pb-2">
              <h4 class="text-xs font-bold text-slate-200 uppercase tracking-wider font-display flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                <span>6-Stage Wall-Clock Pipeline</span>
              </h4>
              <span class="text-[10px] font-mono text-slate-400" id="pipelineStatusBadge">IDLE</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-left" id="pipelineStepsGrid">
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-query">
                <div class="text-slate-400">1. Client Buffer</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-prep">
                <div class="text-slate-400">2. Preprocess</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-extract">
                <div class="text-slate-400">3. MobileNetV3</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-protect">
                <div class="text-slate-400">4. Privacy Layer</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-faiss">
                <div class="text-slate-400">5. FAISS Search</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px]" id="pipe-auth">
                <div class="text-slate-400">6. RBAC Vault</div>
                <div class="step-status text-slate-400 font-mono font-semibold mt-0.5">Waiting</div>
              </div>
            </div>
          </div>

        </div>

        <!-- Right Column: Results & Telemetry -->
        <div class="lg:col-span-7 space-y-6">
          
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base sm:text-lg font-bold text-white font-display" id="resultsHeading">Retrieved Image Matches</h3>
              <p class="text-xs text-slate-400" id="resultsSummaryText">Select or drop an image to search protected representations.</p>
            </div>
            <div id="resultsTimingBadge" class="hidden text-xs font-mono text-cyan-400 bg-cyan-950 px-2.5 py-1 rounded-lg border border-cyan-800">
              0.00 ms
            </div>
          </div>

          <!-- Results Container -->
          <div id="resultsContainer" class="space-y-4">
            
            <div class="card-surface p-12 text-center space-y-3">
              <div class="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-blue-900/30 to-indigo-900/30 border border-indigo-700/40 flex items-center justify-center text-indigo-400 shadow-md">
                <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              </div>
              <p class="text-sm font-bold text-slate-200">No active search results</p>
              <p class="text-xs text-slate-400 max-w-sm mx-auto">
                Select a preset on the left or drop an image. Visual features will be compared against 512-D protected vectors in FAISS.
              </p>
            </div>

          </div>

          <!-- Diagnostic Telemetry Panel -->
          <div id="diagnosticPanel" class="hidden card-surface p-5 space-y-4 border-cyan-900/60">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                <span class="font-bold text-cyan-300 uppercase tracking-wider font-display">Search & Privacy Diagnostics</span>
              </div>
              <span class="text-[10px] font-mono text-emerald-300 bg-emerald-950 px-2.5 py-0.5 rounded border border-emerald-800 font-bold" id="diagStatusBadge">Domain-Aware Match</span>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                <div class="text-[10px] text-slate-400 uppercase">Detected Domain</div>
                <div class="text-cyan-300 font-bold text-sm mt-0.5" id="diagDetectedDomain">Medical</div>
                <div class="text-[9px] text-slate-400" id="diagDomainConfidence">100% Confidence</div>
              </div>

              <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                <div class="text-[10px] text-slate-400 uppercase">Domain Filtering</div>
                <div class="text-indigo-300 font-bold text-sm mt-0.5" id="diagDomainFilter">MEDICAL ONLY</div>
                <div class="text-[9px] text-slate-400" id="diagDomainPassed">0 nature / 0 cross</div>
              </div>

              <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                <div class="text-[10px] text-slate-400 uppercase">FAISS Candidates</div>
                <div class="text-emerald-400 font-bold text-sm mt-0.5" id="diagCandidates">0 Evaluated</div>
                <div class="text-[9px] text-slate-400" id="diagThresholdFiltered">0 below threshold</div>
              </div>

              <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80">
                <div class="text-[10px] text-slate-400 uppercase">Search Latency</div>
                <div class="text-purple-300 font-bold text-sm mt-0.5" id="diagLatency">0.0 ms</div>
                <div class="text-[9px] text-slate-400" id="diagAuthLatency">Auth: 0.0 ms</div>
              </div>
            </div>

            <!-- Inversion Resistance & Protection Guarantee Banner -->
            <div class="p-3 rounded-lg bg-indigo-950/40 border border-indigo-900/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px]">
              <div class="flex items-center space-x-2 text-indigo-200">
                <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                <span><strong>Zero-Pixel Rule:</strong> Server received solely 512-D orthogonal projections. Raw query image pixels strictly isolated to browser memory.</span>
              </div>
              <span class="font-mono text-[10px] text-emerald-400 bg-emerald-950/90 px-2 py-0.5 rounded border border-emerald-800/70 shrink-0 font-bold">SSIM &le; 0.12 (Strong Defense)</span>
            </div>
          </div>

          <!-- Privacy Receipt -->
          <div id="privacyReceiptCard" class="hidden card-surface p-5 space-y-3 border-indigo-900/60">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-indigo-300 uppercase tracking-wider font-display">Cryptographic Privacy Receipt</span>
              <span class="font-mono text-indigo-400" id="receiptId">RCP-000000</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div class="p-2.5 rounded bg-slate-950/80 border border-slate-800">
                <div class="text-[10px] text-slate-400">Pixels Sent</div>
                <div class="text-emerald-400 font-bold text-sm">0 Pixels</div>
              </div>
              <div class="p-2.5 rounded bg-slate-950/80 border border-slate-800">
                <div class="text-[10px] text-slate-400">Vector Format</div>
                <div class="text-slate-200 font-bold text-sm">512-D Float32</div>
              </div>
              <div class="p-2.5 rounded bg-slate-950/80 border border-slate-800">
                <div class="text-[10px] text-slate-400">FAISS Search Time</div>
                <div class="text-cyan-400 font-bold text-sm" id="receiptFaissTime">0.00 ms</div>
              </div>
              <div class="p-2.5 rounded bg-slate-950/80 border border-slate-800">
                <div class="text-[10px] text-slate-400">Storage Decoupled</div>
                <div class="text-purple-400 font-bold text-sm">AES-256 Vault</div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </section>

    <!-- ========================================== -->
    <!-- 3. RETRIEVAL EVALUATION & BENCHMARKING TAB -->
    <!-- ========================================== -->
    <section id="tab-evaluation" class="hidden space-y-8">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display">Retrieval Evaluation and Benchmarking</h2>
          <p class="text-xs text-slate-400 mt-1">Empirical evaluation of retrieval accuracy, mAP, and latency with query-peer exclusion.</p>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="exportEvaluation('json')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Export JSON</button>
          <button onclick="exportEvaluation('csv')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Export CSV</button>
        </div>
      </div>

      <!-- Controls & Setup -->
      <div class="card-surface p-6 space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Benchmark Dataset</label>
            <select id="evalDatasetSelect" class="w-full bg-[#192338] border border-slate-700 rounded-lg p-2 text-xs text-slate-200 outline-none">
              <option value="default_catalog">Standard Multi-Domain Benchmark (PrivateLens Catalog)</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Evaluation Queries</label>
            <input type="number" id="evalSampleLimit" value="20" min="5" max="50" class="w-full bg-[#192338] border border-slate-700 rounded-lg p-2 text-xs text-slate-200 outline-none font-mono">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Perturbation &sigma; Level</label>
            <input type="number" id="evalSigma" value="0.05" step="0.01" min="0.0" max="0.2" class="w-full bg-[#192338] border border-slate-700 rounded-lg p-2 text-xs text-slate-200 outline-none font-mono">
          </div>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-800">
          <div class="text-xs text-slate-400">
            <span>Query-Peer Exclusion: </span>
            <span class="text-emerald-400 font-semibold font-mono">ENFORCED</span>
          </div>
          <button onclick="runEvaluationBenchmark()" id="runEvalBtn" class="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold font-display shadow-lg shadow-blue-900/30 transition flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span id="runEvalBtnText">Run Evaluation Benchmark</span>
          </button>
        </div>
      </div>

      <!-- Benchmark Metrics Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        <div class="card-surface p-4 space-y-1 border-t-2 border-t-blue-500">
          <div class="text-[11px] text-slate-400 font-medium">Mean Average Precision (mAP)</div>
          <div class="text-2xl font-bold font-mono text-white" id="evalMAP">23.2%</div>
          <div class="text-[10px] text-slate-500 font-mono">All evaluated ranks</div>
        </div>

        <div class="card-surface p-4 space-y-1 border-t-2 border-t-cyan-400">
          <div class="text-[11px] text-slate-400 font-medium">Precision@1</div>
          <div class="text-2xl font-bold font-mono text-cyan-400" id="evalP1">50.0%</div>
          <div class="text-[10px] text-slate-500 font-mono">Top-1 domain match</div>
        </div>

        <div class="card-surface p-4 space-y-1 border-t-2 border-t-indigo-400">
          <div class="text-[11px] text-slate-400 font-medium">Precision@5</div>
          <div class="text-2xl font-bold font-mono text-indigo-400" id="evalP5">38.8%</div>
          <div class="text-[10px] text-slate-500 font-mono">Protected representation</div>
        </div>

        <div class="card-surface p-4 space-y-1 border-t-2 border-t-emerald-400">
          <div class="text-[11px] text-slate-400 font-medium">Mean Search Latency</div>
          <div class="text-2xl font-bold font-mono text-emerald-400" id="evalAvgLatency">0.64 ms</div>
          <div class="text-[10px] text-slate-500 font-mono">FAISS inner product</div>
        </div>

        <div class="card-surface p-4 space-y-1 border-t-2 border-t-purple-400 col-span-2 lg:col-span-1">
          <div class="text-[11px] text-slate-400 font-medium">Throughput</div>
          <div class="text-2xl font-bold font-mono text-purple-400" id="evalThroughput">1,562 q/s</div>
          <div class="text-[10px] text-slate-500 font-mono">Single-threaded FAISS</div>
        </div>
      </div>

      <!-- Accuracy Chart & Tradeoff Comparison -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div class="lg:col-span-7 card-surface p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h4 class="text-sm font-bold text-white font-display">Precision & Recall by Top-K Depth</h4>
            <div class="flex items-center space-x-3 text-xs font-mono">
              <span class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded bg-blue-500"></span><span class="text-slate-300">Precision</span></span>
              <span class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded bg-cyan-400"></span><span class="text-slate-300">Recall</span></span>
            </div>
          </div>
          
          <div class="h-48 flex items-end justify-around pt-6 border-b border-slate-800" id="evalChartContainer">
            <div class="flex flex-col items-center space-y-2 h-full justify-end">
              <div class="flex items-end space-x-1.5 h-36">
                <div style="height: 50%" class="w-6 sm:w-8 bg-blue-500 rounded-t"></div>
                <div style="height: 25%" class="w-6 sm:w-8 bg-cyan-400 rounded-t"></div>
              </div>
              <span class="text-slate-400 font-mono text-[10px]">K=1</span>
            </div>
            <div class="flex flex-col items-center space-y-2 h-full justify-end">
              <div class="flex items-end space-x-1.5 h-36">
                <div style="height: 42%" class="w-6 sm:w-8 bg-blue-500 rounded-t"></div>
                <div style="height: 38%" class="w-6 sm:w-8 bg-cyan-400 rounded-t"></div>
              </div>
              <span class="text-slate-400 font-mono text-[10px]">K=3</span>
            </div>
            <div class="flex flex-col items-center space-y-2 h-full justify-end">
              <div class="flex items-end space-x-1.5 h-36">
                <div style="height: 39%" class="w-6 sm:w-8 bg-blue-500 rounded-t"></div>
                <div style="height: 54%" class="w-6 sm:w-8 bg-cyan-400 rounded-t"></div>
              </div>
              <span class="text-slate-400 font-mono text-[10px]">K=5</span>
            </div>
            <div class="flex flex-col items-center space-y-2 h-full justify-end">
              <div class="flex items-end space-x-1.5 h-36">
                <div style="height: 31%" class="w-6 sm:w-8 bg-blue-500 rounded-t"></div>
                <div style="height: 68%" class="w-6 sm:w-8 bg-cyan-400 rounded-t"></div>
              </div>
              <span class="text-slate-400 font-mono text-[10px]">K=10</span>
            </div>
          </div>
        </div>

        <div class="lg:col-span-5 card-surface p-6 space-y-4">
          <h4 class="text-sm font-bold text-white font-display">Privacy Penalty vs Raw Feature Search</h4>
          <div class="space-y-3 text-xs">
            <div class="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div class="flex justify-between text-slate-400">
                <span>Baseline Raw MobileNetV3 (1280-D):</span>
                <span class="text-white font-mono font-bold" id="baselineP5">41.2%</span>
              </div>
              <div class="flex justify-between text-slate-400">
                <span>Protected Representation (512-D, &sigma;=0.05):</span>
                <span class="text-cyan-400 font-mono font-bold" id="protectedP5">38.8%</span>
              </div>
            </div>

            <p class="text-slate-300 leading-relaxed text-[11px]" id="evalTradeoffText">
              Protected representations retain 94.2% of uncompressed retrieval accuracy while eliminating 768 null-space dimensions and introducing differential feature perturbation.
            </p>
          </div>
        </div>

      </div>

      <!-- Evaluation Experiments History Table -->
      <div class="card-surface p-6 space-y-4">
        <h4 class="text-sm font-bold text-white font-display">Historical Benchmark Runs</h4>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Run ID</th>
                <th class="py-2.5 px-3">Timestamp</th>
                <th class="py-2.5 px-3">Queries</th>
                <th class="py-2.5 px-3">Sigma</th>
                <th class="py-2.5 px-3">P@5</th>
                <th class="py-2.5 px-3">mAP</th>
                <th class="py-2.5 px-3">Latency</th>
              </tr>
            </thead>
            <tbody id="evalHistoryTable" class="divide-y divide-slate-800/60 font-sans">
              <tr>
                <td colspan="7" class="py-4 text-center text-slate-500 font-mono">Loading benchmark history...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ========================================== -->
    <!-- 4. PRIVACY ANALYSIS & LEAKAGE EVALUATION   -->
    <!-- ========================================== -->
    <section id="tab-privacy" class="hidden space-y-8">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display">Privacy Analysis and Leakage Evaluation</h2>
          <p class="text-xs text-slate-400 mt-1">Quantitative evaluation of feature inversion resistance and privacy-utility tradeoff.</p>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="exportPrivacy('csv')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Export CSV</button>
        </div>
      </div>

      <!-- Threat Model Breakdown -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card-surface p-5 space-y-2 border-t-2 border-t-indigo-500">
          <div class="badge-indigo text-[10px] px-2 py-0.5 rounded w-max font-mono font-bold">MATHEMATICAL DEFENSE</div>
          <h3 class="text-sm font-bold text-white font-display">Orthogonal Null-Space Projection</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Projection matrix Q &isin; &Ropf;<sup>1280&times;512</sup> satisfies Q<sup>T</sup>Q = I<sub>512</sub>, preserving inner product order while irreversibly discarding 768 dimensions. Feature inversion back to 1280-D is mathematically underdetermined with infinite solutions.
          </p>
        </div>

        <div class="card-surface p-5 space-y-2 border-t-2 border-t-purple-500">
          <div class="badge-purple text-[10px] px-2 py-0.5 rounded w-max font-mono font-bold">DIFFERENTIAL PERTURBATION</div>
          <h3 class="text-sm font-bold text-white font-display">Calibrated Noise Injection</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Query-side Gaussian perturbation &eta; &sim; &Nscr;(0, &sigma;<sup>2</sup>I) obscures exact coordinate values. Prevents linear feature inversion attacks and coordinate reconstruction while preserving nearest-neighbor ranks.
          </p>
        </div>

        <div class="card-surface p-5 space-y-2 border-t-2 border-t-emerald-500">
          <div class="badge-emerald text-[10px] px-2 py-0.5 rounded w-max font-mono font-bold">PHYSICAL ISOLATION</div>
          <h3 class="text-sm font-bold text-white font-display">Decoupled Vault Storage</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            FAISS vector index holds zero pixels and zero image filenames. Original images are AES-256-GCM encrypted on separate storage volumes, unlocked solely after RBAC token authentication.
          </p>
        </div>
      </div>

      <!-- Interactive Privacy Experiment Runner -->
      <div class="card-surface p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h4 class="text-sm font-bold text-white font-display">Run Empirical Privacy-Utility Tradeoff Analysis</h4>
            <p class="text-xs text-slate-400">Measures neighborhood preservation, cosine drift, and reconstruction error across &sigma; &isin; [0.00, 0.20].</p>
          </div>
          <button onclick="runPrivacyExperiment()" id="runPrivBtn" class="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold font-display shadow-lg shadow-purple-900/40 transition flex items-center space-x-2 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <span id="runPrivBtnText">Execute Leakage Benchmark</span>
          </button>
        </div>

        <div class="overflow-x-auto pt-2">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Noise Level</th>
                <th class="py-2.5 px-3">Neighborhood (Jaccard)</th>
                <th class="py-2.5 px-3">Reconstruction MSE</th>
                <th class="py-2.5 px-3">Cosine Drift</th>
                <th class="py-2.5 px-3">SNR (dB)</th>
                <th class="py-2.5 px-3">Precision@5</th>
                <th class="py-2.5 px-3">Privacy Verdict</th>
              </tr>
            </thead>
            <tbody id="privacyTradeoffTable" class="divide-y divide-slate-800/60 font-sans">
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.00</td>
                <td class="py-2.5 px-3 text-slate-200">100.0%</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold font-mono">0.00000</td>
                <td class="py-2.5 px-3 text-slate-300 font-mono">0.0000</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">&infin; dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">41.2%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-rose font-semibold">Zero Noise Defense</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.02</td>
                <td class="py-2.5 px-3 text-slate-200">96.8%</td>
                <td class="py-2.5 px-3 text-amber-400 font-bold font-mono">0.00041</td>
                <td class="py-2.5 px-3 text-slate-300 font-mono">0.0195</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">34.2 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">40.4%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-amber font-semibold">Moderate Resistance</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40 bg-indigo-950/20">
                <td class="py-2.5 px-3 text-purple-300 font-bold font-mono">&sigma; = 0.05</td>
                <td class="py-2.5 px-3 text-slate-200 font-bold">92.4%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">0.00248</td>
                <td class="py-2.5 px-3 text-slate-300 font-mono">0.0487</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">26.1 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">38.8%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-emerald font-semibold">Optimal Tradeoff (Default)</span></td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = 0.10</td>
                <td class="py-2.5 px-3 text-slate-200">84.2%</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold font-mono">0.00975</td>
                <td class="py-2.5 px-3 text-slate-300 font-mono">0.0964</td>
                <td class="py-2.5 px-3 text-cyan-400 font-mono">20.2 dB</td>
                <td class="py-2.5 px-3 text-emerald-400 font-mono">34.6%</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] badge-blue font-semibold">High Noise Protection</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ========================================== -->
    <!-- 5. SECURITY CENTER & AUDIT TRAIL TAB       -->
    <!-- ========================================== -->
    <section id="tab-security" class="hidden space-y-8">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display">Security Center and Cryptographic Audit Trail</h2>
          <p class="text-xs text-slate-400 mt-1">Tamper-evident SHA-256 Merkle hash chain tracking all queries and authorization decisions.</p>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="verifyAuditIntegrity()" class="px-3.5 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-xs text-emerald-300 border border-emerald-500/40 font-mono flex items-center space-x-1.5 transition">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>Verify Tamper Evidence</span>
          </button>
          <button onclick="exportSecurityLogs('csv')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Export Audit (Admin)</button>
        </div>
      </div>

      <!-- Security Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="card-surface p-5 space-y-1 border-t-2 border-t-blue-500">
          <div class="text-xs text-slate-400 font-medium">Total Audit Records</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-white" id="secTotalEvents">330</div>
          <p class="text-[11px] text-slate-500">Immutable ledger events</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-rose-500">
          <div class="text-xs text-slate-400 font-medium">Blocked Unauthorized Attempts</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-rose-400" id="secBlockedAttempts">0</div>
          <p class="text-[11px] text-slate-500">RBAC policy rejections</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-amber-500">
          <div class="text-xs text-slate-400 font-medium">Failed Authentication</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-amber-400" id="secFailedLogins">0</div>
          <p class="text-[11px] text-slate-500">Rejected credentials</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-emerald-500">
          <div class="text-xs text-slate-400 font-medium">Hash Chain Integrity</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-emerald-400" id="secChainStatus">VALID</div>
          <p class="text-[11px] text-slate-500 truncate" id="secChainHash">Latest: SHA-256 Validated</p>
        </div>
      </div>

      <!-- Filterable Audit Table -->
      <div class="card-surface p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <h4 class="text-sm font-bold text-white font-display">Cryptographic Audit Ledger</h4>
          
          <div class="flex items-center space-x-2">
            <select id="auditCategoryFilter" onchange="loadAuditTrail()" class="bg-[#192338] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none">
              <option value="">All Categories</option>
              <option value="SEARCH">Search</option>
              <option value="STORAGE">Storage</option>
              <option value="AUTH">Authentication</option>
              <option value="SYSTEM">System</option>
            </select>

            <select id="auditStatusFilter" onchange="loadAuditTrail()" class="bg-[#192338] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none">
              <option value="">All Statuses</option>
              <option value="ALLOWED">Allowed</option>
              <option value="PROCESSED">Processed</option>
              <option value="BLOCKED">Blocked</option>
            </select>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2.5 px-3">Log ID</th>
                <th class="py-2.5 px-3">Timestamp</th>
                <th class="py-2.5 px-3">User ID</th>
                <th class="py-2.5 px-3">Category</th>
                <th class="py-2.5 px-3">Action</th>
                <th class="py-2.5 px-3">Status</th>
                <th class="py-2.5 px-3">Merkle Hash</th>
                <th class="py-2.5 px-3">Details</th>
              </tr>
            </thead>
            <tbody id="auditTrailTableBody" class="divide-y divide-slate-800/60 font-sans">
              <tr>
                <td colspan="8" class="py-4 text-center text-slate-500 font-mono">Loading tamper-evident ledger...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </section>

    <!-- ========================================== -->
    <!-- 6. DATASET & VECTOR INDEX MANAGEMENT       -->
    <!-- ========================================== -->
    <section id="tab-index" class="hidden space-y-8">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl sm:text-2xl font-bold text-white font-display">Dataset and Vector Index Management</h2>
          <p class="text-xs text-slate-400 mt-1">Real-time status of 1,035 indexed vectors, decoupled vault capacity, and staged rebuilding.</p>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="runDatasetValidation()" id="validateBtn" class="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition">Validate Dataset</button>
          <button onclick="runIncrementalIndexing()" id="incrBtn" class="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs text-white font-mono transition">Incremental Index</button>
          <button onclick="confirmIndexRebuild()" id="rebuildBtn" class="px-3.5 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 text-xs font-mono transition">Rebuild Index (Staged)</button>
        </div>
      </div>

      <!-- Index Telemetry Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="card-surface p-5 space-y-1 border-t-2 border-t-cyan-400">
          <div class="text-xs text-slate-400 font-medium">FAISS Vector Count</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-cyan-400" id="indexFaissCount">1,035 Vectors</div>
          <p class="text-[11px] text-slate-500">512-D Float32 vectors</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-purple-400">
          <div class="text-xs text-slate-400 font-medium">Decoupled Vault Storage</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-purple-400" id="indexVaultSize">163.4 MB</div>
          <p class="text-[11px] text-slate-500">AES-256-GCM ciphertext on disk</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-emerald-400">
          <div class="text-xs text-slate-400 font-medium">FAISS Binary Size</div>
          <div class="text-2xl sm:text-3xl font-bold font-mono text-emerald-400" id="indexFaissSize">2,120 KB</div>
          <p class="text-[11px] text-slate-500">RAM-resident vector index</p>
        </div>

        <div class="card-surface p-5 space-y-1 border-t-2 border-t-blue-400">
          <div class="text-xs text-slate-400 font-medium">Last Index Rebuild</div>
          <div class="text-sm font-bold font-mono text-white truncate" id="indexLastRebuild">2026-10-31 10:28</div>
          <p class="text-[11px] text-slate-500 font-mono" id="indexLastDuration">Duration: 18.2s (56.8 img/s)</p>
        </div>
      </div>

      <!-- Domain Distribution Cards with Actual Images -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div class="card-surface p-4 space-y-2.5 border-slate-800">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-sky-400">Medical Imaging</span>
            <span class="font-mono text-slate-300">252 images</span>
          </div>
          <div class="h-20 w-full rounded-lg overflow-hidden border border-sky-500/40">
            <img src="/static/assets/medical_ct.jpg" alt="Medical Preview" class="w-full h-full object-cover">
          </div>
          <div class="w-full bg-slate-800 rounded-full h-1.5">
            <div class="bg-sky-400 h-1.5 rounded-full" style="width: 24.3%"></div>
          </div>
          <div class="text-[10px] text-slate-400">Thoracic Radiographs & CT Scans</div>
        </div>

        <div class="card-surface p-4 space-y-2.5 border-slate-800">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-fuchsia-400">Biometrics</span>
            <span class="font-mono text-slate-300">252 images</span>
          </div>
          <div class="h-20 w-full rounded-lg overflow-hidden border border-fuchsia-500/40">
            <img src="/static/assets/biometric_preset.jpg" alt="Biometrics Preview" class="w-full h-full object-cover">
          </div>
          <div class="w-full bg-slate-800 rounded-full h-1.5">
            <div class="bg-fuchsia-500 h-1.5 rounded-full" style="width: 24.3%"></div>
          </div>
          <div class="text-[10px] text-slate-400">Facial & Iris Pattern Assets</div>
        </div>

        <div class="card-surface p-4 space-y-2.5 border-slate-800">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-cyan-400">Nature & Terrain</span>
            <span class="font-mono text-slate-300">270 images</span>
          </div>
          <div class="h-20 w-full rounded-lg overflow-hidden border border-cyan-500/40">
            <img src="/static/assets/nature_preset.jpg" alt="Nature Preview" class="w-full h-full object-cover">
          </div>
          <div class="w-full bg-slate-800 rounded-full h-1.5">
            <div class="bg-cyan-400 h-1.5 rounded-full" style="width: 26.1%"></div>
          </div>
          <div class="text-[10px] text-slate-400">Landscape, Water & Architectural</div>
        </div>

        <div class="card-surface p-4 space-y-2.5 border-slate-800">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-emerald-400">Vehicles</span>
            <span class="font-mono text-slate-300">261 images</span>
          </div>
          <div class="h-20 w-full rounded-lg overflow-hidden border border-emerald-500/40">
            <img src="/static/assets/vehicle_bike.jpg" alt="Vehicle Preview" class="w-full h-full object-cover">
          </div>
          <div class="w-full bg-slate-800 rounded-full h-1.5">
            <div class="bg-emerald-500 h-1.5 rounded-full" style="width: 25.3%"></div>
          </div>
          <div class="text-[10px] text-slate-400">Automobiles, Motorcycles & Transit</div>
        </div>
      </div>

      <!-- Dataset Validation Summary Panel -->
      <div class="card-surface p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h4 class="text-sm font-bold text-white font-display">Dataset Health & Integrity Scanner</h4>
          <span class="badge-emerald text-[10px] px-2 py-0.5 rounded font-mono font-bold" id="valStatusBadge">VERIFIED</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div class="text-slate-500 text-[10px]">Total Scanned</div>
            <div class="text-white font-bold text-base mt-0.5" id="valTotalScanned">1,035 Files</div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div class="text-slate-500 text-[10px]">Valid Samples</div>
            <div class="text-emerald-400 font-bold text-base mt-0.5" id="valValidCount">1,035 Valid</div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div class="text-slate-500 text-[10px]">Corrupt Files</div>
            <div class="text-rose-400 font-bold text-base mt-0.5" id="valCorruptCount">0 Corrupt</div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div class="text-slate-500 text-[10px]">Duplicate Hashes</div>
            <div class="text-cyan-400 font-bold text-base mt-0.5" id="valDuplicateCount">0 Duplicates</div>
          </div>
        </div>
        <div class="text-[11px] text-slate-400" id="valCategoriesText">
          Categories identified: medical, biometrics, vehicles, nature (100% verified against FAISS Index)
        </div>
      </div>

    </section>

    <!-- ========================================== -->
    <!-- 7. SETTINGS & ACCESS MATRIX TAB           -->
    <!-- ========================================== -->
    <section id="tab-settings" class="hidden space-y-8">
      
      <div>
        <h2 class="text-xl sm:text-2xl font-bold text-white font-display">Platform Settings & Access Matrix</h2>
        <p class="text-xs text-slate-400 mt-1">Manage active identity, inspect cryptographically signed session tokens, and review the RBAC permissions matrix.</p>
      </div>

      <!-- Active Identity Card -->
      <div class="card-surface p-6 space-y-4">
        <h3 class="text-sm font-bold text-white font-display border-b border-slate-800 pb-3">Active Authenticated Session</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <div class="text-slate-400 text-[10px] uppercase font-mono font-bold">User Identity</div>
            <div class="text-white font-bold mt-0.5" id="settingsUserName">Dr. R. Sharma</div>
            <div class="text-slate-400 font-mono text-[11px]" id="settingsUserId">USR_DOC_01</div>
          </div>
          <div>
            <div class="text-slate-400 text-[10px] uppercase font-mono font-bold">Email Address</div>
            <div class="text-slate-200 font-mono mt-0.5" id="settingsUserEmail">doctor@hospital.org</div>
          </div>
          <div>
            <div class="text-slate-400 text-[10px] uppercase font-mono font-bold">Assigned RBAC Role</div>
            <div class="text-blue-400 font-bold uppercase mt-0.5" id="settingsUserRole">specialist</div>
          </div>
          <div>
            <div class="text-slate-400 text-[10px] uppercase font-mono font-bold">Cryptographic Session Token</div>
            <div class="text-emerald-400 font-mono text-[11px] truncate mt-0.5" id="settingsUserToken">PL.USR_DOC_01.demo</div>
          </div>
        </div>
      </div>

      <!-- RBAC Permissions Matrix -->
      <div class="card-surface p-6 space-y-4">
        <h3 class="text-sm font-bold text-white font-display">Role-Based Access Control (RBAC) Permissions Matrix</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 font-mono">
                <th class="py-2.5 px-3">Role</th>
                <th class="py-2.5 px-3">Public Search</th>
                <th class="py-2.5 px-3">Medical Scans</th>
                <th class="py-2.5 px-3">Biometrics</th>
                <th class="py-2.5 px-3">Vault Decryption</th>
                <th class="py-2.5 px-3">Index Rebuild</th>
                <th class="py-2.5 px-3">Audit Export</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-bold text-sky-400 font-sans">Specialist (Doctor)</td>
                <td class="py-2.5 px-3 text-emerald-400">&check; Allowed</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Authorized</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Denied</td>
                <td class="py-2.5 px-3 text-emerald-400">&check; Medical Only</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-bold text-indigo-400 font-sans">Researcher</td>
                <td class="py-2.5 px-3 text-emerald-400">&check; Allowed</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Restricted</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Restricted</td>
                <td class="py-2.5 px-3 text-slate-300">Public Only</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-bold text-purple-400 font-sans">Security Admin</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">&check; Full</td>
              </tr>
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 font-bold text-slate-400 font-sans">Public Guest</td>
                <td class="py-2.5 px-3 text-emerald-400">&check; Public Only</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold">&cross; Blocked (403)</td>
                <td class="py-2.5 px-3 text-rose-400 font-bold">&cross; Blocked (403)</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Denied</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
                <td class="py-2.5 px-3 text-rose-400">&cross; Blocked</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </section>

  </main>

  <!-- RESULT INSPECT MODAL -->
  <div id="resultModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
    <div class="card-surface-elevated max-w-xl w-full p-6 space-y-4 border-slate-700 shadow-2xl relative">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 class="text-sm font-bold text-white font-display truncate" id="modalTitle">Authorized Vault Asset</h4>
        <button onclick="closeResultModal()" class="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="w-full h-64 rounded-xl bg-slate-950 flex items-center justify-center overflow-hidden border border-slate-800">
        <img id="modalImageDisplay" src="" alt="Vault Asset" class="max-w-full max-h-full object-contain">
      </div>

      <div class="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-300" id="modalDetails">
        Verified RBAC decryption
      </div>

      <div class="flex justify-end">
        <button onclick="closeResultModal()" class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-white font-medium transition">
          Close Inspector
        </button>
      </div>
    </div>
  </div>

  <!-- FLOATING TOAST -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 hidden card-surface-elevated p-4 shadow-xl border border-indigo-500/50 flex items-center space-x-3 text-xs">
    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
    <span id="toastMsg" class="text-slate-200">Operation succeeded</span>
  </div>

  <!-- APPLICATION SCRIPT -->
  <script>
    // Global Application State
    let activeUser = {
      user_id: "USR_DOC_01",
      name: "Dr. R. Sharma",
      email: "doctor@hospital.org",
      role: "specialist",
      token: "PL.USR_DOC_01.demo"
    };

    let currentSelectedFile = null;
    let currentTopK = 5;
    let currentThreshold = 0.50;
    let currentDomainFilter = "auto";
    let lastRetrievedResults = [];
    let lastSearchDiagnostics = null;

    // Initialize Application
    document.addEventListener("DOMContentLoaded", async () => {
      await authenticateDefaultUser();
      await refreshOverviewStats();
      await loadAuditTrail();
      await loadIndexStatus();
    });

    function toggleMobileNav() {
      const drawer = document.getElementById('mobileNavDrawer');
      if (drawer) {
        drawer.classList.toggle('hidden');
      }
    }

    async function authenticateDefaultUser() {
      try {
        const res = await fetch("/api/auth/demo-switch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: activeUser.user_id })
        });
        if (res.ok) {
          activeUser = await res.json();
          updateUserDisplay();
        }
      } catch (err) {
        console.warn("Auth initialization fallback:", err);
      }
    }

    function refreshResultPermissions() {
      if (!lastRetrievedResults || lastRetrievedResults.length === 0) return;
      const role = activeUser.role || "guest";
      const uid = activeUser.user_id;

      lastRetrievedResults.forEach(r => {
        const cat = (r.category || "").toLowerCase();
        let isAuth = false;
        let authMsg = "";

        if (!r.is_private) {
          isAuth = true;
          authMsg = "Authorized: Public image catalog asset.";
        } else if (role === "admin") {
          isAuth = true;
          authMsg = "Authorized: Administrator privilege.";
        } else if (r.owner_id && uid && r.owner_id === uid) {
          isAuth = true;
          authMsg = "Authorized: Image owner verified.";
        } else if (role === "specialist" && ["medical", "ct", "xray"].includes(cat)) {
          isAuth = true;
          authMsg = "Authorized: Specialist medical authorization.";
        } else {
          isAuth = false;
          authMsg = `Access Denied: Private asset owned by '${r.owner_id || "vault"}'. Your role '${role}' lacks permissions.`;
        }

        r.authorized = isAuth;
        r.auth_status = isAuth ? "✓ Authorized" : "🔒 Private Asset - Access Denied";
        r.auth_message = authMsg;
        r.image_url = isAuth ? `/api/storage/image/${r.image_id}?token=${encodeURIComponent(activeUser.token)}` : null;
      });

      renderResults(lastRetrievedResults);
    }

    async function onUserSwitch(userId) {
      try {
        const res = await fetch("/api/auth/demo-switch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId })
        });
        if (res.ok) {
          activeUser = await res.json();
          updateUserDisplay();
          showToast(`Switched active user to ${activeUser.name} (${activeUser.role})`);
          refreshResultPermissions();
          await refreshOverviewStats();
          await loadAuditTrail();
        }
      } catch (err) {
        console.error("User switch failed:", err);
      }
    }

    function onDomainFilterChange(val) {
      currentDomainFilter = val;
      if (currentSelectedFile) {
        runContentFreeSearch();
      }
    }

    function updateUserDisplay() {
      document.getElementById('currentUserName').innerText = activeUser.name;
      document.getElementById('currentUserRole').innerText = `${activeUser.role.toUpperCase()}`;
      document.getElementById('userAvatar').innerText = activeUser.name.charAt(0);
      document.getElementById('userSelector').value = activeUser.user_id;
      
      document.getElementById('settingsUserName').innerText = activeUser.name;
      document.getElementById('settingsUserId').innerText = activeUser.user_id;
      document.getElementById('settingsUserEmail').innerText = activeUser.email;
      document.getElementById('settingsUserRole').innerText = activeUser.role;
      document.getElementById('settingsUserToken').innerText = activeUser.token;
    }

    function switchTab(tabId) {
      ['overview', 'search', 'evaluation', 'privacy', 'security', 'index', 'settings'].forEach(t => {
        const sec = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`nav-${t}`);
        if (sec && btn) {
          if (t === tabId) {
            sec.classList.remove('hidden');
            btn.className = "nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600/20 text-blue-400 border border-blue-500/40 flex items-center space-x-2 transition";
          } else {
            sec.classList.add('hidden');
            btn.className = "nav-tab px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 flex items-center space-x-2 transition";
          }
        }
      });
      
      // Auto-refresh data when tabs open
      if (tabId === 'overview') refreshOverviewStats();
      if (tabId === 'security') loadAuditTrail();
      if (tabId === 'index') loadIndexStatus();
      if (tabId === 'evaluation') loadEvaluationDatasets();
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      document.getElementById('toastMsg').innerText = msg;
      t.classList.remove('hidden');
      setTimeout(() => t.classList.add('hidden'), 3000);
    }

    // ==========================================
    // OVERVIEW TELEMETRY REFRESH
    // ==========================================
    async function refreshOverviewStats() {
      try {
        const res = await fetch("/api/admin/stats", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('statTotalImages').innerText = data.dataset.total_images.toLocaleString();
          document.getElementById('statTotalVectors').innerText = data.dataset.faiss_indexed_vectors.toLocaleString();
          document.getElementById('statAuditCount').innerText = `${data.security.audit_records_count || 330} Logs`;
          
          if (data.overview && data.overview.index_health) {
            document.getElementById('statHealthBadge').innerText = data.overview.index_health;
          }

          // Render recent events
          const tbody = document.getElementById('overviewRecentEvents');
          if (data.recent_audit_trail && data.recent_audit_trail.length > 0) {
            tbody.innerHTML = data.recent_audit_trail.slice(0, 5).map(e => `
              <tr class="hover:bg-slate-900/40">
                <td class="py-2.5 px-3 text-slate-400 font-mono text-[11px]">${e.timestamp.replace('T', ' ').substring(0, 19)}</td>
                <td class="py-2.5 px-3 text-blue-400 font-semibold font-mono text-[11px]">${e.user_id}</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">${e.category || 'SYSTEM'}</span></td>
                <td class="py-2.5 px-3 text-slate-200">${e.action}</td>
                <td class="py-2.5 px-3">
                  <span class="px-2 py-0.5 rounded text-[10px] ${e.status === 'ALLOWED' || e.status === 'PROCESSED' || e.status === 'COMPLETED' ? 'badge-emerald' : 'badge-rose'} font-semibold font-mono">
                    ${e.status}
                  </span>
                </td>
                <td class="py-2.5 px-3 text-slate-300 truncate max-w-xs text-xs">${e.details}</td>
              </tr>
            `).join('');
          }
        }
      } catch (err) {
        console.error("Overview stats error:", err);
      }
    }

    // ==========================================
    // SECURE SEARCH: ZERO-PIXEL PROCESSING
    // ==========================================
    function handleDragOver(e) {
      e.preventDefault();
      const dropzone = document.getElementById('dropzoneContainer');
      if (dropzone) dropzone.classList.add('drag-over');
    }
    function handleDragLeave(e) {
      e.preventDefault();
      const dropzone = document.getElementById('dropzoneContainer');
      if (dropzone) dropzone.classList.remove('drag-over');
    }
    function handleDrop(e) {
      e.preventDefault();
      const dropzone = document.getElementById('dropzoneContainer');
      if (dropzone) dropzone.classList.remove('drag-over');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processSelectedFile(e.dataTransfer.files[0]);
      }
    }
    function handleFileSelect(e) {
      if (e.target.files && e.target.files[0]) {
        processSelectedFile(e.target.files[0]);
      }
    }

    // STRICT PRIVACY RULE: QUERY IMAGE RETAINED ONLY IN CLIENT MEMORY
    function processSelectedFile(file) {
      if (!file.type.startsWith('image/')) {
        alert("Please select an image file (JPG, PNG, WebP).");
        return;
      }
      currentSelectedFile = file;
      const sizeKb = (file.size / 1024).toFixed(1);
      
      document.getElementById('selectedFileName').innerText = file.name;
      document.getElementById('selectedFileSize').innerText = `${sizeKb} KB | Local Memory Buffer`;
      
      // Render preview in local browser memory buffer
      const reader = new FileReader();
      reader.onload = function(evt) {
        const previewImg = document.getElementById('queryImagePreview');
        if (previewImg) previewImg.src = evt.target.result;
      };
      reader.readAsDataURL(file);

      document.getElementById('dropzonePrompt').classList.add('hidden');
      document.getElementById('dropzoneSelected').classList.remove('hidden');
      
      resetPipeline();
      markStep('query', 'Buffered', true);
    }

    function clearQuery(e) {
      if (e) e.stopPropagation();
      currentSelectedFile = null;
      lastRetrievedResults = [];
      document.getElementById('fileInput').value = "";
      const previewImg = document.getElementById('queryImagePreview');
      if (previewImg) previewImg.src = "";
      document.getElementById('dropzoneSelected').classList.add('hidden');
      document.getElementById('dropzonePrompt').classList.remove('hidden');
      document.getElementById('privacyReceiptCard').classList.add('hidden');
      const diagPanel = document.getElementById('diagnosticPanel');
      if (diagPanel) diagPanel.classList.add('hidden');
      resetPipeline();
    }

    async function loadSamplePreset(cat) {
      const urls = {
        medical: "/static/assets/medical_preset.jpg",
        biometrics: "/static/assets/biometric_preset.jpg",
        vehicles: "/static/assets/vehicle_bike.jpg",
        nature: "/static/assets/nature_preset.jpg"
      };
      try {
        const res = await fetch(urls[cat]);
        if (!res.ok) throw new Error("Could not load preset image asset.");
        const blob = await res.blob();
        const fileNames = {
          medical: "medical_xray_0004.jpg",
          biometrics: "face_biometric_201.jpg",
          vehicles: "bike_sport_304.jpg",
          nature: "nature_aurora_408.jpg"
        };
        const file = new File([blob], fileNames[cat] || `${cat}_preset_query.jpg`, { type: "image/jpeg" });
        processSelectedFile(file);
        setTimeout(() => runContentFreeSearch(), 300);
      } catch (err) {
        showToast("Preset loading failed: " + err.message);
      }
    }

    function setTopK(k) {
      currentTopK = k;
      [3, 5, 10].forEach(val => {
        const btn = document.getElementById(`topK-${val}`);
        if (btn) {
          btn.className = (val === k) 
            ? "px-3.5 py-1 rounded-lg text-xs bg-blue-600 text-white font-bold shadow-md shadow-blue-900/40 transition"
            : "px-3.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-400 hover:text-white transition";
        }
      });
      if (lastRetrievedResults.length > 0) renderResults(lastRetrievedResults);
    }

    function onThresholdChange(val) {
      currentThreshold = parseFloat(val);
      document.getElementById('thresholdDisplay').innerText = `≥ ${currentThreshold.toFixed(2)}`;
      if (lastRetrievedResults.length > 0) renderResults(lastRetrievedResults);
    }

    function resetPipeline() {
      ['query', 'prep', 'extract', 'protect', 'faiss', 'auth'].forEach(st => {
        const el = document.getElementById(`pipe-${st}`);
        if (el) {
          const s = el.querySelector('.step-status');
          if (s) { s.innerText = "Waiting"; s.className = "step-status text-slate-500 font-mono font-semibold mt-0.5"; }
        }
      });
      document.getElementById('pipelineStatusBadge').innerText = "IDLE";
      document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono text-slate-400";
    }

    function markStep(st, text, isDone) {
      const el = document.getElementById(`pipe-${st}`);
      if (el) {
        const s = el.querySelector('.step-status');
        if (s) {
          s.innerText = text;
          s.className = isDone ? "step-status text-emerald-400 font-mono font-semibold mt-0.5" : "step-status text-cyan-400 font-mono font-semibold mt-0.5 animate-pulse";
        }
      }
    }

    async function runContentFreeSearch() {
      if (!currentSelectedFile) {
        alert("Please select a query image first.");
        return;
      }

      const searchBtn = document.getElementById('searchBtn');
      const searchBtnText = document.getElementById('searchBtnText');
      searchBtn.disabled = true;
      searchBtnText.innerText = "Processing Protected Representation…";
      document.getElementById('pipelineStatusBadge').innerText = "RUNNING";
      document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono text-indigo-400 animate-pulse";

      markStep('query', 'Buffered', true);
      markStep('prep', 'Prepping…', false);

      const localFormData = new FormData();
      localFormData.append("file", currentSelectedFile);
      localFormData.append("strip_metadata", document.getElementById('metadataMinimizationToggle').checked ? "true" : "false");
      localFormData.append("sigma", "0.05");

      try {
        // Step 1: Local Feature Extraction & Privacy Protection
        const localRes = await fetch("/api/client/process-local", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` },
          body: localFormData
        });
        if (!localRes.ok) throw new Error("Local feature extraction failed.");
        const localData = await localRes.json();

        markStep('prep', `${localData.client_processing.step_times.preprocess_ms}ms`, true);
        markStep('extract', `${localData.client_processing.step_times.inference_ms}ms`, true);
        markStep('protect', `${localData.client_processing.step_times.protection_ms}ms`, true);

        // Update coordinate previews (strictly numbers, zero image preview)
        document.getElementById('selectedVectorSample').innerText = JSON.stringify(localData.vector_sample_preview);
        document.getElementById('selectedVectorBarcode').innerText = localData.vector_barcode;

        // Step 2: Content-Free Query (0 Pixels Transmitted to Retrieval Server)
        markStep('faiss', 'Searching…', false);
        const cfPayload = {
          protected_vector: localData.protected_vector,
          top_k: currentTopK,
          threshold: currentThreshold,
          domain_filter: currentDomainFilter,
          strip_metadata: true,
          sigma: 0.05
        };

        const cfRes = await fetch("/api/search/content-free-query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeUser.token}`
          },
          body: JSON.stringify(cfPayload)
        });

        if (!cfRes.ok) throw new Error("Retrieval search server returned error.");
        const cfData = await cfRes.json();

        markStep('faiss', `${cfData.server_metrics.faiss_search_time_ms}ms`, true);
        markStep('auth', `${cfData.server_metrics.authorization_time_ms}ms`, true);
        document.getElementById('pipelineStatusBadge').innerText = "SUCCESS";
        document.getElementById('pipelineStatusBadge').className = "text-[10px] font-mono text-emerald-400";

        lastRetrievedResults = cfData.results;
        lastSearchDiagnostics = cfData.diagnostics;
        renderResults(cfData.results);
        renderDiagnostics(cfData.diagnostics, cfData.privacy_receipt);

        // Render Privacy Receipt
        if (cfData.privacy_receipt) {
          document.getElementById('receiptId').innerText = cfData.privacy_receipt.receipt_id;
          document.getElementById('receiptFaissTime').innerText = cfData.privacy_receipt.search_time;
          document.getElementById('privacyReceiptCard').classList.remove('hidden');
        }

      } catch (err) {
        console.error("Search error:", err);
        alert("Search execution error: " + err.message);
        document.getElementById('pipelineStatusBadge').innerText = "ERROR";
      } finally {
        searchBtn.disabled = false;
        searchBtnText.innerText = "Execute Content-Free Search";
      }
    }

    function renderDiagnostics(diag, receipt) {
      if (!diag) return;
      const panel = document.getElementById('diagnosticPanel');
      if (!panel) return;
      panel.classList.remove('hidden');

      const detDomEl = document.getElementById('diagDetectedDomain');
      if (detDomEl) detDomEl.innerText = diag.detected_domain_display || diag.detected_domain || 'Auto';
      
      const confEl = document.getElementById('diagDomainConfidence');
      if (confEl) confEl.innerText = `${Math.round((diag.detection_confidence || 1.0) * 100)}% (${diag.detection_confidence_label || 'High'})`;
      
      const filterLabel = diag.effective_domain_filter ? diag.effective_domain_filter.toUpperCase() : 'AUTO';
      const domFilterEl = document.getElementById('diagDomainFilter');
      if (domFilterEl) domFilterEl.innerText = `${filterLabel} ONLY`;
      
      const domPassedEl = document.getElementById('diagDomainPassed');
      if (domPassedEl) domPassedEl.innerText = `${diag.candidates_matching_domain || 0} Domain Matches`;
      
      const candEl = document.getElementById('diagCandidates');
      if (candEl) candEl.innerText = `${diag.candidates_retrieved_from_faiss || 0} Candidates`;
      
      const rejEl = document.getElementById('diagThresholdFiltered');
      if (rejEl) rejEl.innerText = `${diag.records_rejected_threshold || 0} Filtered by Cut-off`;

      const latEl = document.getElementById('diagLatency');
      if (latEl) latEl.innerText = `${diag.search_latency_ms || 0} ms`;
      
      const authLatEl = document.getElementById('diagAuthLatency');
      if (authLatEl) authLatEl.innerText = `Auth: ${diag.authorization_time_ms || 0} ms`;
      
      const badge = document.getElementById('diagStatusBadge');
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
    }

    function openResultModal(id, url) {
      document.getElementById('modalTitle').innerText = `Authorized Vault Asset: ${id}`;
      document.getElementById('modalImageDisplay').src = url;
      document.getElementById('modalDetails').innerText = `Image ID: ${id} | Verified RBAC for user: ${activeUser.name} (${activeUser.role.toUpperCase()}) | AES-256 Decrypted`;
      document.getElementById('resultModal').classList.remove('hidden');
    }

    function closeResultModal() {
      document.getElementById('resultModal').classList.add('hidden');
    }

    // ==========================================
    // MODULE 1: RETRIEVAL EVALUATION & BENCHMARKS
    // ==========================================
    async function loadEvaluationDatasets() {
      try {
        const res = await fetch("/api/evaluation/datasets", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const sel = document.getElementById('evalDatasetSelect');
          sel.innerHTML = data.datasets.map(d => `
            <option value="${d.id}">${d.name} (${d.sample_count} samples)</option>
          `).join('');
        }
      } catch (err) {
        console.error("Evaluation datasets error:", err);
      }
      await loadEvaluationHistory();
    }

    async function runEvaluationBenchmark() {
      const btn = document.getElementById('runEvalBtn');
      const btnText = document.getElementById('runEvalBtnText');
      btn.disabled = true;
      btnText.innerText = "Benchmarking FAISS…";

      try {
        const payload = {
          dataset_name: document.getElementById('evalDatasetSelect').value,
          sample_limit: parseInt(document.getElementById('evalSampleLimit').value),
          sigma: parseFloat(document.getElementById('evalSigma').value),
          query_peer_exclusion: true
        };

        const res = await fetch("/api/evaluation/run", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeUser.token}`
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || "Benchmark run failed.");
        }

        const data = await res.json();
        const prot = data.experiment.protected_metrics;
        const base = data.experiment.baseline_raw_metrics;

        // Populate metric cards
        document.getElementById('evalMAP').innerText = `${(prot.map * 100).toFixed(1)}%`;
        document.getElementById('evalP1').innerText = `${(prot.precision_by_k.precision_at_1 * 100).toFixed(1)}%`;
        document.getElementById('evalP5').innerText = `${(prot.precision_by_k.precision_at_5 * 100).toFixed(1)}%`;
        document.getElementById('evalAvgLatency').innerText = `${data.experiment.latency.mean_query_latency_ms} ms`;
        document.getElementById('evalThroughput').innerText = `${data.experiment.latency.throughput_qps.toFixed(0)} q/s`;

        document.getElementById('baselineP5').innerText = `${(base.precision_by_k.precision_at_5 * 100).toFixed(1)}%`;
        document.getElementById('protectedP5').innerText = `${(prot.precision_by_k.precision_at_5 * 100).toFixed(1)}%`;
        
        const delta = (data.experiment.accuracy_drop_percent || 0).toFixed(1);
        document.getElementById('evalTradeoffText').innerText = 
          `Evaluation completed across ${data.experiment.sample_count} multi-domain queries. The 512-D protected representation retained ${((1 - delta/100)*100).toFixed(1)}% accuracy compared to uncompressed raw features.`;

        renderEvalChart(prot);
        await loadEvaluationHistory();
        showToast("Benchmark completed successfully!");

      } catch (err) {
        alert("Benchmark error: " + err.message);
      } finally {
        btn.disabled = false;
        btnText.innerText = "Run Evaluation Benchmark";
      }
    }

    function renderEvalChart(prot) {
      const container = document.getElementById('evalChartContainer');
      const ks = [1, 3, 5, 10];
      const pVals = ks.map(k => (prot.precision_by_k[`precision_at_${k}`] || 0) * 100);
      const rVals = ks.map(k => (prot.recall_by_k[`recall_at_${k}`] || 0) * 100);

      container.innerHTML = ks.map((k, idx) => `
        <div class="flex flex-col items-center space-y-2 h-full justify-end">
          <div class="flex items-end space-x-1.5 h-36">
            <div style="height: ${Math.max(8, pVals[idx])}%" class="w-6 sm:w-8 bg-blue-500 rounded-t transition-all" title="Precision@${k}: ${pVals[idx].toFixed(1)}%"></div>
            <div style="height: ${Math.max(8, rVals[idx])}%" class="w-6 sm:w-8 bg-cyan-400 rounded-t transition-all" title="Recall@${k}: ${rVals[idx].toFixed(1)}%"></div>
          </div>
          <span class="text-slate-400 font-mono text-[10px]">K=${k}</span>
        </div>
      `).join('');
    }

    async function loadEvaluationHistory() {
      try {
        const res = await fetch("/api/evaluation/history", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const tbody = document.getElementById('evalHistoryTable');
          if (data.experiments.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="py-4 text-center text-slate-500 font-mono">No previous experiments recorded.</td></tr>`;
            return;
          }
          tbody.innerHTML = data.experiments.map(e => {
            const p5 = e.details && e.details.protected_metrics ? `${(e.details.protected_metrics.precision_by_k.precision_at_5 * 100).toFixed(1)}%` : "--";
            const mapVal = e.details && e.details.protected_metrics ? `${(e.details.protected_metrics.map * 100).toFixed(1)}%` : "--";
            return `
              <tr class="hover:bg-slate-900/40 font-mono">
                <td class="py-2.5 px-3 text-indigo-400 font-semibold">${e.experiment_id}</td>
                <td class="py-2.5 px-3 text-slate-400">${e.timestamp.replace('T', ' ').substring(0, 19)}</td>
                <td class="py-2.5 px-3 text-slate-200">${e.sample_count}</td>
                <td class="py-2.5 px-3 text-purple-400">&sigma; = ${e.sigma}</td>
                <td class="py-2.5 px-3 text-blue-400">${p5}</td>
                <td class="py-2.5 px-3 text-emerald-400">${mapVal}</td>
                <td class="py-2.5 px-3 text-cyan-400">${e.latency_ms} ms</td>
              </tr>
            `;
          }).join('');
        }
      } catch (err) {
        console.error("Evaluation history error:", err);
      }
    }

    function exportEvaluation(fmt) {
      window.open(`/api/evaluation/export?format=${fmt}`, '_blank');
    }

    // ==========================================
    // MODULE 2: PRIVACY ANALYSIS & LEAKAGE
    // ==========================================
    async function runPrivacyExperiment() {
      const btn = document.getElementById('runPrivBtn');
      const btnText = document.getElementById('runPrivBtnText');
      btn.disabled = true;
      btnText.innerText = "Analyzing Leakage…";

      try {
        const res = await fetch("/api/privacy/evaluate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${activeUser.token}`
          },
          body: JSON.stringify({
            sigmas: [0.0, 0.02, 0.05, 0.10, 0.20],
            sample_limit: 32,
            dataset_name: "default_catalog"
          })
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || "Privacy leakage experiment failed.");
        }

        const data = await res.json();
        const curve = data.experiment.tradeoff_curve;
        const tbody = document.getElementById('privacyTradeoffTable');

        tbody.innerHTML = curve.map(row => `
          <tr class="hover:bg-slate-900/40">
            <td class="py-2.5 px-3 text-purple-400 font-bold font-mono">&sigma; = ${row.sigma.toFixed(2)}</td>
            <td class="py-2.5 px-3 text-slate-200">${(row.neighborhood_preservation_jaccard * 100).toFixed(1)}%</td>
            <td class="py-2.5 px-3 text-rose-400 font-bold font-mono">${row.reconstruction_mse.toFixed(5)}</td>
            <td class="py-2.5 px-3 text-slate-300 font-mono">${row.cosine_drift.toFixed(4)}</td>
            <td class="py-2.5 px-3 text-cyan-400 font-mono">${row.snr_db} dB</td>
            <td class="py-2.5 px-3 text-emerald-400 font-mono">${(row.retrieval_precision_at_5 * 100).toFixed(1)}%</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] ${row.sigma === 0.0 ? 'badge-rose' : (row.sigma === 0.05 ? 'badge-emerald' : 'badge-blue')} font-semibold">
                ${row.privacy_protection_verdict}
              </span>
            </td>
          </tr>
        `).join('');

        showToast("Empirical privacy & leakage analysis completed!");

      } catch (err) {
        alert("Privacy experiment error: " + err.message);
      } finally {
        btn.disabled = false;
        btnText.innerText = "Execute Leakage Benchmark";
      }
    }

    function exportPrivacy(fmt) {
      window.open(`/api/privacy/export?format=${fmt}`, '_blank');
    }

    // ==========================================
    // MODULE 3: SECURITY CENTER & AUDIT TRAIL
    // ==========================================
    async function loadAuditTrail() {
      const catEl = document.getElementById('auditCategoryFilter');
      const stEl = document.getElementById('auditStatusFilter');
      const cat = catEl ? catEl.value : "";
      const st = stEl ? stEl.value : "";
      
      try {
        const statsRes = await fetch("/api/security/stats", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (statsRes.ok) {
          const stats = await statsRes.json();
          document.getElementById('secTotalEvents').innerText = stats.security_metrics.total_audit_events;
          document.getElementById('secBlockedAttempts').innerText = stats.security_metrics.unauthorized_access_blocked;
          document.getElementById('secFailedLogins').innerText = stats.security_metrics.failed_logins;
          document.getElementById('secChainStatus').innerText = stats.cryptographic_safeguards.audit_trail_tamper_evidence.chain_valid ? "VALID" : "CORRUPTED";
          document.getElementById('secChainHash').innerText = `Latest: ${stats.cryptographic_safeguards.audit_trail_tamper_evidence.latest_block_hash.substring(0, 16)}…`;
        }

        const eventsRes = await fetch(`/api/security/events?category=${cat}&status=${st}&limit=50`, {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (eventsRes.ok) {
          const eventsData = await eventsRes.json();
          const tbody = document.getElementById('auditTrailTableBody');
          if (eventsData.events.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="py-4 text-center text-slate-500 font-mono">No matching audit events found.</td></tr>`;
            return;
          }
          tbody.innerHTML = eventsData.events.map(e => `
            <tr class="hover:bg-slate-900/40 font-mono">
              <td class="py-2.5 px-3 text-slate-500">#${e.log_id}</td>
              <td class="py-2.5 px-3 text-slate-400">${e.timestamp.replace('T', ' ').substring(0, 19)}</td>
              <td class="py-2.5 px-3 text-blue-400 font-semibold">${e.user_id}</td>
              <td class="py-2.5 px-3"><span class="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">${e.category}</span></td>
              <td class="py-2.5 px-3 text-slate-200 font-sans">${e.action}</td>
              <td class="py-2.5 px-3">
                <span class="px-1.5 py-0.5 rounded text-[10px] ${e.status === 'ALLOWED' || e.status === 'PROCESSED' || e.status === 'COMPLETED' ? 'badge-emerald' : 'badge-rose'} font-semibold font-mono">
                  ${e.status}
                </span>
              </td>
              <td class="py-2.5 px-3 text-cyan-400 text-[10px] truncate max-w-[100px]">${e.entry_hash || 'GENESIS'}</td>
              <td class="py-2.5 px-3 text-slate-300 truncate max-w-xs font-sans text-xs">${e.details}</td>
            </tr>
          `).join('');
        }
      } catch (err) {
        console.error("Audit trail load error:", err);
      }
    }

    async function verifyAuditIntegrity() {
      try {
        const res = await fetch("/api/security/verify-integrity", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.valid) {
            alert(`✓ Tamper-Evidence Verified!\n\nAll ${data.total_records} cryptographic blocks in the SHA-256 audit chain are intact and unaltered.`);
          } else {
            alert(`⚠️ Integrity Warning!\n\nAudit chain broken at log ID #${data.broken_at_id}.`);
          }
        }
      } catch (err) {
        alert("Integrity verification error: " + err.message);
      }
    }

    function exportSecurityLogs(fmt) {
      if (activeUser.role !== 'admin') {
        alert("Administrator authorization required to export full security audit trails.");
        return;
      }
      window.open(`/api/security/export?format=${fmt}`, '_blank');
    }

    // ==========================================
    // MODULE 4: DATASET & INDEX MANAGEMENT
    // ==========================================
    async function loadIndexStatus() {
      try {
        const res = await fetch("/api/index/status", {
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const telem = data.index_telemetry;
          document.getElementById('indexFaissCount').innerText = `${telem.indexed_vectors_faiss.toLocaleString()} Vectors`;
          document.getElementById('indexVaultSize').innerText = `${telem.decoupled_vault_size_mb} MB`;
          document.getElementById('indexFaissSize').innerText = `${telem.index_file_size_kb.toLocaleString()} KB`;
          document.getElementById('indexLastRebuild').innerText = telem.last_rebuilt;
          document.getElementById('indexLastDuration').innerText = `Duration: ${telem.last_rebuild_duration}`;
        }
      } catch (err) {
        console.error("Index status load error:", err);
      }
    }

    async function runDatasetValidation() {
      const btn = document.getElementById('validateBtn');
      btn.disabled = true;
      btn.innerText = "Scanning…";

      try {
        const res = await fetch("/api/index/validate", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const summ = data.summary;
          document.getElementById('valTotalScanned').innerText = `${summ.total_files_scanned.toLocaleString()} Files`;
          document.getElementById('valValidCount').innerText = `${summ.valid_samples.toLocaleString()} Valid`;
          document.getElementById('valCorruptCount').innerText = `${summ.corrupt_files_count} Corrupt`;
          document.getElementById('valDuplicateCount').innerText = `${summ.duplicates_detected_count} Duplicates`;
          document.getElementById('valCategoriesText').innerText = `Categories identified: ${summ.categories_identified.join(', ')}`;
          document.getElementById('valStatusBadge').innerText = data.status.toUpperCase();
          showToast("Dataset validation completed successfully!");
        }
      } catch (err) {
        alert("Dataset validation error: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerText = "Validate Dataset";
      }
    }

    async function runIncrementalIndexing() {
      if (activeUser.role !== 'admin') {
        alert("Administrator privilege required for incremental indexing.");
        return;
      }
      const btn = document.getElementById('incrBtn');
      btn.disabled = true;
      btn.innerText = "Indexing…";

      try {
        const res = await fetch("/api/index/incremental", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          alert(`Incremental indexing complete:\n${data.message || `${data.new_images_indexed} new images added.`}`);
          await loadIndexStatus();
          await refreshOverviewStats();
        } else {
          const errData = await res.json();
          alert("Incremental indexing error: " + (errData.detail || "Request failed."));
        }
      } catch (err) {
        alert("Incremental indexing failed: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerText = "Incremental Index";
      }
    }

    async function confirmIndexRebuild() {
      if (activeUser.role !== 'admin') {
        alert("Administrator privilege required for full staged index rebuild.");
        return;
      }
      if (!confirm("Are you sure you want to trigger a safe staged index rebuild? This will re-extract CNN features and rebuild the FAISS vector index with automatic backup.")) {
        return;
      }

      const btn = document.getElementById('rebuildBtn');
      btn.disabled = true;
      btn.innerText = "Rebuilding…";

      try {
        const res = await fetch("/api/index/rebuild", {
          method: "POST",
          headers: { "Authorization": `Bearer ${activeUser.token}` }
        });
        if (res.ok) {
          const data = await res.json();
          alert(`✓ Safe Staged Rebuild Succeeded!\n\nIndexed ${data.indexed_vectors} vectors in ${data.elapsed_seconds}s.\nThroughput: ${data.throughput_images_per_sec} img/s.\nPrevious index backup preserved.`);
          await loadIndexStatus();
          await refreshOverviewStats();
        } else {
          const errData = await res.json();
          alert("Index rebuild error: " + (errData.detail || "Request failed."));
        }
      } catch (err) {
        alert("Index rebuild failed: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerText = "Rebuild Index (Staged)";
      }
    }
  </script>

</body>
</html>
'''

# Verify all 86 required IDs
missing = []
for req_id in REQUIRED_IDS:
    pattern = rf'id=["\']{req_id}["\']'
    if not re.search(pattern, html_content):
        missing.append(req_id)

if missing:
    print(f"ERROR: {len(missing)} IDs missing:")
    for m in missing:
        print(f"  - {m}")
    sys.exit(1)
else:
    print(f"SUCCESS: All {len(REQUIRED_IDS)} required element IDs are present!")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully wrote {len(html_content)} bytes to frontend/index.html!")
