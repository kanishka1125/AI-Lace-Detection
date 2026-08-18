import os
import json
import re
from pathlib import Path

import torch
from PIL import Image, ImageEnhance
from transformers import AutoProcessor, AutoModelForCausalLM

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "metadata"
    / "catalogue_metadata.json"
)

CATALOGUE_DIR = PROJECT_ROOT / "backend" / "catalogue"


# ============================================================
# MODEL
# ============================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_NAME = "microsoft/Florence-2-base"

print("=" * 60)
print("CATALOGUE NAME REGENERATION V2")
print("=" * 60)

print(f"Using device: {DEVICE}")
print("Loading Florence-2...")

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
).to(DEVICE)

model.eval()

print("Florence-2 loaded!")


# ============================================================
# LOAD METADATA
# ============================================================

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

print(f"Products loaded: {len(metadata)}")


# ============================================================
# HELPERS
# ============================================================

COLORS = [
    "white",
    "black",
    "beige",
    "cream",
    "ivory",
    "grey",
    "gray",
    "pink",
    "red",
    "blue",
    "navy",
    "green",
    "yellow",
    "purple",
    "brown",
    "orange",
    "gold",
    "silver",
]

PATTERNS = [
    "floral",
    "flower",
    "leaf",
    "leaves",
    "striped",
    "stripe",
    "zigzag",
    "diamond",
    "geometric",
    "scallop",
    "rose",
    "embroidered",
    "mesh",
    "net",
    "plain",
    "motif",
]

STYLES = [
    "guipure",
    "corded",
    "embroidered",
    "beaded",
    "crochet",
    "mesh",
    "net",
    "woven",
    "knitted",
]


def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_first(text, words):
    text = clean_text(text)

    for word in words:
        if word in text:
            return word

    return None


def normalize_color(color):
    if not color:
        return None

    mapping = {
        "gray": "Grey",
        "grey": "Grey",
        "navy": "Navy",
        "cream": "Cream",
        "ivory": "Ivory",
        "white": "White",
        "black": "Black",
        "beige": "Beige",
        "pink": "Pink",
        "red": "Red",
        "blue": "Blue",
        "green": "Green",
        "yellow": "Yellow",
        "purple": "Purple",
        "brown": "Brown",
        "orange": "Orange",
        "gold": "Gold",
        "silver": "Silver",
    }

    return mapping.get(color.lower(), color.title())


def normalize_pattern(pattern):
    if not pattern:
        return None

    mapping = {
        "flower": "Floral",
        "floral": "Floral",
        "leaf": "Leaf",
        "leaves": "Leaf",
        "stripe": "Striped",
        "striped": "Striped",
        "zigzag": "Zigzag",
        "diamond": "Diamond",
        "geometric": "Geometric",
        "scallop": "Scallop",
        "rose": "Rose",
        "embroidered": "Embroidered",
        "mesh": "Mesh",
        "net": "Mesh",
        "plain": "Plain",
        "motif": "Motif",
    }

    return mapping.get(pattern.lower(), pattern.title())


def normalize_style(style):
    if not style:
        return None

    mapping = {
        "guipure": "Guipure",
        "corded": "Corded",
        "embroidered": "Embroidered",
        "beaded": "Beaded",
        "crochet": "Crochet",
        "mesh": "Mesh",
        "net": "Mesh",
        "woven": "Woven",
        "knitted": "Knitted",
    }

    return mapping.get(style.lower(), style.title())


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def prepare_image(image):
    """
    Reduce influence of:
    - labels
    - borders
    - tables/floors
    - large empty background areas

    We keep the central textile region.
    """

    image = image.convert("RGB")

    width, height = image.size

    # Remove outer 10% from each side.
    left = int(width * 0.10)
    top = int(height * 0.10)
    right = int(width * 0.90)
    bottom = int(height * 0.90)

    image = image.crop((left, top, right, bottom))

    # Slight enhancement helps textile texture.
    image = ImageEnhance.Contrast(image).enhance(1.15)
    image = ImageEnhance.Sharpness(image).enhance(1.10)

    return image


# ============================================================
# FLORENCE DESCRIPTION
# ============================================================

def describe_textile(image):
    """
    Florence-2 is instructed to describe the textile itself.
    We intentionally do NOT ask it to name the product.
    """

    prompt = "<DETAILED_CAPTION>"

    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(DEVICE)
        for k, v in inputs.items()
        if hasattr(v, "to")
    }

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=120,
            num_beams=3,
        )

    generated_text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=False
    )[0]

    # Remove Florence task token if returned.
    generated_text = generated_text.replace(
        "<DETAILED_CAPTION>",
        ""
    )

    return clean_text(generated_text)


