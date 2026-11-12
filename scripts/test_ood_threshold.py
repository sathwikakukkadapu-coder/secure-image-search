import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine

extractor = FeatureExtractor.get_instance()
projector = KeyedProjectionManager.get_instance()
retriever = FAISSRetrievalEngine.get_instance()

# 1. Test in-domain Medical
med_img = Image.open('test_dataset/01_Medical/test_medical_xray_05.jpg').convert('RGB')
raw_med, _, _ = extractor.extract_features(med_img)
proj_med, _ = projector.project(raw_med)
res_med, _ = retriever.search(proj_med, top_k=1)
print(f"In-Domain Medical Top-1 Similarity: {res_med[0]['similarity_percent']}")

# 2. Test in-domain Vehicle
veh_img = Image.open('test_dataset/03_Vehicles/test_vehicles_cars_01.jpg').convert('RGB')
raw_veh, _, _ = extractor.extract_features(veh_img)
proj_veh, _ = projector.project(raw_veh)
res_veh, _ = retriever.search(proj_veh, top_k=1)
print(f"In-Domain Vehicle Top-1 Similarity: {res_veh[0]['similarity_percent']}")

# 3. Test in-domain Nature
nat_img = Image.open('test_dataset/04_Nature/test_nature_general_01.jpg').convert('RGB')
raw_nat, _, _ = extractor.extract_features(nat_img)
proj_nat, _ = projector.project(raw_nat)
res_nat, _ = retriever.search(proj_nat, top_k=1)
print(f"In-Domain Nature Top-1 Similarity: {res_nat[0]['similarity_percent']}")

# 4. Test synthetic white paper / document
paper_img = Image.new('RGB', (500, 500), color=(240, 240, 240))
raw_paper, _, _ = extractor.extract_features(paper_img)
proj_paper, _ = projector.project(raw_paper)
res_paper, _ = retriever.search(proj_paper, top_k=1)
print(f"Out-of-Domain White Paper Top-1 Similarity: {res_paper[0]['similarity_percent']}")

# 5. Test synthetic red can (Coca-Cola red)
coke_img = Image.new('RGB', (300, 500), color=(220, 20, 20))
raw_coke, _, _ = extractor.extract_features(coke_img)
proj_coke, _ = projector.project(raw_coke)
res_coke, _ = retriever.search(proj_coke, top_k=1)
print(f"Out-of-Domain Red Can/Tin Top-1 Similarity: {res_coke[0]['similarity_percent']}")

# 6. Random high-entropy noise
np.random.seed(42)
noise_arr = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
noise_img = Image.fromarray(noise_arr)
raw_noise, _, _ = extractor.extract_features(noise_img)
proj_noise, _ = projector.project(raw_noise)
res_noise, _ = retriever.search(proj_noise, top_k=1)
print(f"Out-of-Domain Random Noise Top-1 Similarity: {res_noise[0]['similarity_percent']}")
