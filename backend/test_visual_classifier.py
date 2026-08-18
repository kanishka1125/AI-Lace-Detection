from pathlib import Path
import random
import torch
import open_clip
from PIL import Image


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_DIR = PROJECT_ROOT / "backend" / "catalogue"


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "hf-hub:Marqo/marqo-fashionSigLIP"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("=" * 60)
print("VISUAL ATTRIBUTE TEST")
print("=" * 60)
print(f"Device: {DEVICE}")
print("Loading FashionSigLIP with OpenCLIP...")

model, _, preprocess = open_clip.create_model_and_transforms(
    MODEL_NAME,
    device=DEVICE
)

tokenizer = open_clip.get_tokenizer(MODEL_NAME)

model.eval()

print("FashionSigLIP loaded!")


# ============================================================
# CANDIDATES
# ============================================================

COLORS = [
    "white",
    "black",
    "pink",
    "red",
    "blue",
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
    "cloth",
    "embroidered lace",
    "floral lace",
    "guipure lace",
    "corded lace",
    "mesh lace",
    "sequin fabric",
]


# ============================================================
# CLASSIFICATION
# ============================================================

def classify(image, labels):

    # Fashion-focused prompts
    prompts = [
        f"a close-up product photo of {label}"
        for label in labels
    ]

    image_tensor = preprocess(image).unsqueeze(0).to(DEVICE)
    text_tensor = tokenizer(prompts).to(DEVICE)

    with torch.no_grad():

        image_features = model.encode_image(
            image_tensor,
            normalize=True
        )

        text_features = model.encode_text(
            text_tensor,
            normalize=True
        )

        similarity = (
            100.0
            * image_features
            @ text_features.T
        )

        probabilities = torch.softmax(
            similarity,
            dim=-1
        )[0]

    values, indices = torch.topk(
        probabilities,
        min(3, len(labels))
    )

    results = []

    for value, index in zip(values, indices):

        results.append(
            (
                labels[index.item()],
                float(value)
            )
        )

    return results


# ============================================================
# FIND IMAGES
# ============================================================

images = [
    p
    for p in CATALOGUE_DIR.rglob("*")
    if p.suffix.lower() in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }
]

print(f"\nCatalogue images: {len(images)}")

random.seed(42)

sample = random.sample(
    images,
    min(12, len(images))
)


# ============================================================
# TEST
# ============================================================

for number, path in enumerate(sample, 1):

    product_id = path.parent.name

    print()
    print("=" * 60)
    print(f"{number}/12: {product_id}")
    print(f"Image: {path.name}")
    print("=" * 60)

    try:

        image = Image.open(path).convert("RGB")

        print("\nCOLOR:")

        for label, score in classify(
            image,
            COLORS
        ):
            print(
                f"  {label:<12} {score:.3f}"
            )

        print("\nPATTERN:")

        for label, score in classify(
            image,
            PATTERNS
        ):
            print(
                f"  {label:<15} {score:.3f}"
            )

        print("\nTYPE:")

        for label, score in classify(
            image,
            TYPES
        ):
            print(
                f"  {label:<20} {score:.3f}"
            )

    except Exception as e:

        print(f"ERROR: {e}")


print()
print("=" * 60)
print("12-IMAGE VISUAL CLASSIFICATION TEST COMPLETE")
print("=" * 60)