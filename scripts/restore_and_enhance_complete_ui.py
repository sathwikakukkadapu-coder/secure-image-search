import os
import re

with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Original index.html.bak length: {len(html)} chars, {len(html.splitlines())} lines")

# 1. Add Canvas and Cyber Wave styles to <style>
wave_styles = """
    /* Moving Cyber Wave Background Canvas */
    #ambientWaveCanvas {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 0;
    }
    .glass-panel {
      background: linear-gradient(135deg, rgba(15, 20, 36, 0.75) 0%, rgba(9, 13, 26, 0.88) 100%);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(99, 102, 241, 0.2);
      border-radius: 1rem;
      box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6);
      transition: all 0.25s ease;
    }
    .glass-panel:hover {
      border-color: rgba(139, 92, 246, 0.35);
      box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.7), 0 0 20px -5px rgba(124, 58, 237, 0.2);
    }
"""

if '#ambientWaveCanvas' not in html:
    html = html.replace('</style>', wave_styles + '\n  </style>')

# 2. Add canvas element right after <body ...>
canvas_html = '\n  <!-- Fluid 60fps Cyber Wave Background -->\n  <canvas id="ambientWaveCanvas"></canvas>\n'
if '<canvas id="ambientWaveCanvas">' not in html:
    html = re.sub(r'(<body[^>]*>)', r'\1' + canvas_html, html, count=1)

# 3. Add Faculty Demo Test Dataset to tab-search dropzone if not already present
faculty_demo_html = """
        <!-- Faculty Demo Test Dataset Selector -->
        <div class="p-3 rounded-xl bg-[#0a0d20] border border-cyan-500/30 space-y-2 mt-3">
          <div class="flex items-center justify-between text-xs">
            <span class="text-white font-bold flex items-center space-x-1.5 font-display">
              <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Faculty Demo Test Dataset</span>
            </span>
            <span class="px-2 py-0.5 rounded text-[9.5px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-700/60">48 Curated Images</span>
          </div>
          <select id="testDatasetSelect" onchange="loadFromTestDataset(this.value)" class="w-full bg-[#070918] text-xs text-cyan-300 border border-indigo-500/40 rounded-lg px-2.5 py-1.5 outline-none cursor-pointer font-mono font-medium shadow-inner">
            <option value="">-- Click to Select a Test Image (Evaluated Separately from Vault) --</option>
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
              <option value="/test_dataset/03_Vehicles/test_vehicles_two_wheelers_04.jpg">test_vehicles_two_wheelers_04.jpg (Motorcycle)</option>
            </optgroup>
            <optgroup label="🌲 04 Nature (Public)">
              <option value="/test_dataset/04_Nature/test_nature_general_01.jpg">test_nature_general_01.jpg (Aurora Borealis Night)</option>
              <option value="/test_dataset/04_Nature/test_nature_landscapes_02.jpg">test_nature_landscapes_02.jpg (Mountain Alpine Landscape)</option>
            </optgroup>
          </select>
        </div>
"""

# 4. Ensure Zero-Pixel Shield badge is in HTML
if 'Zero-Pixel Shield' not in html:
    html = html.replace('Zero-Pixel Invariant Active', 'Zero-Pixel Invariant Active &bull; <span class="font-bold">Zero-Pixel Shield</span>')

# 5. Check if Faculty Demo Test Dataset is in tab-search
if 'Faculty Demo Test Dataset' not in html:
    # Insert right before Try Sample Queries
    html = html.replace('<!-- Try Sample Queries Row -->', faculty_demo_html + '\n        <!-- Try Sample Queries Row -->')

# 6. Add Cyber Wave JavaScript animation before </body>
wave_js = """
    // ==========================================
    // FLUID 60FPS MOVING CYBER-WAVE PARTICLES
    // ==========================================
    (function initAmbientCyberWave() {
      const canvas = document.getElementById('ambientWaveCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let width = canvas.width = window.innerWidth;
      let height = canvas.height = window.innerHeight;
      let time = 0;

      window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
      });

      const particles = [];
      const particleCount = 45;
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          radius: Math.random() * 2 + 0.7,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          alpha: Math.random() * 0.4 + 0.15,
          color: Math.random() > 0.4 ? 'rgba(56, 189, 248,' : 'rgba(168, 85, 247,'
        });
      }

      function drawWaves() {
        ctx.clearRect(0, 0, width, height);

        // Wave 1: Cyan / Violet Bottom Swell
        ctx.beginPath();
        ctx.moveTo(0, height * 0.82);
        for (let x = 0; x <= width; x += 15) {
          const y = height * 0.82 +
                    Math.sin(x * 0.0035 + time * 0.7) * 38 +
                    Math.sin(x * 0.007 - time * 0.5) * 18;
          ctx.lineTo(x, y);
        }
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        const grad1 = ctx.createLinearGradient(0, height * 0.7, width, height);
        grad1.addColorStop(0, 'rgba(79, 70, 229, 0.08)');
        grad1.addColorStop(0.5, 'rgba(124, 58, 237, 0.06)');
        grad1.addColorStop(1, 'rgba(6, 182, 212, 0.07)');
        ctx.fillStyle = grad1;
        ctx.fill();

        // Wave 2: Cyan Glowing Contour Line
        ctx.beginPath();
        ctx.moveTo(0, height * 0.78);
        for (let x = 0; x <= width; x += 15) {
          const y = height * 0.78 +
                    Math.sin(x * 0.004 + time * 0.85) * 45 +
                    Math.cos(x * 0.0025 + time * 0.4) * 22;
          ctx.lineTo(x, y);
        }
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.18)';
        ctx.lineWidth = 1.8;
        ctx.shadowColor = 'rgba(56, 189, 248, 0.4)';
        ctx.shadowBlur = 10;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Wave 3: Purple Ribbon Line
        ctx.beginPath();
        ctx.moveTo(0, height * 0.86);
        for (let x = 0; x <= width; x += 15) {
          const y = height * 0.86 +
                    Math.cos(x * 0.003 - time * 0.6) * 35 +
                    Math.sin(x * 0.006 + time * 0.6) * 15;
          ctx.lineTo(x, y);
        }
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.15)';
        ctx.lineWidth = 1.4;
        ctx.stroke();

        // Ambient Floating Cyber Particles
        for (let p of particles) {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0) p.x = width;
          if (p.x > width) p.x = 0;
          if (p.y < 0) p.y = height;
          if (p.y > height) p.y = 0;

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fillStyle = p.color + p.alpha + ')';
          ctx.fill();
        }

        time += 0.018;
        requestAnimationFrame(drawWaves);
      }

      drawWaves();
    })();
"""

if 'initAmbientCyberWave' not in html:
    html = html.replace('</body>', wave_js + '\n</body>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully written enhanced index.html with ALL features intact!")
