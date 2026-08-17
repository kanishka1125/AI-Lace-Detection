import os
import json
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM


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

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "catalogue_metadata.json"
)


# ==========================================
# DEVICE
# ==========================================

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("Using device:", device)


# ==========================================
# LOAD METADATA
# ==========================================

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)

print(
    "Products loaded:",
    len(metadata)
)


# ==========================================
# LOAD FLORENCE
# ==========================================

MODEL_ID = "microsoft/Florence-2-base"

print("\nLoading Florence-2...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
).to(device)

processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
)

model.eval()

print("Florence-2 loaded!")


# ==========================================
# GENERATE DETAILED VISUAL CAPTION
# ==========================================

def get_caption(image):

    task = "<MORE_DETAILED_CAPTION>"

    inputs = processor(
        text=task,
        images=image,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=150,
            num_beams=3
        )

    generated_text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=False
    )[0]

    parsed = processor.post_process_generation(
        generated_text,
        task=task,
        image_size=image.size
    )

    caption = parsed.get(
        task,
        ""
    )

    if isinstance(caption, dict):
        caption = str(caption)

    return caption.strip()


# ==========================================
# GENERATE PRODUCT NAME
# ==========================================

def create_product_name(
    product_id,
    caption
):

    text = caption.lower()

    # --------------------------------------
    # Remove obvious photography noise
    # --------------------------------------

    noise_words = [
        "white background",
        "plain white background",
        "white surface",
        "wooden surface",
        "wooden floor",
        "white floor",
        "label",
        "barcode",
        "logo",
        "text",
        "brand",
        "tag"
    ]

    for word in noise_words:
        text = text.replace(
            word,
            ""
        )


    # --------------------------------------
    # Colors
    # --------------------------------------

    colors = [
        ("champagne", "Champagne"),
        ("ivory", "Ivory"),
        ("blush", "Blush"),
        ("beige", "Beige"),
        ("cream", "Cream"),
        ("navy", "Navy"),
        ("black", "Black"),
        ("white", "White"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("pink", "Pink"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("lavender", "Lavender"),
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("brown", "Brown"),
        ("peach", "Peach"),
        ("orange", "Orange"),
        ("yellow", "Yellow"),
        ("grey", "Grey"),
        ("gray", "Grey")
    ]

    color = None

    for keyword, label in colors:

        if keyword in text:

            color = label
            break


    # --------------------------------------
    # Patterns / motifs
    # --------------------------------------

    patterns = [
        ("floral", "Floral"),
        ("flower", "Floral"),
        ("leaf", "Leaf"),
        ("leaves", "Leaf"),
        ("rose", "Rose"),
        ("scroll", "Scroll"),
        ("geometric", "Geometric"),
        ("diamond", "Diamond"),
        ("lattice", "Lattice"),
        ("zigzag", "Zigzag"),
        ("chevron", "Chevron"),
        ("stripe", "Striped"),
        ("striped", "Striped"),
        ("dot", "Polka Dot"),
        ("polka", "Polka Dot"),
        ("paisley", "Paisley"),
        ("vine", "Vine"),
        ("ornamental", "Ornamental")
    ]

    detected_patterns = []

    for keyword, label in patterns:

        if keyword in text:

            if label not in detected_patterns:

                detected_patterns.append(
                    label
                )

    # --------------------------------------
    # Construction / style
    # --------------------------------------

    styles = [
        ("embroidered", "Embroidered"),
        ("embroidery", "Embroidered"),
        ("beaded", "Beaded"),
        ("bead", "Beaded"),
        ("corded", "Corded"),
        ("guipure", "Guipure"),
        ("chantilly", "Chantilly"),
        ("cutwork", "Cutwork"),
        ("scallop", "Scallop"),
        ("scalloped", "Scallop"),
        ("mesh", "Mesh"),
        ("net", "Net")
    ]

    detected_styles = []

    for keyword, label in styles:

        if keyword in text:

            if label not in detected_styles:

                detected_styles.append(
                    label
                )


    # ======================================
    # BUILD NAME
    # ======================================

    parts = []

    if color:
        parts.append(color)

    # Prefer construction/style
    for style in detected_styles:

        if style not in parts:

            parts.append(style)

        if len(parts) >= 3:
            break

    # Add pattern
    for pattern in detected_patterns:

        if pattern not in parts:

            parts.append(pattern)

        if len(parts) >= 4:
            break


    # --------------------------------------
    # Ensure catalogue type
    # --------------------------------------

    if "Lace" not in parts:

        parts.append("Lace")


    # --------------------------------------
    # Remove duplicates
    # --------------------------------------

    clean_parts = []

    for part in parts:

        if part not in clean_parts:

            clean_parts.append(part)


    name = " ".join(
        clean_parts
    )


    # --------------------------------------
    # Fallback
    # --------------------------------------

    if name == "Lace":

        name = f"Lace Collection {product_id}"


    return name


# ==========================================
# PROCESS PRODUCTS
# ==========================================

product_ids = list(
    metadata.keys()
)

print(
    "\nGenerating catalogue names for:",
    len(product_ids),
    "products"
)


for i, product_id in enumerate(
    product_ids,
    start=1
):

    product = metadata[
        product_id
    ]

    print(
        f"\nProcessing {i}/{len(product_ids)}: "
        f"{product_id}"
    )


    # --------------------------------------
    # Get image
    # --------------------------------------

    image_path = product.get(
        "image",
        ""
    )

    if not image_path:

        print(
            "No image path."
        )

        continue


    image_path = image_path.replace(
        "\\",
        "/"
    )

    image_path = image_path.replace(
        "/catalogue/",
        ""
    )

    image_path = image_path.lstrip("/")


    full_image_path = os.path.join(
        CATALOGUE_DIR,
        image_path
    )


    if not os.path.exists(
        full_image_path
    ):

        print(
            "Image not found:",
            full_image_path
        )

        continue


    try:

        image = Image.open(
            full_image_path
        ).convert("RGB")


        # ----------------------------------
        # Get fresh visual caption
        # ----------------------------------

        caption = get_caption(
            image
        )


        # ----------------------------------
        # Create catalogue name
        # ----------------------------------

        name = create_product_name(
            product_id,
            caption
        )


        # ----------------------------------
        # Save
        # ----------------------------------

        metadata[product_id][
            "name"
        ] = name


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
            "Saved:",
            product_id
        )


    except Exception as e:

        print(
            f"ERROR processing {product_id}: {e}"
        )


# ==========================================
# COMPLETE
# ==========================================

print("\n========================================")
print("PRODUCT NAME GENERATION COMPLETE")
print("========================================")

print(
    "Products:",
    len(metadata)
)

print(
    "Metadata saved to:",
    METADATA_FILE
)