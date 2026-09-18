import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import backend.database.db as db
from backend.services.feature_extraction.extractor import FeatureExtractor
from backend.services.privacy.protector import PrivacyProtectionLayer
from backend.services.retrieval.faiss_index import FAISSRetrievalEngine
from backend.services.storage.vault import PrivateImageVault

from backend.api.auth import router as auth_router
from backend.api.search import router as search_router
from backend.api.admin import router as admin_router
from backend.api.evaluation import router as eval_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== [Starting Private Image Search Engine] ===")
    db.init_db()
    
    # Pre-warm AI and Retrieval singletons
    extractor = FeatureExtractor.get_instance(model_name="mobilenet_v3_large")
    protector = PrivacyProtectionLayer.get_instance(input_dim=extractor.feature_dim, protected_dim=512)
    retriever = FAISSRetrievalEngine.get_instance(dimension=512)
    vault = PrivateImageVault.get_instance()
    
    print(f"[System Ready] Indexed Vectors in FAISS: {retriever.count()}")
    yield
    print("=== [Shutting Down Private Image Search Engine] ===")

app = FastAPI(
    title="Private Image Search API",
    description="Privacy-Preserving Image Retrieval Using Protected Visual Representations",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(admin_router)
app.include_router(eval_router)

# Mount frontend directory for SPA
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Private Image Search API is running. Frontend not found."}

@app.get("/health")
def health_check():
    retriever = FAISSRetrievalEngine.get_instance()
    return {
        "status": "healthy",
        "faiss_vectors": retriever.count(),
        "zero_pixel_invariant": True
    }
