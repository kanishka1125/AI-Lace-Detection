# Embedding----> Nearest Images

import faiss
import numpy as np

from .embedding import (
    load_image,
    preprocess_image,
    get_image_embedding
)


def build_faiss_index(embeddings):

    embedding_dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(embedding_dimension)

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

    image = load_image(query_image_path)

    inputs = preprocess_image(
        image,
        preprocess,
        device
    )

    embedding = get_image_embedding(
        model,
        inputs
    )

    faiss.normalize_L2(embedding)

    scores, indices = index.search(embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append(catalogue[idx])

    return scores, results


