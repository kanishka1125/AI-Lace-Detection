from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import tempfile
import shutil
import json
import numpy as np
import torch
import open_clip
import faiss

from utils.retrieval import (
    search
)


# ==========================================
# APP
# ==========================================

app = FastAPI(
    title="AI Fabric & Lace Visual Search API",
    version="1.0.0"
)


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CATALOGUE_DIR = os.path.join(
    BASE_DIR,
    "catalogue"
)

EMBEDDINGS_DIR = os.path.join(
    BASE_DIR,
    "embeddings"
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "catalogue_metadata.json"
)


# ==========================================
# SERVE CATALOGUE IMAGES
# ==========================================

app.mount(
    "/catalogue",
    StaticFiles(
        directory=CATALOGUE_DIR
    ),
    name="catalogue"
)


# ==========================================
# CORS
# ==========================================

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


# ==========================================
# EMBEDDING FILES
# ==========================================

EMBEDDINGS_PATH = os.path.join(
    EMBEDDINGS_DIR,
    "catalogue_embeddings.npy"
)

PATHS_PATH = os.path.join(
    EMBEDDINGS_DIR,
    "catalogue_paths.npy"
)


# ==========================================
# LOAD PRODUCT METADATA
# ==========================================

print("Loading product metadata...")

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    product_metadata = json.load(f)

print(
    f"Products loaded: {len(product_metadata)}"
)


# ==========================================
# DEVICE
# ==========================================

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(
    "Using device:",
    device
)


# ==========================================
# LOAD MARQO FASHION SIGLIP
# ==========================================

print(
    "\nLoading Marqo FashionSigLIP..."
)

model, _, preprocess = open_clip.create_model_and_transforms(
    "hf-hub:Marqo/marqo-fashionSigLIP",
    device=device
)

model.eval()

print(
    "Marqo FashionSigLIP loaded!"
)


# ==========================================
# LOAD CATALOGUE IMAGE EMBEDDINGS
# ==========================================

print(
    "\nLoading catalogue embeddings..."
)

catalogue_embeddings = np.load(
    EMBEDDINGS_PATH
).astype(np.float32)

catalogue = np.load(
    PATHS_PATH,
    allow_pickle=True
).tolist()

print(
    "Embedding shape:",
    catalogue_embeddings.shape
)

print(
    "Catalogue images:",
    len(catalogue)
)


# ==========================================
# VALIDATION
# ==========================================

if len(catalogue_embeddings) != len(catalogue):

    raise ValueError(
        "Number of embeddings does not match "
        "number of catalogue image paths."
    )


# ==========================================
# NORMALIZE CATALOGUE EMBEDDINGS
# ==========================================

print(
    "\nNormalizing catalogue embeddings..."
)

faiss.normalize_L2(
    catalogue_embeddings
)

print(
    "First embedding norm after normalization:",
    np.linalg.norm(
        catalogue_embeddings[0]
    )
)


# ==========================================
# BUILD FAISS INDEX
# ==========================================

print(
    "\nBuilding FAISS index..."
)

embedding_dimension = (
    catalogue_embeddings.shape[1]
)

index = faiss.IndexFlatIP(
    embedding_dimension
)

index.add(
    catalogue_embeddings
)

print(
    "FAISS index ready!"
)

# ==========================================
# CATALOGUE ENDPOINT
# ==========================================

@app.get("/api/catalogue")
async def get_catalogue():

    output = []

    for product_id, metadata in product_metadata.items():

        image_path = metadata.get(
            "image",
            ""
        )

        image_path = str(
            image_path
        ).replace(
            "\\",
            "/"
        )

        # Remove possible catalogue prefixes
        image_path = image_path.replace(
            "../catalogue/",
            ""
        )

        image_path = image_path.replace(
            "/catalogue/",
            ""
        )

        image_path = image_path.lstrip("/")

        image_url = (
            "/catalogue/"
            + image_path
        )

        output.append({

            "product_id": product_id,

            "name": metadata.get(
                "name",
                product_id
            ),

            "image": image_url,

            "category": metadata.get(
                "category",
                "Lace"
            ),

            "material": metadata.get(
                "material",
                "—"
            ),

            "pattern": metadata.get(
                "pattern",
                metadata.get(
                    "visual_attributes",
                    {}
                ).get(
                    "pattern",
                    "—"
                )
            ),

            "color": metadata.get(
                "color",
                metadata.get(
                    "visual_attributes",
                    {}
                ).get(
                    "color",
                    "—"
                )
            ),

            "description": metadata.get(
                "description",
                ""
            ),

            "applications": metadata.get(
                "applications",
                []
            )

        })

    return {
        "success": True,
        "total": len(output),
        "products": output
    }

