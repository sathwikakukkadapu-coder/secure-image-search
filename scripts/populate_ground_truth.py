import sqlite3
import json
import os

DB_PATH = "backend/database/private_search.db"
JSON_OUT = "backend/database/catalog_ground_truth.json"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check existing columns
cur.execute("PRAGMA table_info(images)")
cols = [c[1] for c in cur.fetchall()]

if "subtype" not in cols:
    cur.execute("ALTER TABLE images ADD COLUMN subtype TEXT")
if "modality" not in cols:
    cur.execute("ALTER TABLE images ADD COLUMN modality TEXT")
if "semantic_class" not in cols:
    cur.execute("ALTER TABLE images ADD COLUMN semantic_class TEXT")
conn.commit()

cur.execute("SELECT image_id, original_filename, category FROM images")
rows = cur.fetchall()

taxonomy = {}
for iid, fname, cat in rows:
    f_lower = fname.lower()
    
    # 1. Medical
    if cat == "medical":
        if "xray" in f_lower or "x_ray" in f_lower or "chest" in f_lower:
            modality = "radiograph"
            subtype = "thoracic_xray"
            sem_class = "diagnostic_radiology"
        elif "mri" in f_lower:
            modality = "magnetic_resonance"
            subtype = "brain_mri"
            sem_class = "neuroimaging"
        elif "ct" in f_lower:
            modality = "computed_tomography"
            subtype = "pulmonary_ct"
            sem_class = "cross_sectional_imaging"
        else:
            modality = "clinical_imaging"
            subtype = "medical_pathology"
            sem_class = "general_medical"

    # 2. Biometrics
    elif cat == "biometrics":
        if "fingerprint" in f_lower:
            modality = "dactyloscopy"
            subtype = "fingerprint_minutiae"
            sem_class = "friction_ridge"
        elif "iris" in f_lower:
            modality = "ophthalmic_pattern"
            subtype = "iris_pattern"
            sem_class = "ocular_biometric"
        elif "thermal" in f_lower:
            modality = "thermography"
            subtype = "thermal_face"
            sem_class = "facial_thermal"
        elif "face" in f_lower or "profile" in f_lower:
            modality = "facial_crop"
            subtype = "facial_identity"
            sem_class = "facial_recognition"
        else:
            modality = "biometric_scan"
            subtype = "biometric_sample"
            sem_class = "identity_verification"

    # 3. Vehicles
    elif cat == "vehicles":
        if "bike" in f_lower or "two_wheel" in f_lower:
            modality = "two_wheel_vehicle"
            subtype = "motorcycle_bicycle"
            sem_class = "light_transit"
        elif "commercial" in f_lower or "truck" in f_lower or "bus" in f_lower:
            modality = "commercial_transport"
            subtype = "heavy_freight_bus"
            sem_class = "commercial_transit"
        elif "car" in f_lower or "sedan" in f_lower or "suv" in f_lower:
            modality = "passenger_automobile"
            subtype = "sedan_suv_sports"
            sem_class = "passenger_transit"
        else:
            modality = "specialized_transit"
            subtype = "automotive_transit"
            sem_class = "general_vehicular"

    # 4. Nature
    elif cat == "nature":
        if "landscapes" in f_lower or "landscape" in f_lower:
            modality = "geospatial_terrain"
            subtype = "terrestrial_landscape"
            sem_class = "landscape_terrain"
        elif "wildlife" in f_lower or "animal" in f_lower:
            modality = "biological_fauna"
            subtype = "wildlife_species"
            sem_class = "faunal_biology"
        elif "weather" in f_lower or "aurora" in f_lower or "cloud" in f_lower:
            modality = "atmospheric_phenomenon"
            subtype = "aurora_meteorology"
            sem_class = "meteorological"
        elif "vegetation" in f_lower or "forest" in f_lower or "tree" in f_lower:
            modality = "botanical_flora"
            subtype = "forest_vegetation"
            sem_class = "floral_ecology"
        elif "water" in f_lower or "lake" in f_lower or "ocean" in f_lower or "river" in f_lower:
            modality = "hydrological_body"
            subtype = "aquatic_water"
            sem_class = "hydrology"
        elif "building" in f_lower:
            modality = "structural_architecture"
            subtype = "architectural_landmark"
            sem_class = "built_environment"
        else:
            modality = "environmental_scene"
            subtype = "natural_ecology"
            sem_class = "general_nature"
    else:
        modality = "unknown"
        subtype = "unknown"
        sem_class = "unknown"

    taxonomy[iid] = {
        "image_id": iid,
        "filename": fname,
        "domain": cat,
        "subtype": subtype,
        "modality": modality,
        "semantic_class": sem_class
    }

    cur.execute("""
        UPDATE images 
        SET subtype = ?, modality = ?, semantic_class = ?
        WHERE image_id = ?
    """, (subtype, modality, sem_class, iid))

conn.commit()
conn.close()

with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump(taxonomy, f, indent=2)

print(f"Updated {len(taxonomy)} images in database and saved {JSON_OUT} successfully!")
