import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def test_gen():
    os.makedirs("scratch/test_images", exist_ok=True)
    
    # 1. High-Res CT Scan (640x640)
    w, h = 640, 640
    img = Image.new("RGB", (w, h), color=(8, 10, 15))
    draw = ImageDraw.Draw(img)
    
    # Torso contour
    draw.ellipse([50, 70, 590, 570], fill=(20, 24, 32), outline=(140, 160, 180), width=6)
    # Subcutaneous fat layer
    draw.ellipse([65, 85, 575, 555], fill=(30, 35, 45), outline=(90, 100, 115), width=3)
    # Muscle / rib cage perimeter
    draw.ellipse([80, 100, 560, 540], fill=(15, 18, 25), outline=(180, 195, 215), width=8)
    
    # Ribs cross-sections
    for angle in range(25, 160, 22):
        rad = math.radians(angle)
        x1 = 320 - int(240 * math.sin(rad))
        y1 = 320 - int(220 * math.cos(rad))
        draw.ellipse([x1-12, y1-8, x1+12, y1+8], fill=(235, 240, 250), outline=(255, 255, 255))
        
        x2 = 320 + int(240 * math.sin(rad))
        draw.ellipse([x2-12, y1-8, x2+12, y1+8], fill=(235, 240, 250), outline=(255, 255, 255))
        
    # Thoracic spine / Vertebral body
    draw.ellipse([275, 470, 365, 535], fill=(240, 245, 255), outline=(210, 220, 235), width=3)
    draw.ellipse([305, 490, 335, 515], fill=(10, 12, 18)) # Spinal canal
    
    # Left and Right Lung Cavities (Darker parenchyma with vascular markings)
    draw.ellipse([105, 130, 280, 470], fill=(8, 12, 18), outline=(60, 80, 100), width=3)
    draw.ellipse([360, 130, 535, 470], fill=(8, 12, 18), outline=(60, 80, 100), width=3)
    
    # Bronchial tree / pulmonary vessels
    for lx, ly in [(190, 300), (450, 300)]:
        for offset in range(-50, 60, 20):
            draw.line([(lx, ly), (lx + offset, ly - 80)], fill=(120, 150, 180), width=3)
            draw.line([(lx, ly), (lx + offset*1.2, ly + 90)], fill=(100, 130, 160), width=2)
            draw.line([(lx, ly), (lx + (offset*1.5), ly + 20)], fill=(110, 140, 170), width=2)
            
    # Mediastinum / Heart silhouette
    draw.ellipse([250, 230, 390, 420], fill=(45, 55, 70), outline=(80, 100, 125), width=4)
    # Aorta cross-section
    draw.ellipse([290, 390, 335, 435], fill=(70, 85, 105), outline=(130, 150, 180), width=3)
    
    # Metadata HUD Overlay
    draw.text((25, 25), "AXIAL PULMONARY CT #101\nGE MEDICAL SYSTEM 64-SLICE\nFOV: 350mm | KV: 120 | MA: 280", fill=(140, 200, 255))
    draw.text((25, 590), "WW: 1500 WL: -600 (LUNG WINDOW)\nSLICE THICKNESS: 1.25mm", fill=(100, 160, 220))
    draw.text((580, 320), "R", fill=(180, 220, 255))
    draw.text((45, 320), "L", fill=(180, 220, 255))
    
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save("scratch/test_images/sample_ct.jpg", "JPEG", quality=95)
    print("Generated sample_ct.jpg successfully! Size:", os.path.getsize("scratch/test_images/sample_ct.jpg"), "bytes")

test_gen()
