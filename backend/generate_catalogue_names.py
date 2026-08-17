import os
import json
import numpy as np
import torch
import open_clip
from PIL import Image, ImageEnhance


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CATALOGUE_DIR = os.path.join(
    BASE_DIR,
    "catalogue"
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "catalogue_metadata.json"
)


# ============================================================
# DEVICE
# ============================================================

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("Using device:", device)


# ============================================================
# LOAD METADATA
# ============================================================

print("\nLoading metadata...")

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)

print(
    "Products:",
    len(metadata)
)


# ============================================================
# LOAD MARQO FASHION SIGLIP
# ============================================================

print("\nLoading Marqo FashionSigLIP...")

model, _, preprocess = open_clip.create_model_and_transforms(
    "hf-hub:Marqo/marqo-fashionSigLIP",
    device=device
)

model.eval()

tokenizer = open_clip.get_tokenizer(
    "hf-hub:Marqo/marqo-fashionSigLIP"
)

print("Marqo FashionSigLIP loaded!")


# ============================================================
# FOREGROUND EXTRACTION
# ============================================================

def prepare_image(image):

    image = image.convert("RGB")

    arr = np.array(image)

    # --------------------------------------------------------
    # Detect whether the image has a dark background
    # --------------------------------------------------------

    brightness = (
        0.299 * arr[:, :, 0]
        + 0.587 * arr[:, :, 1]
        + 0.114 * arr[:, :, 2]
    )

    dark_ratio = np.mean(
        brightness < 45
    )

    # --------------------------------------------------------
    # If image has substantial dark background,
    # isolate brighter lace/fabric pixels.
    # --------------------------------------------------------

    if dark_ratio > 0.15:

        mask = brightness > 55

        ys, xs = np.where(mask)

        if (
            len(xs) > 100
            and len(ys) > 100
        ):

            x1 = max(
                int(xs.min()) - 10,
                0
            )

            y1 = max(
                int(ys.min()) - 10,
                0
            )

            x2 = min(
                int(xs.max()) + 10,
                arr.shape[1]
            )

            y2 = min(
                int(ys.max()) + 10,
                arr.shape[0]
            )

            image = image.crop(
                (x1, y1, x2, y2)
            )

    # --------------------------------------------------------
    # Slight enhancement
    # --------------------------------------------------------

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.15)

    return image


# ============================================================
# IMAGE EMBEDDING
# ============================================================

def image_embedding(image):

    image_tensor = preprocess(
        image
    ).unsqueeze(0).to(device)

    with torch.no_grad():

        embedding = model.encode_image(
            image_tensor
        )

    embedding = embedding / embedding.norm(
        dim=-1,
        keepdim=True
    )

    return embedding


# ============================================================
# TEXT EMBEDDING
# ============================================================

def text_embeddings(labels):

    prompts = [
        f"a photograph of {label}"
        for label in labels
    ]

    tokens = tokenizer(
        prompts
    ).to(device)

    with torch.no_grad():

        embeddings = model.encode_text(
            tokens
        )

    embeddings = embeddings / embeddings.norm(
        dim=-1,
        keepdim=True
    )

    return embeddings


# ============================================================
# CLASSIFICATION
# ============================================================

def classify(
    image_embedding_value,
    labels
):

    text_embed = text_embeddings(
        labels
    )

    scores = (
        image_embedding_value
        @ text_embed.T
    )

    scores = scores[0]

    best_index = torch.argmax(
        scores
    ).item()

    return (
        labels[best_index],
        float(scores[best_index])
    )


# ============================================================
# ATTRIBUTE LISTS
# ============================================================

COLORS = [

    "white lace",
    "ivory lace",
    "cream lace",
    "beige lace",
    "champagne lace",
    "blush lace",
    "pink lace",
    "peach lace",
    "red lace",
    "orange lace",
    "yellow lace",
    "green lace",
    "blue lace",
    "navy lace",
    "purple lace",
    "lavender lace",
    "black lace",
    "brown lace",
    "grey lace",
    "silver lace",
    "gold lace"
]


