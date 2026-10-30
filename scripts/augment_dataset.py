"""
PrivateLens Robustness Augmentation Engine
Creates a strictly separated evaluation dataset of augmented image variants
to measure retrieval robustness against photometric and geometric perturbations.

Guarantees:
- Original dataset is untouched and preserved.
- Augmented samples stored in dataset_augmented/ with separate metadata_augmented.csv.
- Each sample explicitly tracks original_image_id and transformation type.
"""

import os
import sys
import csv
import time
from PIL import Image, ImageEnhance, ImageFilter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
AUGMENTED_DIR = os.path.join(BASE_DIR, "dataset_augmented")
AUGMENTED_CSV = os.path.join(AUGMENTED_DIR, "metadata_augmented.csv")

def apply_transformations(image: Image.Image):
    """Generates 5 controlled, semantically preserving transformations."""
    transforms = {}
    
    # 1. Brightness adjustment (+25%)
    enh_b = ImageEnhance.Brightness(image)
    transforms["brightness_up"] = enh_b.enhance(1.25)
    
    # 2. Contrast adjustment (+30%)
    enh_c = ImageEnhance.Contrast(image)
    transforms["contrast_up"] = enh_c.enhance(1.30)
    
    # 3. Small rotation (+5 degrees with edge crop)
    rot = image.rotate(5, resample=Image.Resampling.BILINEAR)
    transforms["rotation_5deg"] = rot
    
    # 4. Mild Gaussian Blur (radius 1.2)
    blur = image.filter(ImageFilter.GaussianBlur(radius=1.2))
    transforms["mild_blur"] = blur
    
    # 5. Mild Sharpening
    sharp = image.filter(ImageFilter.SHARPEN)
    transforms["sharpen"] = sharp
    
    return transforms

def run_augmentation(samples_per_domain: int = 25):
    """
    Selects representative samples from each domain and applies transformations.
    Saves results into dataset_augmented/ maintaining domain folders.
    """
    print("=" * 68)
    print("      PrivateLens Robustness Dataset Augmentation Engine       ")
    print(f"      Target: {samples_per_domain} images per domain x 5 variants")
    print("=" * 68)
    
    os.makedirs(AUGMENTED_DIR, exist_ok=True)
    expected_domains = ["biometrics", "medical", "nature", "vehicles"]
    augmented_records = []
    
    total_generated = 0
    
    for domain in expected_domains:
        dom_src = os.path.join(DATASET_DIR, domain)
        dom_dest = os.path.join(AUGMENTED_DIR, domain)
        os.makedirs(dom_dest, exist_ok=True)
        
        # Collect candidate images
        candidates = []
        for root, _, files in os.walk(dom_src):
            for f in sorted(files):
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    candidates.append(os.path.join(root, f))
                    
        selected = candidates[:samples_per_domain]
        print(f"  * Domain [{domain.capitalize()}]: Processing {len(selected)} source images...")
        
        for fpath in selected:
            orig_fname = os.path.basename(fpath)
            orig_id = os.path.splitext(orig_fname)[0]
            
            try:
                with Image.open(fpath) as pil_img:
                    if pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")
                    variants = apply_transformations(pil_img)
                    
                for tname, trans_img in variants.items():
                    aug_fname = f"{orig_id}_aug_{tname}.jpg"
                    aug_path = os.path.join(dom_dest, aug_fname)
                    trans_img.save(aug_path, "JPEG", quality=90)
                    
                    aug_size = os.path.getsize(aug_path)
                    rel_path = os.path.relpath(aug_path, BASE_DIR).replace("\\", "/")
                    
                    augmented_records.append({
                        "augmented_image_id": f"AUG_{orig_id}_{tname}",
                        "original_image_id": orig_id,
                        "domain": domain,
                        "transformation_type": tname,
                        "relative_path": rel_path,
                        "image_width": trans_img.width,
                        "image_height": trans_img.height,
                        "file_size_bytes": aug_size,
                        "generation_date": time.strftime("%Y-%m-%d")
                    })
                    total_generated += 1
            except Exception as e:
                print(f"    Error augmenting {fpath}: {e}")
                
    # Save metadata_augmented.csv
    fieldnames = [
        "augmented_image_id", "original_image_id", "domain",
        "transformation_type", "relative_path", "image_width",
        "image_height", "file_size_bytes", "generation_date"
    ]
    with open(AUGMENTED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(augmented_records)
        
    print("=" * 68)
    print(f"AUGMENTATION COMPLETED: {total_generated} augmented samples created.")
    print(f"Stored strictly separately in: {AUGMENTED_DIR}")
    print(f"Metadata recorded in: {AUGMENTED_CSV}")
    print("=" * 68)
    return total_generated

if __name__ == "__main__":
    n = 25
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        n = int(sys.argv[1])
    run_augmentation(samples_per_domain=n)
