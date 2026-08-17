# Image Embedding → Nearest Catalogue Images

import faiss
import numpy as np

from .embedding import (
    load_image,
    preprocess_image,
    get_image_embedding
)


def build_faiss_index(embeddings):

    # Make sure embeddings are float32
    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    # Normalize catalogue embeddings
    faiss.normalize_L2(embeddings)

    embedding_dimension = embeddings.shape[1]

    # Inner Product on normalized vectors
    # = Cosine Similarity
    index = faiss.IndexFlatIP(
        embedding_dimension
    )

    index.add(embeddings)

    return index


def search(
    query_image_path,
    index,
    catalogue,
    model,
    preprocess,
    device,
    top_k=5
):

    # -----------------------------
    # Load uploaded image
    # -----------------------------

    image = load_image(
        query_image_path
    )

    # -----------------------------
    # Preprocess image
    # -----------------------------

    inputs = preprocess_image(
        image,
        preprocess,
        device
    )

    # -----------------------------
    # Generate Marqo embedding
    # -----------------------------

    embedding = get_image_embedding(
        model,
        inputs
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    # -----------------------------
    # Normalize query embedding
    # -----------------------------

    faiss.normalize_L2(
        embedding
    )

    # -----------------------------
    # Search catalogue
    # -----------------------------

    scores, indices = index.search(
        embedding,
        top_k
    )

    # -----------------------------
    # Get matching image paths
    # -----------------------------

    results = []

    for idx in indices[0]:

        if idx < 0:
            continue

        results.append(
            catalogue[idx]
        )

    return scores, results