PATTERNS = [

    "plain lace",
    "floral lace",
    "rose motif lace",
    "leaf motif lace",
    "vine motif lace",
    "scroll motif lace",
    "geometric lace",
    "diamond pattern lace",
    "lattice pattern lace",
    "zigzag pattern lace",
    "chevron pattern lace",
    "striped lace",
    "paisley lace",
    "polka dot lace",
    "ornamental lace"
]


STYLES = [

    "embroidered lace",
    "corded lace",
    "beaded lace",
    "guipure lace",
    "chantilly lace",
    "cutwork lace",
    "scalloped lace",
    "mesh lace",
    "net lace",
    "woven lace",
    "decorative lace"
]


# ============================================================
# PROCESS PRODUCTS
# ============================================================

for i, (
    product_id,
    product
) in enumerate(
    metadata.items(),
    start=1
):

    print(
        f"\nProcessing {i}/{len(metadata)}: "
        f"{product_id}"
    )


    # --------------------------------------------------------
    # Image path
    # --------------------------------------------------------

    image_path = product.get(
        "image",
        ""
    )

    image_path = image_path.replace(
        "\\",
        "/"
    )

    image_path = image_path.replace(
        "/catalogue/",
        ""
    )

    image_path = image_path.lstrip("/")


    full_path = os.path.join(
        CATALOGUE_DIR,
        image_path
    )


    if not os.path.exists(
        full_path
    ):

        print(
            "Image not found:",
            full_path
        )

        continue


    try:

        # ----------------------------------------------------
        # Load image
        # ----------------------------------------------------

        original = Image.open(
            full_path
        ).convert("RGB")


        # ----------------------------------------------------
        # Remove dark background where possible
        # ----------------------------------------------------

        image = prepare_image(
            original
        )


        # ----------------------------------------------------
        # Generate visual embedding
        # ----------------------------------------------------

        embedding = image_embedding(
            image
        )


        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------

        color, color_score = classify(
            embedding,
            COLORS
        )


        # ----------------------------------------------------
        # PATTERN
        # ----------------------------------------------------

        pattern, pattern_score = classify(
            embedding,
            PATTERNS
        )


        # ----------------------------------------------------
        # STYLE
        # ----------------------------------------------------

        style, style_score = classify(
            embedding,
            STYLES
        )


        # ----------------------------------------------------
        # Remove repeated word "lace"
        # ----------------------------------------------------

        color_word = color.replace(
            " lace",
            ""
        )

        pattern_word = pattern.replace(
            " lace",
            ""
        ).replace(
            " pattern",
            ""
        )

        style_word = style.replace(
            " lace",
            ""
        )


        # ----------------------------------------------------
        # BUILD PRODUCT NAME
        # ----------------------------------------------------

        parts = []

        if color_word:
            parts.append(
                color_word.title()
            )

        if style_word:

            # Avoid redundant generic style
            if style_word.lower() not in [
                "woven",
                "decorative"
            ]:

                parts.append(
                    style_word.title()
                )

        if pattern_word.lower() != "plain":

            parts.append(
                pattern_word.title()
            )


        parts.append(
            "Lace"
        )


        # ----------------------------------------------------
        # Remove duplicate words
        # ----------------------------------------------------

        final_parts = []

        for part in parts:

            if part.lower() not in [
                x.lower()
                for x in final_parts
            ]:

                final_parts.append(
                    part
                )


        name = " ".join(
            final_parts
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        metadata[
            product_id
        ]["name"] = name


        metadata[
            product_id
        ]["visual_attributes"] = {

            "color": color_word.title(),

            "pattern": pattern_word.title(),

            "style": style_word.title(),

            "color_score": color_score,

            "pattern_score": pattern_score,

            "style_score": style_score
        }


        with open(
            METADATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4,
                ensure_ascii=False
            )


        print(
            "Name:",
            name
        )

        print(
            "Color:",
            color_word.title()
        )

        print(
            "Pattern:",
            pattern_word.title()
        )

        print(
            "Style:",
            style_word.title()
        )

        print(
            "Saved:",
            product_id
        )


    except Exception as e:

        print(
            f"ERROR processing {product_id}: {e}"
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("CATALOGUE NAME GENERATION COMPLETE")
print("========================================")

print(
    "Products processed:",
    len(metadata)
)

print(
    "Metadata:",
    METADATA_FILE
)