from pathlib import Path
import json
import random
import math

import matplotlib.pyplot as plt
from PIL import Image


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CATALOGUE_DIR = PROJECT_ROOT / "backend" / "catalogue"
METADATA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "metadata"
    / "catalogue_metadata.json"
)


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_SIZE = 12
COLS = 3


# ============================================================
# LOAD METADATA
# ============================================================

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# ============================================================
# FIND ALL IMAGES
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

print(f"Total catalogue images: {len(images)}")


# ============================================================
# RANDOM SAMPLE
# ============================================================

random.seed()

sample = random.sample(
    images,
    min(SAMPLE_SIZE, len(images))
)


# ============================================================
# CREATE MATPLOTLIB GRID
# ============================================================

rows = math.ceil(len(sample) / COLS)

fig, axes = plt.subplots(
    rows,
    COLS,
    figsize=(18, rows * 6)
)

# Make axes always iterable
if hasattr(axes, "flatten"):
    axes = axes.flatten()
else:
    axes = [axes]


# ============================================================
# DISPLAY
# ============================================================

for i, image_path in enumerate(sample):

    ax = axes[i]

    product_id = image_path.parent.name

    try:
        image = Image.open(image_path).convert("RGB")

        ax.imshow(image)
        ax.axis("off")

        item = metadata.get(product_id, {})

        name = item.get("name", "—")
        color = item.get("color", "—")
        pattern = item.get("pattern", "—")
        description = item.get(
            "description",
            "No description"
        )

        # Keep description short for the figure
        description = (
            description
            .replace("\n", " ")
            .replace("<s>", "")
            .replace("</s>", "")
        )

        if len(description) > 180:
            description = description[:180] + "..."

        title = (
            f"{product_id}\n"
            f"NAME: {name}\n"
            f"COLOR: {color}   |   PATTERN: {pattern}\n\n"
            f"{description}"
        )

        ax.set_title(
            title,
            fontsize=8,
            loc="left",
            pad=8
        )

    except Exception as e:

        ax.text(
            0.5,
            0.5,
            f"ERROR\n{product_id}\n{e}",
            ha="center",
            va="center"
        )

        ax.axis("off")


# ============================================================
# HIDE EMPTY AXES
# ============================================================

for j in range(len(sample), len(axes)):
    axes[j].axis("off")


plt.suptitle(
    "Random Catalogue Metadata Validation",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout(
    rect=[0, 0, 1, 0.96]
)

plt.show()