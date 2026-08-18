from pathlib import Path
import json
import shutil
import re

import torch
import open_clip
from PIL import Image


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

CATALOGUE = ROOT / "backend" / "catalogue"
METADATA = ROOT / "backend" / "metadata" / "catalogue_metadata.json"
BACKUP = ROOT / "backend" / "metadata" / "catalogue_metadata_before_final_fix.json"


# ============================================================
# MODEL
# ============================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_NAME = "hf-hub:Marqo/marqo-fashionSigLIP"

print("=" * 70)
print("FINAL CATALOGUE METADATA FIX")
print("=" * 70)
print(f"Device: {DEVICE}")
print("Loading FashionSigLIP...")

model, _, preprocess = open_clip.create_model_and_transforms(
    MODEL_NAME,
    device=DEVICE
)

tokenizer = open_clip.get_tokenizer(MODEL_NAME)

model.eval()

print("FashionSigLIP loaded!")


# ============================================================
# CONTROLLED LABELS
# ============================================================

COLORS = [
    "white",
    "black",
    "pink",
    "red",
    "blue",
    "navy",
    "green",
    "yellow",
    "purple",
    "brown",
    "beige",
    "grey",
    "cream",
    "ivory",
    "gold",
    "silver",
    "multicolor",
]

PATTERNS = [
    "floral",
    "leaf",
    "striped",
    "zigzag",
    "diamond",
    "geometric",
    "scallop",
    "rose",
    "plain",
    "sequin",
    "embroidered",
    "mesh",
    "net",
]

TYPES = [
    "lace",
    "fabric",
    "embroidered lace",
    "floral lace",
    "guipure lace",
    "corded lace",
    "mesh lace",
    "sequin fabric",
]


# ============================================================
# NORMALIZATION
# ============================================================

COLOR_MAP = {
    "white": "White",
    "black": "Black",
    "pink": "Pink",
    "red": "Red",
    "blue": "Blue",
    "navy": "Navy",
    "green": "Green",
    "yellow": "Yellow",
    "purple": "Purple",
    "brown": "Brown",
    "beige": "Beige",
    "grey": "Grey",
    "cream": "Cream",
    "ivory": "Ivory",
    "gold": "Gold",
    "silver": "Silver",
    "multicolor": "Multicolor",
}

PATTERN_MAP = {
    "floral": "Floral",
    "leaf": "Leaf",
    "striped": "Striped",
    "zigzag": "Zigzag",
    "diamond": "Diamond",
    "geometric": "Geometric",
    "scallop": "Scallop",
    "rose": "Rose",
    "plain": "Plain",
    "sequin": "Sequin",
    "embroidered": "Embroidered",
    "mesh": "Mesh",
    "net": "Net",
}

TYPE_MAP = {
    "lace": "Lace",
    "fabric": "Fabric",
    "embroidered lace": "Embroidered Lace",
    "floral lace": "Floral Lace",
    "guipure lace": "Guipure Lace",
    "corded lace": "Corded Lace",
    "mesh lace": "Mesh Lace",
    "sequin fabric": "Sequin Fabric",
}


# ============================================================
# IMAGE CROPS
# ============================================================

def make_crops(image):
    """
    Create several views so the label/background has less influence.
    """

    image = image.convert("RGB")

    w, h = image.size

    crops = []

    # Original
    crops.append(image)

    # Remove outer 10%
    crops.append(
        image.crop((
            int(w * 0.10),
            int(h * 0.10),
            int(w * 0.90),
            int(h * 0.90)
        ))
    )

    # Stronger central crop
    crops.append(
        image.crop((
            int(w * 0.18),
            int(h * 0.18),
            int(w * 0.82),
            int(h * 0.82)
        ))
    )

    return crops


# ============================================================
# CLASSIFIER
# ============================================================

def classify_image(image, labels):

    crops = make_crops(image)

    all_scores = []

    prompts = [
        f"a close-up fashion textile showing {label}"
        for label in labels
    ]

    text = tokenizer(prompts).to(DEVICE)

    with torch.no_grad():

        text_features = model.encode_text(
            text,
            normalize=True
        )

        for crop in crops:

            image_tensor = preprocess(crop).unsqueeze(0).to(DEVICE)

            image_features = model.encode_image(
                image_tensor,
                normalize=True
            )

            scores = (
                100
                * image_features
                @ text_features.T
            )[0]

            probabilities = torch.softmax(
                scores,
                dim=0
            )

            all_scores.append(
                probabilities
            )

    # Average all views
    final_scores = torch.stack(
        all_scores
    ).mean(dim=0)

    values, indices = torch.topk(
        final_scores,
        min(3, len(labels))
    )

    return [
        (
            labels[index.item()],
            float(value)
        )
        for value, index in zip(values, indices)
    ]


# ============================================================
# FIND IMAGE FOR PRODUCT
# ============================================================

