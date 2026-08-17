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
# LOAD EXISTING METADATA
# ==========================================

print("\nLoading existing metadata...")

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
# LOAD FLORENCE-2
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
# CREATE SHORT PRODUCT NAME
# ==========================================

def create_product_name(
    product_id,
    description
):

    text = description.lower()

    # --------------------------------------
    # Detect color
    # --------------------------------------

    colors = [
        "white",
        "black",
        "ivory",
        "cream",
        "beige",
        "brown",
        "blue",
        "navy",
        "green",
        "pink",
        "blush",
        "red",
        "purple",
        "lavender",
        "grey",
        "gray",
        "gold",
        "silver",
        "champagne",
        "peach",
        "orange",
        "yellow"
    ]

    detected_color = None

    for color in colors:

        if color in text:

            detected_color = color.title()
            break


    # --------------------------------------
    # Detect pattern / style
    # --------------------------------------

    styles = [
        ("floral", "Floral"),
        ("flower", "Floral"),
        ("embroidered", "Embroidered"),
        ("embroidery", "Embroidered"),
        ("geometric", "Geometric"),
        ("diamond", "Diamond"),
        ("zigzag", "Zigzag"),
        ("chevron", "Chevron"),
        ("scallop", "Scallop"),
        ("scroll", "Scroll"),
        ("leaf", "Leaf"),
        ("leaves", "Leaf"),
        ("mesh", "Mesh"),
        ("net", "Net"),
        ("striped", "Striped"),
        ("stripe", "Striped"),
        ("polka", "Polka Dot"),
        ("lace", "Lace"),
        ("cutwork", "Cutwork"),
        ("corded", "Corded"),
        ("beaded", "Beaded"),
        ("lattice", "Lattice")
    ]

    detected_styles = []

    for keyword, label in styles:

        if keyword in text and label not in detected_styles:

            detected_styles.append(label)


    # --------------------------------------
    # Build product name
    # --------------------------------------

    parts = []

    if detected_color:
        parts.append(detected_color)

    for style in detected_styles:

        if style not in parts:

            parts.append(style)

        if len(parts) >= 3:
            break


    parts.append("Lace")


    name = " ".join(parts)

    return name


# ==========================================
# PROCESS ALL PRODUCTS
# ==========================================

product_ids = list(
    metadata.keys()
)

print(
    "\nProducts to check:",
    len(product_ids)
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


    # ======================================
    # SKIP PRODUCTS ALREADY COMPLETED
    # ======================================

    if (
        product.get("name")
        and product.get("description")
    ):

        print(
            "Skipping already processed:",
            product_id
        )

        continue


    # ======================================
    # GET IMAGE PATH
    # ======================================

    image_path = product.get(
        "image",
        ""
    )

    if not image_path:

        print(
            "No image path found."
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


    # ======================================
    # CHECK IMAGE
    # ======================================

    if not os.path.exists(
        full_image_path
    ):

        print(
            "Image not found:",
            full_image_path
        )

        continue


    try:

        # ==================================
        # LOAD IMAGE
        # ==================================

        image = Image.open(
            full_image_path
        ).convert("RGB")


        # ==================================
        # FLORENCE DETAILED CAPTION
        # ==================================

        print(
            "Generating detailed description..."
        )

        task = (
            "<MORE_DETAILED_CAPTION>"
        )


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
                input_ids=inputs[
                    "input_ids"
                ],
                pixel_values=inputs[
                    "pixel_values"
                ],
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


        description = parsed.get(
            task,
            ""
        )


        if isinstance(
            description,
            dict
        ):

            description = str(
                description
            )


        description = (
            description
            .replace("\n", " ")
            .strip()
        )


        # ==================================
        # CREATE SHORT FRONTEND NAME
        # ==================================

        name = create_product_name(
            product_id,
            description
        )


        # ==================================
        # UPDATE METADATA
        # ==================================

        metadata[product_id][
            "name"
        ] = name

        metadata[product_id][
            "description"
        ] = description


        if "pattern" not in metadata[
            product_id
        ]:

            metadata[product_id][
                "pattern"
            ] = ""


        if "color" not in metadata[
            product_id
        ]:

            metadata[product_id][
                "color"
            ] = ""


        if "applications" not in metadata[
            product_id
        ]:

            metadata[product_id][
                "applications"
            ] = []


        # ==================================
        # SHOW RESULT
        # ==================================

        print(
            "Name:",
            name
        )

        print(
            "Description:",
            description
        )


        # ==================================
        # SAVE IMMEDIATELY
        # ==================================

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
print("METADATA GENERATION COMPLETE")
print("========================================")

print(
    "Total products:",
    len(metadata)
)

print(
    "Metadata saved to:",
    METADATA_FILE
)