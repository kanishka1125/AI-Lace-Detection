import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "catalogue_metadata.json"
)

EMBEDDINGS_DIR = os.path.join(
    BASE_DIR,
    "metadata",
    "embeddings"
)

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# ==========================================
# KEEP MODEL CACHE ON D DRIVE
# ==========================================

CACHE_DIR = os.path.join(
    os.path.dirname(BASE_DIR),
    "model_cache"
)

os.makedirs(CACHE_DIR, exist_ok=True)

os.environ["HF_HOME"] = CACHE_DIR
os.environ["SENTENCE_TRANSFORMERS_HOME"] = CACHE_DIR

# ==========================================
# LOAD METADATA
# ==========================================

print("Loading metadata...")

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:
    metadata = json.load(f)

print(f"Products found: {len(metadata)}")

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

MODEL_NAME = "all-MiniLM-L6-v2"

print("\nLoading embedding model...")
print("Model cache:", CACHE_DIR)

model = SentenceTransformer(
    MODEL_NAME,
    cache_folder=CACHE_DIR
)

print("Embedding model loaded!")

# ==========================================
# CREATE TEXT FOR EACH PRODUCT
# ==========================================

product_ids = []
texts = []

for product_id, item in metadata.items():

    description = item.get("description", "")
    pattern = item.get("pattern", "")
    color = item.get("color", "")
    applications = item.get("applications", [])

    if isinstance(applications, list):
        applications = ", ".join(applications)

    text = f"""
    Product ID: {product_id}
    Pattern: {pattern}
    Color: {color}
    Description: {description}
    Applications: {applications}
    """

    product_ids.append(product_id)
    texts.append(text)

# ==========================================
# GENERATE EMBEDDINGS
# ==========================================

print("\nGenerating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    normalize_embeddings=True
)

embeddings = np.array(embeddings)

print("Embeddings generated!")
print("Shape:", embeddings.shape)

# ==========================================
# SAVE EMBEDDINGS
# ==========================================

EMBEDDINGS_FILE = os.path.join(
    EMBEDDINGS_DIR,
    "catalogue_embeddings.npy"
)

IDS_FILE = os.path.join(
    EMBEDDINGS_DIR,
    "product_ids.json"
)

np.save(
    EMBEDDINGS_FILE,
    embeddings
)

with open(
    IDS_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        product_ids,
        f,
        indent=4
    )

# ==========================================
# COMPLETE
# ==========================================

print("\n========================================")
print("EMBEDDINGS GENERATION COMPLETE")
print("========================================")

print(f"Products embedded: {len(product_ids)}")
print(f"Embedding shape: {embeddings.shape}")

print("\nSaved files:")

print(EMBEDDINGS_FILE)
print(IDS_FILE)