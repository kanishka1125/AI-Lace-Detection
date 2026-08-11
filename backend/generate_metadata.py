import os
import json
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM

# =========================
# PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CATALOGUE_DIR = os.path.join(BASE_DIR, "catalogue")
METADATA_DIR = os.path.join(BASE_DIR, "metadata")

os.makedirs(METADATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    METADATA_DIR,
    "catalogue_metadata.json"
)

# =========================
# DEVICE
# =========================

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

# =========================
# LOAD EXISTING METADATA
# =========================

if os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"Existing metadata found: {len(metadata)} records")

else:

    metadata = {}

# =========================
# LOAD FLORENCE-2
# =========================

MODEL_ID = "microsoft/Florence-2-base"

print("Loading Florence-2...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
).to(device)

processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
)

print("Florence-2 loaded!")

# =========================
# FIND IMAGES
# =========================

image_files = []

for root, dirs, files in os.walk(CATALOGUE_DIR):

    for file in files:

        if file.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):

            image_files.append(
                os.path.join(root, file)
            )

print(f"Found {len(image_files)} images.")

# =========================
# GENERATE METADATA
# =========================

for i, image_path in enumerate(image_files, start=1):

    relative_path = os.path.relpath(
        image_path,
        CATALOGUE_DIR
    )

    relative_path = relative_path.replace("\\", "/")

    parts = relative_path.split("/")

    product_id = parts[0]

    filename = os.path.basename(image_path)

    # --------------------------------
    # SKIP IF ALREADY PROCESSED
    # --------------------------------

    existing_record = metadata.get(product_id)

    if existing_record:

        existing_image = existing_record.get("image", "")

        # Convert /catalogue/X/file.jpeg
        # into X/file.jpeg
        existing_image = existing_image.replace(
            "/catalogue/",
            ""
        ).lstrip("/")

        if existing_image == relative_path:

            print(
                f"Skipping already processed: "
                f"{relative_path}"
            )

            continue

    print(
        f"\nProcessing {i}/{len(image_files)}: "
        f"{relative_path}"
    )

    try:

        image = Image.open(image_path).convert("RGB")

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

        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=100,
            num_beams=3
        )

        generated_text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=False
        )[0]

        parsed_answer = processor.post_process_generation(
            generated_text,
            task=task,
            image_size=image.size
        )

        description = parsed_answer[task]

        # --------------------------------
        # ADD / UPDATE RECORD
        # --------------------------------

        metadata[product_id] = {

            "sku": product_id,

            "image": f"/catalogue/{relative_path}",

            "pattern": "",

            "color": "",

            "description": description,

            "applications": []

        }

        print("Description:", description)

        # --------------------------------
        # SAVE IMMEDIATELY
        # --------------------------------

        with open(
            OUTPUT_FILE,
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
            f"Saved! Total metadata records: "
            f"{len(metadata)}"
        )

    except Exception as e:

        print(
            f"ERROR processing {image_path}: {e}"
        )

# =========================
# COMPLETE
# =========================

print("\n================================")
print("METADATA GENERATION COMPLETE")
print("================================")

print(
    f"Found images: {len(image_files)}"
)

print(
    f"Metadata records: {len(metadata)}"
)

print(
    f"Saved to: {OUTPUT_FILE}"
)