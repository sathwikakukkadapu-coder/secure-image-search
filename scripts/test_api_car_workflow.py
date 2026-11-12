import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
import numpy as np
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.api.search import ContentFreeVectorQuery, execute_content_free_search

# 1. Extract & protect car features
extractor = FeatureExtractor.get_instance()
protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)

img = Image.open('test_dataset/03_Vehicles/test_vehicles_cars_01.jpg').convert('RGB')
raw, _, _ = extractor.extract_features(img)
proj, _ = protector.protect_vector(raw, apply_noise=True, sigma=0.05)

# 2. Query with domain_filter='vehicles' and threshold=0.0
query = ContentFreeVectorQuery(
    protected_vector=proj.tolist(),
    top_k=4,
    threshold=0.0,
    domain_filter='vehicles',
    include_below_threshold=True,
    sigma=0.05
)

# Admin user context
user = {"user_id": "USR_ADM_00", "role": "admin"}

import asyncio
res = asyncio.run(execute_content_free_search(query, current_user=user))

print(f"Content-free search returned {len(res['results'])} results for Car:")
for r in res['results']:
    print(f"Rank #{r['rank']} | ID: {r['image_id']} | Category: {r['category']} | Sim: {r['similarity_percent']} | URL: {r['image_url']}")
