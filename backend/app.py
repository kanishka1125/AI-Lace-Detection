from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import tempfile
import shutil
import numpy as np
import torch
import open_clip
import faiss

from utils.embedding import (
    load_image,
    preprocess_image,
    get_image_embedding
)

from utils.retrieval import (
    build_faiss_index,
    search
)

app = FastAPI(
    title="AI Fabric & Lace Visual Search API",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/catalogue",
    StaticFiles(directory=os.path.join(BASE_DIR, "catalogue")),
    name="catalogue"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


EMBEDDINGS_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "catalogue_embeddings.npy"
)

PATHS_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "catalogue_paths.npy"
)

device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "hf-hub:Marqo/marqo-fashionSigLIP",
    device=device
)

model.eval()

catalogue_embeddings = np.load(EMBEDDINGS_PATH)

faiss.normalize_L2(catalogue_embeddings)

index = build_faiss_index(catalogue_embeddings)

catalogue = np.load(PATHS_PATH, allow_pickle=True).tolist()



@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        scores, results = search(
            query_image_path=temp_path,
            index=index,
            catalogue=catalogue,
            model=model,
            preprocess=preprocess,
            device=device,
            top_k=5
        )

        output = []

        for score, image_path in zip(scores[0], results):

            image_url = image_path.replace("\\", "/")

            if image_url.startswith("../catalogue/"):
                image_url = image_url.replace("../catalogue/", "/catalogue/")

            output.append({
                "image": image_url,
                "score": float(score)
            })

        return {
            "success": True,
            "results": output
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)