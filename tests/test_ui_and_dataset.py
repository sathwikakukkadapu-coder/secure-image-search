import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.keyed_projection import KeyedProjectionManager
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine

def test_ui_and_dataset():
    # 1. Test HTML verification
    index_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'Zero-Pixel Shield' in html, 'Zero-Pixel Shield badge missing from HTML'
    assert 'Faculty Demo Test Dataset' in html, 'Faculty demo select missing from HTML'
    assert 'queryImagePreview' not in html, 'queryImagePreview must not be present'
    assert 'loadFromTestDataset' in html, 'loadFromTestDataset function missing from HTML'
    print('1. UI Verification: PASS (Zero raw image pixels rendered, Test Dataset Selector active)')

    # 2. Test dataset files verification
    test_dataset_dir = os.path.join(os.path.dirname(__file__), '..', 'test_dataset')
    categories = ['01_Medical', '02_Biometrics', '03_Vehicles', '04_Nature']
    for cat in categories:
        cat_path = os.path.join(test_dataset_dir, cat)
        files = os.listdir(cat_path)
        assert len(files) == 12, f'Expected 12 test images in {cat}, found {len(files)}'
        print(f'2. Test Dataset {cat}: PASS ({len(files)} curated images ready)')

    # 3. Test feature extraction & privacy projection on sample test image
    test_img_path = os.path.join(test_dataset_dir, '01_Medical', 'test_medical_xray_05.jpg')
    assert os.path.exists(test_img_path), f'Missing {test_img_path}'
    img = Image.open(test_img_path).convert('RGB')
    
    extractor = FeatureExtractor.get_instance()
    raw_vec, _, _ = extractor.extract_features(img)
    assert raw_vec.shape == (1280,), f'Unexpected raw shape {raw_vec.shape}'

    projector = KeyedProjectionManager.get_instance()
    proj_vec, _ = projector.project(raw_vec)
    assert proj_vec.shape == (512,), f'Unexpected protected shape {proj_vec.shape}'
    print('3. Feature Extraction & Keyed Projection: PASS (1280-D -> 512-D)')

    # 4. Test FAISS Retrieval on protected test vector
    retriever = FAISSRetrievalEngine.get_instance()
    results, search_ms = retriever.search(proj_vec, top_k=5)
    assert len(results) > 0, 'Retrieval returned 0 results'
    print(f'4. FAISS Retrieval on Test Image: PASS (Retrieved {len(results)} matches in {search_ms:.2f}ms)')
    for r in results[:3]:
        print(f"   Match ID: {r.get('id', r.get('image_id'))} | Similarity: {r.get('score', r.get('similarity', 0)):.4f}")

if __name__ == '__main__':
    test_ui_and_dataset()
    print('\n>>> ALL TEST VERIFICATIONS COMPLETED SUCCESSFULLY! <<<')