# ==========================================
# SEARCH ENDPOINT
# ==========================================

@app.post("/api/search")
async def search_image(
    file: UploadFile = File(...)
):

    # --------------------------------------
    # Save uploaded image temporarily
    # --------------------------------------

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    ) as temp_file:

        shutil.copyfileobj(
            file.file,
            temp_file
        )

        temp_path = temp_file.name

    try:

        # ----------------------------------
        # Search catalogue
        # ----------------------------------

        scores, results = search(
            query_image_path=temp_path,
            index=index,
            catalogue=catalogue,
            model=model,
            preprocess=preprocess,
            device=device,
            top_k=5
        )


        # ----------------------------------
        # Build response
        # ----------------------------------

        output = []

        for score, image_path in zip(
            scores[0],
            results
        ):

            # Normalize path separators

            image_path = image_path.replace(
                "\\",
                "/"
            )


            # --------------------------------
            # Convert path to API URL
            # --------------------------------

            if image_path.startswith(
                "../catalogue/"
            ):

                image_url = image_path.replace(
                    "../catalogue/",
                    "/catalogue/"
                )

            elif image_path.startswith(
                "catalogue/"
            ):

                image_url = (
                    "/"
                    + image_path
                )

            else:

                image_url = (
                    "/catalogue/"
                    + image_path
                )


            # --------------------------------
            # Get product ID
            # --------------------------------

            parts = image_path.split("/")

            try:

                catalogue_index = (
                    parts.index("catalogue")
                )

                product_id = (
                    parts[
                        catalogue_index + 1
                    ]
                )

            except (
                ValueError,
                IndexError
            ):

                product_id = None


            # --------------------------------
            # Get product metadata
            # --------------------------------

            metadata = product_metadata.get(
                product_id,
                {}
            )


            # --------------------------------
            # Add result
            # --------------------------------

            output.append({

                "product_id": product_id,
                "name": metadata.get(
                    "name",
                    product_id
                ),

                "image": image_url,

                "score": float(score),

                "pattern": metadata.get(
                    "pattern",
                    ""
                ),

                "color": metadata.get(
                    "color",
                    ""
                ),

                "description": metadata.get(
                    "description",
                    ""
                ),

                "applications": metadata.get(
                    "applications",
                    []
                )

            })


        # ----------------------------------
        # Return response
        # ----------------------------------

        return {

            "success": True,

            "results": output

        }


    finally:

        # ----------------------------------
        # Delete temporary image
        # ----------------------------------

        if os.path.exists(
            temp_path
        ):

            os.remove(
                temp_path
            )

# ==========================================
# TEXT SEARCH
# ==========================================

