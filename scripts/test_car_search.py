import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine

extractor = FeatureExtractor.get_instance()
projector = KeyedProjectionManager.get_instance()
retriever = FAISSRetrievalEngine.get_instance()

test_img = Image.open('test_dataset/03_Vehicles/test_vehicles_cars_01.jpg').convert('RGB')
raw, _, _ = extractor.extract_features(test_img)
proj, _ = projector.project(raw)
results, search_ms = retriever.search(proj, top_k=4)

print('Search for Vehicle (Car) returned keys:', results[0].keys())
for r in results:
    print(r)
