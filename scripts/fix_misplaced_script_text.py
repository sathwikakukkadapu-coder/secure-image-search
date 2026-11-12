with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate the misplaced raw script outside </script>
target = """  </script>


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

</body>"""

replacement = """
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

  </script>
</body>"""

norm_target = target.replace('\r\n', '\n')
norm_text = text.replace('\r\n', '\n')

if norm_target in norm_text:
    norm_text = norm_text.replace(norm_target, replacement.replace('\r\n', '\n'))
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(norm_text)
    print("SUCCESS: Relocated wave script inside <script> tag! Zero raw text in HTML body!")
else:
    print("WARNING: target not matched directly, checking lines...")
    # Find position of last </script>
    last_script_end = text.rfind('</script>')
    body_end = text.rfind('</body>')
    between = text[last_script_end + 9:body_end]
    print(f"Content between </script> and </body>: {repr(between[:100])}")
    # Clear anything between </script> and </body>
    text = text[:last_script_end] + "\n" + between.strip() + "\n  </script>\n" + text[body_end:]
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Cleaned text between </script> and </body>!")
