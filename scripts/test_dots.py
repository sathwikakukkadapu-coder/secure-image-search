import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
import numpy as np
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager

extractor = FeatureExtractor.get_instance()
projector = KeyedProjectionManager.get_instance()

car_path = 'test_dataset/03_Vehicles/test_vehicles_cars_01.jpg'
img = Image.open(car_path).convert('RGB')
raw, _, _ = extractor.extract_features(img)
proj, _ = projector.project(raw)

centroids = np.load('vector_db/domain_centroids.npz')
for k in centroids.keys():
    print(k, "dot product:", float(np.dot(proj, centroids[k])))