def find_images(product_id):

    folder = CATALOGUE / product_id

    if not folder.exists():
        return []

    return [
        p for p in folder.iterdir()
        if p.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }
    ]


# ============================================================
# PRODUCT ATTRIBUTE AGGREGATION
# ============================================================

def classify_product(product_id):

    images = find_images(product_id)

    if not images:
        return None

    color_votes = []
    pattern_votes = []
    type_votes = []

    # Use every image belonging to this product
    for image_path in images:

        try:

            image = Image.open(image_path).convert("RGB")

            color_results = classify_image(
                image,
                COLORS
            )

            pattern_results = classify_image(
                image,
                PATTERNS
            )

            type_results = classify_image(
                image,
                TYPES
            )

            # Take strongest result
            color_votes.append(color_results[0])
            pattern_votes.append(pattern_results[0])
            type_votes.append(type_results[0])

        except Exception as e:

            print(
                f"WARNING: {product_id} / "
                f"{image_path.name}: {e}"
            )

    if not color_votes:
        return None

    # --------------------------------------------------------
    # Aggregate
    # --------------------------------------------------------

    def weighted_vote(votes):

        scores = {}

        for label, score in votes:
            scores[label] = scores.get(label, 0) + score

        return max(
            scores.items(),
            key=lambda x: x[1]
        )[0]

    color = weighted_vote(color_votes)
    pattern = weighted_vote(pattern_votes)
    textile_type = weighted_vote(type_votes)

    return {
        "color": color,
        "pattern": pattern,
        "type": textile_type,
    }


# ============================================================
# NAME GENERATION
# ============================================================

def generate_name(attributes):

    color = COLOR_MAP.get(
        attributes["color"]
    )

    pattern = PATTERN_MAP.get(
        attributes["pattern"]
    )

    textile_type = TYPE_MAP.get(
        attributes["type"]
    )

    # --------------------------------------------------------
    # Sequin fabric
    # --------------------------------------------------------

    if textile_type == "Sequin Fabric":

        if color:
            return f"{color} Sequin Fabric"

        return "Sequin Fabric"

    # --------------------------------------------------------
    # Strong fabric prediction
    # --------------------------------------------------------

    if textile_type == "Fabric":

        parts = []

        if color:
            parts.append(color)

        if pattern and pattern != "Plain":
            parts.append(pattern)

        parts.append("Fabric")

        return " ".join(parts)

    # --------------------------------------------------------
    # Lace
    # --------------------------------------------------------

    parts = []

    if color:
        parts.append(color)

    if pattern and pattern != "Plain":
        parts.append(pattern)

    if textile_type in {
        "Embroidered Lace",
        "Floral Lace",
        "Guipure Lace",
        "Corded Lace",
        "Mesh Lace",
    }:
        parts.append(textile_type)

    else:
        parts.append("Lace")

    return " ".join(parts)


# ============================================================
# LOAD METADATA
# ============================================================

with open(
    METADATA,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


# ============================================================
# BACKUP FIRST
# ============================================================

print()
print("Creating metadata backup...")

shutil.copy2(
    METADATA,
    BACKUP
)

print(f"Backup created:")
print(BACKUP)


# ============================================================
# PROCESS PRODUCTS
# ============================================================

print()
print("=" * 70)
print("PROCESSING PRODUCTS")
print("=" * 70)

total = len(metadata)

processed = 0
failed = 0

for number, (product_id, item) in enumerate(
    metadata.items(),
    start=1
):

    print()
    print(
        f"[{number}/{total}] {product_id}"
    )

    attributes = classify_product(
        product_id
    )

    if attributes is None:

        print("  No image found")
        failed += 1
        continue

    name = generate_name(
        attributes
    )

    # --------------------------------------------------------
    # ONLY UPDATE THESE FIELDS
    # --------------------------------------------------------

    item["name"] = name

    item["color"] = COLOR_MAP.get(
        attributes["color"],
        attributes["color"]
    )

    item["pattern"] = PATTERN_MAP.get(
        attributes["pattern"],
        attributes["pattern"]
    )

    # Keep existing description.
    # Keep existing applications.
    # Keep existing width/GSM/material.

    processed += 1

    print(
        f"  Color:   {item['color']}"
    )

    print(
        f"  Pattern: {item['pattern']}"
    )

    print(
        f"  Type:    {TYPE_MAP.get(attributes['type'], attributes['type'])}"
    )

    print(
        f"  NAME:    {name}"
    )


# ============================================================
# SAVE
# ============================================================

with open(
    METADATA,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# DONE
# ============================================================

print()
print("=" * 70)
print("FINAL METADATA UPDATE COMPLETE")
print("=" * 70)

print(
    f"Products processed: {processed}"
)

print(
    f"Products failed:    {failed}"
)

print()
print("Updated:")
print(METADATA)

print()
print("Backup:")
print(BACKUP)

print("=" * 70)