@app.get("/api/text-search")
async def text_search(
    q: str,
    top_k: int = 10
):

    query = q.strip().lower()

    if not query:
        return {
            "success": True,
            "query": q,
            "results": []
        }

    # --------------------------------------
    # Helpers
    # --------------------------------------

    def infer_color(name, description, existing):
        if existing:
            return existing

        text = f"{name} {description}".lower()

        colors = [
            "black",
            "white",
            "ivory",
            "cream",
            "beige",
            "grey",
            "gray",
            "navy",
            "blue",
            "green",
            "red",
            "pink",
            "purple",
            "yellow",
            "orange",
            "brown",
            "gold",
            "silver",
            "champagne",
            "blush"
        ]

        for color in colors:
            if color in text:
                return color.title()

        return "—"


    def infer_pattern(name, description, existing):
        if existing:
            return existing

        text = f"{name} {description}".lower()

        patterns = [
            "floral",
            "leaf",
            "leaf motif",
            "striped",
            "stripe",
            "zigzag",
            "diamond",
            "geometric",
            "scroll",
            "rose",
            "embroidered",
            "beaded",
            "lattice",
            "scallop",
            "cutwork",
            "plain"
        ]

        for pattern in patterns:
            if pattern in text:
                return pattern.title()

        return "—"


    def infer_material(name, description, existing):
        if existing:
            return existing

        text = f"{name} {description}".lower()

        materials = [
            "cotton",
            "nylon",
            "polyester",
            "silk",
            "rayon",
            "viscose",
            "polyamide",
            "tulle",
            "mesh"
        ]

        found = []

        for material in materials:
            if material in text:
                found.append(material.title())

        if found:
            return " / ".join(found)

        return "—"


    def infer_applications(
        name,
        description,
        existing
    ):

        if existing:
            return existing

        text = f"{name} {description}".lower()

        applications = []

        if any(
            word in text
            for word in [
                "bridal",
                "wedding",
                "veil"
            ]
        ):
            applications.append(
                "Bridal Wear"
            )

        if any(
            word in text
            for word in [
                "evening",
                "gown",
                "party"
            ]
        ):
            applications.append(
                "Evening Wear"
            )

        if any(
            word in text
            for word in [
                "dress",
                "garment",
                "apparel",
                "fashion"
            ]
        ):
            applications.append(
                "Fashion Apparel"
            )

        if any(
            word in text
            for word in [
                "curtain",
                "home",
                "interior"
            ]
        ):
            applications.append(
                "Home Décor"
            )

        # General lace fallback
        if not applications:
            applications = [
                "Fashion Apparel",
                "Garment Decoration"
            ]

        return applications


    # --------------------------------------
    # Query words
    # --------------------------------------

    query_words = [
        word
        for word in query.split()
        if len(word) > 1
    ]

    results = []


    # --------------------------------------
    # Search catalogue
    # --------------------------------------

    for product_id, metadata in product_metadata.items():

        name = str(
            metadata.get("name", "")
        )

        description = str(
            metadata.get("description", "")
        )

        pattern_existing = str(
            metadata.get("pattern", "")
        )

        color_existing = str(
            metadata.get("color", "")
        )

        material_existing = str(
            metadata.get("material", "")
        )

        style_existing = str(
            metadata.get("style", "")
        )

        applications_existing = metadata.get(
            "applications",
            []
        )


        name_lower = name.lower()
        description_lower = description.lower()
        pattern_lower = pattern_existing.lower()
        color_lower = color_existing.lower()
        material_lower = material_existing.lower()
        style_lower = style_existing.lower()


        applications_text = ""

        if isinstance(
            applications_existing,
            list
        ):
            applications_text = " ".join(
                str(x).lower()
                for x in applications_existing
            )
        else:
            applications_text = str(
                applications_existing
            ).lower()


        # ----------------------------------
        # Ranking
        # ----------------------------------

        score = 0

        for word in query_words:

            if word in name_lower:
                score += 10

            if word in pattern_lower:
                score += 8

            if word in color_lower:
                score += 8

            if word in material_lower:
                score += 6

            if word in style_lower:
                score += 6

            if word in applications_text:
                score += 5

            if word in description_lower:
                score += 3


        if score <= 0:
            continue


        # ----------------------------------
        # FIND ACTUAL IMAGE
        # ----------------------------------

        image_url = ""

        product_folder = os.path.join(
            CATALOGUE_DIR,
            product_id
        )

        if os.path.isdir(
            product_folder
        ):

            image_files = [
                filename
                for filename in os.listdir(
                    product_folder
                )
                if filename.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".webp"
                    )
                )
            ]

            if image_files:

                image_filename = sorted(
                    image_files
                )[0]

                image_url = (
                    f"/catalogue/"
                    f"{product_id}/"
                    f"{image_filename}"
                )


        # ----------------------------------
        # INFER PRODUCT INFORMATION
        # ----------------------------------

        color = infer_color(
            name,
            description,
            color_existing
        )

        pattern = infer_pattern(
            name,
            description,
            pattern_existing
        )

        material = infer_material(
            name,
            description,
            material_existing
        )

        applications = infer_applications(
            name,
            description,
            applications_existing
        )


        # ----------------------------------
        # RESULT
        # ----------------------------------

        results.append({

            "product_id": product_id,

            "name": name or product_id,

            "image": image_url,

            "score": score,

            "pattern": pattern,

            "color": color,

            "material": material,

            "style": style_existing or "—",

            "description": description,

            "applications": applications

        })


    # --------------------------------------
    # SORT
    # --------------------------------------

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    # --------------------------------------
    # RESPONSE
    # --------------------------------------

    return {

        "success": True,

        "query": q,

        "results": results[:top_k]

    }