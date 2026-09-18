import os
import time
from typing import Tuple, List, Optional
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models

class FeatureExtractor:
    """
    Extracts deep visual feature representations using pretrained CNN backbones.
    Uses MobileNetV3-Large by default for fast CPU inference (<30ms) or ResNet-50.
    Embeddings are taken from the penultimate layer and L2-normalized.
    """
    _instance = None

    def __init__(self, model_name: str = "mobilenet_v3_large"):
        self.device = torch.device("cpu")
        self.model_name = model_name
        self.model = None
        self.feature_dim = 1280 if "mobilenet_v3_large" in model_name else (2048 if "resnet50" in model_name else 1024)
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        self._load_model()

    @classmethod
    def get_instance(cls, model_name: str = "mobilenet_v3_large"):
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    def _load_model(self):
        print(f"[AI Backbone] Loading pretrained {self.model_name}...")
        start_t = time.time()
        
        if self.model_name == "resnet50":
            base_model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            base_model.fc = torch.nn.Identity()
            self.feature_dim = 2048
            self.model = base_model
        else: # mobilenet_v3_large default
            base_model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
            base_model.classifier[3] = torch.nn.Identity()
            self.feature_dim = 1280
            self.model = base_model
            
        self.model.to(self.device)
        self.model.eval()
        load_ms = (time.time() - start_t) * 1000
        print(f"[AI Backbone] Model {self.model_name} loaded in {load_ms:.1f}ms. Feature dim: {self.feature_dim}")

    def preprocess_image(self, image: Image.Image) -> Tuple[torch.Tensor, float]:
        t0 = time.time()
        if image.mode != "RGB":
            image = image.convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        preprocess_ms = (time.time() - t0) * 1000
        return tensor, preprocess_ms

    def extract_features(self, image: Image.Image) -> Tuple[np.ndarray, float, float]:
        tensor, preprocess_ms = self.preprocess_image(image)
        t0 = time.time()
        with torch.no_grad():
            features = self.model(tensor)
            features = features.squeeze().cpu().numpy()
            
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        else:
            features = np.zeros_like(features)
            
        inference_ms = (time.time() - t0) * 1000
        return features.astype(np.float32), preprocess_ms, inference_ms
