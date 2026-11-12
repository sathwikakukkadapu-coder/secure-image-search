import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
import numpy as np
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from backend.services.retrieval.domain_classifier import DomainClassifier

extractor = FeatureExtractor.get_instance()
projector = KeyedProjectionManager.get_instance()
classifier = DomainClassifier.get_instance()

# Test vehicle
car_path = 'test_dataset/03_Vehicles/test_vehicles_cars_01.jpg'
img = Image.open(car_path).convert('RGB')
raw, _, _ = extractor.extract_features(img)
proj, _ = projector.project(raw)

info = classifier.classify_protected_vector(proj)
print("Classification for Car test vector:", info)
