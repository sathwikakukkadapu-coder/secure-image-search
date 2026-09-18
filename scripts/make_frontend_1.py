import os

HTML_PART_1 = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Private Image Search | Privacy-Preserving Image Retrieval</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    body { font-family: 'Inter', sans-serif; background-color: #080c16; color: #f1f5f9; overflow-x: hidden; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glass-card { background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.88) 100%); border: 1px solid rgba(59, 130, 246, 0.22); backdrop-filter: blur(16px); }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-track { background: #0f172a; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
  </style>
</head>
<body class="custom-scroll antialiased min-h-screen flex flex-col selection:bg-blue-600 selection:text-white">

  <!-- TOP APP HEADER -->
  <header class="bg-[#0b101d]/95 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="p-2 rounded-lg bg-blue-950/60 border border-blue-500/40 text-cyan-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        </div>
        <div>
          <h1 class="text-sm sm:text-base font-bold text-white tracking-wide flex items-center gap-2">
            Private Image Search
            <span class="text-[10px] font-mono font-normal px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">Production Pipeline</span>
          </h1>
          <p class="text-[11px] text-slate-400">Find similar images while protecting original visual data</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <nav class="hidden md:flex items-center space-x-1 text-xs font-medium">
        <button onclick="switchTab('search')" id="tabBtn-search" class="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-semibold transition">Search Engine</button>
        <button onclick="switchTab('privacy')" id="tabBtn-privacy" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Privacy Architecture</button>
        <button onclick="switchTab('eval')" id="tabBtn-eval" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Evaluation</button>
        <button onclick="switchTab('admin')" id="tabBtn-admin" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Admin & Audit</button>
      </nav>

      <!-- User Profile Selector -->
      <div class="flex items-center space-x-3 text-xs">
        <div class="hidden lg:flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg font-mono text-[11px]">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-slate-400">Storage Invariant:</span>
          <span class="text-emerald-300">0 Pixels in Index</span>
        </div>

        <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg p-1">
          <span class="text-[10px] font-mono text-slate-400 pl-1.5">User:</span>
          <select id="userSelector" onchange="onUserChange()" class="bg-slate-800 border-0 text-xs font-semibold text-cyan-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500 cursor-pointer">
            <option value="USR_DOC_01">Dr. R. Sharma (Specialist - Medical Vault Owner)</option>
            <option value="USR_RES_02">Alex Verma (Researcher - Public Catalog)</option>
            <option value="USR_GST_99">Public Guest (Search Only - Locked Vault)</option>
            <option value="USR_ADM_00">System Admin (Full Vault Access)</option>
          </select>
        </div>
      </div>
    </div>
  </header>
"""
with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(HTML_PART_1)
print("Part 1 written")