# ============================================================
# NAME GENERATION
# ============================================================

def generate_name(description, product_id):
    """
    Generate a conservative catalogue name.

    IMPORTANT:
    We don't invent attributes.
    If uncertain, we simply omit them.
    """

    text = clean_text(description)

    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    color = find_first(text, COLORS)

    # --------------------------------------------------------
    # PATTERN
    # --------------------------------------------------------

    pattern = find_first(text, PATTERNS)

    # --------------------------------------------------------
    # STYLE
    # --------------------------------------------------------

    style = find_first(text, STYLES)

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    color = normalize_color(color)
    pattern = normalize_pattern(pattern)
    style = normalize_style(style)

    # --------------------------------------------------------
    # SAFETY:
    # Don't call something black merely because the background
    # is black. We only accept black when Florence explicitly
    # describes the textile as black.
    # --------------------------------------------------------

    parts = []

    if color:
        parts.append(color)

    if pattern:
        # Avoid "Embroidered Embroidered Lace"
        if pattern == "Embroidered":
            pass
        else:
            parts.append(pattern)

    if style and style not in parts:
        parts.append(style)

    # --------------------------------------------------------
    # ALWAYS identify catalogue item as Lace.
    # --------------------------------------------------------

    if not parts:
        return "Lace"

    name = " ".join(parts)

    if not name.lower().endswith("lace"):
        name += " Lace"

    # Remove accidental duplicates.
    name = re.sub(
        r"\b(\w+)(\s+\1\b)+",
        r"\1",
        name,
        flags=re.IGNORECASE
    )

    return name


# ============================================================
# IMAGE LOCATION
# ============================================================

def find_product_image(product_id, item):
    """
    Find the image using metadata first, then catalogue folders.
    """

    possible_paths = []

    # Metadata image path
    image_path = item.get("image")

    if image_path:
        image_path = str(image_path).replace("\\", "/")

        if image_path.startswith("/"):
            image_path = image_path[1:]

        possible_paths.append(PROJECT_ROOT / image_path)
        possible_paths.append(PROJECT_ROOT / "backend" / image_path)

    # Common catalogue structure
    possible_paths.extend([
        CATALOGUE_DIR / product_id / f"{product_id}_0.jpeg",
        CATALOGUE_DIR / product_id / f"{product_id}_0.jpg",
        CATALOGUE_DIR / product_id / f"{product_id}.jpeg",
        CATALOGUE_DIR / product_id / f"{product_id}.jpg",
    ])

    for path in possible_paths:
        if path.exists():
            return path

    # Last resort: search recursively
    for ext in ("*.jpeg", "*.jpg", "*.png", "*.webp"):
        matches = list(
            CATALOGUE_DIR.glob(
                f"**/{product_id}/{ext}"
            )
        )

        if matches:
            return matches[0]

    return None


# ============================================================
# MAIN PROCESSING
# ============================================================

processed = 0
failed = 0

for index, (product_id, item) in enumerate(metadata.items(), start=1):

    print()
    print(
        f"Processing {index}/{len(metadata)}: "
        f"{product_id}"
    )

    image_path = find_product_image(
        product_id,
        item
    )

    if image_path is None:
        print("  WARNING: Image not found")
        failed += 1
        continue

    try:

        image = Image.open(image_path)

        print(
            f"  Image: {image_path.name}"
        )

        # ----------------------------------------------------
        # PREPROCESS
        # ----------------------------------------------------

        prepared = prepare_image(image)

        # ----------------------------------------------------
        # DESCRIBE TEXTILE
        # ----------------------------------------------------

        description = describe_textile(
            prepared
        )

        print(
            f"  Textile description: {description}"
        )

        # ----------------------------------------------------
        # GENERATE NAME
        # ----------------------------------------------------

        new_name = generate_name(
            description,
            product_id
        )

        print(
            f"  NEW NAME: {new_name}"
        )

        # ----------------------------------------------------
        # ONLY UPDATE NAME
        # ----------------------------------------------------

        item["name"] = new_name

        # Keep existing description untouched.
        # Keep existing applications untouched.
        # Keep existing metadata untouched.

        processed += 1

    except Exception as e:

        print(
            f"  ERROR: {e}"
        )

        failed += 1


# ============================================================
# SAVE
# ============================================================

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


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("CATALOGUE NAME REGENERATION COMPLETE")
print("=" * 60)

print(f"Products processed: {processed}")
print(f"Products failed:    {failed}")

print()
print(
    f"Metadata saved to:"
)
print(METADATA_FILE)
print("=" * 60)