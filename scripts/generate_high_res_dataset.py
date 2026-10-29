"""
scripts/generate_high_res_dataset.py
Generates 32 High-Resolution (640x640), Presentation-Grade Images Across 4 Key Categories:
1. Medical (8 scans: CT Pulmonary, Thorax X-Ray, Brain MRI, Spine X-Ray, Abdominal CT)
2. Biometrics (8 scans: Face Frontal, Face Profile, Iris Patterns, Fingerprint Minutiae, Thermal Face)
3. Vehicles (8 vehicles: Sedan, Sports Coupe, Cruiser Bike, Superbike, SUV, EV Fastback, Scooter, Truck)
4. Nature & Architecture (8 scenes: Alpine Ridge, Forest Canopy, Skyscraper, Suspension Bridge, Ocean Surf, Desert Dunes, Gothic Cathedral, Aurora Borealis)
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

def create_gradient_bg(width, height, color1, color2, vertical=True):
    """Creates a smooth linear gradient background."""
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            val = int(255 * (y / height if vertical else x / width))
            mask_data.append(val)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

# ==============================================================================
# MEDICAL GENERATORS (High-Res 640x640)
# ==============================================================================

def draw_ct_scan(variant=1):
    img = create_gradient_bg(640, 640, (6, 8, 12), (14, 18, 26))
    draw = ImageDraw.Draw(img)
    
    # Outer body contour
    draw.ellipse([50, 70, 590, 570], fill=(22, 26, 35), outline=(130, 150, 175), width=6)
    draw.ellipse([65, 85, 575, 555], fill=(32, 38, 50), outline=(80, 95, 115), width=3)
    draw.ellipse([80, 100, 560, 540], fill=(14, 16, 22), outline=(190, 205, 225), width=8)
    
    # Ribs cross-sections
    for angle in range(25, 160, 20):
        rad = math.radians(angle)
        x1 = 320 - int(240 * math.sin(rad))
        y1 = 320 - int(220 * math.cos(rad))
        draw.ellipse([x1-12, y1-8, x1+12, y1+8], fill=(240, 245, 255), outline=(255, 255, 255))
        
        x2 = 320 + int(240 * math.sin(rad))
        draw.ellipse([x2-12, y1-8, x2+12, y1+8], fill=(240, 245, 255), outline=(255, 255, 255))
        
    # Thoracic spine / Vertebra
    draw.ellipse([275, 470, 365, 535], fill=(240, 245, 255), outline=(200, 215, 235), width=3)
    draw.ellipse([305, 490, 335, 515], fill=(10, 12, 18))
    
    # Lungs parenchyma
    draw.ellipse([105, 130, 280, 470], fill=(6, 10, 16), outline=(50, 70, 95), width=3)
    draw.ellipse([360, 130, 535, 470], fill=(6, 10, 16), outline=(50, 70, 95), width=3)
    
    # Vascular tree
    for lx, ly in [(190, 300), (450, 300)]:
        for offset in range(-55, 65, 18):
            draw.line([(lx, ly), (lx + offset, ly - 80)], fill=(130, 160, 190), width=3)
            draw.line([(lx, ly), (lx + offset*1.2, ly + 90)], fill=(110, 140, 170), width=2)
            draw.line([(lx, ly), (lx + (offset*1.5), ly + 20)], fill=(120, 150, 180), width=2)
            
    # Mediastinum & Cardiac silhouette
    draw.ellipse([250, 230, 390, 420], fill=(45, 55, 70), outline=(80, 100, 125), width=4)
    draw.ellipse([290, 390, 335, 435], fill=(70, 85, 105), outline=(130, 150, 180), width=3)
    
    # Diagnostic HUD Overlay
    title = f"CHEST CT AXIAL #PULM-80{variant}"
    draw.text((25, 25), f"{title}\nVOLUMETRIC MULTI-DETECTOR CT\nFOV: 350mm | KV: 120 | MA: 280", fill=(140, 200, 255))
    draw.text((25, 590), "WW: 1500 WL: -600 (LUNG WINDOW)\nSLICE THICKNESS: 1.25mm", fill=(100, 160, 220))
    draw.text((585, 315), "R", fill=(180, 220, 255))
    draw.text((45, 315), "L", fill=(180, 220, 255))
    
    return img.filter(ImageFilter.GaussianBlur(radius=0.5))

def draw_xray_scan(variant=1):
    img = create_gradient_bg(640, 640, (10, 12, 16), (20, 24, 32))
    draw = ImageDraw.Draw(img)
    
    # Clavicles
    draw.line([(140, 120), (300, 150)], fill=(220, 230, 245), width=12)
    draw.line([(500, 120), (340, 150)], fill=(220, 230, 245), width=12)
    
    # Spine column
    draw.line([(320, 110), (320, 520)], fill=(230, 240, 255), width=24)
    
    # Rib cage arc
    for i in range(8):
        y = 170 + i * 38
        draw.arc([100, y - 40, 320, y + 40], start=90, end=270, fill=(190, 210, 230), width=8)
        draw.arc([320, y - 40, 540, y + 40], start=270, end=90, fill=(190, 210, 230), width=8)
        
    # Lung fields (radiolucent dark regions)
    draw.ellipse([110, 160, 280, 480], fill=(12, 16, 24), outline=(100, 130, 160), width=4)
    draw.ellipse([360, 160, 530, 480], fill=(12, 16, 24), outline=(100, 130, 160), width=4)
    
    # Heart silhouette (left-shifted)
    draw.ellipse([270, 280, 420, 480], fill=(160, 180, 205), outline=(210, 225, 245), width=4)
    
    # Diaphragm domes
    draw.arc([80, 460, 320, 560], start=180, end=360, fill=(210, 225, 240), width=8)
    draw.arc([320, 480, 560, 580], start=180, end=360, fill=(210, 225, 240), width=8)
    
    # Radiograph stamps
    draw.text((25, 25), f"THORAX DIGITAL RADIOGRAPH #TX-44{variant}\nPOSTEROANTERIOR (PA) VIEW\nEXPOSURE: 110kVp / 4.0mAs", fill=(140, 200, 255))
    draw.text((580, 35), "PA", fill=(200, 230, 255))
    draw.text((580, 60), "R", fill=(200, 230, 255))
    
    return img.filter(ImageFilter.GaussianBlur(radius=0.7))

def draw_brain_mri(variant=1):
    img = create_gradient_bg(640, 640, (5, 6, 10), (12, 15, 22))
    draw = ImageDraw.Draw(img)
    
    # Cranium / Skull oval
    draw.ellipse([80, 60, 560, 580], fill=(25, 30, 40), outline=(220, 230, 245), width=8)
    draw.ellipse([95, 75, 545, 565], fill=(10, 14, 20), outline=(90, 110, 135), width=4)
    
    # Cerebral hemispheres & gyri / sulci convolutions
    draw.ellipse([110, 90, 310, 550], fill=(35, 45, 60), outline=(130, 155, 185), width=3)
    draw.ellipse([330, 90, 530, 550], fill=(35, 45, 60), outline=(130, 155, 185), width=3)
    
    # Interhemispheric fissure
    draw.line([(320, 90), (320, 550)], fill=(10, 14, 20), width=6)
    
    # Lateral ventricles
    draw.ellipse([270, 240, 310, 370], fill=(190, 215, 240), outline=(240, 250, 255), width=3)
    draw.ellipse([330, 240, 370, 370], fill=(190, 215, 240), outline=(240, 250, 255), width=3)
    
    # Sulcal lines
    for y in range(140, 500, 30):
        draw.arc([130, y, 290, y + 25], start=20, end=160, fill=(70, 90, 115), width=3)
        draw.arc([350, y, 510, y + 25], start=20, end=160, fill=(70, 90, 115), width=3)
        
    draw.text((25, 25), f"BRAIN MRI 3.0T #MRI-BR-{variant}\nT2-FLAIR AXIAL SLICE\nTR: 9000ms | TE: 95ms", fill=(140, 200, 255))
    draw.text((25, 595), "CONTRAST: GADOLINIUM-FREE", fill=(100, 160, 220))
    return img.filter(ImageFilter.GaussianBlur(radius=0.6))

def draw_spine_or_abdomen(variant=1):
    img = create_gradient_bg(640, 640, (8, 10, 14), (18, 22, 30))
    draw = ImageDraw.Draw(img)
    
    if variant == 1: # Lumbar Spine
        draw.line([(320, 50), (320, 590)], fill=(200, 215, 235), width=18)
        # Vertebral bodies L1 - L5
        for i, lvl in enumerate(["L1", "L2", "L3", "L4", "L5"]):
            y = 120 + i * 85
            draw.rectangle([250, y, 390, y + 55], fill=(225, 235, 250), outline=(255, 255, 255), width=3)
            # Disc space
            draw.rectangle([260, y + 55, 380, y + 70], fill=(20, 30, 45), outline=(100, 120, 150), width=2)
            draw.text((410, y + 18), lvl, fill=(140, 200, 255))
        draw.text((25, 25), "LUMBAR SPINE RADIOGRAPH #SPN-701\nLATERAL WEIGHT-BEARING\nLORDOSIS ANGLE: 48°", fill=(140, 200, 255))
    else: # Abdominal CT
        draw.ellipse([70, 100, 570, 540], fill=(20, 25, 35), outline=(130, 150, 175), width=6)
        # Liver (Right)
        draw.polygon([(110, 160), (280, 160), (310, 380), (130, 360)], fill=(75, 90, 110), outline=(140, 165, 195))
        # Spleen (Left)
        draw.ellipse([450, 200, 530, 320], fill=(65, 80, 100), outline=(130, 155, 185))
        # Kidneys
        draw.ellipse([180, 360, 250, 450], fill=(55, 70, 90), outline=(120, 145, 175))
        draw.ellipse([390, 360, 460, 450], fill=(55, 70, 90), outline=(120, 145, 175))
        # Aorta
        draw.ellipse([300, 380, 340, 420], fill=(160, 180, 210), outline=(230, 240, 255), width=3)
        draw.text((25, 25), "ABDOMINAL CONTRAST CT #ABD-901\nPORTAL VENOUS PHASE\nFOV: 380mm | SLICE: 2.0mm", fill=(140, 200, 255))
        
    return img.filter(ImageFilter.GaussianBlur(radius=0.5))

# ==============================================================================
# BIOMETRICS GENERATORS (High-Res 640x640)
# ==============================================================================

def draw_face_portrait(variant=1):
    img = create_gradient_bg(640, 640, (14, 12, 28), (28, 22, 54))
    draw = ImageDraw.Draw(img)
    
    # Biometric grid background
    for x in range(0, 640, 40):
        draw.line([(x, 0), (x, 640)], fill=(35, 30, 60), width=1)
    for y in range(0, 640, 40):
        draw.line([(0, y), (640, y)], fill=(35, 30, 60), width=1)
        
    # Face silhouette & contour
    draw.ellipse([180, 110, 460, 520], fill=(55, 48, 90), outline=(160, 140, 230), width=4)
    # Hair / Forehead
    draw.arc([160, 80, 480, 300], start=180, end=360, fill=(80, 65, 130), width=14)
    
    # Eyebrows
    draw.line([(220, 230), (285, 220)], fill=(190, 175, 245), width=5)
    draw.line([(355, 220), (420, 230)], fill=(190, 175, 245), width=5)
    
    # Eyes & Iris
    for ex in [250, 390]:
        draw.ellipse([ex - 35, 245, ex + 35, 285], fill=(230, 235, 250), outline=(130, 110, 210), width=3)
        draw.ellipse([ex - 18, 248, ex + 18, 282], fill=(56, 189, 248), outline=(14, 165, 233), width=2)
        draw.ellipse([ex - 8, 257, ex + 8, 273], fill=(8, 10, 16)) # Pupil
        draw.ellipse([ex - 4, 259, ex, 263], fill=(255, 255, 255)) # Catchlight
        
    # Nose bridge & base
    draw.line([(320, 235), (315, 345)], fill=(160, 140, 230), width=3)
    draw.line([(305, 350), (335, 350)], fill=(160, 140, 230), width=4)
    
    # Mouth & Lips
    draw.line([(275, 410), (365, 410)], fill=(210, 130, 180), width=5)
    draw.arc([275, 400, 365, 435], start=0, end=180, fill=(210, 130, 180), width=3)
    
    # 3D Biometric mesh tracking landmarks
    landmarks = [(250, 265), (390, 265), (320, 350), (275, 410), (365, 410), (320, 235), (320, 480)]
    for lx, ly in landmarks:
        draw.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(56, 189, 248), outline=(255, 255, 255))
    # Inter-landmark lines
    draw.line([landmarks[0], landmarks[2]], fill=(56, 189, 248), width=1)
    draw.line([landmarks[1], landmarks[2]], fill=(56, 189, 248), width=1)
    draw.line([landmarks[2], landmarks[3]], fill=(56, 189, 248), width=1)
    draw.line([landmarks[2], landmarks[4]], fill=(56, 189, 248), width=1)
    
    draw.text((25, 25), f"BIOMETRIC FACIAL IDENTIFIER #ID-20{variant}\nISO/IEC 19794-5 STANDARDS\nPOINTS: 128-PTS MESH | SCORE: 99.4%", fill=(167, 139, 250))
    return img

def draw_iris_scan(variant=1):
    img = create_gradient_bg(640, 640, (10, 15, 28), (18, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Polar biometric grid
    cx, cy = 320, 320
    for r in range(50, 270, 30):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(40, 70, 100), width=1)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        draw.line([(cx + int(50*math.cos(rad)), cy + int(50*math.sin(rad))),
                   (cx + int(260*math.cos(rad)), cy + int(260*math.sin(rad)))], fill=(40, 70, 100), width=1)
        
    # Sclera
    draw.ellipse([cx - 250, cy - 250, cx + 250, cy + 250], fill=(225, 235, 245), outline=(14, 165, 233), width=6)
    # Iris perimeter
    draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=(14, 116, 144), outline=(56, 189, 248), width=5)
    
    # Iris trabecular fibers
    for angle in range(0, 360, 4):
        rad = math.radians(angle)
        r_inner = 65 + (angle % 7) * 2
        r_outer = 175 - (angle % 5) * 3
        x1 = cx + int(r_inner * math.cos(rad))
        y1 = cy + int(r_inner * math.sin(rad))
        x2 = cx + int(r_outer * math.cos(rad))
        y2 = cy + int(r_outer * math.sin(rad))
        col = (6, 182, 212) if angle % 2 == 0 else (125, 211, 252)
        draw.line([(x1, y1), (x2, y2)], fill=col, width=2)
        
    # Pupil
    draw.ellipse([cx - 65, cy - 65, cx + 65, cy + 65], fill=(8, 10, 14), outline=(6, 182, 212), width=3)
    # Specular reflection
    draw.ellipse([cx - 30, cy - 35, cx - 15, cy - 20], fill=(255, 255, 255))
    
    draw.text((25, 25), f"BIOMETRIC IRIS PATTERN #IRS-20{variant}\nDAUGMAN POLAR ENCODING\nENTROPY: 3.2 BITS/MM² | QUAL: HIGH", fill=(56, 189, 248))
    return img

def draw_fingerprint_or_thermal(variant=1):
    img = create_gradient_bg(640, 640, (12, 10, 22), (25, 18, 42))
    draw = ImageDraw.Draw(img)
    cx, cy = 320, 320
    
    if variant == 1: # Fingerprint Minutiae
        draw.ellipse([140, 80, 500, 560], fill=(20, 16, 32), outline=(168, 85, 247), width=4)
        for r in range(30, 220, 14):
            # Elliptical ridge arches
            draw.arc([cx - r, cy - int(r*1.3), cx + r, cy + int(r*1.1)], start=10, end=170, fill=(216, 180, 254), width=4)
            draw.arc([cx - r, cy - int(r*1.1), cx + r, cy + int(r*1.3)], start=190, end=350, fill=(216, 180, 254), width=4)
        # Minutiae marker boxes
        for mx, my, label in [(270, 240, "BIF"), (370, 340, "END"), (310, 320, "CORE"), (250, 410, "BIF")]:
            draw.rectangle([mx - 10, my - 10, mx + 10, my + 10], outline=(236, 72, 153), width=2)
            draw.text((mx + 14, my - 6), label, fill=(244, 114, 182))
        draw.text((25, 25), "DERMAL RIDGE MINUTIAE #FPR-207\nAFIS NIST COMPLIANT FORMAT\nCORE: DETECTED | DELTA: DETECTED", fill=(216, 180, 254))
    else: # Thermal Facial Map
        draw.ellipse([180, 110, 460, 520], fill=(30, 58, 138), outline=(59, 130, 246), width=4)
        # Thermal heat zones
        draw.ellipse([220, 230, 420, 370], fill=(220, 38, 38)) # High heat nasal/forehead
        draw.ellipse([270, 270, 370, 340], fill=(251, 191, 36)) # Core zone
        draw.ellipse([200, 380, 440, 480], fill=(147, 51, 234)) # Cooler jaw
        draw.text((25, 25), "INFRARED THERMOGRAPHY #THM-208\nFLIR LWIR SENSOR (8-14μm)\nMAX TEMP: 37.1°C | MIN: 34.2°C", fill=(248, 113, 113))
        
    return img

# ==============================================================================
# VEHICLES GENERATORS (High-Res 640x640)
# ==============================================================================

def draw_car(car_type="sedan", variant=1):
    img = create_gradient_bg(640, 640, (15, 23, 42), (8, 12, 20))
    draw = ImageDraw.Draw(img)
    
    # Asphalt road & grid
    draw.rectangle([0, 460, 640, 640], fill=(20, 25, 35))
    draw.line([(0, 460), (640, 460)], fill=(71, 85, 105), width=3)
    draw.line([(0, 560), (640, 560)], fill=(234, 179, 8), width=4) # Road center line
    
    if car_type == "sedan":
        body_col = (37, 99, 235)
        roof_col = (29, 78, 216)
        label = f"MODERN AERODYNAMIC SEDAN #V-30{variant}"
    elif car_type == "sport":
        body_col = (220, 38, 38)
        roof_col = (185, 28, 28)
        label = f"HIGH-PERFORMANCE SPORTS COUPE #V-30{variant}"
    elif car_type == "suv":
        body_col = (5, 150, 105)
        roof_col = (4, 120, 87)
        label = f"ALL-WHEEL COMPACT SUV #V-30{variant}"
    else: # electric
        body_col = (6, 182, 212)
        roof_col = (14, 116, 144)
        label = f"CLEAN ENERGY EV FASTBACK #V-30{variant}"
        
    # Lower Body Chassis
    draw.rounded_rectangle([70, 310, 570, 460], radius=18, fill=body_col, outline=(255, 255, 255), width=2)
    # Greenhouse / Cabin Roof
    cabin_points = [(180, 310), (240, 210), (440, 210), (510, 310)]
    draw.polygon(cabin_points, fill=roof_col, outline=(255, 255, 255))
    
    # Windows
    draw.polygon([(200, 305), (250, 225), (330, 225), (330, 305)], fill=(147, 197, 253))
    draw.polygon([(345, 225), (430, 225), (490, 305), (345, 305)], fill=(147, 197, 253))
    
    # Headlights & Taillights
    draw.polygon([(545, 335), (570, 335), (565, 365), (540, 365)], fill=(254, 240, 138))
    draw.polygon([(70, 335), (95, 335), (100, 365), (75, 365)], fill=(239, 68, 68))
    
    # Wheels (Alloy rims + Rubber tires)
    for wx in [180, 460]:
        draw.ellipse([wx - 55, 405, wx + 55, 515], fill=(15, 23, 42), outline=(100, 116, 139), width=8)
        draw.ellipse([wx - 35, 425, wx + 35, 495], fill=(203, 213, 225), outline=(148, 163, 184), width=4)
        draw.ellipse([wx - 15, 445, wx + 15, 475], fill=(30, 41, 59)) # Center cap
        
    draw.text((25, 25), f"{label}\nPOWERTRAIN: PERFORMANCE TUNED\nAERODYNAMIC DRAG COEFFICIENT: Cd 0.24", fill=(148, 163, 184))
    return img

def draw_motorcycle(bike_type="cruiser", variant=1):
    img = create_gradient_bg(640, 640, (15, 23, 42), (10, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # Road
    draw.rectangle([0, 470, 640, 640], fill=(24, 30, 40))
    draw.line([(0, 470), (640, 470)], fill=(100, 116, 139), width=3)
    
    # Wheels
    for wx in [150, 490]:
        draw.ellipse([wx - 65, 395, wx + 65, 525], fill=(15, 23, 42), outline=(148, 163, 184), width=10)
        draw.ellipse([wx - 40, 420, wx + 40, 500], fill=(71, 85, 105), outline=(226, 232, 240), width=4)
        for a in range(0, 360, 45):
            rad = math.radians(a)
            draw.line([(wx, 460), (wx + int(38*math.cos(rad)), 460 + int(38*math.sin(rad)))], fill=(203, 213, 225), width=2)
            
    # Frame & Engine Block
    draw.polygon([(220, 380), (370, 380), (390, 460), (240, 460)], fill=(51, 65, 85), outline=(203, 213, 225), width=3)
    
    # Fuel tank
    tank_color = (234, 88, 12) if bike_type == "cruiser" else (34, 197, 94)
    draw.ellipse([260, 280, 410, 350], fill=tank_color, outline=(255, 255, 255), width=3)
    
    # Exhaust pipe (Chrome)
    draw.line([(270, 450), (510, 450)], fill=(226, 232, 240), width=12)
    # Handlebars
    draw.line([(380, 240), (430, 210)], fill=(203, 213, 225), width=7)
    
    label = f"V-TWIN CRUISER MOTORCYCLE #B-0{variant}" if bike_type == "cruiser" else f"SUPERBIKE RACING MOTORCYCLE #B-1{variant}"
    draw.text((25, 25), f"{label}\nENGINE: 1200CC DOHC 4-VALVE\nBRAKING: DUAL BREMBO CALIPERS", fill=(148, 163, 184))
    return img

def draw_heavy_or_scooter(variant=1):
    img = create_gradient_bg(640, 640, (15, 23, 42), (10, 15, 25))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 480, 640, 640], fill=(24, 30, 40))
    
    if variant == 1: # Urban Scooter
        draw.ellipse([160, 440, 260, 540], fill=(15, 23, 42), outline=(100, 116, 139), width=8)
        draw.ellipse([420, 440, 520, 540], fill=(15, 23, 42), outline=(100, 116, 139), width=8)
        # Step-through deck
        draw.rounded_rectangle([200, 450, 440, 490], radius=10, fill=(244, 63, 94), outline=(255, 255, 255), width=2)
        # Stem and Handlebars
        draw.line([(440, 470), (400, 260)], fill=(203, 213, 225), width=6)
        draw.line([(380, 260), (420, 260)], fill=(15, 23, 42), width=8)
        draw.text((25, 25), "URBAN ELECTRIC COMMUTER #SCT-307\nBATTERY: 72V 30Ah LITHIUM-ION\nRANGE: 85 KM PER CHARGE", fill=(244, 114, 182))
    else: # Cargo Hauler Truck
        # Cab
        draw.rounded_rectangle([360, 200, 580, 460], radius=14, fill=(234, 179, 8), outline=(255, 255, 255), width=3)
        draw.rectangle([440, 230, 570, 310], fill=(147, 197, 253)) # Windshield
        # Cargo Trailer
        draw.rounded_rectangle([60, 140, 350, 460], radius=10, fill=(71, 85, 105), outline=(203, 213, 225), width=3)
        # Wheels
        for wx in [140, 220, 300, 500]:
            draw.ellipse([wx - 35, 430, wx + 35, 500], fill=(15, 23, 42), outline=(148, 163, 184), width=6)
        draw.text((25, 25), "COMMERCIAL CARGO HAULER #TRK-308\nGROSS VEHICLE WEIGHT: 36,000 KG\nDIESEL TURBOCHARGED 450 HP", fill=(253, 224, 71))
        
    return img

# ==============================================================================
# NATURE & ARCHITECTURE GENERATORS (High-Res 640x640)
# ==============================================================================

def draw_nature_mountain_forest(scene="mountain", variant=1):
    if scene == "mountain":
        img = create_gradient_bg(640, 640, (30, 41, 59), (12, 74, 110))
        draw = ImageDraw.Draw(img)
        # Sun / Moon
        draw.ellipse([450, 80, 540, 170], fill=(254, 240, 138))
        # Mountain Back Range
        draw.polygon([(40, 480), (220, 200), (380, 480)], fill=(71, 85, 105))
        draw.polygon([(220, 200), (380, 480), (580, 240), (640, 480)], fill=(51, 65, 85))
        # Snowcaps
        draw.polygon([(180, 260), (220, 200), (260, 260)], fill=(248, 250, 252))
        draw.polygon([(540, 290), (580, 240), (620, 290)], fill=(248, 250, 252))
        # Foreground Lake & Pine Trees
        draw.rectangle([0, 480, 640, 640], fill=(15, 23, 42))
        label = f"ALPINE GLACIAL RIDGE #GEO-40{variant}"
    else: # Forest
        img = create_gradient_bg(640, 640, (15, 23, 42), (6, 78, 59))
        draw = ImageDraw.Draw(img)
        # Pine tree silhouettes
        for i in range(12):
            tx = 30 + i * 55
            ty = 260 + (i % 3) * 40
            draw.polygon([(tx - 40, ty + 200), (tx, ty), (tx + 40, ty + 200)], fill=(4, 47, 46))
            draw.polygon([(tx - 30, ty + 120), (tx, ty), (tx + 30, ty + 120)], fill=(13, 148, 136))
        label = f"PINE FOREST CANOPY #GEO-40{variant}"
        
    draw.text((25, 25), f"{label}\nBIOME CLASSIFICATION: TEMPERATE CONIFEROUS\nELEVATION: 2,450 METERS", fill=(203, 213, 225))
    return img

def draw_architecture(arch_type="tower", variant=1):
    img = create_gradient_bg(640, 640, (15, 23, 42), (49, 46, 129))
    draw = ImageDraw.Draw(img)
    
    if arch_type == "tower":
        # Skyscraper
        draw.rectangle([220, 100, 420, 640], fill=(30, 27, 75), outline=(129, 140, 248), width=3)
        # Spire
        draw.line([(320, 40), (320, 100)], fill=(199, 210, 254), width=4)
        # Windows illumination matrix
        for wy in range(120, 620, 24):
            for wx in range(235, 410, 20):
                if (wx + wy) % 5 != 0:
                    draw.rectangle([wx, wy, wx + 12, wy + 14], fill=(254, 240, 138))
        label = f"CONTEMPORARY SKYSCRAPER #ARC-40{variant}"
    elif arch_type == "bridge":
        # Suspension Bridge
        draw.rectangle([0, 500, 640, 640], fill=(12, 74, 110)) # Water
        # Towers
        draw.rectangle([140, 180, 190, 520], fill=(220, 38, 38), outline=(255, 255, 255))
        draw.rectangle([450, 180, 500, 520], fill=(220, 38, 38), outline=(255, 255, 255))
        # Main Cables
        draw.arc([165, 180, 475, 480], start=0, end=180, fill=(254, 240, 138), width=4)
        # Vertical Suspenders
        for sx in range(200, 450, 25):
            draw.line([(sx, 330), (sx, 480)], fill=(226, 232, 240), width=2)
        label = f"SUSPENSION ARCH BRIDGE #ARC-40{variant}"
    else: # Cathedral
        draw.polygon([(200, 560), (320, 120), (440, 560)], fill=(51, 65, 85), outline=(203, 213, 225), width=3)
        draw.ellipse([270, 250, 370, 350], fill=(30, 41, 59), outline=(234, 179, 8), width=4) # Rose window
        label = f"GOTHIC CATHEDRAL FACADE #ARC-40{variant}"
        
    draw.text((25, 25), f"{label}\nSTRUCTURAL SYSTEM: STEEL & REINFORCED CONCRETE\nSEISMIC COMPLIANCE: ZONE 4 RATED", fill=(199, 210, 254))
    return img

def draw_ocean_desert_aurora(scene="ocean", variant=1):
    if scene == "ocean":
        img = create_gradient_bg(640, 640, (15, 23, 42), (14, 116, 144))
        draw = ImageDraw.Draw(img)
        # Horizon and surf
        for y in range(350, 640, 40):
            draw.arc([40, y, 600, y + 60], start=0, end=180, fill=(240, 249, 255), width=5)
        label = f"DEEP OCEAN SURF #GEO-40{variant}"
    elif scene == "desert":
        img = create_gradient_bg(640, 640, (120, 53, 15), (251, 191, 36))
        draw = ImageDraw.Draw(img)
        # Dunes
        draw.polygon([(0, 640), (220, 380), (450, 520), (640, 410), (640, 640)], fill=(217, 119, 6))
        draw.polygon([(220, 380), (450, 520), (340, 640), (0, 640)], fill=(180, 83, 9))
        label = f"DESERT SAND DUNES #GEO-40{variant}"
    else: # Aurora
        img = create_gradient_bg(640, 640, (3, 7, 18), (17, 24, 39))
        draw = ImageDraw.Draw(img)
        # Stars
        for _ in range(120):
            draw.point((random.randint(0, 640), random.randint(0, 380)), fill=(255, 255, 255))
        # Aurora ribbon (Neon Green + Violet)
        draw.arc([60, 100, 580, 340], start=160, end=340, fill=(52, 211, 153), width=24)
        draw.arc([100, 140, 540, 380], start=160, end=340, fill=(167, 139, 250), width=18)
        # Snowy ground
        draw.polygon([(0, 540), (320, 480), (640, 520), (640, 640), (0, 640)], fill=(226, 232, 240))
        label = f"ARCTIC AURORA BOREALIS #GEO-40{variant}"
        
    draw.text((25, 25), f"{label}\nGEOGRAPHIC LOCATION: 68°N LATITUDE\nATMOSPHERIC MONITORING ACTIVE", fill=(240, 249, 255))
    return img

# ==============================================================================
# MAIN DATASET GENERATOR DISPATCHER
# ==============================================================================

def generate_all_32_images():
    print("==================================================")
    print("  Generating 32 High-Resolution Dataset Images    ")
    print("==================================================")
    
    spec = {
        "medical": [
            ("ct_pulmonary_101.jpg", lambda: draw_ct_scan(1)),
            ("ct_pulmonary_102.jpg", lambda: draw_ct_scan(2)),
            ("xray_thorax_103.jpg", lambda: draw_xray_scan(3)),
            ("xray_thorax_104.jpg", lambda: draw_xray_scan(4)),
            ("mri_brain_105.jpg", lambda: draw_brain_mri(5)),
            ("mri_brain_106.jpg", lambda: draw_brain_mri(6)),
            ("xray_spine_107.jpg", lambda: draw_spine_or_abdomen(1)),
            ("ct_abdomen_108.jpg", lambda: draw_spine_or_abdomen(2)),
        ],
        "biometrics": [
            ("face_biometric_201.jpg", lambda: draw_face_portrait(1)),
            ("face_biometric_202.jpg", lambda: draw_face_portrait(2)),
            ("face_profile_203.jpg", lambda: draw_face_portrait(3)),
            ("face_profile_204.jpg", lambda: draw_face_portrait(4)),
            ("iris_scan_205.jpg", lambda: draw_iris_scan(5)),
            ("iris_scan_206.jpg", lambda: draw_iris_scan(6)),
            ("fingerprint_minutiae_207.jpg", lambda: draw_fingerprint_or_thermal(1)),
            ("face_thermal_208.jpg", lambda: draw_fingerprint_or_thermal(2)),
        ],
        "vehicles": [
            ("car_sedan_301.jpg", lambda: draw_car("sedan", 1)),
            ("car_sport_302.jpg", lambda: draw_car("sport", 2)),
            ("bike_cruiser_303.jpg", lambda: draw_motorcycle("cruiser", 3)),
            ("bike_sport_304.jpg", lambda: draw_motorcycle("sport", 4)),
            ("car_suv_305.jpg", lambda: draw_car("suv", 5)),
            ("car_electric_306.jpg", lambda: draw_car("electric", 6)),
            ("scooter_urban_307.jpg", lambda: draw_heavy_or_scooter(1)),
            ("truck_cargo_308.jpg", lambda: draw_heavy_or_scooter(2)),
        ],
        "nature": [
            ("nature_mountain_401.jpg", lambda: draw_nature_mountain_forest("mountain", 1)),
            ("nature_forest_402.jpg", lambda: draw_nature_mountain_forest("forest", 2)),
            ("building_tower_403.jpg", lambda: draw_architecture("tower", 3)),
            ("building_bridge_404.jpg", lambda: draw_architecture("bridge", 4)),
            ("nature_ocean_405.jpg", lambda: draw_ocean_desert_aurora("ocean", 5)),
            ("nature_desert_406.jpg", lambda: draw_ocean_desert_aurora("desert", 6)),
            ("building_cathedral_407.jpg", lambda: draw_architecture("cathedral", 7)),
            ("nature_aurora_408.jpg", lambda: draw_ocean_desert_aurora("aurora", 8)),
        ]
    }
    
    total = 0
    for cat, items in spec.items():
        cat_dir = os.path.join(DATASET_DIR, cat)
        os.makedirs(cat_dir, exist_ok=True)
        for fname, gen_func in items:
            fpath = os.path.join(cat_dir, fname)
            img = gen_func()
            img.save(fpath, "JPEG", quality=95)
            total += 1
            print(f"  [Created] {cat:<11} / {fname:<28} (640x640, {os.path.getsize(fpath)} bytes)")
            
    print("--------------------------------------------------")
    print(f"Generated {total} high-resolution presentation images!")
    print("==================================================")

if __name__ == "__main__":
    generate_all_32_images()
